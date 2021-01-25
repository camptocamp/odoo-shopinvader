# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ShopinvaderAddressValidate(models.TransientModel):
    """
    Wizard used to validate customers' addresses for a given backend.
    """

    _name = "shopinvader.address.validate"
    _description = "Shopinvader address validate"

    backend_ids = fields.Many2many(
        comodel_name="shopinvader.backend",
        string="ShopInvader Backends",
        required=True,
        readonly=False,
        default=lambda self: self._default_backend_ids(),
    )
    partner_ids = fields.Many2many(
        string="Addresses",
        comodel_name="res.partner",
        default=lambda self: self._default_partner_ids(),
        required=True,
    )
    is_shopinvader_active = fields.Boolean(default=True)

    def _default_backend_ids(self):
        return self.env.context.get("backend_ids") or self.env[
            "shopinvader.backend"
        ].search([])

    def _default_partner_ids(self):
        return self.env.context.get("active_ids")

    def action_apply(self):
        self.ensure_one()
        # TODO: filter out addresses not belonging to any bound partner?
        records = self.partner_ids.filtered_domain(
            [("is_shopinvader_active", "!=", self.is_shopinvader_active)]
        )
        records.write({"is_shopinvader_active": self.is_shopinvader_active})
        if self.is_shopinvader_active:
            for record in records:
                record._event("on_shopinvader_validate").notify(
                    record, self.backend_ids
                )
        return {"type": "ir.actions.act_window_close"}
