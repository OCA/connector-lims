# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from . import lims_stage


class LIMSOrder(models.Model):
    _name = "lims.order"
    _description = "LIMS Order"
    _inherit = ["mail.thread", "mail.activity.mixin", "lims.model.mixin"]
    _stage_type = "order"

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

    def _track_subtype(self, init_values):
        self.ensure_one()
        if "stage_id" in init_values:
            if self.stage_id.id == self.env.ref("lims.lims_stage_order_completed").id:
                return self.env.ref("lims.mt_order_completed")
            elif self.stage_id.id == self.env.ref("lims.lims_stage_order_cancelled").id:
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
        "res.partner",
        string="Laboratory",
        default=lambda self: self._default_laboratory_id(),
        index=True,
        required=True,
        tracking=True,
        domain="[('is_laboratory', '=', True)]",
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
    test_ids = fields.One2many("lims.order.test", "order_id", string="Tests")
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        tracking=True,
        index=True,
        copy=False,
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
    physician_id = fields.Many2one(
        "res.partner",
        string="Ordering Physician",
        index=True,
        domain="[('is_physician', '=', True)]",
    )
    specimen_id = fields.Many2one("lims.specimen", string="Specimen", index=True)
    scheduled_date = fields.Date()
    date = fields.Date()
    template_id = fields.Many2one("lims.template", string="Template")
    category_ids = fields.Many2many("lims.category", string="Categories")
    instrument_id = fields.Many2one("lims.instrument", string="Instrument")

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
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("stage_id", False):
            stage_id = self.env["lims.stage"].browse(vals.get("stage_id"))
            if stage_id == self.env.ref("lims.lims_stage_order_completed"):
                raise UserError(_("Cannot move to completed from Kanban"))
        return super().write(vals)

    def can_unlink(self):
        """:return True if the order can be deleted, False otherwise"""
        return self.stage_id == self._default_stage_id()

    def unlink(self):
        if all(order.can_unlink() for order in self):
            return super().unlink()
        raise ValidationError(_("You cannot delete this order."))

    def action_complete(self):
        return self.write(
            {
                "stage_id": self.env.ref("lims.lims_stage_order_completed").id,
            }
        )

    def action_cancel(self):
        return self.write(
            {"stage_id": self.env.ref("lims.lims_stage_order_cancelled").id}
        )

    def _prepare_order_test_values(self):
        order_test_data = [fields.Command.clear()]
        for test in self.template_id.test_ids:
            values = test._prepare_order_test_values()
            values.update({"operator_id": self.template_id.operator_id.id})
            order_test_data += [fields.Command.create(values)]
        return order_test_data

    @api.onchange("template_id")
    def _onchange_template_id(self):
        if self.template_id:
            self.write(
                {
                    "operator_id": self.template_id.operator_id.id,
                    "category_ids": self.template_id.category_ids,
                    "test_ids": self._prepare_order_test_values(),
                }
            )
