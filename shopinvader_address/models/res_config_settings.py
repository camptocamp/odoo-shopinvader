# Copyright 2024 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    shopinvader_allow_so_invoice_address_update = fields.Boolean(
        related="company_id.shopinvader_allow_so_invoice_address_update",
        readonly=False,
    )
    shopinvader_allow_so_delivery_address_update = fields.Boolean(
        related="company_id.shopinvader_allow_so_delivery_address_update",
        readonly=False,
    )
