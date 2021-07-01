# Copyright 2021 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if


class SeasonalConfigLineEventListener(Component):
    _name = "seasonal.config.line.event.listener"
    _inherit = "base.event.listener"

    _apply_on = ["seasonal.config.line"]

    @skip_if(lambda self, record, **kw: self._check_product_bindings(record, **kw))
    def on_record_create(self, record, fields=None):
        self._create_config_line_bindings_if_missing(record)

    def _check_product_bindings(self, record, **kw):
        return not any(
            (
                record.product_id.shopinvader_bind_ids,
                record.product_template_id.shopinvader_bind_ids,
            )
        )

    def _create_config_line_bindings_if_missing(self, seasonal_config_line):
        self.env[
            "shopinvader.seasonal.config.line"
        ].with_delay().create_bindings_from_lines(seasonal_config_line)
