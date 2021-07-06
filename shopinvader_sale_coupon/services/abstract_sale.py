# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _is_item(self, line):
        return super()._is_item(line) and not line.is_reward_line

    def _convert_one_sale(self, sale):
        res = super()._convert_one_sale(sale)
        res.update(
            {
                "promo_code": sale.promo_code,
                "reward_amount": sale.reward_amount,
                "applied_coupon_ids": self._convert_coupon_coupons(
                    sale.applied_coupon_ids
                ),
                "generated_coupon_ids": self._convert_coupon_coupons(
                    sale.generated_coupon_ids
                ),
                "no_code_promo_program_ids": self._convert_coupon_programs(
                    sale.no_code_promo_program_ids
                ),
                "code_promo_program_id": self._convert_coupon_programs(
                    sale.code_promo_program_id
                ),
            }
        )
        return res

    def _convert_one_line(self, line):
        res = super()._convert_one_line(line)
        res.update(
            {
                "is_reward_line": line.is_reward_line,
            }
        )
        return res

    def _convert_one_coupon_program(self, program):
        return {
            "id": program.id,
            "name": program.name,
        }

    def _convert_one_coupon_coupon(self, coupon):
        return {
            "id": coupon.id,
            "code": coupon.code,
            "state": coupon.state,
            "expiration_date": coupon.expiration_date,
            "partner_id": coupon.partner_id.id,
            "program_id": coupon.program_id.id,
        }

    def _convert_coupon_programs(self, programs):
        return {
            "items": [
                self._convert_one_coupon_program(program) for program in programs
            ],
            "count": len(programs),
        }

    def _convert_coupon_coupons(self, coupons):
        return {
            "items": [self._convert_one_coupon_coupon(coupon) for coupon in coupons],
            "count": len(coupons),
        }
