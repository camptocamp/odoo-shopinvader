# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, exceptions
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component
from odoo.osv import expression


class WishlistService(Component):
    _name = "shopinvader.wishlist.service"
    _inherit = "base.shopinvader.service"
    _usage = "wishlist"
    _expose_model = "product.set"

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    def get(self, _id):
        record = self._get(_id)
        return self._to_json_one(record)

    def search(self, **params):
        return self._paginate_search(**params)

    # pylint: disable=W8106
    def create(self, **params):
        if not self._is_logged_in():
            # TODO: is there any way to control this in the REST API?
            raise exceptions.UserError(
                _("Must be authenticated to create a wishlist")
            )
        vals = self._prepare_params(params.copy())
        record = self.env[self._expose_model].create(vals)
        self._post_create(record)
        return {"data": self._to_json_one(record)}

    def update(self, _id, **params):
        record = self._get(_id)
        record.write(self._prepare_params(params))
        self._post_update(record)
        return self.search()

    def delete(self, _id):
        self._get(_id).unlink()
        return self.search()

    def add_to_cart(self, _id):
        record = self._get(_id)
        cart = self.component(usage="cart")._get()
        wizard = self.env["product.set.add"].create(
            {
                "shopinvader_backend_id": self.shopinvader_backend.id,
                "order_id": cart.id,
                "partner_id": self.partner.id,
                "product_set_id": record.id,
                "skip_existing_products": True,
            }
        )
        wizard.add_set()
        return self.search()

    def _post_create(self, record):
        pass

    def _post_update(self, record):
        pass

    def _validator_get(self):
        return {}

    def _validator_search(self):
        return {
            "id": {"coerce": to_int},
            "per_page": {"coerce": to_int, "nullable": True},
            "page": {"coerce": to_int, "nullable": True},
            "scope": {"type": "dict", "nullable": True},
        }

    def _validator_create(self):
        return {
            "name": {"type": "string", "required": True},
            "ref": {"type": "string", "required": True, "empty": False},
            "partner_id": {
                "type": "integer",
                "coerce": to_int,
                "nullable": True,
            },
            "typology": {"type": "string", "nullable": True},
            "lines": {
                "type": "list",
                "required": False,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "product_id": {"type": "integer", "required": True},
                        "quantity": {"type": "float", "required": True},
                    },
                },
            },
        }

    def _validator_update(self):
        res = self._validator_create()
        for key in res:
            if "required" in res[key]:
                del res[key]["required"]
        return res

    def _get_base_search_domain(self):
        if not self._is_logged_in():
            return expression.FALSE_DOMAIN
        return [
            ("partner_id", "=", self.partner.id),
            ("typology", "in", self._wishlist_typologies()),
        ]

    def _wishlist_typologies(self):
        """Wishlists can have different types, hook here to control allowed."""
        return ("wishlist",)

    def _prepare_params(self, params):
        if not params.get("partner_id"):
            params["partner_id"] = self.partner.id
        if not params.get("typology"):
            params["typology"] = "wishlist"
        params["set_line_ids"] = [
            (0, 0, line) for line in params.pop("lines", [])
        ]
        return params

    def _to_json(self, records):
        return records.jsonify(self._json_parser())

    def _to_json_one(self, records):
        values = self._to_json(records)
        if len(records) == 1:
            values = values[0]
        return values

    def _json_parser(self):
        return [
            "id",
            "name",
            "typology",
            "ref",
            ("partner_id:partner", ["id", "name"]),
            ("set_line_ids:lines", self._json_parser_line()),
        ]

    def _json_parser_line(self):
        return [
            "id",
            "sequence",
            "quantity",
            ("product_id:product", ["id", "name", "default_code:sku"]),
        ]
