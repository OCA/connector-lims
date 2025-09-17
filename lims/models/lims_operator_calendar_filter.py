# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class LIMSOperatorCalendarFilter(models.Model):
    """Assigned Operator Calendar Filter"""

    _name = "lims.operator.calendar.filter"
    _description = "LIMS Operator Calendar Filter"

    user_id = fields.Many2one(
        "res.users",
        "Me",
        required=True,
        default=lambda self: self.env.user,
        ondelete="cascade",
    )
    operator_id = fields.Many2one("lims.operator", "LIMS Operator", required=True)
    active = fields.Boolean(default=True)
    person_checked = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "user_id_lims_operator_id_unique",
            "UNIQUE(user_id,operator_id)",
            "You cannot have the same operator twice.",
        )
    ]
