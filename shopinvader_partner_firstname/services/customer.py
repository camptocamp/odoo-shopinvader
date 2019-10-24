# Copyright 2019 Camptocamp (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CustomerService(Component):
    _inherit = "shopinvader.customer.service"

    def _validator_create(self):
        schema = super()._validator_create()
        schema.update(
            {
                "name": {
                    "type": "string",
                    "required": False,
                    "nullable": True,
                },
                "firstname": {"type": "string", "required": True},
                "lastname": {"type": "string", "required": True},
            }
        )
        return schema

    def _prepare_params(self, params):
        params = super()._prepare_params(params)
        # make sure name is not passed to create, even empty,
        # otherwise partner creation will be broken
        params.pop("name", None)
        return params


class AddressService(Component):
    _inherit = "shopinvader.address.service"

    def _json_parser(self):
        parser = super()._json_parser()
        parser.extend(["firstname", "lastname"])
        return parser
