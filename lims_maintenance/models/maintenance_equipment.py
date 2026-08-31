# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    is_lims_instrument = fields.Boolean(
        string="LIMS Instrument",
        help="Mark this equipment as a LIMS instrument so it appears"
        " under LIMS → Instruments.",
    )
