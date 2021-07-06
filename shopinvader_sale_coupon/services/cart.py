# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.exceptions import UserError

from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    # Public Methods

    def apply_coupon(self, code):
        cart = self._get()
        self._apply_coupon(cart, code)
        return self._to_json(cart)

    # Private Methods

    def _apply_coupon(self, cart, code):
        """
        Apply a coupon or promotion code.
        :return: Boolean
        """
        SaleCouponApplyCode = self.env["sale.coupon.apply.code"].sudo()
        status = SaleCouponApplyCode.apply_coupon(cart, code)
        if status.get("error"):
            raise UserError(status["error"])
        return not status

    # Private Overrides

    def _update(self, cart, params):
        coupon_code = params.pop("coupon_code", None)
        res = super()._update(cart, params)
        if coupon_code:
            self._apply_coupon(cart, coupon_code)
        return res

    def _add_item(self, cart, params):
        res = super()._add_item(cart, params)
        cart.recompute_coupon_lines()
        return res

    def _update_item(self, cart, params, item=False):
        res = super()._update_item(cart, params, item)
        cart.recompute_coupon_lines()
        return res

    def _delete_item(self, cart, params):
        res = super()._delete_item(cart, params)
        cart.recompute_coupon_lines()
        return res

    def _get_lines_to_copy(self, cart):
        return super()._get_lines_to_copy(cart).filtered(lambda l: not l.is_reward_line)

    # Validator

    def _validator_apply_coupon(self):
        return {}

    def _validator_update(self):
        res = super()._validator_update()
        res.update(
            {
                "coupon_code": {
                    "type": "string",
                    "required": False,
                    "nullable": True,
                }
            }
        )
        return res
