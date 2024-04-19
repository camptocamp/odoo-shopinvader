# Copyright 2024 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_api_cart.schemas import (
    CartUpdateInput as BaseCartUpdateInput,
)


class CartUpdateInput(BaseCartUpdateInput, extends=True):

    current_step: str | None = None
    next_step: str | None = None

    def convert_to_sale_write(self, cart):
        vals = super().convert_to_sale_write(cart)
        if self.current_step or self.next_step:
            step_data = cart._cart_step_update_vals(
                current_step=self.current_step, next_step=self.next_step
            )
            vals.update(step_data)
        return vals
