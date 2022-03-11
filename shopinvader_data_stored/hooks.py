# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


def pre_init_hook(cr):
    query = """
        ALTER TABLE shopinvader_variant ADD COLUMN jsonified_data TEXT;
    """
    cr.execute(query)
