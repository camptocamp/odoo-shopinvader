from odoo.addons.component.core import Component
from odoo.addons.base_rest.components.service import to_int


class ProductService(Component):
    _inherit = "base.shopinvader.service"
    _name = "shopinvader.product.service"
    _usage = "product"
    _expose_model = "shopinvader.variant"

    # The following method are 'public' and can be called from the controller.
    def get(self, _id):
        return self._to_json(self._get(_id))[0]

    def search(self, **params):
        return self._paginate_search(**params)

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _get(self, _id):
        return self.env[self._expose_model].browse(_id)

    def _to_json(self, rec):
        exporter = self.env.ref('shopinvader.ir_exp_shopinvader_variant')
        parser = exporter.get_json_parser()
        # weird... price is not included by the exporter conf
        parser.append('price')
        # TODO: this should be move to a module that depends on 
        # `shopinvader_product_stock_state`
        if 'stock_data' in self.env[self._expose_model]:
            parser.append('stock_data')
        return rec.jsonify(parser)

    # Validator
    def _validator_get(self):
        return {}

    def _validator_search(self):
        return {
            "domain": {"type": "list", "nullable": True},
        }

