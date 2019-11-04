# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class BaseShopinvaderConnectorComponent(AbstractComponent):
    """ Base Shopinvader Connector Component
    All components of this connector should inherit from it.
    """

    _name = "base.shopinvader.connector"
    _collection = "shopinvader.backend"

    @property
    def backend(self):
        return self.collection
