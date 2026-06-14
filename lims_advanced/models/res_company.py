# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    lims_order_request_late_lowest = fields.Float(
        string="Hours of Buffer for Lowest Priority LIMS Orders",
        default=72,
    )
    lims_order_request_late_low = fields.Float(
        string="Hours of Buffer for Low Priority LIMS Orders",
        default=48,
    )
    lims_order_request_late_medium = fields.Float(
        string="Hours of Buffer for Medium Priority LIMS Orders",
        default=24,
    )
    lims_order_request_late_high = fields.Float(
        string="Hours of Buffer for High Priority LIMS Orders", default=8
    )
