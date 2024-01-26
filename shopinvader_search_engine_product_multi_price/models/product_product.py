# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    shopinvader_prices = fields.Json(compute="_compute_shopinvader_prices")

    @api.depends_context("index_id")
    def _compute_shopinvader_prices(self):
        index_id = self.env.context.get("index_id", False)
        index = self.env["se.index"].browse(index_id)
        for product in self:
            prices = {"default": product._get_price()}
            if index_id:
                for pricelist in index._get_pricelists():
                    price = product._get_price(pricelist=pricelist)
                    prices.update({f"{pricelist.id}": price})
            product.shopinvader_prices = prices
