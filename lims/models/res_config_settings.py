# Copyright (C) 2025 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_lims_advanced = fields.Boolean(
        string="Advanced LIMS Features",
    )
