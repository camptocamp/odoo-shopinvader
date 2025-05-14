# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, StreamingResponse

from odoo import fields, models
from odoo.api import Environment
from odoo.http import content_disposition
from odoo.tools.safe_eval import safe_eval

from odoo.addons.account.models.account_move import AccountMove
from odoo.addons.base.models.res_partner import Partner as ResPartner
from odoo.addons.extendable_fastapi.schemas import PagedCollection
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
    odoo_env,
    paging,
)
from odoo.addons.fastapi.schemas import Paging
from odoo.addons.shopinvader_filtered_model.utils import FilteredModelAdapter
from odoo.addons.shopinvader_schema_invoice.schemas import Invoice

invoice_router = APIRouter(tags=["invoices"])


@invoice_router.get("/invoices")
async def search(
    env: Annotated[Environment, Depends(odoo_env)],
    paging: Annotated[Paging, Depends(paging)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> PagedCollection[Invoice]:  # noqa: B008
    """Get the list of current partner's invoices"""
    count, invoices = (
        env["shopinvader_api_invoice.invoice_router.helper"]
        .new({"partner": partner})
        ._search(paging)
    )
    return PagedCollection[Invoice](
        count=count,
        items=Invoice.from_records(invoices),
    )


@invoice_router.get("/invoices/{invoice_id}/download")
def download(
    invoice_id: int,
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    partner: Annotated[ResPartner, Depends(authenticated_partner)],
) -> FileResponse:
    """Download document."""
    filename, pdf = get_pdf(env, invoice_id)
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"
    header = {
        "Content-Disposition": content_disposition(filename),
    }

    def pseudo_stream():
        yield pdf

    return StreamingResponse(
        pseudo_stream(), headers=header, media_type="application/pdf"
    )


def get_pdf(env, record_id) -> tuple[str, bytes]:
    report_name = "account.account_invoices"
    record = env["account.move"].sudo().browse(record_id)
    report = env["ir.actions.report"]._get_report(report_name)
    filename = safe_eval(report.print_report_name, {"object": record})
    content = (
        env["ir.actions.report"].sudo()._render_qweb_pdf(report_name, [record.id])[0]
    )
    return filename, content


class ShopinvaderApiInvoiceRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_invoice.invoice_router.helper"
    _description = "Shopinvader Api Invoice Service Helper"

    partner = fields.Many2one("res.partner")

    def _get_domain_adapter(self):
        return [
            ("partner_id", "=", self.partner.id),
            ("move_type", "in", ("out_invoice", "out_refund")),
            ("state", "not in", ("cancel", "draft")),
        ]

    @property
    def model_adapter(self) -> FilteredModelAdapter[AccountMove]:
        # Adding record rules for any possible models
        # that relates directly on indirectly to an invoice
        # seems over killing.
        # Moreover, having a rule for records not tied to partners
        # can be quite complicated.
        # Let's use sudo!
        return FilteredModelAdapter[AccountMove](self.sudo().env, [])

    def _search(self, paging) -> tuple[int, AccountMove]:
        return self.model_adapter.search_with_count(
            domain=self._get_domain_adapter(),
            limit=paging.limit,
            offset=paging.offset,
        )
