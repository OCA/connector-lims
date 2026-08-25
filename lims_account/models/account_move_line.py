# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    lims_analyte_ids = fields.Many2many(
        "lims.analyte",
        relation="account_move_line_lims_analyte_rel",
        column1="line_id",
        column2="analyte_id",
        help="Analytes (parameters) invoiced on this line.",
    )
