# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock
from odoo.addons.shopinvader.tests.common import CommonCase


class CommonWishlistCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(CommonWishlistCase, cls).setUpClass()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.wl_params = {
            "name": "My new wishlist :)",
            "ref": "MY_NEW",
            "partner_id": cls.partner.id,
            "lines": [
                {
                    "product_id": cls.env.ref(
                        "shopinvader.product_product_39"
                    ).id,
                    "quantity": 1.0,
                },
                {
                    "product_id": cls.env.ref(
                        "shopinvader.product_product_41"
                    ).id,
                    "quantity": 5.0,
                },
            ],
        }

    def setUp(self, *args, **kwargs):
        super(CommonWishlistCase, self).setUp(*args, **kwargs)
        with self.work_on_services(partner=self.partner) as work:
            self.wishlist_service = work.component(usage="wishlist")

    def _check_data(self, record, data):
        data_lines = data.pop("lines", [])
        rec_data = record._convert_to_write(record._cache)
        rec_lines = record.set_line_ids
        for key in data:
            self.assertEqual(rec_data[key], data[key])
        for dline in data_lines:
            list_line = rec_lines.filtered(
                lambda x: x.product_id.id == dline["product_id"]
            )
            self.assertTrue(list_line)
            for key in ("quantity", "sequence"):
                if key in dline:
                    self.assertEqual(list_line[key], dline.get(key))


class WishlistCase(CommonWishlistCase):
    @classmethod
    def setUpClass(cls):
        super(WishlistCase, cls).setUpClass()
        cls.prod_set = cls.env.ref("shopinvader_wishlist.wishlist_1")
        cls.prod_set.shopinvader_backend_id = cls.backend

    def test_create(self):
        params = dict(self.wl_params)
        res = self.wishlist_service.dispatch("create", params=params)["data"]
        record = self.env["product.set"].browse(res["id"])
        self.assertEqual(record.partner_id, self.partner)
        self._check_data(record, params)

    def test_update(self):
        params = {"name": "Baz"}
        self.assertEqual(self.prod_set.name, "Wishlist 1")
        self.wishlist_service.dispatch(
            "update", self.prod_set.id, params=params
        )
        self.assertEqual(self.prod_set.name, "Baz")

    def test_search(self):
        res = self.wishlist_service.dispatch(
            "search", params={"scope": {"typology": "foo"}}
        )
        self.assertEqual(res["size"], 0)
        res = self.wishlist_service.dispatch(
            "search", params={"scope": {"ref": "WISH_1"}}
        )
        self.assertEqual(res["size"], 1)
        self.assertEqual(res["data"][0]["ref"], "WISH_1")

    def test_get(self):
        res = self.wishlist_service.dispatch("get", self.prod_set.id)
        self.assertEqual(res["ref"], "WISH_1")

    def test_delete(self):
        self.wishlist_service.delete(self.prod_set.id)
        self.assertFalse(self.prod_set.exists())

    def _bind_product(self, product):
        bind_wizard_model = self.env["shopinvader.variant.binding.wizard"]
        bind_wizard = bind_wizard_model.create(
            {
                "backend_id": self.backend.id,
                "product_ids": [(6, 0, [product.id])],
            }
        )
        bind_wizard.bind_products()

    def test_add_to_cart(self):
        prod = self.env.ref("product.product_product_4b")
        # make sure no binding exists
        prod.shopinvader_bind_ids.unlink()

        with self.work_on_services(partner=self.partner) as work:
            cart_service = work.component(usage="cart")
        cart = cart_service._get()
        # no line yet
        self.assertFalse(cart.order_line)

        # make sure the wishlist service use the same cart
        with mock.patch.object(type(cart_service), "_get") as mocked:
            mocked.return_value = cart
            self.wishlist_service.add_to_cart(self.prod_set.id)
            # no binding for the product -> no line added
            self.assertFalse(cart.order_line)
            # bind the product and try again
            self._bind_product(prod)
            self.wishlist_service.add_to_cart(self.prod_set.id)
            self.assertEqual(cart.order_line[0].product_id, prod)

    def test_jsonify(self):
        res = self.wishlist_service._to_json_one(self.prod_set)
        self.assertEqual(res["ref"], "WISH_1")
        self.assertEqual(res["name"], "Wishlist 1")
        self.assertEqual(res["typology"], "wishlist")
        self.assertEqual(
            res["partner"], {"id": self.partner.id, "name": self.partner.name}
        )
        variant = self.env.ref(
            "product.product_product_4b"
        ).shopinvader_bind_ids[0]
        res_line = res["lines"][0]
        self.assertEqual(res_line["id"], self.prod_set.set_line_ids[0].id)
        self.assertEqual(res_line["quantity"], 1)
        self.assertEqual(res_line["sequence"], 10)
        self.assertEqual(res_line["product"]["id"], variant.id)
        self.assertEqual(res_line["product"]["name"], variant.name)
        self.assertEqual(res_line["product"]["sku"], variant.default_code)
        self.assertEqual(res_line["product"]["url_key"], variant.url_key)
        self.assertIn("price", res_line["product"])
        self.assertIn("image", res_line["product"])
