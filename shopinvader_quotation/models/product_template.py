# Copyright 2017-2018 Akretion (http://www.akretion.com).
# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    shop_only_quotation = fields.Boolean(
        string="Shopinvader: Only for Quotation",
        compute="_compute_shop_only_quotation",
        inverse="_inverse_shop_only_quotation",
    )

    @api.depends("product_variant_ids.shop_only_quotation")
    def _compute_shop_only_quotation(self):
        for rec in self:
            if len(rec.product_variant_ids) == 1:
                rec.shop_only_quotation = rec.product_variant_ids.shop_only_quotation
            else:
                rec.shop_only_quotation = False

    def _inverse_shop_only_quotation(self):
        for rec in self:
            if len(rec.product_variant_ids) == 1:
                rec.product_variant_ids.shop_only_quotation = rec.shop_only_quotation
