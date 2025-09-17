# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class LIMSSample(models.Model):
    _name = "lims.sample"
    _inherit = ["mail.thread", "mail.activity.mixin", "lims.model.mixin"]
    _description = "LIMS Sample"
    _stage_type = "sample"

    def _default_stage_id(self):
        stage = self.env["lims.stage"].search(
            [
                ("stage_type", "=", "sample"),
                ("is_default", "=", True),
                ("company_id", "in", (self.env.company.id, False)),
            ],
            order="sequence asc",
            limit=1,
        )
        if stage:
            return stage
        raise ValidationError(_("You must create a LIMS sample stage first."))

    name = fields.Char(
        required=True,
        index=True,
        copy=False,
        default=lambda self: _("New"),
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
    owner_id = fields.Many2one(
        "res.partner",
        string="Owner",
        tracking=True,
        index=True,
        copy=False,
    )
