# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    lims_sample_ids = fields.One2many("lims.sample", "sale_order_id")
    lims_sample_count = fields.Integer(compute="_compute_lims_sample_count")

    @api.depends("lims_sample_ids")
    def _compute_lims_sample_count(self):
        for order in self:
            order.lims_sample_count = len(order.lims_sample_ids)

    def action_view_lims_samples(self):
        self.ensure_one()
        return {
            "name": self.env._("LIMS Samples"),
            "type": "ir.actions.act_window",
            "res_model": "lims.sample",
            "view_mode": "list,form",
            "domain": [("sale_order_id", "=", self.id)],
            "context": {"default_sale_order_id": self.id},
        }

    def action_confirm(self):
        result = super().action_confirm()
        self._create_lims_samples_from_order()
        return result

    def _create_lims_samples_from_order(self):
        for order in self:
            created_order_templates = self.env["product.template"]
            for line in order.order_line:
                product = line.product_id.product_tmpl_id
                tracking = product.lims_tracking
                if tracking == "no" or not product.lims_sample_type_id:
                    continue
                analytes = line.lims_analyte_ids
                if not analytes:
                    continue
                if tracking == "order":
                    if product in created_order_templates:
                        continue
                    product._create_lims_sample(order, analytes)
                    created_order_templates |= product
                    continue
                if tracking == "line":
                    product._create_lims_sample(order, analytes)
                    continue
                # quantity
                qty = int(line.product_uom_qty)
                if qty < 1:
                    continue
                for index in range(qty):
                    product._create_lims_sample(
                        order,
                        analytes,
                        sale_origin=f"{order.name}-{index + 1}",
                    )
