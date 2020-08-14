# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _convert_one_line(self, line):
        res = super()._convert_one_line(line)
        pkg_vals = {"packaging": None, "packaging_qty": 0.0}
        if line.product_packaging:
            pkg_vals.update(
                {
                    "packaging": line.product_packaging.jsonify(
                        ["id", "name"]
                    )[0],
                    "packaging_qty": line.product_packaging_qty,
                }
            )
        res.update(pkg_vals)
        return res
