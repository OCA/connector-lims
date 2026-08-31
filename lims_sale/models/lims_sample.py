# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class LimsSample(models.Model):
    _inherit = "lims.sample"

    # M2M: one sample may be covered by several sale orders (e.g. patient + insurer).
    sale_order_ids = fields.Many2many(
        "sale.order",
        "lims_sample_sale_order_rel",
        "sample_id",
        "sale_order_id",
        index=True,
    )
    sale_origin = fields.Char(help="Original sale reference")

    def action_open_sale_orders(self):
        self.ensure_one()
        if not self.sale_order_ids:
            return False
        action = {
            "type": "ir.actions.act_window",
            "name": self.env._("Sale Orders"),
            "res_model": "sale.order",
            "target": "current",
        }
        if len(self.sale_order_ids) == 1:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": self.sale_order_ids.id,
                }
            )
        else:
            action.update(
                {
                    "view_mode": "list,form",
                    "domain": [("id", "in", self.sale_order_ids.ids)],
                }
            )
        return action
