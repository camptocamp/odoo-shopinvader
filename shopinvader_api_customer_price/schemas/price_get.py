# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from typing import Optional

from extendable_pydantic import StrictExtendableBaseModel


class PriceGetInput(StrictExtendableBaseModel, extra="ignore"):
    ids: list
    pricelist_id: Optional[int] = None
