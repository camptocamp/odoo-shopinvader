# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from fastapi import APIRouter, Depends

from odoo.api import Environment

from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.extendable_fastapi.schemas import PagedCollection
from odoo.addons.fastapi.dependencies import authenticated_partner, odoo_env, paging
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.shopinvader_schema_invoice.schemas import Invoice

invoice_router = APIRouter(tags=["invoices"])


@invoice_router.get("/invoices")
async def search(
    env: Environment = Depends(odoo_env),  # noqa: B008
    paging: Paging = Depends(paging),  # noqa: B008
    partner: ResPartner = Depends(authenticated_partner),  # noqa: B008
) -> PagedCollection[Invoice]:  # noqa: B008
    """Get the list of current partner's invoices"""
    domain = [
        ("partner_id", "=", partner.id),
        ("move_type", "=", "out_invoice"),
        ("state", "not in", ("cancel", "draft")),
    ]
    # TODO: @simahawk added `sudo`
    # Question: why do we need to respect permissions on related fields?
    # Had the same problem w/ sales and had to use sudo too.
    # Adding record rules for any possible models
    # that relates directly on indirectly to an invoice
    # seems over killing.
    # Moreover, having a rule for records not tied to partners
    # can be quite complicated.
    count = env["account.move"].sudo().search_count(domain)
    invoices = (
        env["account.move"]
        .sudo()
        .search(domain, limit=paging.limit, offset=paging.offset)
    )
    return PagedCollection[Invoice](
        count=count,
        items=Invoice.from_many(invoices),
    )
