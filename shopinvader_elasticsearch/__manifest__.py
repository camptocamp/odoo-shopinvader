# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Elasticsearch",
    "description": """
        Shopinvader Elasticsearch Connector""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["shopinvader_search_engine", "connector_elasticsearch"],
    "data": ["data/ir_export_product.xml"],
    "demo": ["demo/index_config_demo.xml", "demo/backend_demo.xml"],
}
