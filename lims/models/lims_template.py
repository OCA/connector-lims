# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LIMSTemplate(models.Model):
    _name = "lims.template"
    _description = "LIMS Order Template"

    name = fields.Char(required=True)
    operator_id = fields.Many2one(
        "res.partner", string="Operator", domain="[('is_lims_operator', '=', True)]"
    )
    physician_id = fields.Many2one(
        "res.partner", domain="[('is_physician', '=', True)]"
    )
    test_ids = fields.Many2many("lims.test", string="Tests")
    category_ids = fields.Many2many("lims.category", string="Categories")
    tag_ids = fields.Many2many("lims.tag", string="Tags")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        index=True,
        help="Company related to this template",
    )
