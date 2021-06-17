# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import first

from odoo.addons.component.core import Component


class ShopinvaderSiteExportMapper(Component):
    _inherit = ["shopinvader.site.export.mapper"]

    def _get_indexes_config(self, se_backend):
        indices, routes = super()._get_indexes_config(se_backend)

        index = first(
            se_backend.index_ids.filtered(
                lambda i: i.model_id.model == "shopinvader.seasonal.config.line"
            )
        )
        if index:
            indices.append(
                {
                    "name": "products_availability",
                    "index": self._get_index_name(index),
                }
            )

        return indices, routes
