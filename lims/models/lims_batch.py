# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from . import lims_stage


class LIMSBatch(models.Model):
    _name = "lims.batch"
    _description = "LIMS Batch"
    _inherit = ["mail.thread", "mail.activity.mixin", "lims.model.mixin"]

    def _default_stage_id(self):
        stage = self.env["lims.stage"].search(
            [
                ("stage_type", "=", "batch"),
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
        rec = self.env["res.partner"].search(
            [
                ("is_laboratory", "=", True),
                ("company_id", "in", (self.env.company.id, False)),
            ],
            order="id asc",
            limit=1,
        )
        if rec:
            return rec
        raise ValidationError(_("You must create a laboratory first."))

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
    laboratory_id = fields.Many2one(
        "res.partner",
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
    name = fields.Char(
        required=True,
        index=True,
        copy=False,
        default=lambda self: _("New"),
    )
    test_id = fields.Many2one("lims.test")
    test_ids = fields.One2many(
        "lims.order.test",
        "batch_id",
        string="Tests",
        domain="[('test_id', '=', test_id.id)]",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
        help="Company related to this order",
    )
    description = fields.Text()
    operator_id = fields.Many2one(
        "res.partner",
        string="Assigned To",
        index=True,
        domain="[('is_lims_operator', '=', True)]",
    )
    instrument_id = fields.Many2one(related="test_id.instrument_id")
    scheduled_date = fields.Date()

    @api.model
    def _read_group_stage_ids(self, stages, domain, order=None):
        search_domain = [("stage_type", "=", "batch")]
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
                vals["name"] = self.env["ir.sequence"].next_by_code("lims.batch") or _(
                    "New"
                )
        return super().create(vals_list)

    def can_unlink(self):
        """:return True if the order can be deleted, False otherwise"""
        return self.stage_id == self._default_stage_id()

    def unlink(self):
        if all(rec.can_unlink() for rec in self):
            return super().unlink()
        raise ValidationError(_("You cannot delete this batch."))

    def action_complete(self):
        completed_stage = self.env.ref(
            "lims.lims_stage_order_completed", raise_if_not_found=False
        )
        for batch in self:
            # Find tests that are not completed
            incomplete_tests = batch.test_ids.filtered(
                lambda t: t.stage_id != completed_stage
            )
            if incomplete_tests:
                raise ValidationError(
                    _(
                        "You cannot complete this batch because some associated tests "
                        "are not yet completed:\n %s"
                    )
                    % ", ".join(incomplete_tests.mapped("name"))
                )

            batch.stage_id = completed_stage.id
        return True

    def action_cancel(self):
        return self.write(
            {"stage_id": self.env.ref("lims.lims_stage_order_cancelled").id}
        )

    @api.onchange("operator_id", "scheduled_date", "instrument_id")
    def _onchange_test_ids(self):
        if self.operator_id or self.scheduled_date or self.instrument_id:
            self.test_ids.write(
                {
                    "operator_id": self.operator_id.id,
                    "scheduled_date": self.scheduled_date,
                    "instrument_id": self.instrument_id.id,
                }
            )
