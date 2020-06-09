# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.addons.base_sparse_field.models.fields import Serialized


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    packaging = Serialized(
        compute="_compute_packaging",
        help="Technical field to store packaging for the shop",
    )

    @api.depends("record_id.packaging_ids.qty")
    def _compute_packaging(self):
        for rec in self:
            rec.packaging = rec._get_variant_packaging()

    def _get_variant_packaging(self):
        res = []
        contained_mapping = self.record_id.packaging_contained_mapping or {}
        packaging = self.record_id._ordered_packaging()
        for pkg in packaging:
            pkg_info = pkg._asdict()
            pkg_info["contained"] = contained_mapping.get(str(pkg.id))
            res.append(pkg_info)
        return res
