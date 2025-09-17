# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from . import lims_stage


class LIMSOrder(models.Model):
    _name = "lims.order"
    _description = "LIMS Order"
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

    def _default_team_id(self):
        team = self.env["lims.team"].search(
            [("company_id", "in", (self.env.company.id, False))],
            order="sequence asc",
            limit=1,
        )
        if team:
            return team
        raise ValidationError(_("You must create an LIMS team first."))

    def _default_laboratory_id(self):
        rec = self.env["lims.laboratory"].search(
            [("company_id", "in", (self.env.company.id, False))],
            order="sequence asc",
            limit=1,
        )
        if rec:
            return rec
        raise ValidationError(_("You must create a laboratory first."))

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

    @api.depends("stage_id")
    def _get_stage_color(self):
        """Get stage color"""
        self.custom_color = self.stage_id.custom_color or "#FFFFFF"

    def _track_subtype(self, init_values):
        self.ensure_one()
        if "stage_id" in init_values:
            if self.stage_id.id == self.env.ref("lims.lims_stage_completed").id:
                return self.env.ref("lims.mt_order_completed")
            elif self.stage_id.id == self.env.ref("lims.lims_stage_cancelled").id:
                return self.env.ref("lims.mt_order_cancelled")
        return super()._track_subtype(init_values)

    def _calc_request_late(self, vals):
        if vals.get("request_early", False):
            early = fields.Datetime.from_string(vals.get("request_early"))
        else:
            early = datetime.now()

        if vals.get("priority") == "0":
            vals["request_late"] = early + timedelta(
                hours=self.env.company.lims_order_request_late_lowest
            )
        elif vals.get("priority") == "1":
            vals["request_late"] = early + timedelta(
                hours=self.env.company.lims_order_request_late_low
            )
        elif vals.get("priority") == "2":
            vals["request_late"] = early + timedelta(
                hours=self.env.company.lims_order_request_late_medium
            )
        elif vals.get("priority") == "3":
            vals["request_late"] = early + timedelta(
                hours=self.env.company.lims_order_request_late_high
            )
        return vals

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
    tag_ids = fields.Many2many(
        "lims.tag",
        "lims_order_tag_rel",
        "lims_order_id",
        "tag_id",
        string="Tags",
        help="Classify and analyze your analysis",
    )
    color = fields.Integer("Color Index", default=0)
    laboratory_id = fields.Many2one(
        "lims.laboratory",
        string="Laboratory",
        default=lambda self: self._default_laboratory_id(),
        index=True,
        required=True,
        tracking=True,
    )
    team_id = fields.Many2one(
        "lims.team",
        string="Team",
        default=lambda self: self._default_team_id(),
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
    line_ids = fields.One2many("lims.order.line", "order_id", string="Work Orders")
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        tracking=True,
        index=True,
        copy=False,
    )
    request_early = fields.Datetime(
        string="Earliest Request Date", default=datetime.now()
    )
    request_late = fields.Datetime(string="Latest Request Date")
    color = fields.Integer("Color Index")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
        help="Company related to this order",
    )

    description = fields.Text()

    # Planning
    operator_id = fields.Many2one("lims.operator", string="Assigned To", index=True)
    sample_id = fields.Many2one("lims.sample", string="Sample", index=True)
    scheduled_date_start = fields.Datetime(string="Scheduled Start (ETA)")
    scheduled_duration = fields.Float(help="Scheduled duration of the work in hours")
    scheduled_date_end = fields.Datetime(string="Scheduled End")
    sequence = fields.Integer(default=10)

    # Execution
    date_start = fields.Datetime(string="Actual Start")
    date_end = fields.Datetime(string="Actual End")
    duration = fields.Float(
        string="Actual duration",
        compute=_compute_duration,
        help="Actual duration in hours",
    )
    current_date = fields.Datetime(default=fields.Datetime.now, store=True)

    # Field for Stage Color
    custom_color = fields.Char(related="stage_id.custom_color", string="Stage Color")

    # Template
    template_id = fields.Many2one("lims.template", string="Template")
    category_ids = fields.Many2many("lims.category", string="Categories")

    # Equipment used for Maintenance
    equipment_id = fields.Many2one("lims.equipment", string="Equipment")

    type = fields.Many2one("lims.order.type")
    internal_type = fields.Selection(related="type.internal_type")

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
                vals["name"] = self.env["ir.sequence"].next_by_code("lims.order") or _(
                    "New"
                )
            self._calc_scheduled_dates(vals)
            if not vals.get("request_late"):
                vals = self._calc_request_late(vals)
        return super().create(vals_list)

    is_button = fields.Boolean(default=False)

    def write(self, vals):
        if vals.get("stage_id", False) and vals.get("is_button", False):
            vals["is_button"] = False
        else:
            stage_id = self.env["lims.stage"].browse(vals.get("stage_id"))
            if stage_id == self.env.ref("lims.lims_stage_completed"):
                raise UserError(_("Cannot move to completed from Kanban"))
        self._calc_scheduled_dates(vals)
        res = super().write(vals)
        return res

    def can_unlink(self):
        """:return True if the order can be deleted, False otherwise"""
        return self.stage_id == self._default_stage_id()

    def unlink(self):
        if all(order.can_unlink() for order in self):
            return super().unlink()
        raise ValidationError(_("You cannot delete this order."))

    def _calc_scheduled_dates(self, vals):
        """Calculate scheduled dates and duration"""

        if (
            vals.get("scheduled_duration") is not None
            or vals.get("scheduled_date_start")
            or vals.get("scheduled_date_end")
        ):
            if vals.get("scheduled_date_start") and vals.get("scheduled_date_end"):
                new_date_start = fields.Datetime.from_string(
                    vals.get("scheduled_date_start", False)
                )
                new_date_end = fields.Datetime.from_string(
                    vals.get("scheduled_date_end", False)
                )
                hours = new_date_end.replace(second=0) - new_date_start.replace(
                    second=0
                )
                hrs = hours.total_seconds() / 3600
                vals["scheduled_duration"] = float(hrs)

            elif vals.get("scheduled_date_end"):
                hrs = (
                    vals.get("scheduled_duration", False)
                    or self.scheduled_duration
                    or 0
                )
                date_to_with_delta = fields.Datetime.from_string(
                    vals.get("scheduled_date_end", False)
                ) - timedelta(hours=hrs)
                vals["scheduled_date_start"] = str(date_to_with_delta)

            elif (
                vals.get("scheduled_duration", False) is not None
                and vals.get("scheduled_date_start", self.scheduled_date_start)
                and (
                    self.scheduled_date_start != vals.get("scheduled_date_start", False)
                )
            ):
                hours = vals.get("scheduled_duration", False)
                start_date_val = vals.get(
                    "scheduled_date_start", self.scheduled_date_start
                )
                start_date = fields.Datetime.from_string(start_date_val)
                date_to_with_delta = start_date + timedelta(hours=hours)
                vals["scheduled_date_end"] = str(date_to_with_delta)
        elif vals.get("scheduled_date_start") is not None:
            vals["scheduled_date_end"] = False

    def action_complete(self):
        return self.write(
            {
                "stage_id": self.env.ref("lims.lims_stage_completed").id,
                "is_button": True,
            }
        )

    def action_cancel(self):
        return self.write({"stage_id": self.env.ref("lims.lims_stage_cancelled").id})

    @api.onchange("scheduled_date_end")
    def onchange_scheduled_date_end(self):
        if self.scheduled_date_end:
            date_to_with_delta = fields.Datetime.from_string(
                self.scheduled_date_end
            ) - timedelta(hours=self.scheduled_duration)
            self.date_start = str(date_to_with_delta)

    @api.onchange("scheduled_date_start", "scheduled_duration")
    def onchange_scheduled_duration(self):
        if self.scheduled_duration and self.scheduled_date_start:
            date_to_with_delta = fields.Datetime.from_string(
                self.scheduled_date_start
            ) + timedelta(hours=self.scheduled_duration)
            self.scheduled_date_end = str(date_to_with_delta)
        else:
            self.scheduled_date_end = self.scheduled_date_start

    @api.onchange("template_id")
    def _onchange_template_id(self):
        if self.template_id:
            self.category_ids = self.template_id.category_ids
            self.scheduled_duration = self.template_id.duration
            if self.template_id.type_id:
                self.type = self.template_id.type_id
            if self.template_id.team_id:
                self.team_id = self.template_id.team_id

    @api.constrains("scheduled_date_start")
    def check_day(self):
        for rec in self:
            if not rec.scheduled_date_start:
                continue

            holidays = self.env["resource.calendar.leaves"].search(
                [
                    ("date_from", ">=", rec.scheduled_date_start),
                    ("date_to", "<=", rec.scheduled_date_end),
                ]
            )
            if holidays:
                msg = (
                    f"{rec.scheduled_date_start.date()} is a holiday {holidays[0].name}"
                )
                raise ValidationError(_(msg))
