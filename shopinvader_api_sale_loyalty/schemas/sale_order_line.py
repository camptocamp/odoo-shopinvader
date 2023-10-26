# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_api_cart.schemas import SaleOrderLine as BaseSaleOrderLine


class SaleOrderLine(BaseSaleOrderLine):
    is_reward_line: bool

    @classmethod
    def from_sale_order_line(cls, odoo_rec):
        obj = super().from_sale_order_line(odoo_rec)
        obj.is_reward_line = odoo_rec.is_reward_line
        return obj
