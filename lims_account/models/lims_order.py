# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class LimsOrder(models.Model):
    _inherit = "lims.order"

    account_move_ids = fields.Many2many(
        comodel_name="account.move",
        relation="lims_order_account_move_rel",
        column1="lims_order_id",
        column2="move_id",
        string="Account Moves",
    )
    account_move_count = fields.Integer(
        compute="_compute_account_move_count", string="Invoices Count"
    )

    @api.depends("account_move_ids")
    def _compute_account_move_count(self):
        for rec in self:
            rec.account_move_count = len(rec.account_move_ids)

    def action_open_account_moves(self):
        self.ensure_one()
        return {
            "name": _("Invoices"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "list,form",
            "domain": [("id", "in", self.account_move_ids.ids)],
        }
