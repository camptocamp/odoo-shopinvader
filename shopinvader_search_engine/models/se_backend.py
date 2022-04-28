# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools


class SeBackend(models.Model):

    _inherit = "se.backend"

    primary_webshop_id = fields.Many2one('shopinvader.backend')
    linked_shops_ids = fields.One2many("shopinvader.backend", "se_backend_id")
