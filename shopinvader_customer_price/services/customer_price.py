# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import functools

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component
from odoo.osv import expression


class CustomerPriceService(Component):
    _name = "shopinvader.customer.price.service"
    _inherit = "base.shopinvader.service"
    _usage = "customer_price"
    _expose_model = "shopinvader.variant"

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !
    def products(self, **params):
        domain = expression.normalize_domain(self._get_base_search_domain())
        domain = expression.AND([domain, [("id", "in", params["ids"])]])
        records = self.env[self._expose_model].search(domain)
        return self._to_json(records, one=params.get("one"))

    def _validator_products(self):
        return {
            "ids": {
                "type": "list",
                "nullable": True,
                "required": True,
                "schema": {"coerce": to_int, "type": "integer"},
            },
            "one": {"type": "boolean", "nullable": True, "required": False},
        }

    def _get_base_search_domain(self):
        if not self._is_logged_in():
            return expression.FALSE_DOMAIN
        return super()._get_base_search_domain()

    def _to_json(self, records, **kw):
        return records.jsonify(self._json_parser(), **kw)

    def _json_parser(self):
        # These are the same for all products for current partner.
        # Pass them all once w/ partial.
        pricelist = self._get_pricelist()
        fposition = self._get_fiscal_position()
        company = self.shopinvader_backend.company_id
        return [
            "id",
            "object_id:objectID",
            (
                "price",
                functools.partial(
                    self._get_price, pricelist, fposition, company
                ),
            ),
        ]

    def _get_price(self, pricelist, fposition, company, record, fname):
        return record._get_price(
            pricelist, fposition=fposition, company=company
        )

    def _get_fiscal_position(self):
        fp_model = self.env["account.fiscal.position"].with_context(
            force_company=self.shopinvader_backend.company_id.id
        )
        fpos_id = fp_model.get_fiscal_position(
            self.partner.id, delivery_id=self.partner.id,
        )
        return fp_model.browse(fpos_id)

    def _get_pricelist(self):
        return self.shopinvader_backend._get_cart_pricelist(self.partner)
