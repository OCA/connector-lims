# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.fields import Command


class SaleOrder(models.Model):
    _inherit = "sale.order"

    lims_sample_ids = fields.Many2many(
        "lims.sample",
        "lims_sample_sale_order_rel",
        "sale_order_id",
        "sample_id",
    )
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
            "domain": [("sale_order_ids", "in", self.ids)],
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
                if not line.lims_analyte_ids:
                    continue
                if tracking == "order":
                    if product in created_order_templates:
                        continue
                    sibling_lines = order.order_line.filtered(
                        lambda line_rec, p=product: (
                            line_rec.product_id.product_tmpl_id == p
                            and line_rec.product_id.product_tmpl_id.lims_tracking
                            == "order"
                            and line_rec.lims_analyte_ids
                        )
                    )
                    analysis_commands = []
                    seen_analytes = self.env["lims.analyte"]
                    for sibling in sibling_lines:
                        for analyte in sibling.lims_analyte_ids:
                            if analyte in seen_analytes:
                                continue
                            seen_analytes |= analyte
                            analysis_commands.append(
                                Command.create(
                                    {
                                        "analyte_id": analyte.id,
                                        "sale_order_line_id": sibling.id,
                                    }
                                )
                            )
                    product._create_lims_sample(order, analysis_commands)
                    created_order_templates |= product
                    continue
                if tracking == "line":
                    product._create_lims_sample(
                        order, line._prepare_lims_analysis_commands()
                    )
                    continue
                # quantity
                qty = int(line.product_uom_qty)
                if qty < 1:
                    continue
                commands = line._prepare_lims_analysis_commands()
                for index in range(qty):
                    product._create_lims_sample(
                        order,
                        commands,
                        sale_origin=f"{order.name}-{index + 1}",
                    )
