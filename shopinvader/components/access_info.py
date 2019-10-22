# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class PartnerAccess(Component):
    """Define access rules to partner from client side."""

    _name = "shopinvader.partner.access"
    _inherit = "base.shopinvader.component"
    _usage = "access.info"
    _apply_on = "res.partner"

    def profile(self, partner=None):
        return {
            "create": False,
            "read": True,
            "update": True,
            "delete": False,
            # easy check on client side for being able to edit
            "readonly": False,
        }

    def address(self, address_id):
        return {
            # TODO: create should be a global params
            "create": True,
            "read": True,
            "update": True,
            "delete": True,
            # easy check on client side for being able to edit
            "readonly": False,
        }
