# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class PartnerAccess(Component):
    _inherit = "shopinvader.partner.access"

    def profile(self, partner):
        info = super().profile(partner)
        if partner != self.service_work.partner_user:
            info.update({"update": False, "readonly": True})
        return info

    def address(self, address_id):
        info = super().address(address_id)
        if (
            self.partner != self.partner_user
            and not address_id == self.partner_user
        ):
            info.update(
                {
                    "read": True,
                    "update": False,
                    "delete": False,
                    # easy check on client side for being able to edit
                    "readonly": False,
                }
            )
        return info
