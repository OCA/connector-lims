# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_laboratory = fields.Boolean("Is a laboratory")
    is_lims_operator = fields.Boolean("Is a lab operator")
    is_physician = fields.Boolean("Is a physician")
