# Copyright 2024 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    shopinvader_allow_so_invoice_address_update = fields.Boolean(
        string="Allow sale order invoice address modification",
    )
    shopinvader_allow_so_delivery_address_update = fields.Boolean(
        string="Allow sale order delivery address modification",
    )
