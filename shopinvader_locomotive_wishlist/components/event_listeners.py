# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if


class ShopinvaderWishlistListener(Component):
    """Export info on partner when wishlist is updated.
    """

    _name = "shopinvader.wishlist.event.listener"
    _inherit = "base.connector.listener"

    _apply_on = ["product.set"]

    def _get_fields_to_export(self):
        return ["name", "set_line_ids"]

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_create(self, record, fields=None):
        fields_to_export = self._get_fields_to_export()
        if not set(fields_to_export).intersection(set(fields)):
            return
        self._export_partner_info(record, fields=fields)

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        fields_to_export = self._get_fields_to_export()
        if not set(fields_to_export).intersection(set(fields)):
            return
        self._export_partner_info(record, fields=fields)

    def on_record_unlink(self, record, fields=None):
        self._export_partner_info(record, fields=fields)

    def _export_partner_info(self, record, fields=None):
        for binding in record.mapped("partner_id.shopinvader_bind_ids"):
            binding.with_delay().export_record(_fields=fields)