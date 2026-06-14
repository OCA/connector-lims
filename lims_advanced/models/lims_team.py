# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields, models


class LIMSTeam(models.Model):
    _name = "lims.team"
    _description = "LIMS Team"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _default_stages(self):
        return self.env["lims.stage"].search([("is_default", "=", True)])

    def _compute_sample_count(self):
        sample_data = self.env["lims.sample"].read_group(
            [("team_id", "in", self.ids), ("stage_id.is_closed", "=", False)],
            ["team_id"],
            ["team_id"],
        )
        result = {
            data["team_id"][0]: int(data["team_id_count"]) for data in sample_data
        }
        for team in self:
            team.sample_count = result.get(team.id, 0)

    def _compute_sample_need_assign_count(self):
        sample_data = self.env["lims.sample"].read_group(
            [
                ("team_id", "in", self.ids),
                ("operator_id", "=", False),
                ("stage_id.is_closed", "=", False),
            ],
            ["team_id"],
            ["team_id"],
        )
        result = {
            data["team_id"][0]: int(data["team_id_count"]) for data in sample_data
        }
        for team in self:
            team.sample_need_assign_count = result.get(team.id, 0)

    def _compute_analysis_scheduled_counts(self):
        today = fields.Date.context_today(self)
        day1 = today + timedelta(days=1)
        day8 = today + timedelta(days=8)
        day31 = today + timedelta(days=31)

        Analysis = self.env["lims.analysis"]
        for team in self:
            base = [
                ("sample_id.team_id", "=", team.id),
                ("stage_id.is_closed", "=", False),
                ("scheduled_date", "!=", False),
            ]
            team.analysis_late_count = Analysis.search_count(
                base + [("scheduled_date", "<", str(today))]
            )
            team.analysis_today_count = Analysis.search_count(
                base
                + [
                    ("scheduled_date", ">=", str(today)),
                    ("scheduled_date", "<", str(day1)),
                ]
            )
            team.analysis_week_count = Analysis.search_count(
                base
                + [
                    ("scheduled_date", ">=", str(day1)),
                    ("scheduled_date", "<", str(day8)),
                ]
            )
            team.analysis_month_count = Analysis.search_count(
                base
                + [
                    ("scheduled_date", ">=", str(day8)),
                    ("scheduled_date", "<", str(day31)),
                ]
            )
            team.analysis_later_count = Analysis.search_count(
                base + [("scheduled_date", ">=", str(day31))]
            )

    def _compute_batch_scheduled_counts(self):
        today = fields.Date.context_today(self)
        day8 = today + timedelta(days=8)
        day31 = today + timedelta(days=31)

        Batch = self.env["lims.batch"]
        for team in self:
            base = [
                ("team_id", "=", team.id),
                ("stage_id.is_closed", "=", False),
                ("scheduled_date", "!=", False),
            ]
            team.batch_late_count = Batch.search_count(
                base + [("scheduled_date", "<", today)]
            )
            team.batch_today_count = Batch.search_count(
                base + [("scheduled_date", "=", today)]
            )
            team.batch_week_count = Batch.search_count(
                base + [("scheduled_date", ">", today), ("scheduled_date", "<", day8)]
            )
            team.batch_month_count = Batch.search_count(
                base + [("scheduled_date", ">=", day8), ("scheduled_date", "<", day31)]
            )
            team.batch_later_count = Batch.search_count(
                base + [("scheduled_date", ">=", day31)]
            )

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
    sample_ids = fields.One2many(
        "lims.sample",
        "team_id",
        string="Samples",
        domain=[("stage_id.is_closed", "=", False)],
    )
    sample_count = fields.Integer(compute="_compute_sample_count")
    sample_need_assign_count = fields.Integer(
        compute="_compute_sample_need_assign_count", string="Samples to Assign"
    )
    analysis_late_count = fields.Integer(
        compute="_compute_analysis_scheduled_counts", string="Analyses Late"
    )
    analysis_today_count = fields.Integer(
        compute="_compute_analysis_scheduled_counts", string="Analyses Today"
    )
    analysis_week_count = fields.Integer(
        compute="_compute_analysis_scheduled_counts", string="Analyses This Week"
    )
    analysis_month_count = fields.Integer(
        compute="_compute_analysis_scheduled_counts", string="Analyses This Month"
    )
    analysis_later_count = fields.Integer(
        compute="_compute_analysis_scheduled_counts", string="Analyses Later"
    )
    batch_late_count = fields.Integer(
        compute="_compute_batch_scheduled_counts", string="Batches Late"
    )
    batch_today_count = fields.Integer(
        compute="_compute_batch_scheduled_counts", string="Batches Today"
    )
    batch_week_count = fields.Integer(
        compute="_compute_batch_scheduled_counts", string="Batches This Week"
    )
    batch_month_count = fields.Integer(
        compute="_compute_batch_scheduled_counts", string="Batches This Month"
    )
    batch_later_count = fields.Integer(
        compute="_compute_batch_scheduled_counts", string="Batches Later"
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

    _sql_constraints = [
        ("name_uniq", "unique (name, company_id)", "Team name already exists!")
    ]
