# Copyright 2023 Dixmit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class LimsSample(models.Model):
    _name = "lims.sample"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Sample"
    _rec_name = "identifier"
    _check_company_auto = True

    identifier = fields.Char(required=True, default="/", readonly=True, copy=False)
    external_identifier = fields.Char()
    stage_id = fields.Many2one(
        "lims.stage",
        string="Stage",
        domain=[("stage_type", "=", "sample")],
        group_expand="_read_group_stage_ids",
        default=lambda self: self._default_stage_id(),
        tracking=True,
        index=True,
        copy=False,
    )
    is_closed = fields.Boolean(related="stage_id.is_closed")
    is_default_stage = fields.Boolean(related="stage_id.is_default")
    sample_type_id = fields.Many2one(
        "lims.sample.type",
        required=True,
        tracking=True,
    )
    sample_date = fields.Datetime(
        default=fields.Datetime.now,
        required=True,
        tracking=True,
    )
    received_date = fields.Datetime(readonly=True)
    published_date = fields.Datetime(readonly=True)
    customer_id = fields.Many2one("res.partner", tracking=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company.id, tracking=True
    )
    priority = fields.Selection(
        [
            ("0", "Normal"),
            ("1", "Low"),
            ("2", "High"),
            ("3", "Critical"),
        ],
        default="0",
    )
    analysis_ids = fields.One2many("lims.analysis", inverse_name="sample_id")
    interpretation = fields.Html()
    progress = fields.Float(
        compute="_compute_progress",
        store=True,
    )

    _sql_constraints = [
        (
            "identifier_unique",
            "unique(identifier, company_id)",
            "Sample identifier must be unique",
        )
    ]

    @api.model
    def _read_group_stage_ids(self, stages, domain, order=None):
        return stages.search([("stage_type", "=", "sample")], order=order)

    def _default_stage_id(self):
        return self.env["lims.stage"].search(
            [("stage_type", "=", "sample"), ("is_default", "=", True)], limit=1
        )

    @api.model_create_multi
    def create(self, mvals):
        for vals in mvals:
            if vals.get("identifier", "/") == "/":
                vals["identifier"] = self._get_identifier(vals)
        return super().create(mvals)

    def _get_identifier(self, vals):
        company = self.env["res.company"].browse(
            vals.get("company_id") or self.env.company.id
        )
        return (
            self.env["ir.sequence"].with_company(company).next_by_code("lims.sample")
            or "/"
        )

    def write(self, vals):
        received_stage = self.env.ref(
            "lims.lims_stage_sample_received", raise_if_not_found=False
        )
        moving_to_received = (
            received_stage and vals.get("stage_id") == received_stage.id
        )
        if moving_to_received and "received_date" not in vals:
            vals = dict(vals, received_date=fields.Datetime.now())
        result = super().write(vals)
        if moving_to_received:
            self.analysis_ids._receive_sample()
        return result

    def action_next_workflow_stage(self):
        for record in self:
            if not record.stage_id or record.stage_id.is_closed:
                continue
            next_stage = self.env["lims.stage"].search(
                [
                    ("stage_type", "=", "sample"),
                    ("sequence", ">", record.stage_id.sequence),
                ],
                order="sequence asc",
                limit=1,
            )
            if next_stage:
                record.stage_id = next_stage

    def receive_sample_action(self):
        received_stage = self.env.ref("lims.lims_stage_sample_received")
        for record in self.filtered(
            lambda r: not r.is_closed and r.stage_id != received_stage
        ):
            record.write(record._receive_sample_vals())

    def _receive_sample_vals(self):
        return {
            "stage_id": self.env.ref("lims.lims_stage_sample_received").id,
            "received_date": fields.Datetime.now(),
        }

    def check_to_verify(self):
        for record in self:
            if record._check_to_verify():
                record.write(record._check_to_verify_vals())

    def _check_to_verify(self):
        pending = self.env.ref("lims.lims_stage_analysis_registered") | self.env.ref(
            "lims.lims_stage_analysis_to_analyze"
        )
        return not any(self.analysis_ids.filtered(lambda r: r.stage_id in pending))

    def _check_to_verify_vals(self):
        return {"stage_id": self.env.ref("lims.lims_stage_sample_to_be_verified").id}

    def check_verify(self):
        for record in self:
            if record._check_verify():
                record.write(record._check_verify_vals())

    def _check_verify(self):
        active = self.get_analysis()
        return bool(active) and not any(active.filtered(lambda r: not r.is_closed))

    def _check_verify_vals(self):
        return {"stage_id": self.env.ref("lims.lims_stage_sample_verified").id}

    @api.depends("analysis_ids", "analysis_ids.progress")
    def _compute_progress(self):
        for record in self:
            record.progress = record._get_progress()

    def get_analysis(self):
        rejected = self.env.ref(
            "lims.lims_stage_analysis_rejected", raise_if_not_found=False
        )
        return self.analysis_ids.filtered(lambda r: r.stage_id != rejected)

    def _get_progress(self):
        analysis = self.get_analysis()
        if not analysis:
            return 0
        return sum(analysis.mapped("progress")) / len(analysis)
