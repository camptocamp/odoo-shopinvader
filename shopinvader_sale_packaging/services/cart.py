# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component


class CartService(Component):
    _name = "shopinvader.cart.service"
    _inherit = [
        "shopinvader.cart.service",
        "shopinvader.packaging.service.mixin",
    ]

    def _parser_product(self):
        return super()._parser_product() + ["packaging"]

    def _convert_one_line(self, line):
        res = super()._convert_one_line(line)
        if line.product_packaging:
            res.update(
                {
                    # Add packaging info related to the line
                    "available_packaging": self._packaging_info_by_qty(
                        line.product_id, line.product_uom_qty
                    ),
                    "packaging": line.product_packaging.jsonify(
                        ["id", "name"]
                    )[0],
                    "packaging_qty": line.product_packaging_qty,
                    "sell_only_by_packaging": line.product_id.sell_only_by_packaging,
                }
            )
        return res

    def _validator_add_item(self):
        res = super()._validator_add_item()
        res.update(self._validator_packaging_info())
        return res

    def _validator_update_item(self):
        res = super()._validator_update_item()
        res.update(self._validator_packaging_info())
        return res

    def _prepare_cart_item(self, params, cart):
        # TODO: in theory we should be able to skip prod qty
        # since it's computed in `sale_order_line_packaging_qty `
        res = super()._prepare_cart_item(params, cart)
        res.update(self._packaging_values_from_params(params))
        return res

    def _get_line_copy_vals(self, line):
        res = super()._get_line_copy_vals(line)
        if line.product_packaging_qty:
            res.update(
                {
                    "packaging_id": line.product_packaging.id,
                    "packaging_qty": line.product_packaging_qty,
                }
            )
        return res

    def _upgrade_cart_item_quantity_vals(self, item, params, **kw):
        res = super()._upgrade_cart_item_quantity_vals(item, params, **kw)
        pkg_params = self._packaging_values_from_params(params)
        if pkg_params:
            res.pop("product_uom_qty", None)
            res.update(pkg_params)
        return res
