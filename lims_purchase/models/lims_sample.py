# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class LimsSample(models.Model):
    _inherit = "lims.sample"

    purchase_order_ids = fields.One2many(
        "purchase.order",
        "lims_sample_id",
        string="Purchase Orders",
    )
    purchase_order_count = fields.Integer(
        string="PO Count",
        compute="_compute_purchase_order_count",
    )

    @api.depends("purchase_order_ids")
    def _compute_purchase_order_count(self):
        for sample in self:
            sample.purchase_order_count = len(sample.purchase_order_ids)

    def action_view_purchase_orders(self):
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "name": self.env._("Purchase Orders"),
            "res_model": "purchase.order",
            "view_mode": "list,form",
            "domain": [("lims_sample_id", "=", self.id)],
            "context": self._prepare_purchase_order_context(),
        }
        if self.purchase_order_count == 0:
            action.update(
                {
                    "view_mode": "form",
                    "target": "current",
                }
            )
        elif self.purchase_order_count == 1:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": self.purchase_order_ids.id,
                }
            )
        return action

    def _prepare_purchase_order_context(self):
        self.ensure_one()
        ctx = {
            "default_lims_sample_id": self.id,
        }
        if self.partner_id:
            ctx["default_partner_id"] = self.partner_id.id
        return ctx
