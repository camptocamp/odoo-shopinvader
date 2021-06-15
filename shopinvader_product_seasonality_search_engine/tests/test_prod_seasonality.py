# Copyright 2021 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import exceptions

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
        cls.backend._add_missing_indexes()

    def _create_line(self, **kw):
        vals = {
            "seasonal_config_id": self.seasonal_conf.id,
            "date_start": "2021-05-10",
            "date_end": "2021-05-16",
            "monday": True,
            "tuesday": True,
            "product_id": self.env.ref("product.product_product_2").id,
            "backend_id": self.backend.id,
        }
        vals.update(kw)
        return self.env["shopinvader.seasonal.config.line"].create(vals)

    def test_no_index(self):
        self.backend.index_ids.unlink()
        s_line = self._create_line()
        # There's no index on the backend yet
        self.assertFalse(s_line.index_id)

    def test_index(self):
        index = self.backend.index_ids.filtered(
            lambda x: x.model_id.model == "shopinvader.seasonal.config.line"
        )
        self.assertTrue(index)
        s_line = self._create_line()
        # There's no index on the backend yet
        self.assertEqual(s_line.index_id, index)

    def test_json_data(self):
        s_line = self._create_line(monday=False, tuesday=False)
        # Not computed yet for search engine
        self.assertEqual(s_line.get_shop_data(), {})
        s_line.recompute_json()
        expected = {
            "config_id": s_line.seasonal_config_id.id,
            "date_end": "2021-05-16T02:00:00+02:00",
            "date_start": "2021-05-10T02:00:00+02:00",
            "id": s_line.id,
            "objectID": s_line.record_id.id,
            "product_id": s_line.product_id.id,
            "weekdays": [2, 3, 4, 5, 6],
        }
        self.assertEqual(s_line.get_shop_data(), expected)
        # change value, no repercution on indexed data
        s_line.monday = True
        self.assertEqual(s_line.get_shop_data(), expected)
        # until data is recomputed
        s_line.recompute_json()
        expected["weekdays"] = [0, 2, 3, 4, 5, 6]
        self.assertEqual(s_line.get_shop_data(), expected)

    def test_unlink(self):
        s_line = self._create_line(monday=False, tuesday=False)
        # record is new, not indexed yet, it can be deleted
        self.assertEqual(s_line.sync_state, "new")
        s_line.record_id.unlink()
        self.assertFalse(s_line.exists())
        s_line = self._create_line(monday=False, tuesday=False)
        s_line.sync_state = "done"
        with self.assertRaises(exceptions.UserError) as err:
            s_line.record_id.unlink()
        # Somehow `assertRaisesRegex` fails even if the msg is the same, fallback to this
        self.assertEqual(err.exception.name, s_line._msg_cannot_delete_active())
        s_line.active = False
        self.assertEqual(s_line.sync_state, "to_update")
        with self.assertRaises(exceptions.UserError) as err:
            s_line.record_id.unlink()
        self.assertEqual(
            err.exception.name, s_line._msg_cannot_delete_not_synchronized()
        )
        s_line.sync_state = "done"
        s_line.record_id.unlink()
        self.assertFalse(s_line.exists())
