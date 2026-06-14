# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

AVAILABLE_PRIORITIES = [("0", "Normal"), ("1", "Low"), ("2", "High"), ("3", "Urgent")]


class LimsStage(models.Model):
    _inherit = "lims.stage"

    legend_priority = fields.Text(
        "Priority Management Explanation",
        translate=True,
        help="Explanation text to help users using"
        " the star and priority mechanism on"
        " stages or orders that are in this"
        " stage.",
    )
    team_ids = fields.Many2many(
        "lims.team",
        "order_team_stage_rel",
        "stage_id",
        "team_id",
        string="Teams",
        default=lambda self: self._default_team_ids(),
    )

    def _default_team_ids(self):
        default_team_id = self.env.context.get("default_team_id")
        return [default_team_id] if default_team_id else None
