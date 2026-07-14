# Copyright 2026 Dixmit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    lims_unforce_double_verification_manager = fields.Boolean(
        string="Unforce double verification for managers",
        config_parameter="lims.unforce_double_verification_manager",
        help="Allow managers to validate analyses without double verification",
    )
