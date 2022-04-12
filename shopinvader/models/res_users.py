# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class Users(models.Model):
    _inherit = 'res.users'

    # pylint: disable=W8102,W8106
    def copy(self, default=None):
        # due to check introduces in shopinvader copying for users is not allowed
        # we add an email here so in case of user check will pass
        self.ensure_one()
        default = dict(default or {})
        if 'email' not in default:
            default['email'] = _("%s (copy)", self.email)
        return super(Users, self).copy(default)
