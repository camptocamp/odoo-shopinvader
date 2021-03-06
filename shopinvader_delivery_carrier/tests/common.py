# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


class CommonCarrierCase(CommonConnectedCartCase):
    def setUp(self):
        super(CommonCarrierCase, self).setUp()
        self.free_carrier = self.env.ref("delivery.free_delivery_carrier")
        self.poste_carrier = self.env.ref("delivery.delivery_carrier")
        self.product_1 = self.env.ref("product.product_product_4b")

    def extract_cart(self, response):
        self.shopinvader_session["cart_id"] = response["set_session"][
            "cart_id"
        ]
        self.assertEqual(response["store_cache"], {"cart": response["data"]})
        return response["data"]

    def add_item(self, product_id, qty):
        return self.extract_cart(
            self.service.dispatch(
                "add_item", params={"product_id": product_id, "item_qty": qty}
            )
        )

    def update_item(self, item_id, qty):
        return self.extract_cart(
            self.service.dispatch(
                "update_item", params={"item_id": item_id, "item_qty": qty}
            )
        )

    def delete_item(self, item_id):
        return self.extract_cart(
            self.service.dispatch("delete_item", params={"item_id": item_id})
        )

    def _set_carrier(self, carrier):
        response = self.service.dispatch(
            "apply_delivery_method", params={"carrier": {"id": carrier.id}}
        )
        self.assertEqual(self.cart.carrier_id.id, carrier.id)
        return response["data"]

    def _apply_carrier_and_assert_set(self):
        cart = self._set_carrier(self.poste_carrier)
        self.assertEqual(cart["shipping"]["amount"]["total"], 20)
        return cart
