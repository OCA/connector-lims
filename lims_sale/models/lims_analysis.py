# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class LimsAnalysis(models.Model):
    _inherit = "lims.analysis"

    # Commercial link: the sale order line that sold this parameter (analyte).
    sale_order_line_id = fields.Many2one(
        "sale.order.line",
        index=True,
        help="Sale order line that invoiced this analysis parameter.",
    )
