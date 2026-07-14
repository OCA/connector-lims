# Copyright 2023 Dixmit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import AccessDenied
from odoo.tools import format_date, format_datetime


class LimsAnalysis(models.Model):
    """
    Identifies the specific value provided by the laboratory.
    It is linked to a sample and a product (which identifies the type of analysis).
    """

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
    sequence = fields.Integer(
        default=10,
    )
    display_type = fields.Selection(
        [
            ("analyte", "Analyte"),
            ("line_section", "Section"),
            ("line_subsection", "Subsection"),
            ("line_note", "Note"),
        ],
        default="analyte",
    )
    analyte_id = fields.Many2one(
        "lims.analyte",
        readonly=True,
    )
    name = fields.Char(
        required=True,
        readonly=True,
        compute="_compute_name",
        store=True,
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
        compute="_compute_uom_id",
        store=True,
    )
    progress = fields.Float(compute="_compute_progress", store=True)
    can_verify = fields.Boolean(compute="_compute_can_verify")
    value = fields.Json(
        readonly=True,
        compute="_compute_value",
        store=True,
    )
    value_state = fields.Selection(
        [
            ("valid", "Valid"),
            ("min", "Minimum"),
            ("max", "Maximum"),
            ("min_warning", "Minimum Warning"),
            ("max_warning", "Maximum Warning"),
        ],
        compute="_compute_value_state",
        store=True,
    )
    _identifier_unique = models.Constraint(
        "unique(identifier, company_id)", "Analysis identifier must be unique"
    )

    @api.depends("analyte_id")
    def _compute_name(self):
        for record in self:
            if record.analyte_id:
                record.name = record.analyte_id.name

    @api.depends("analyte_id")
    def _compute_value(self):
        for record in self:
            record.value = record.analyte_id._get_default_value(
                record.sample_id.sample_type_id
            )

    @api.depends("analyte_id")
    def _compute_uom_id(self):
        for record in self:
            record.uom_id = record.analyte_id.uom_id

    @api.depends("value")
    def _compute_value_state(self):
        for record in self:
            record.value_state = record._get_value_state()

    def _get_value_state(self):
        if not self.value:
            return False
        if self.value.get("result_type") != "float":
            return False
        if not self.value.get("min_operator") and not self.value.get("max_operator"):
            return False
        value = self.value.get("value", 0.0)
        if self.value.get("min_operator") and self._get_value_evaluation(
            self.value["min_operator"], value, self.value.get("min", 0.0)
        ):
            return "min"
        if self.value.get("max_operator") and self._get_value_evaluation(
            self.value["max_operator"], value, self.value.get("max", 0.0)
        ):
            return "max"
        if self.value.get("min_operator") and self._get_value_evaluation(
            self.value["min_operator"], value, self.value.get("min_warning", 0.0)
        ):
            return "min_warning"
        if self.value.get("max_operator") and self._get_value_evaluation(
            self.value["max_operator"], value, self.value.get("max_warning", 0.0)
        ):
            return "max_warning"
        return "valid"

    def _get_value_evaluation(self, operator, value, warning):
        if operator == "lt":
            return value < warning
        if operator == "le":
            return value <= warning
        if operator == "gt":
            return value > warning
        if operator == "ge":
            return value >= warning

    @api.model_create_multi
    def create(self, mvals):
        for vals in mvals:
            if vals.get("identifier", "/") == "/":
                vals["identifier"] = self._get_identifier(vals)
        return super().create(mvals)

    def _get_identifier(self, vals):
        return (
            self.env["ir.sequence"]
            .with_company(vals.get("company_id", self.env.company.id))
            .next_by_code("lims.analysis")
            or "/"
        )

    @api.model
    def _add_missing_default_values(self, values):
        defaults = super()._add_missing_default_values(values)
        analyte = self.env["lims.analyte"].browse(defaults.get("analyte_id")).exists()
        if "uom_id" not in values:
            defaults["uom_id"] = analyte.uom_id.id
        if "name" not in values:
            defaults["name"] = analyte.name
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
            raise AccessDenied(self.env._("You are not allowed to analyze this"))
        for record in self.filtered(lambda r: r.state == "to_analyze"):
            record.write(record._analyze_action_vals())
        # We need to use sudo as an analyst shouldn't be able to modify the sample,
        # but we want to trigger the check to verify which is based on analyses states
        self.mapped("sample_id").sudo()._check_analysis_state()

    def _analyze_action_vals(self):
        return {
            "state": "to_be_verified",
            "analyst_id": self.env.user.id,
            "submitted_date": fields.Datetime.now(),
        }

    def verify_action(self):
        if not self.env.user.has_group("lims.group_lims_verifier"):
            raise AccessDenied(self.env._("You are not allowed to verify an analysis"))
        for record in self.filtered(lambda r: r.can_verify):
            record.write(record._verify_action_vals())
        # We need to use sudo as a verifier shouldn't be able to modify the sample,
        # but we want to trigger the check verify which is based on analyses states
        self.mapped("sample_id").sudo()._check_analysis_state()

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
        verify_param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("lims.unforce_double_verification_manager")
        ) and self.env.user.has_group("lims.group_lims_manager")
        for record in self:
            record.can_verify = record.state == "to_be_verified" and (
                verify_param
                or record.analyst_id != self.env.user
                or record.analyte_id.autoverify
            )

    def retract_action(self):
        if not self.env.user.has_group("lims.group_lims_verifier"):
            raise AccessDenied(
                self.env._("You are not allowed to retract an analysis to be verified")
            )
        for record in self.filtered(
            lambda r: r.state in ["to_be_verified", "rejected"]
        ):
            record.write(record._retract_action_vals())
        # We need to use sudo as a verifier shouldn't be able to modify the sample,
        # but we want to trigger the check verify which is based on analyses states
        self.mapped("sample_id").sudo()._check_analysis_state()

    def _retract_action_vals(self):
        return {
            "state": "to_analyze",
            "analyst_id": False,
            "submitted_date": False,
        }

    def reject_action(self):
        self.write({"state": "rejected"})
        self.mapped("sample_id").sudo()._check_analysis_state()

    def _get_report_value(self):
        self.ensure_one()
        if self.value["result_type"] == "float":
            lang = self.env["res.lang"]._lang_get(
                self.env.context.get("lang") or self.env.user.lang
            )
            return lang.format(
                f"%.{self.value.get('digits')}f", self.value.get("value"), grouping=True
            )
        if self.value["result_type"] == "date" and self.value.get("value"):
            return format_date(self.env, fields.Date.to_date(self.value.get("value")))
        if self.value["result_type"] == "datetime" and self.value.get("value"):
            return format_datetime(
                self.env, fields.Datetime.to_datetime(self.value.get("value"))
            )
        if self.value["result_type"] == "multiselection":
            return ", ".join(self.value.get("value", []))
        return self.value.get("value")

    def _get_reference_value(self):
        self.ensure_one()
        if self.value["result_type"] != "float":
            return ""
        value = []
        lang = self.env["res.lang"]._lang_get(
            self.env.context.get("lang") or self.env.user.lang
        )
        if self.value.get("min_operator"):
            value.append(
                lang.format(
                    f"%.{self.value.get('digits')}f",
                    self.value.get("min_warning"),
                    grouping=True,
                )
            )
        if self.value.get("max_operator"):
            value.append(
                lang.format(
                    f"%.{self.value.get('digits')}f",
                    self.value.get("max_warning"),
                    grouping=True,
                )
            )
        if not value:
            return ""
        result = self.env._("RV: ") + ("/".join(value))
        if self.uom_id:
            result += f" {self.uom_id.name}"
        return result
