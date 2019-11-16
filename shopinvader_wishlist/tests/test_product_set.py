# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase


class ProductSet(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(ProductSet, cls).setUpClass()
        cls.prod_set = cls.env.ref("shopinvader_wishlist.wishlist_1")
        cls.prod_set.shopinvader_backend_id = cls.backend

    def test_create_no_variant(self):
        # ensure we can create a line from the product and we get the variant
        prod = self.env.ref("product.product_product_4b")
        line = self.prod_set.set_line_ids.create(
            {
                "product_set_id": self.prod_set.id,
                "product_id": prod.id,
                "quantity": 1,
            }
        )
        variant = prod.shopinvader_bind_ids[0]
        self.assertEqual(line.shopinvader_variant_id, variant)

    def test_create_no_product(self):
        # ensure we can create a line from the variant and we get the product
        prod = self.env.ref("product.product_product_4b")
        variant = prod.shopinvader_bind_ids[0]
        line = self.prod_set.set_line_ids.create(
            {
                "product_set_id": self.prod_set.id,
                "shopinvader_variant_id": variant.id,
                "quantity": 1,
            }
        )
        self.assertEqual(line.product_id, prod)
