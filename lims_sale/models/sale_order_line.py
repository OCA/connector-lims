# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.fields import Command


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    lims_analyte_ids = fields.Many2many(
        "lims.analyte",
        relation="sale_order_line_lims_analyte_rel",
        column1="line_id",
        column2="analyte_id",
        help="Analytes (parameters) sold on this line. "
        "These determine which analyses are created on the LIMS sample.",
    )

    @api.onchange("product_id")
    def _onchange_product_id_lims_analytes(self):
        for line in self:
            product = line.product_id.product_tmpl_id
            if product.lims_tracking != "no" and product.lims_analyte_ids:
                line.lims_analyte_ids = [Command.set(product.lims_analyte_ids.ids)]
            else:
                line.lims_analyte_ids = [Command.clear()]

    def _prepare_lims_analysis_commands(self):
        """Return Command.create values linking each analyte to this sale line."""
        self.ensure_one()
        return [
            Command.create(
                {
                    "analyte_id": analyte.id,
                    "sale_order_line_id": self.id,
                }
            )
            for analyte in self.lims_analyte_ids
        ]
