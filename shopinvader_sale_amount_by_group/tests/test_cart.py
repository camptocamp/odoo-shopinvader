# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


class TestCart(CommonConnectedCartCase):
    def setUp(self):
        super().setUp()
        # TODO: This should be in setUpClass, but that should be changed
        # in shopinvader's CommonConnectedCartCase first
        # Configure multiple taxes on a sale order
        self.tax_10 = self.env.ref("shopinvader_sale_amount_by_group.tax_10")
        self.tax_20 = self.env.ref("shopinvader_sale_amount_by_group.tax_20")
        self.cart.order_line[0].tax_id = [(6, 0, self.tax_10.ids)]
        self.cart.order_line[1].tax_id = [(6, 0, self.tax_20.ids)]

    def test_cart(self):
        data = self.service.dispatch("update", params=dict())["data"]
        groups = [g["name"] for g in data["amount"]["amount_by_group"]]
        self.assertEqual(
            groups, (self.tax_10 | self.tax_20).mapped("tax_group_id.name")
        )
