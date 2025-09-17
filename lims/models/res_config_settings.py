# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Groups
    group_lims_laboratory = fields.Boolean(
        string="Manage Laboratories", implied_group="lims.group_lims_laboratory"
    )
    group_lims_team = fields.Boolean(
        string="Manage Teams", implied_group="lims.group_lims_team"
    )
    group_lims_category = fields.Boolean(
        string="Manage Categories", implied_group="lims.group_lims_category"
    )
    group_lims_tag = fields.Boolean(
        string="Manage Tags", implied_group="lims.group_lims_tag"
    )
    group_lims_equipment = fields.Boolean(
        string="Manage Equipments", implied_group="lims.group_lims_equipment"
    )
    group_lims_template = fields.Boolean(
        string="Manage Templates", implied_group="lims.group_lims_template"
    )
    group_lims_batch = fields.Boolean(
        string="Manage Batches", implied_group="lims.group_lims_batch"
    )

    # Modules
    module_lims_account = fields.Boolean(string="Invoice your analysis")
    module_lims_maintenance = fields.Boolean(
        string="Manage maintenance of your equipments"
    )
    module_lims_purchase = fields.Boolean(
        string="Manage subcontractors and their pricelists"
    )
    module_lims_sale = fields.Boolean(string="Sell LIMS services")
    module_lims_stock = fields.Boolean(string="Use Odoo Logistics")

    # Priorities
    lims_order_request_late_lowest = fields.Float(
        string="Hours of Buffer for Lowest Priority LIMS Orders",
        related="company_id.lims_order_request_late_lowest",
        readonly=False,
    )
    lims_order_request_late_low = fields.Float(
        string="Hours of Buffer for Low Priority LIMS Orders",
        related="company_id.lims_order_request_late_low",
        readonly=False,
    )
    lims_order_request_late_medium = fields.Float(
        string="Hours of Buffer for Medium Priority LIMS Orders",
        related="company_id.lims_order_request_late_medium",
        readonly=False,
    )
    lims_order_request_late_high = fields.Float(
        string="Hours of Buffer for High Priority LIMS Orders",
        related="company_id.lims_order_request_late_high",
        readonly=False,
    )
