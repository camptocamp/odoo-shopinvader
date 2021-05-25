# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.base_sparse_field.models.fields import Serialized


class ShopinvaderSeasonalConfig(models.Model):
    _name = "shopinvader.seasonal.config.line"
    _inherit = ["shopinvader.binding"]
    _inherits = {"seasonal.config.line": "record_id"}
    _description = "Shopinvader Seasonal Config Binding"

    record_id = fields.Many2one(
        "seasonal.config.line", required=True, ondelete="cascade", index=True
    )
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

    _exporter_xid = "shopinvader_product_seasonality.ir_exp_seasonal_config_line"

    def _get_shop_data(self):
        """Compute shop data base_jsonify parser."""
        exporter = self.env.ref(self._exporter_xid)
        return self.jsonify(exporter.get_json_parser(), one=True)
