# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LIMSSpecimen(models.Model):
    _name = "lims.specimen"
    _inherit = ["mail.thread", "mail.activity.mixin", "lims.model.mixin"]
    _description = "LIMS Specimen"
    _stage_type = "specimen"

    def _default_stage_id(self):
        stage = self.env["lims.stage"].search(
            [
                ("stage_type", "=", "specimen"),
                ("is_default", "=", True),
                ("company_id", "in", (self.env.company.id, False)),
            ],
            order="sequence asc",
            limit=1,
        )
        if stage:
            return stage
        raise ValidationError(_("You must create a LIMS specimen stage first."))

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
    partner_id = fields.Many2one(
        "res.partner",
        string="Owner",
        tracking=True,
        index=True,
        copy=False,
    )
    collection_date = fields.Datetime()
    specimen_type = fields.Char()
    order_id = fields.Many2one("lims.order")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "lims.specimen"
                ) or _("New")
        return super().create(vals_list)
