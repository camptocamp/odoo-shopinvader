# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductSet(models.Model):

    _inherit = "product.set"

    shopinvader_backend_id = fields.Many2one(
        comodel_name="shopinvader.backend",
        help="If you are using this set for shopinvader customer "
        "you must select a backend.",
    )


class ProductSetLine(models.Model):

    _inherit = "product.set.line"

    shopinvader_variant_id = fields.Many2one(
        comodel_name="shopinvader.variant",
        compute="_compute_shopinvader_variant",
        inverse="_inverse_shopinvader_variant",
    )
    product_id = fields.Many2one(
        # make it required in the form
        required=False
    )

    @api.multi
    def _inverse_shopinvader_variant(self):
        for record in self:
            if record.shopinvader_variant_id and not record.product_id:
                record.product_id = record.shopinvader_variant_id.record_id

    @api.depends("product_id")
    def _compute_shopinvader_variant(self):
        for record in self:
            if record.product_id and not record.shopinvader_variant_id:
                variant = record.product_id.shopinvader_bind_ids.filtered(
                    lambda x: x.backend_id
                    == record.product_set_id.shopinvader_backend_id
                )
                record.shopinvader_variant_id = variant
