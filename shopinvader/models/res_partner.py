# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .shopinvader_partner import STATE_ACTIVE, STATE_PENDING


class ResPartner(models.Model):
    _inherit = "res.partner"

    shopinvader_bind_ids = fields.One2many(
        "shopinvader.partner", "record_id", string="Shopinvader Binding"
    )
    address_type = fields.Selection(
        selection=[("profile", "Profile"), ("address", "Address")],
        string="Shopinvader Address Type",
        compute="_compute_address_type",
        store=True,
    )
    # In europe we use more the opt_in
    opt_in = fields.Boolean(
        compute="_compute_opt_in", inverse="_inverse_opt_in"
    )
    is_shopinvader_active = fields.Boolean(
        string="Shop enabled",
        help="This address is enabled to be used for Shopinvader.",
    )
    has_shopinvader_user = fields.Boolean(
        help="This partner has at least a Shopinvader user.",
        compute="_compute_has_shopinvader_user",
        compute_sudo=True,
    )
    has_shopinvader_user_active = fields.Boolean(
        help="This partner has at least a Shopinvader active user.",
        compute="_compute_has_shopinvader_user",
        compute_sudo=True,
    )
    has_shopinvader_user_to_validate = fields.Boolean(
        help="This partner has at least a Shopinvader user to be validated.",
        compute="_compute_has_shopinvader_user",
        store=True,
        compute_sudo=True,
    )

    @api.depends("is_blacklisted")
    def _compute_opt_in(self):
        for record in self:
            record.opt_in = not record.is_blacklisted

    def _inverse_opt_in(self):
        blacklist_model = self.env["mail.blacklist"]
        for record in self:
            if record.opt_in:
                blacklist_model._remove(record.email)
            else:
                blacklist_model._add(record.email)

    @api.depends("shopinvader_bind_ids.state")
    def _compute_has_shopinvader_user(self):
        for record in self:
            record.has_shopinvader_user = bool(record.shopinvader_bind_ids)
            record.has_shopinvader_user_active = any(
                record.shopinvader_bind_ids.filtered(
                    lambda x: x.state == STATE_ACTIVE
                )
            )
            record.has_shopinvader_user_to_validate = any(
                record.shopinvader_bind_ids.filtered(
                    lambda x: x.state == STATE_PENDING
                )
            )

    @api.depends("parent_id")
    def _compute_address_type(self):
        for partner in self:
            if partner.parent_id:
                partner.address_type = "address"
            else:
                partner.address_type = "profile"

    @api.constrains("email")
    def _check_unique_email(self):
        config = self.env["shopinvader.config.settings"]
        if config.is_partner_duplication_allowed():
            return True
        self.env.cr.execute(
            """
            SELECT
                email
            FROM (
                SELECT
                    id,
                    email,
                    ROW_NUMBER() OVER (PARTITION BY email) AS Row
                FROM
                    res_partner
                WHERE email is not null and active = True
                ) dups
            WHERE dups.Row > 1;
        """
        )
        duplicate_emails = {r[0] for r in self.env.cr.fetchall()}
        invalid_emails = [
            e for e in self.mapped("email") if e in duplicate_emails
        ]
        if invalid_emails:
            raise ValidationError(
                _(
                    "Email must be unique: The following "
                    "mails are not unique: %s"
                )
                % ", ".join(invalid_emails)
            )

    def write(self, vals):
        super(ResPartner, self).write(vals)
        if "country_id" in vals:
            carts = (
                self.env["sale.order"]
                .sudo()
                .search(
                    [
                        ("typology", "=", "cart"),
                        ("partner_shipping_id", "in", self.ids),
                    ]
                )
            )
            for cart in carts:
                # Trigger a write on cart to recompute the
                # fiscal position if needed
                cart.sudo().write_with_onchange(
                    {"partner_shipping_id": cart.partner_shipping_id.id}
                )
        return True

    def addr_type_display(self):
        return self._fields["address_type"].convert_to_export(
            self.address_type, self
        )

    def action_shopinvader_validate_customer(self):
        return self.shopinvader_bind_ids.action_shopinvader_validate()

    def action_shopinvader_validate_address(self):
        wiz = self._get_shopinvader_validate_address_wizard()
        action = self.env.ref(
            "shopinvader.shopinvader_partner_validate_act_window"
        )
        action_data = action.read()[0]
        action_data["res_id"] = wiz.id
        return action_data

    def _get_shopinvader_validate_address_wizard(self, **kw):
        vals = dict(partner_ids=self.ids, **kw)
        return self.env["shopinvader.address.validate"].create(vals)

    def get_shop_partner(self, backend):
        """Retrieve current partner customer account.

        By default is the same user's partner.
        Hook here to provide your own behavior.

        This partner is used to provide main account information client side
        and to assign the partner to the sale order / cart.

        :return: res.partner record.
        """
        return self

    def _get_invader_partner(self, backend):
        """Get bound partner matching backend."""
        domain = [("backend_id", "=", backend.id)]
        return self.shopinvader_bind_ids.filtered_domain(domain)
