# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase, CommonTestDownload


class QuotationDownloadCase(CommonCase, CommonTestDownload):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass(*args, **kwargs)
        cls.quotation = cls.env.ref("shopinvader.sale_order_2")
        cls.quotation.write({"typology": "quotation"})
        cls.partner = cls.env.ref("shopinvader.partner_1")
        with cls.work_on_services(partner=cls.partner) as work:
            cls.service = work.component(usage="quotations")

    def test_quotation_download(self):
        self.assertEqual(self.quotation.typology, "quotation")
        self._test_download_allowed(self.service, self.quotation)
