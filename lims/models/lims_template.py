# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LIMSTemplate(models.Model):
    _name = "lims.template"
    _description = "LIMS Order Template"

    name = fields.Char(required=True)
    instructions = fields.Text()
    category_ids = fields.Many2many("lims.category", string="Categories")
    duration = fields.Float(help="Default duration in hours")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        index=True,
        help="Company related to this template",
    )
    type_id = fields.Many2one("lims.order.type", string="Type")
    team_id = fields.Many2one(
        "lims.team",
        string="Team",
        help="Choose a team to be set on orders of this template",
    )
