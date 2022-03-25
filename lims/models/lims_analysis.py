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
    state = fields.Selection(
        [
            ("registered", "Registered"),
            ("to_analyze", "To Analyze"),
            ("to_be_verified", "To be verified"),
            ("verified", "Verified"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="registered",
        readonly=True,
    )
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
    value = fields.Char(
        readonly=True,
    )
    # TODO: Replace this for something better. isn't it?

    _sql_constraints = [
        (
            "identifier_unique",
            "unique(identifier, company_id)",
            "Sample identifier must be unique",
        )
    ]

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
        return (
            self.env["ir.sequence"]
            .with_context(force_company=vals.get("company_id", self.env.company.id))
            .next_by_code("lims.analysis")
            or "/"
        )

    @api.model
    def _add_missing_default_values(self, values):
        defaults = super()._add_missing_default_values(values)
        product = self.env["product.product"].browse(defaults["product_id"])
        if "uom_id" not in values:
            defaults["uom_id"] = product.laboratory_uom_id.id
        if values.get("name"):
            defaults["name"] = product.name
        return defaults

    def _receive_sample(self):
        for record in self:
            record.write(record._receive_sample_vals())

    def _receive_sample_vals(self):
        return {
            "state": "to_analyze",
        }

    def analyze_action(self):
        if not self.env.user.has_group("lims.group_lims_analyst"):
            raise AccessDenied(_("You are not allowed to analyze this"))
        for record in self.filtered(lambda r: r.state == "to_analyze"):
            record.write(record._analyze_action_vals())
        self.mapped("sample_id").check_to_verify()

    def _analyze_action_vals(self):
        return {
            "state": "to_be_verified",
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
            "state": "verified",
            "verified_by": self.env.user.id,
            "verification_date": fields.Datetime.now(),
        }

    @api.depends("state")
    def _compute_progress(self):
        for record in self:
            record.progress = record._get_progress()

    def final_states(self):
        return ["verified"]

    def _get_progress(self):
        if self.state in self.final_states():
            return 100
        if self.state == "to_be_verified":
            return 50
        return 0

    @api.depends_context("uid")
    @api.depends("state", "analyst_id")
    def _compute_can_verify(self):
        verify_param = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("lims.unforce_double_verification_manager"),
        ) and self.env.user.has_group("lims.group_lims_manager")
        for record in self:
            record.can_verify = record.state == "to_be_verified" and (
                verify_param or record.analyst_id != self.env.user
            )

    def retract_action(self):
        if not self.env.user.has_group("lims.group_lims_verifier"):
            raise AccessDenied(
                _("You are not allowed to retract an analysis to be verified")
            )
        for record in self.filtered(lambda r: r.state == "to_be_verified"):
            record.write(record._retract_action_vals())

    def _retract_action_vals(self):
        return {
            "state": "to_analyze",
            "analyst_id": False,
            "submitted_date": False,
        }
