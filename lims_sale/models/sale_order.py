from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    lims_order_count = fields.Integer(
        string="LIMS Orders", compute="_compute_lims_order_count", store=False
    )

    def _compute_lims_order_count(self):
        lims_order_data = self.env["lims.order"].read_group(
            [("sale_order_id", "in", self.ids)], ["sale_order_id"], ["sale_order_id"]
        )
        mapped_data = {
            data["sale_order_id"][0]: data["sale_order_id_count"]
            for data in lims_order_data
        }
        for order in self:
            order.lims_order_count = mapped_data.get(order.id, 0)

    def action_view_lims_orders(self):
        self.ensure_one()
        return {
            "name": "LIMS Orders",
            "type": "ir.actions.act_window",
            "res_model": "lims.order",
            "view_mode": "list,form",
            "domain": [("sale_order_id", "=", self.id)],
            "context": {"default_sale_order_id": self.id},
        }

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            for line in order.order_line:
                product = line.product_id
                if product.lims_tracking and product.lims_tracking != "no":
                    template = product.lims_template_id
                    if not template:
                        continue

                    if product.lims_tracking == "order":
                        lims_order = template.create_lims_order_from_template()
                        lims_order.write(
                            {
                                "sale_order_id": order.id,
                                "sale_origin": order.name,
                            }
                        )

                    elif product.lims_tracking == "line":
                        lims_order = template.create_lims_order_from_template()
                        lims_order.write(
                            {
                                "sale_order_id": order.id,
                                "sale_order_line_id": line.id,
                                "sale_origin": order.name,
                            }
                        )

                    elif product.lims_tracking == "quantity":
                        for i in range(int(line.product_uom_qty)):
                            lims_order = template.create_lims_order_from_template()
                            lims_order.write(
                                {
                                    "sale_order_id": order.id,
                                    "sale_order_line_id": line.id,
                                    "sale_origin": f"{order.name}-{i+1}",
                                }
                            )
        return res
