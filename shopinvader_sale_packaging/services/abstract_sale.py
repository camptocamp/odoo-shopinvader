# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _name = "shopinvader.abstract.sale.service"
    _inherit = [
        "shopinvader.abstract.sale.service",
        "shopinvader.packaging.service.mixin",
    ]

    def _parser_product(self):
        return super()._parser_product() + [
            "packaging",
            "sell_only_by_packaging",
        ]

    def _convert_one_line(self, line):
        res = super()._convert_one_line(line)
        pkg_vals = {
            "packaging": None,
            "packaging_qty": 0.0,
            "packaging_by_qty": [],
        }
        if line.product_packaging:
            pkg_vals.update(self._convert_one_line_packaging(line))
        res.update(pkg_vals)
        return res

    def _convert_one_line_packaging(self, line):
        return {
            "packaging": {
                "id": line.product_packaging.id,
                # packaging type name is translatable, better than pkg.name
                "name": line.product_packaging.packaging_type_id.name,
            },
            "packaging_qty": line.product_packaging_qty,
            "packaging_by_qty": self._packaging_info_by_qty(
                line.product_id, line.product_uom_qty
            ),
        }
