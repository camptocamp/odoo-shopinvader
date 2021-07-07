# Copyright 2017 Akretion (http://www.akretion.com).
# Copyright 2021 Camptocamp (http://www.camptocamp.com)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from odoo.addons.shopinvader.tests.test_customer import TestCustomerCommon


class TestCustomer(TestCustomerCommon):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        # TODO: This should be in setUpClass, but it should be changed
        # in shopinvader TestCustomerCommon
        self.data.update(
            {
                "external_id": "jdoe",
                "name": "John Doe",
                "firstname": "John",
                "lastname": "Doe",
            }
        )

    def test_create_customer_firstname(self):
        """Test that we can create partners using firstname and lastname"""
        params = self.data.copy()
        params.pop("name")
        partner_id = self.service.dispatch("create", params=params)["data"]["id"]
        partner = self.env["res.partner"].browse(partner_id)
        self._test_partner_data(partner, self.data)

    def test_create_customer_normal(self):
        """Test that we can create partners using name"""
        params = self.data.copy()
        params.pop("firstname")
        params.pop("lastname")
        partner_id = self.service.dispatch("create", params=params)["data"]["id"]
        partner = self.env["res.partner"].browse(partner_id)
        self._test_partner_data(partner, self.data)

    def test_create_customer_exclude(self):
        """Test that we can't use name with firstname and lastname"""
        # Case 1: name, firstname and lastname can't all be together
        params = self.data.copy()
        with self.assertRaises(UserError):
            self.service.dispatch("create", params=params)
        # Case 2: name and firstname can't be together
        params = self.data.copy()
        params.pop("lastname")
        with self.assertRaises(UserError):
            self.service.dispatch("create", params=params)
        # Case 3: name and lastname can't be together
        params = self.data.copy()
        params.pop("firstname")
        with self.assertRaises(UserError):
            self.service.dispatch("create", params=params)
