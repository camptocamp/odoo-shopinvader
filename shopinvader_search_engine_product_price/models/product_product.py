# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    shopinvader_price = fields.Json(compute="_compute_shopinvader_price")

    @api.depends_context("index_id")
    def _compute_shopinvader_price(self):
        index_id = self.env.context.get("index_id", False)
        index = self.env["se.index"].browse(index_id)
        pricelist = None
        if index_id:
            pricelist = index._get_pricelist()
        price_unit_list = self._get_price(pricelist=pricelist)
        for record in self:
            record.shopinvader_price = price_unit_list[record.id]
