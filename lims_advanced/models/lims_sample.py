# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from . import lims_stage


class LimsSample(models.Model):
    _inherit = "lims.sample"

    tag_ids = fields.Many2many(
        "lims.tag",
        "lims_sample_tag_rel",
        "sample_id",
        "tag_id",
        string="Tags",
    )
    category_ids = fields.Many2many("lims.category", string="Categories")
    team_id = fields.Many2one("lims.team", index=True, tracking=True)
    laboratory_id = fields.Many2one(
        "res.partner",
        string="Laboratory",
        index=True,
        tracking=True,
        domain="[('is_laboratory', '=', True)]",
    )
    operator_id = fields.Many2one(
        "res.partner",
        string="Assigned Operator",
        index=True,
        domain="[('is_lims_operator', '=', True)]",
    )
    physician_id = fields.Many2one(
        "res.partner",
        string="Ordering Physician",
        index=True,
        domain="[('is_physician', '=', True)]",
    )
    workflow_priority = fields.Selection(
        lims_stage.AVAILABLE_PRIORITIES,
        default=lims_stage.AVAILABLE_PRIORITIES[0][0],
    )
    color = fields.Integer(default=0)
