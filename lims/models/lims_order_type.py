# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LIMSOrderType(models.Model):
    _name = "lims.order.type"
    _description = "LIMS Order Type"

    name = fields.Char(required=True)

    internal_type = fields.Selection(
        selection=[("lims", "LIMS")],
        default="lims",
    )
