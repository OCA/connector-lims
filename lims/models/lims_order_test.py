# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LIMSOrderTest(models.Model):
    _name = "lims.order.test"
    _description = "LIMS Order Test"
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
    category_ids = fields.Many2many("lims.category", string="Categories")
    tag_ids = fields.Many2many(
        "lims.tag",
        "lims_order_line_tag_rel",
        "lims_order_line_id",
        "tag_id",
        string="Tags",
        help="Classify and analyze your work orders",
    )
    batch_id = fields.Many2one(
        "lims.batch",
        string="Batch",
        index=True,
    )
    laboratory_id = fields.Many2one(
        "res.partner",
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
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
        help="Company related to this order",
    )
    specimen_id = fields.Many2one(
        "lims.specimen", string="Specimen", related="order_id.specimen_id", index=True
    )
    operator_id = fields.Many2one(
        "res.partner",
        string="Assigned To",
        index=True,
        domain="[('is_lims_operator', '=', True)]",
    )
    scheduled_date = fields.Datetime()
    date = fields.Datetime()
    todo = fields.Text(string="Instructions", related="test_id.method_id.description")
    instrument_id = fields.Many2one("lims.instrument")
    test_id = fields.Many2one("lims.test")
    result_ids = fields.One2many("lims.result", "order_test_id", string="Results")

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
                    "lims.order.test"
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
        return self.write(
            {"stage_id": self.env.ref("lims.lims_stage_order_completed").id}
        )

    def action_cancel(self):
        return self.write(
            {"stage_id": self.env.ref("lims.lims_stage_order_cancelled").id}
        )
