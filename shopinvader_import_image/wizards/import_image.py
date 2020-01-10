# Copyright 2018 Akretion (http://www.akretion.com).
# Author: Sylvain Calador (<https://www.akretion.com>)
# Author: Saritha Sahadevan (<https://www.cybrosys.com>)
# Copyright 2020 Camptocamp (http://www.camptocamp.com)
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import base64
import csv
import io
import logging
import os
import sys
from contextlib import closing
from urllib.request import urlopen
from zipfile import ZipFile

from odoo import _, api, exceptions, fields, models
from odoo.tools.pycompat import csv_reader

_logger = logging.getLogger(__name__)

try:
    import validators
    import magic
except (ImportError, IOError) as err:
    _logger.debug(err)


class ProductImageImportWizard(models.TransientModel):

    _name = "shopinvader.import.product_image"

    storage_backend_id = fields.Many2one(
        "storage.backend", "Storage Backend", required=True
    )
    product_model = fields.Selection(
        [
            ("product.template", "Product template"),
            ("product.product", "Product variants"),
        ],
        string="Product Model",
        required=True,
    )
    overwrite = fields.Boolean("Overwrite image with same name")
    file_csv = fields.Binary("CSV files descriptors", required=True)
    csv_header = fields.Char(default="default_code,tag,path")
    csv_delimiter = fields.Char(default=",")
    file_zip = fields.Binary("ZIP with images", required=False)
    report = fields.Serialized(readonly=True)
    report_html = fields.Html(readonly=True)

    @api.model
    def _get_base64(self, file_path):
        binary = None
        if validators.url(file_path):
            binary = self._read_from_url(file_path)
        elif self.file_zip:
            binary = self._read_from_zip(file_path)
        mimetype = magic.from_buffer(binary, mime=True)
        return mimetype, binary and base64.encodestring(binary)

    def _read_from_url(self, file_path):
        return urlopen(file_path).read()

    def _read_from_zip(self, file_path):
        file_content = base64.b64decode(self.file_zip)
        with closing(io.BytesIO(file_content)) as zip_file:
            with ZipFile(zip_file, "r") as z:
                return z.read(file_path)

    def _get_lines(self):
        lines = []
        file_content = base64.b64decode(self.file_csv)
        with closing(io.BytesIO(file_content)) as file_csv:
            reader = csv_reader(file_csv, delimiter=self.csv_delimiter)
            headers = next(reader, None)

            if headers != self.csv_header.split(self.csv_delimiter):
                raise exceptions.UserError(
                    _("Invalid CSV file headers found! Expected: %s")
                    % self.csv_header
                )
            csv.field_size_limit(sys.maxsize)

            for row in reader:
                if not row:
                    continue
                default_code, tag_name, file_path = row
                lines.append(
                    {
                        "default_code": default_code,
                        "tag_name": tag_name,
                        "file_path": file_path,
                    }
                )
        return lines

    def do_import(self):
        self.report = self.report_html = False
        lines = self._get_lines()
        created, missing = self._do_import(
            lines, self.product_model, overwrite=self.overwrite
        )
        self.report = {"created": created, "missing": missing}
        report_html = (
            "<p><strong>Created</strong></p><p>{created}</p>"
            "<p><strong>Missing</strong></p><p>{missing}</p>"
        ).format(created=", ".join(created), missing=", ".join(missing))
        self.report_html = report_html

    def _do_import(self, lines, product_model, overwrite=False):
        created = []
        # do all queries at once
        lines_by_code = {x["default_code"]: x for x in lines}
        all_codes = list(lines_by_code.keys())
        _fields = ["default_code", "product_tmpl_id"]
        if self.product_model == "product.template":
            # exclude template id
            _fields = _fields[:1]
        products = self.env[self.product_model].search_read(
            [("default_code", "in", all_codes)], _fields
        )
        existing_by_code = {x["default_code"]: x for x in products}
        missing = [
            code for code in all_codes if not existing_by_code.get(code)
        ]

        all_tags = [x["tag_name"] for x in lines]
        tags = self.env["image.tag"].search_read(
            [("name", "in", all_tags)], ["name"]
        )
        tag_by_name = {x.name: x for x in tags}

        file_obj = self.env["storage.file"]
        image_obj = self.env["storage.image"]
        relation_obj = self.env["product.image.relation"]

        for prod in products:
            line = lines_by_code[prod["default_code"]]
            file_path = line["file_path"]
            file_vals = self._prepare_file_values(file_path)
            file_id = file_obj.create(file_vals)
            tag_id = tag_by_name.get(line["tag_name"])

            image = image_obj.create(
                {
                    "file_id": file_id.id,
                    "name": file_vals["name"],
                    "alt_name": file_vals["name"],
                }
            )

            if overwrite:
                domain = [
                    ("image_id.name", "=", image.name),
                    ("tag_id", "=", tag_id),
                    ("product_tmpl_id", "=", prod["id"]),
                ]
                relation_obj.search(domain).unlink()

            if product_model == "product.template":
                tmpl_id = prod["id"]
            elif product_model == "product.product":
                tmpl_id = prod["product_tmpl_id"]

            relation_obj.create(
                {
                    "image_id": image.id,
                    "tag_id": tag_id,
                    "product_tmpl_id": tmpl_id,
                }
            )
            created.append(prod["default_code"])

        return created, missing

    def _prepare_file_values(self, file_path, filetype="image"):
        name = os.path.basename(file_path)
        mimetype, file_b64 = self._get_base64(file_path)
        vals = {
            "data": file_b64,
            "name": name,
            "file_type": filetype,
            "mimetype": mimetype,
            "backend_id": self.storage_backend_id.id,
        }
        return vals
