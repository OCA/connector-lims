# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class LimsSample(models.Model):
    _inherit = "lims.sample"

    account_move_ids = fields.Many2many(
        comodel_name="account.move",
        relation="lims_sample_account_move_rel",
        column1="lims_sample_id",
        column2="move_id",
    )
    account_move_count = fields.Integer(compute="_compute_account_move_count")

    @api.depends("account_move_ids")
    def _compute_account_move_count(self):
        for sample in self:
            sample.account_move_count = len(sample.account_move_ids)

    def action_open_account_moves(self):
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "name": self.env._("Invoices"),
            "res_model": "account.move",
            "view_mode": "list,form",
            "domain": [("id", "in", self.account_move_ids.ids)],
            "context": {
                "default_move_type": "out_invoice",
                "default_partner_id": self.partner_id.id,
                "default_lims_sample_ids": [(6, 0, [self.id])],
            },
        }
        if self.account_move_count == 0:
            action.update(
                {
                    "view_mode": "form",
                    "target": "current",
                }
            )
        elif self.account_move_count == 1:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": self.account_move_ids.id,
                }
            )
        return action
