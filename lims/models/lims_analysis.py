# Copyright 2023 Dixmit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import AccessDenied


class LimsAnalysis(models.Model):
    _name = "lims.analysis"
    _description = "Analysis"
    _check_company_auto = True

    identifier = fields.Char(required=True, default="/", readonly=True)
    sample_id = fields.Many2one("lims.sample", required=True)
    company_id = fields.Many2one(
        "res.company", related="sample_id.company_id", store=True
    )
    stage_id = fields.Many2one(
        "lims.stage",
        string="Stage",
        domain=[("stage_type", "=", "result")],
        group_expand="_read_group_stage_ids",
        default=lambda self: self._default_stage_id(),
        index=True,
        copy=False,
    )
    is_closed = fields.Boolean(related="stage_id.is_closed")
    is_first_stage = fields.Boolean(compute="_compute_is_first_stage")
    can_analyze = fields.Boolean(compute="_compute_can_analyze")
    can_retract = fields.Boolean(compute="_compute_can_retract")
    can_reject = fields.Boolean(compute="_compute_can_reject")

    product_id = fields.Many2one(
        "product.product",
        required=True,
        domain=[("laboratory_ok", "=", True)],
        readonly=True,
    )
    name = fields.Char(
        required=True,
        readonly=True,
    )
    analyst_id = fields.Many2one("res.users", readonly=True)
    capture_date = fields.Datetime(readonly=True)
    submitted_date = fields.Datetime()
    verified_by = fields.Many2one("res.users", readonly=True)
    due_date = fields.Datetime(readonly=True)
    verification_date = fields.Datetime(readonly=True)
    uom_id = fields.Many2one(
        "uom.uom",
        readonly=True,
    )
    progress = fields.Float(compute="_compute_progress", store=True)
    can_verify = fields.Boolean(compute="_compute_can_verify")
    value = fields.Char()

    _sql_constraints = [
        (
            "identifier_unique",
            "unique(identifier, company_id)",
            "Sample identifier must be unique",
        )
    ]

    @api.model
    def _read_group_stage_ids(self, stages, domain, order=None):
        return stages.search([("stage_type", "=", "result")], order=order)

    def _default_stage_id(self):
        return self.env["lims.stage"].search(
            [("stage_type", "=", "result")], order="sequence asc", limit=1
        )

    @api.depends("stage_id")
    def _compute_is_first_stage(self):
        first = self.env["lims.stage"].search(
            [("stage_type", "=", "result")], order="sequence asc", limit=1
        )
        for record in self:
            record.is_first_stage = record.stage_id == first

    @api.depends("stage_id")
    def _compute_can_analyze(self):
        stage = self.env.ref(
            "lims.lims_stage_analysis_to_analyze", raise_if_not_found=False
        )
        for record in self:
            record.can_analyze = bool(stage and record.stage_id == stage)

    @api.depends("stage_id")
    def _compute_can_retract(self):
        stage = self.env.ref(
            "lims.lims_stage_analysis_to_be_verified", raise_if_not_found=False
        )
        for record in self:
            record.can_retract = bool(stage and record.stage_id == stage)

    @api.depends("stage_id")
    def _compute_can_reject(self):
        rejected = self.env.ref(
            "lims.lims_stage_analysis_rejected", raise_if_not_found=False
        )
        for record in self:
            record.can_reject = bool(
                not record.is_first_stage
                and not record.is_closed
                and record.stage_id != rejected
            )

    @api.onchange("product_id")
    def _onchange_product(self):
        for record in self:
            if not record.product_id:
                continue
            record.name = record.product_id.name
            record.uom_id = record.product_id.laboratory_uom_id

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
            self.env["ir.sequence"].with_company(company).next_by_code("lims.analysis")
            or "/"
        )

    @api.model
    def _add_missing_default_values(self, values):
        defaults = super()._add_missing_default_values(values)
        product = self.env["product.product"].browse(
            values.get("product_id") or defaults.get("product_id")
        )
        if "uom_id" not in values:
            defaults["uom_id"] = product.laboratory_uom_id.id
        if "name" not in values:
            defaults["name"] = product.name
        return defaults

    def _receive_sample(self):
        for record in self:
            record.write(record._receive_sample_vals())

    def _receive_sample_vals(self):
        return {
            "stage_id": self.env.ref("lims.lims_stage_analysis_to_analyze").id,
        }

    def analyze_action(self):
        if not self.env.user.has_group("lims.group_lims_analyst"):
            raise AccessDenied(_("You are not allowed to analyze this"))
        for record in self.filtered("can_analyze"):
            record.write(record._analyze_action_vals())
        self.mapped("sample_id").check_to_verify()

    def _analyze_action_vals(self):
        return {
            "stage_id": self.env.ref("lims.lims_stage_analysis_to_be_verified").id,
            "analyst_id": self.env.user.id,
            "submitted_date": fields.Datetime.now(),
        }

    def verify_action(self):
        if not self.env.user.has_group("lims.group_lims_verifier"):
            raise AccessDenied(_("You are not allowed to verify an analysis"))
        for record in self.filtered(lambda r: r.can_verify):
            record.write(record._verify_action_vals())
        self.mapped("sample_id").check_verify()

    def _verify_action_vals(self):
        return {
            "stage_id": self.env.ref("lims.lims_stage_analysis_verified").id,
            "verified_by": self.env.user.id,
            "verification_date": fields.Datetime.now(),
        }

    @api.depends("stage_id")
    def _compute_progress(self):
        for record in self:
            record.progress = record._get_progress()

    def _get_progress(self):
        verified = self.env.ref(
            "lims.lims_stage_analysis_verified", raise_if_not_found=False
        )
        to_be_verified = self.env.ref(
            "lims.lims_stage_analysis_to_be_verified", raise_if_not_found=False
        )
        if verified and self.stage_id == verified:
            return 100
        if to_be_verified and self.stage_id == to_be_verified:
            return 50
        return 0

    @api.depends_context("uid")
    @api.depends("stage_id", "analyst_id")
    def _compute_can_verify(self):
        to_be_verified = self.env.ref(
            "lims.lims_stage_analysis_to_be_verified", raise_if_not_found=False
        )
        is_manager = self.env.user.has_group("lims.group_lims_manager")
        for record in self:
            record.can_verify = bool(
                to_be_verified and record.stage_id == to_be_verified
            ) and (is_manager or record.analyst_id != self.env.user)

    def retract_action(self):
        if not self.env.user.has_group("lims.group_lims_verifier"):
            raise AccessDenied(
                _("You are not allowed to retract an analysis to be verified")
            )
        for record in self.filtered("can_retract"):
            record.write(record._retract_action_vals())

    def _retract_action_vals(self):
        return {
            "stage_id": self.env.ref("lims.lims_stage_analysis_to_analyze").id,
            "analyst_id": False,
            "submitted_date": False,
        }

    def reject_action(self):
        if not (
            self.env.user.has_group("lims.group_lims_analyst")
            or self.env.user.has_group("lims.group_lims_verifier")
        ):
            raise AccessDenied(_("You are not allowed to reject an analysis"))
        for record in self.filtered("can_reject"):
            record.write(record._reject_action_vals())

    def _reject_action_vals(self):
        return {
            "stage_id": self.env.ref("lims.lims_stage_analysis_rejected").id,
        }
