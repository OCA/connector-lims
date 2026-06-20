# Copyright (C) 2025 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LimsStage(models.Model):
    _name = "lims.stage"
    _description = "LIMS Stage"
    _order = "sequence, name, id"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    sequence = fields.Integer(default=1, help="Used to order stages. Lower is better.")
    fold = fields.Boolean(
        "Folded in Kanban",
        help="This stage is folded in the kanban view when "
        "there are no records in that stage to display.",
    )
    is_closed = fields.Boolean(
        "Is a close stage", help="Services in this stage are considered as closed."
    )
    is_default = fields.Boolean("Is a default stage", help="Used as default stage")
    description = fields.Text(translate=True)
    stage_type = fields.Selection(
        [
            ("sample", "Sample"),
            ("order", "Order"),
            ("batch", "Batch"),
            ("instrument", "Instrument"),
            ("result", "Result"),
        ],
        "Apply on",
        required=True,
        default="sample",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.user.company_id.id,
    )

    @api.model_create_multi
    def create(self, vals_list):
        stages = self.search([])
        for vals in vals_list:
            for stage in stages:
                if stage.stage_type == vals.get(
                    "stage_type"
                ) and stage.sequence == vals.get("sequence"):
                    raise ValidationError(
                        _(
                            "Cannot create LIMS Stage because "
                            "it has the same Type and Sequence "
                            "of an existing one."
                        )
                    )
        return super().create(vals_list)
