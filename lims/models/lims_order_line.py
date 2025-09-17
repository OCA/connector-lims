# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from . import lims_stage


class LIMSOrderLine(models.Model):
    _name = "lims.order.line"
    _description = "LIMS Order Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _default_stage_id(self):
        stage = self.env["lims.stage"].search(
            [
                ("stage_type", "=", "order"),
                ("is_default", "=", True),
                ("company_id", "in", (self.env.company.id, False)),
            ],
            order="sequence asc",
            limit=1,
        )
        if stage:
            return stage
        raise ValidationError(_("You must create a LIMS order stage first."))

    @api.depends("date_start", "date_end")
    def _compute_duration(self):
        for rec in self:
            duration = 0.0
            if rec.date_start and rec.date_end:
                start = fields.Datetime.from_string(rec.date_start)
                end = fields.Datetime.from_string(rec.date_end)
                delta = end - start
                duration = delta.total_seconds() / 3600
            rec.duration = duration

    def _track_subtype(self, init_values):
        self.ensure_one()
        if "stage_id" in init_values:
            if self.stage_id.id == self.env.ref("lims.lims_stage_completed").id:
                return self.env.ref("lims.mt_order_completed")
            elif self.stage_id.id == self.env.ref("lims.lims_stage_cancelled").id:
                return self.env.ref("lims.mt_order_cancelled")
        return super()._track_subtype(init_values)

    stage_id = fields.Many2one(
        "lims.stage",
        string="Stage",
        tracking=True,
        index=True,
        copy=False,
        group_expand="_read_group_stage_ids",
        default=lambda self: self._default_stage_id(),
    )
    is_closed = fields.Boolean(
        "Is closed",
        related="stage_id.is_closed",
    )
    priority = fields.Selection(
        lims_stage.AVAILABLE_PRIORITIES,
        index=True,
        default=lims_stage.AVAILABLE_PRIORITIES[0][0],
    )
    category_ids = fields.Many2many("lims.category", string="Categories")
    tag_ids = fields.Many2many(
        "lims.tag",
        "lims_order_line_tag_rel",
        "lims_order_line_id",
        "tag_id",
        string="Tags",
        help="Classify and analyze your work orders",
    )
    color = fields.Integer("Color Index", default=0)
    batch_id = fields.Many2one(
        "lims.batch",
        string="Batch",
        index=True,
    )
    laboratory_id = fields.Many2one(
        "lims.laboratory",
        string="Laboratory",
        related="order_id.laboratory_id",
        index=True,
        required=True,
        tracking=True,
    )
    team_id = fields.Many2one(
        "lims.team",
        string="Team",
        related="order_id.team_id",
        index=True,
        required=True,
        tracking=True,
    )

    # Request
    name = fields.Char(
        required=True,
        index=True,
        copy=False,
        default=lambda self: _("New"),
    )
    order_id = fields.Many2one(
        "lims.order",
        string="Analysis",
        required=True,
        index=True,
    )
    request_early = fields.Datetime(
        string="Earliest Request Date", default=datetime.now()
    )
    request_late = fields.Datetime(string="Latest Request Date")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
        help="Company related to this order",
    )

    # Planning
    sample_id = fields.Many2one(
        "lims.sample", string="Sample", related="order_id.sample_id", index=True
    )
    operator_id = fields.Many2one("lims.operator", string="Assigned To", index=True)
    scheduled_date_start = fields.Datetime(string="Scheduled Start (ETA)")
    scheduled_duration = fields.Float(help="Scheduled duration of the work in hours")
    scheduled_date_end = fields.Datetime(string="Scheduled End")

    # Execution
    date_start = fields.Datetime(string="Actual Start")
    date_end = fields.Datetime(string="Actual End")
    duration = fields.Float(
        string="Actual duration",
        compute=_compute_duration,
        help="Actual duration in hours",
    )
    todo = fields.Text(string="Instructions")
    current_date = fields.Datetime(default=fields.Datetime.now, store=True)

    # Equipment used for Maintenance
    equipment_id = fields.Many2one("lims.equipment", string="Equipment")

    type = fields.Many2one("lims.order.type")
    internal_type = fields.Selection(related="type.internal_type")

    # Result
    result_type = fields.Selection(
        [
            ("manual", "Manual"),
            ("calculated", "Calculated"),
        ],
        required=True,
        default="manual",
    )
    result_formula = fields.Text()
    result_min = fields.Float(string="Minimum")
    result_max = fields.Float(string="Maximum")
    result_value = fields.Float(string="Value")
    success = fields.Boolean()

    @api.model
    def _read_group_stage_ids(self, stages, domain, order=None):
        search_domain = [("stage_type", "=", "order")]
        if self.env.context.get("default_team_id"):
            search_domain = [
                "&",
                ("team_ids", "in", self.env.context["default_team_id"]),
            ] + search_domain
        return stages.search(search_domain, order=order)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "lims.order.line"
                ) or _("New")
        return super().create(vals_list)

    def can_unlink(self):
        """:return True if the order can be deleted, False otherwise"""
        return self.stage_id == self._default_stage_id()

    def unlink(self):
        if all(order.can_unlink() for order in self):
            return super().unlink()
        raise ValidationError(_("You cannot delete this order."))

    def action_complete(self):
        return self.write({"stage_id": self.env.ref("lims.lims_stage_completed").id})

    def action_cancel(self):
        return self.write({"stage_id": self.env.ref("lims.lims_stage_cancelled").id})
