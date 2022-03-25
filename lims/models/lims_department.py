# Copyright 2023 Dixmit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class LimsDepartment(models.Model):
    _name = "lims.department"
    _description = "Department"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    user_ids = fields.Many2many("res.users")
