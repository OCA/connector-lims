# Copyright (C) 2025 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LIMSEquipment(models.Model):
    _name = "lims.equipment"
    _description = "LIMS Equipment"
    _inherit = ["mail.thread", "mail.activity.mixin", "lims.model.mixin"]
    _stage_type = "equipment"

    name = fields.Char(required=True)
    operator_id = fields.Many2one("lims.operator", string="Assigned Operator")
    notes = fields.Text()
    color = fields.Integer("Color Index")
    laboratory_id = fields.Many2one("lims.laboratory", string="Laboratory")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
        help="Company related to this equipment",
    )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Equipment name already exists!")
    ]
