# Copyright 2021 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader_search_engine.tests.test_backend import BackendCaseBase


class TestProductSeasonalityCase(BackendCaseBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.seasonal_conf = cls.env["seasonal.config"].create(
            {
                "name": "Test seasonal conf",
            }
        )

    def _create_line(self):
        return self.env["shopinvader.seasonal.config.line"].create(
            {
                "seasonal_config_id": self.seasonal_conf.id,
                "date_start": "2021-05-10",
                "date_end": "2021-05-16",
                "product_id": self.env.ref("product.product_product_2").id,
                "backend_id": self.backend.id,
            }
        )

    def test_no_index(self):
        s_line = self._create_line()
        # There's no index on the backend yet
        self.assertFalse(s_line.index_id)

    def test_index(self):
        self.backend._add_missing_indexes()
        index = self.backend.index_ids.filtered(
            lambda x: x.model_id.model == "shopinvader.seasonal.config.line"
        )
        self.assertTrue(index)
        s_line = self._create_line()
        # There's no index on the backend yet
        self.assertEqual(s_line.index_id, index)
