# Copyright 2021 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if


class SeasonalConfigLineEventListener(Component):
    _name = "seasonal.config.line.event.listener"
    _inherit = "base.event.listener"

    _apply_on = ["seasonal.config.line"]

    @skip_if(lambda self, record, **kwargs: not record.product_id.shopinvader_bind_ids)
    def on_record_create(self, record, fields=None):
        self._create_config_line_bindings_if_missing(record.product_id)

    def _create_config_line_bindings_if_missing(self, prod):
        config_model = self.env["seasonal.config.line"]
        config_lines = config_model.find_for_product(prod)
        if config_lines:
            s_config_model = self.env["shopinvader.seasonal.config.line"]
            s_config_model.with_delay().create_bindings_from_lines(config_lines)
