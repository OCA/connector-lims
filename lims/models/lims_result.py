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
    result_min = fields.Float(related="order_test_id.test_id.normal_range_min")
    result_max = fields.Float(related="order_test_id.test_id.normal_range_max")
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
        related="order_test_id.specimen_id.partner_id",
        tracking=True,
        index=True,
        copy=False,
    )
    validated_by_user_id = fields.Many2one("res.users")
    order_test_id = fields.Many2one("lims.order.test")
    team_id = fields.Many2one(related="order_test_id.team_id")
    specimen_id = fields.Many2one(related="order_test_id.specimen_id")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code("lims.result") or _(
                    "New"
                )
        return super().create(vals_list)
