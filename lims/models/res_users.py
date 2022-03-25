# Copyright 2023 Dixmit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    lims_department_ids = fields.Many2many("lims.department")
