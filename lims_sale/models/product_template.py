# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models
from odoo.fields import Command


class ProductTemplate(models.Model):
    _inherit = "product.template"

    lims_tracking = fields.Selection(
        [
            ("no", "No LIMS Sample"),
            ("order", "Per Sales Order"),
            ("line", "Per Sales Order Line"),
            ("quantity", "Per Quantity"),
        ],
        default="no",
        help="Defines how LIMS samples are generated when a sale order is confirmed.",
    )
    lims_sample_type_id = fields.Many2one(
        "lims.sample.type",
        help="Sample type used when creating a LIMS sample from a sale order.",
    )
    lims_analyte_ids = fields.Many2many(
        "lims.analyte",
        help="Default analytes proposed on sale order lines for this product.",
    )

    def _prepare_lims_sample_vals(
        self, sale_order, analysis_commands, sale_origin=None
    ):
        """Build values to create a lims.sample from this product configuration.

        ``analysis_commands`` is a list of ``Command.create`` values for
        ``lims.analysis``, including ``analyte_id`` and optional
        ``sale_order_line_id``.
        """
        self.ensure_one()
        return {
            "sample_type_id": self.lims_sample_type_id.id,
            "partner_id": sale_order.partner_id.id,
            "company_id": sale_order.company_id.id,
            "sale_order_ids": [Command.set(sale_order.ids)],
            "sale_origin": sale_origin or sale_order.name,
            "external_identifier": sale_origin or sale_order.name,
            "analysis_ids": analysis_commands,
        }

    def _create_lims_sample(self, sale_order, analysis_commands, sale_origin=None):
        self.ensure_one()
        if (
            self.lims_tracking == "no"
            or not self.lims_sample_type_id
            or not analysis_commands
        ):
            return self.env["lims.sample"]
        return self.env["lims.sample"].create(
            self._prepare_lims_sample_vals(
                sale_order, analysis_commands, sale_origin=sale_origin
            )
        )
