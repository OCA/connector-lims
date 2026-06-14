# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LIMSResult(models.Model):
    _name = "lims.result"
    _inherit = ["mail.thread", "mail.activity.mixin", "lims.model.mixin"]
    _description = "LIMS Result"
    _stage_type = "result"

    def _default_stage_id(self):
        stage = self.env["lims.stage"].search(
            [
                ("stage_type", "=", "result"),
                ("is_default", "=", True),
                ("company_id", "in", (self.env.company.id, False)),
            ],
            order="sequence asc",
            limit=1,
        )
        if stage:
            return stage
        raise ValidationError(_("You must create a LIMS result stage first."))

    name = fields.Char(
        required=True,
        index=True,
        copy=False,
        default=lambda self: _("New"),
    )
    description = fields.Char()
    result_value = fields.Float()
    result_date = fields.Date()
    result_min = fields.Float(
        compute="_compute_result_range",
        store=True,
    )
    result_max = fields.Float(
        compute="_compute_result_range",
        store=True,
    )
    interpretation = fields.Selection(
        [("preliminary", "Preliminary"), ("final", "Final"), ("approved", "Approved")]
    )
    stage_id = fields.Many2one(
        "lims.stage",
        string="Stage",
        tracking=True,
        index=True,
        copy=False,
        group_expand="_read_group_stage_ids",
        default=lambda self: self._default_stage_id(),
    )
    partner_id = fields.Many2one(
        "res.partner",
        compute="_compute_partner_id",
        store=True,
        tracking=True,
        index=True,
    )
    validated_by_user_id = fields.Many2one("res.users")
    analysis_id = fields.Many2one("lims.analysis", index=True, ondelete="cascade")
    test_result_id = fields.Many2one(
        "lims.test.result",
        string="Result Definition",
        domain="[('test_id', '=', analysis_id.test_id)]",
    )
    team_id = fields.Many2one("lims.team", compute="_compute_team_id", store=True)

    @api.depends("analysis_id")
    def _compute_partner_id(self):
        for result in self:
            if result.analysis_id.sample_id:
                result.partner_id = result.analysis_id.sample_id.customer_id
            else:
                result.partner_id = False

    @api.depends("analysis_id")
    def _compute_team_id(self):
        for result in self:
            if result.analysis_id.sample_id:
                result.team_id = result.analysis_id.sample_id.team_id
            else:
                result.team_id = False

    @api.depends("analysis_id", "analysis_id.product_id", "test_result_id")
    def _compute_result_range(self):
        for result in self:
            test_result = result.test_result_id
            product = result.analysis_id.product_id if result.analysis_id else False
            result.result_min = (
                test_result.result_min
                if test_result
                else (product.normal_range_min if product else 0.0)
            )
            result.result_max = (
                test_result.result_max
                if test_result
                else (product.normal_range_max if product else 0.0)
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code("lims.result") or _(
                    "New"
                )
        return super().create(vals_list)
