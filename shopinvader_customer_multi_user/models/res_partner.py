# Copyright 2019 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import random
import string

from odoo import api, fields, models


def _generate_token(length=8):
    return "".join(
        random.choice(string.ascii_letters + string.digits)
        for __ in range(length)
    )


class ResPartner(models.Model):

    _inherit = "res.partner"

    invader_user_token = fields.Char(readonly=True, index=True)
    type = fields.Selection(
        selection_add=[("invader_client_user", "Invader client user")]
    )

    _sql_constraints = [
        (
            "unique_invader_user_token",
            "unique(invader_user_token)",
            "Already exists in database",
        )
    ]

    @api.model
    def _generate_invader_user_token(self, length=8):
        """Generate a random token."""
        _token = _generate_token(length=length)
        while self.find_by_invader_user_token(_token):
            _token = _generate_token()
        return _token

    @api.model
    def find_by_invader_user_token(self, token):
        return self.search([("invader_user_token", "=", token)], limit=1)

    @api.multi
    def assign_invader_user_token(self, token=None):
        token = token or self._generate_invader_user_token()
        self.write({"invader_user_token": token})

    def invader_client_user_type(self):
        return "invader_client_user"

    @api.multi
    def is_invader_user(self):
        self.ensure_one()
        return self.type == self.invader_client_user_type()
