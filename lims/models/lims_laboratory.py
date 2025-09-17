# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LIMSLaboratory(models.Model):
    _name = "lims.laboratory"
    _description = "Laboratories"
    _inherits = {"res.partner": "partner_id"}
    _inherit = ["mail.thread", "mail.activity.mixin"]

    partner_id = fields.Many2one(
        "res.partner",
        string="Related Partner",
        required=True,
        ondelete="restrict",
        delegate=True,
        auto_join=True,
    )

    sequence = fields.Integer(default=1, help="Used to order laboratories.")
    description = fields.Text(translate=True)
    color = fields.Integer("Color Index")
