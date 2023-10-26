# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api, models

from odoo.addons.fastapi.dependencies import authenticated_partner_env

from ..schemas import LoyaltyRewardResponse

loyalty_router = APIRouter(tags=["loyalties"])


@loyalty_router.get("/rewards/{code}")
def get_rewards(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    code: str,
) -> list[LoyaltyRewardResponse]:
    rewards = env["shopinvader_api_loyalty.service.helper"]._get_rewards(code)
    return [LoyaltyRewardResponse.from_loyalty_reward(reward) for reward in rewards]


class ShopinvaderApiLoyaltyServiceHelper(models.AbstractModel):
    _name = "shopinvader_api_loyalty.service.helper"
    _description = "ShopInvader API Loyalty Service Helper"

    # Get rewards
    @api.model
    def _get_rewards(self, code: str):
        card = self.env["loyalty.card"].search([("code", "=", code)], limit=1)
        program_id = self.env["loyalty.program"]
        if card:
            program_id = card.program_id
        else:
            rule_id = self.env["loyalty.rule"].search([("code", "=", code)], limit=1)
            if rule_id:
                program_id = rule_id.program_id
        if program_id:
            return program_id.reward_ids
        return self.env["loyalty.reward"]
