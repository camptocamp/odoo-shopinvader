# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def store(self, **params):
        """Stores the current cart"""
        cart = self._get(create_if_not_found=False)
        if not cart or not self._is_logged_in():
            return {}
        self._store(cart, **params)
        return self._to_json(self.env["sale.order"].browse())

    def _store(self, cart, **params):
        """Stores the given cart"""
        cart.typology = "stored"

    def _validator_store(self):
        return {}
