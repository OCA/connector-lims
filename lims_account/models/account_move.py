# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    lims_sample_ids = fields.Many2many(
        comodel_name="lims.sample",
        relation="lims_sample_account_move_rel",
        column1="move_id",
        column2="lims_sample_id",
    )
    lims_sample_count = fields.Integer(compute="_compute_lims_sample_count")

    @api.depends("lims_sample_ids")
    def _compute_lims_sample_count(self):
        for move in self:
            move.lims_sample_count = len(move.lims_sample_ids)

    def action_open_lims_samples(self):
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "name": self.env._("LIMS Samples"),
            "res_model": "lims.sample",
            "view_mode": "list,form",
            "domain": [("id", "in", self.lims_sample_ids.ids)],
        }
        if self.lims_sample_count == 1:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": self.lims_sample_ids.id,
                }
            )
        return action
