# Copyright 2020 Camptocamp SA
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def _parser_product(self):
        return super()._parser_product() + [
            # Add product packaging info
            "packaging"
        ]

    def _convert_one_line(self, line):
        res = super()._convert_one_line(line)
        res.update(
            {
                # Add packaging info relate to the line
                "packaging": self._get_line_packaging(line),
                "packaging_id": line.product_packaging.id,
                "packaging_qty": line.product_packaging_qty,
                "sell_only_by_packaging": line.product_id.sell_only_by_packaging,
            }
        )
        return res

    def _get_line_packaging(self, line):
        return line.product_id.with_context(
            **self._line_packaging_ctx(line)
        ).product_qty_by_packaging(line.product_uom_qty, with_contained=True)

    def _line_packaging_ctx(self, line):
        return {
            # consider only packaging that can be sold
            "_packaging_filter": lambda x: x.mapped(
                "packaging_type_id.can_be_sold"
            ),
            # to support multilang shop we rely on packaging type's name
            # which is already translatable.
            "_packaging_name_getter": lambda x: x.mapped(
                "packaging_type_id.name"
            ),
        }

    def _validator_packaging_info(self):
        return {
            "packaging_id": {
                "coerce": int,
                "nullable": True,
                "required": False,
                "type": "integer",
            },
            "packaging_qty": {
                "coerce": float,
                "type": "float",
                "required": False,
                "nullable": True,
            },
        }

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
        if params.get("packaging_id"):
            res.pop("product_uom_qty", None)
            res.update(self._packaging_values_from_params(params))
        return res

    def _packaging_values_from_params(self, params):
        if params.get("packaging_qty"):
            return {
                "product_packaging": params.get("packaging_id"),
                "product_packaging_qty": params.get("packaging_qty"),
            }
        return {}
