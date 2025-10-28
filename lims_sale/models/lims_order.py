from odoo import fields, models


class LimsOrder(models.Model):
    _inherit = "lims.order"

    sale_order_id = fields.Many2one("sale.order", string="Sale Order", index=True)
    sale_order_line_id = fields.Many2one(
        "sale.order.line", string="Sale Order Line", index=True
    )
    sale_origin = fields.Char(help="Original sale reference")

    def action_open_sale_order(self):
        self.ensure_one()
        if not self.sale_order_id:
            return
        return {
            "type": "ir.actions.act_window",
            "name": "Sale Order",
            "res_model": "sale.order",
            "view_mode": "form",
            "res_id": self.sale_order_id.id,
            "target": "current",
        }
