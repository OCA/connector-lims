# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class LIMSInstrument(models.Model):
    _name = "lims.instrument"
    _description = "LIMS Instrument"
    _inherit = ["mail.thread", "mail.activity.mixin", "lims.model.mixin"]
    _stage_type = "instrument"

    def _default_stage_id(self):
        stage = self.env["lims.stage"].search(
            [
                ("stage_type", "=", "instrument"),
                ("is_default", "=", True),
                ("company_id", "in", (self.env.company.id, False)),
            ],
            order="sequence asc",
            limit=1,
        )
        if stage:
            return stage
        raise ValidationError(_("You must create a LIMS instrument stage first."))

    name = fields.Char(required=True)
    color = fields.Integer("Color Index", default=0)
    operator_id = fields.Many2one(
        "res.partner",
        string="Assigned Operator",
        domain="[('is_lims_operator', '=', True)]",
    )
    notes = fields.Text()
    laboratory_id = fields.Many2one(
        "res.partner", string="Laboratory", domain="[('is_laboratory', '=', True)]"
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
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
        help="Company related to this equipment",
    )

    _sql_constraints = [
        ("name_company_uniq", "unique (name, company_id)", "Instrument already exists!")
    ]
