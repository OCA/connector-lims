# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LIMSTeam(models.Model):
    _name = "lims.team"
    _description = "LIMS Team"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _default_stages(self):
        return self.env["lims.stage"].search([("is_default", "=", True)])

    def _compute_order_count(self):
        order_data = self.env["lims.order"].read_group(
            [("team_id", "in", self.ids), ("stage_id.is_closed", "=", False)],
            ["team_id"],
            ["team_id"],
        )
        result = {data["team_id"][0]: int(data["team_id_count"]) for data in order_data}
        for team in self:
            team.order_count = result.get(team.id, 0)

    def _compute_order_need_assign_count(self):
        order_data = self.env["lims.order"].read_group(
            [
                ("team_id", "in", self.ids),
                ("operator_id", "=", False),
                ("stage_id.is_closed", "=", False),
            ],
            ["team_id"],
            ["team_id"],
        )
        result = {data["team_id"][0]: int(data["team_id_count"]) for data in order_data}
        for team in self:
            team.order_need_assign_count = result.get(team.id, 0)

    def _compute_order_need_schedule_count(self):
        order_data = self.env["lims.order"].read_group(
            [
                ("team_id", "in", self.ids),
                ("scheduled_date_start", "=", False),
                ("stage_id.is_closed", "=", False),
            ],
            ["team_id"],
            ["team_id"],
        )
        result = {data["team_id"][0]: int(data["team_id_count"]) for data in order_data}
        for team in self:
            team.order_need_schedule_count = result.get(team.id, 0)

    name = fields.Char(required=True, translate=True)
    description = fields.Text(translate=True)
    color = fields.Integer("Color Index")
    stage_ids = fields.Many2many(
        "lims.stage",
        "lims_order_team_stage_rel",
        "team_id",
        "stage_id",
        string="Stages",
        default=_default_stages,
    )
    order_ids = fields.One2many(
        "lims.order",
        "team_id",
        string="Analysis",
        domain=[("stage_id.is_closed", "=", False)],
    )
    order_count = fields.Integer(
        compute="_compute_order_count", string="Analysis Count"
    )
    order_need_assign_count = fields.Integer(
        compute="_compute_order_need_assign_count", string="Analysis to Assign"
    )
    order_need_schedule_count = fields.Integer(
        compute="_compute_order_need_schedule_count", string="Analysis to Schedule"
    )
    sequence = fields.Integer(default=1, help="Used to sort teams. Lower is better.")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
        help="Company related to this team",
    )

    _sql_constraints = [("name_uniq", "unique (name)", "Team name already exists!")]
