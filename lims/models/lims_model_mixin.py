# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class LIMSModelMixin(models.AbstractModel):
    _name = "lims.model.mixin"
    _description = "LIMS Model Mixin"
    _stage_type = ""

    stage_id = fields.Many2one(
        "lims.stage",
        string="Stage",
        tracking=True,
        index=True,
        copy=False,
        group_expand="_read_group_stage_ids",
        default=lambda self: self._default_stage_id(),
    )
    hide = fields.Boolean()

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        return self.env["lims.stage"].search([("stage_type", "=", self._stage_type)])

    def _default_stage_id(self):
        return self.env["lims.stage"].search(
            [("stage_type", "=", self._stage_type)], limit=1
        )

    def new_stage(self, operator):
        seq = self.stage_id.sequence
        order_by = "asc" if operator == ">" else "desc"
        new_stage = self.env["lims.stage"].search(
            [("stage_type", "=", self._stage_type), ("sequence", operator, seq)],
            order=f"sequence {order_by}",
            limit=1,
        )
        if new_stage:
            self.stage_id = new_stage
            self._onchange_stage_id()

    def next_stage(self):
        self.new_stage(">")

    def previous_stage(self):
        self.new_stage("<")

    @api.onchange("stage_id")
    def _onchange_stage_id(self):
        # get last stage
        highest_stage = self.env["lims.stage"].search(
            [("stage_type", "=", self._stage_type)], order="sequence desc", limit=1
        )
        self.hide = self.stage_id.name == highest_stage.name
