# Copyright 2023 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from extendable_pydantic import StrictExtendableBaseModel

from .amount import InvoiceAmount


class Invoice(StrictExtendableBaseModel, extra="ignore"):
    id: int
    name: str
    date_invoice: date
    date_due: date | None = None
    state: str
    payment_state: str
    ref: str | str
    payment_reference: str | str
    amount: InvoiceAmount | None

    @classmethod
    def from_one(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.name,
            date_invoice=odoo_rec.invoice_date,
            date_due=odoo_rec.invoice_date_due or None,
            state=odoo_rec.state,
            payment_state=odoo_rec.payment_state,
            ref=odoo_rec.ref or "",
            payment_reference=odoo_rec.payment_reference or "",
            amount=InvoiceAmount.from_one(odoo_rec),
        )

    @classmethod
    def from_many(cls, odoo_recs):
        return [cls.from_one(rec) for rec in odoo_recs]
