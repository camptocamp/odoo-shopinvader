# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.base_sparse_field.models.fields import Serialized


class ShopinvaderSeasonalConfigLine(models.Model):
    _name = "shopinvader.seasonal.config.line"
    _inherit = ["shopinvader.binding"]
    _inherits = {"seasonal.config.line": "record_id"}
    _description = "Shopinvader Seasonal Config Binding"

    record_id = fields.Many2one(
        "seasonal.config.line", required=True, ondelete="cascade", index=True
    )
    display_name = fields.Char(related="record_id.display_name")
    weekdays = Serialized(
        default=[],
        compute="_compute_weekdays",
        help="List of weekdays numbers (zero-based)",
    )

    def _compute_weekdays_depends(self):
        return (
            "record_id.monday",
            "record_id.tuesday",
            "record_id.wednesday",
            "record_id.thursday",
            "record_id.friday",
            "record_id.saturday",
            "record_id.sunday",
        )

    @api.depends(lambda self: self._compute_weekdays_depends())
    def _compute_weekdays(self):
        weekday_fields = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        values = {x["id"]: x for x in self.read(weekday_fields)}
        for rec in self:
            weekdays = []
            for i, day in enumerate(weekday_fields):
                if values[rec.id].get(day):
                    weekdays.append(i)
            rec.weekdays = weekdays

    def get_shop_data(self):
        """Return data for the shop."""
        return self._get_shop_data()

    def _get_shop_data_exporter(self):
        exporter_xid = "shopinvader_product_seasonality.ir_exp_seasonal_config_line"
        return self.env.ref(exporter_xid)

    def _get_shop_data(self):
        """Compute shop data base_jsonify parser."""
        exporter = self._get_shop_data_exporter()
        return self.jsonify(exporter.get_json_parser(), one=True)

    def create_bindings_from_lines(self, config_lines):
        to_create = []
        all_backends = config_lines.shopinvader_bind_ids.backend_id
        for backend in all_backends:
            existing = self.search(
                [
                    ("record_id", "in", config_lines.ids),
                    ("backend_id", "=", backend.id),
                ]
            )
            missing = config_lines - existing.record_id
            for line in missing:
                to_create.append(self._prepare_config_line_values(backend, line))
        return self.create(to_create)

    def _prepare_config_line_values(self, backend, line):
        return {
            "backend_id": backend.id,
            "record_id": line.id,
        }
