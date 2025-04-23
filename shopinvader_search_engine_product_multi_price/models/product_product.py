# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    shopinvader_price_by_pricelist = fields.Json(
        compute="_compute_shopinvader_price_by_pricelist"
    )

    @api.depends_context("index_id")
    def _compute_shopinvader_price_by_pricelist(self):
        index_id = self.env.context.get("index_id", False)
        index = self.env["se.index"].browse(index_id)
        prices = {}
        if index_id:
            for pricelist in index._get_pricelists():
                price_unit_list = self._get_price(pricelist=pricelist)
                prices[pricelist.id] = price_unit_list
        for product in self:
            price_by_pricelist = {}
            if index_id:
                for pricelist in index._get_pricelists():
                    if product.id in prices[pricelist.id]:
                        price_by_pricelist.update(
                            {pricelist.id: prices[pricelist.id][product.id]}
                        )
            product.shopinvader_price_by_pricelist = price_by_pricelist
