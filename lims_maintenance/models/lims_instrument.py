# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class LimsInstrument(models.Model):
    _inherit = "lims.instrument"

    equipment_id = fields.Many2one(
        comodel_name="maintenance.equipment",
        string="Maintenance Equipment",
        help="Link this instrument to a Maintenance Equipment record.",
    )
