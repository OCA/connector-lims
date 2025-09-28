# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LIMSMethod(models.Model):
    _name = "lims.method"
    _description = "LIMS Method"

    name = fields.Char(required=True, index=True, copy=False)
    description = fields.Text(required=True, copy=False)
    partner_id = fields.Many2one(
        "res.partner",
        string="Manufacturer",
        index=True,
        copy=False,
    )
