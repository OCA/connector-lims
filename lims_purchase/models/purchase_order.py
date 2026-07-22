# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    lims_sample_id = fields.Many2one(
        "lims.sample",
        string="LIMS Sample",
        index=True,
        ondelete="set null",
        help="LIMS sample related to this purchase order.",
    )

    def action_open_linked_lims_sample(self):
        self.ensure_one()
        if not self.lims_sample_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("LIMS Sample"),
            "res_model": "lims.sample",
            "view_mode": "form",
            "res_id": self.lims_sample_id.id,
            "target": "current",
        }
