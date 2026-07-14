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
    state = fields.Selection(
        [
            ("registered", "Registered"),
            ("scheduled_sampling", "Scheduled Sampling"),
            ("due", "Sample due"),
            ("received", "Received"),
            ("to_be_verified", "To be verified"),
            ("verified", "Verified"),
            ("cancelled", "Cancelled"),
            ("invalid", "Invalid"),
        ],
        required=True,
        default="due",
        readonly=True,
        tracking=True,
    )
    sample_type_id = fields.Many2one(
        "lims.sample.type",
        required=True,
        tracking=True,
    )
    sample_date = fields.Datetime(
        default=fields.Datetime.now(),
        required=True,
        readonly=True,
        tracking=True,
    )
    received_date = fields.Datetime(readonly=True)
    verification_date = fields.Datetime(readonly=True)
    partner_id = fields.Many2one("res.partner", tracking=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company.id, tracking=True
    )
    priority = fields.Selection(
        [
            ("1", "Highest"),
            ("2", "High"),
            ("3", "Normal"),
            ("4", "Low"),
            ("5", "Lowest"),
        ],
        required=True,
        default="3",
    )
    analysis_ids = fields.One2many("lims.analysis", inverse_name="sample_id")
    interpretation = fields.Html()
    progress = fields.Float(
        compute="_compute_progress",
        store=True,
    )
    _identifier_unique = models.Constraint(
        "unique(identifier, company_id)", "Sample identifier must be unique"
    )

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
            .next_by_code("lims.sample")
            or "/"
        )

    def receive_sample_action(self):
        for record in self.filtered(lambda r: r.state == "due"):
            record.write(record._receive_sample_vals())
            record.analysis_ids._receive_sample()

    def _receive_sample_vals(self):
        return {
            "state": "received",
            "received_date": fields.Datetime.now(),
        }

    def _check_analysis_state(self):
        for record in self:
            if record.state in ["registered", "scheduled_sampling", "due"]:
                continue
            if record._check_verify():
                if record.state != "verified":
                    record.write(record._check_verify_vals())
            elif record._check_to_verify():
                if record.state != "to_be_verified":
                    record.write(record._check_to_verify_vals())
            else:
                record.write({"state": "received"})

    def _check_to_verify(self):
        return not self.analysis_ids.filtered(
            lambda r: r.state in ["registered", "to_analyze"]
            and r.display_type == "analyte"
        )

    def _check_to_verify_vals(self):
        return {"state": "to_be_verified"}

    def _check_verify(self):
        return not self.analysis_ids.filtered(
            lambda r: r.state in ["registered", "to_analyze", "to_be_verified"]
            and r.display_type == "analyte"
        )

    def _check_verify_vals(self):
        return {"state": "verified", "verification_date": fields.Datetime.now()}

    @api.depends("analysis_ids", "analysis_ids.progress")
    def _compute_progress(self):
        for record in self:
            record.progress = record._get_progress()

    def get_analysis(self):
        return self.analysis_ids.filtered(
            lambda r: r.state not in ["invalid"] and r.display_type == "analyte"
        )

    def _get_progress(self):
        analysis = self.get_analysis()
        if not analysis:
            return 0
        return sum(analysis.mapped("progress")) / len(analysis)
