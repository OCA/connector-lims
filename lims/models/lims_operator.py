# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class LIMSOperator(models.Model):
    _name = "lims.operator"
    _inherits = {"res.partner": "partner_id"}
    _inherit = ["mail.thread.blacklist", "lims.model.mixin"]
    _description = "LIMS Operator"
    _stage_type = "operator"

    partner_id = fields.Many2one(
        "res.partner",
        string="Related Partner",
        required=True,
        ondelete="restrict",
        delegate=True,
        auto_join=True,
    )
    category_ids = fields.Many2many("lims.category", string="Categories")
    calendar_id = fields.Many2one("resource.calendar", string="Working Schedule")
    active = fields.Boolean(default=True)
    active_partner = fields.Boolean(
        related="partner_id.active", readonly=True, string="Partner is Active"
    )

    def toggle_active(self):
        for person in self:
            if not person.active and not person.partner_id.active:
                person.partner_id.toggle_active()
        return super().toggle_active()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.update({"lims_operator": True})
        return super().create(vals_list)
