# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class WishlistService(Component):
    _inherit = "shopinvader.wishlist.service"

    # TODO: if we had a centralized way to retrieve prices for customers
    # we could avoid this module completely.
    def _json_parser_product(self, rec, fname):
        res = super()._json_parser_product(rec, fname)
        customer_price_service = self.component(usage="customer_price")
        res["price"] = customer_price_service._get_price(
            rec.shopinvader_variant_id, fname
        )
        return res
