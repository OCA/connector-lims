from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    lims_tracking = fields.Selection(
        [
            ("no", "No LIMS Order"),
            ("order", "Per Sales Order"),
            ("line", "Per Sales Order Line"),
            ("quantity", "Per Quantity"),
        ],
        string="LIMS Tracking",
        default="no",
        help="Defines how LIMS orders are generated when a sale order is confirmed.",
    )

    lims_template_id = fields.Many2one(
        "lims.template",
        string="LIMS Template",
        help="Template used to create the LIMS Order when a Sale Order is confirmed.",
    )
