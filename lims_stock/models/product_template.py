# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_specimen = fields.Boolean(
        help="If checked, this product is storable and tracked by serial number "
        "for LIMS samples.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("is_specimen"):
                vals["tracking"] = "serial"
                vals["is_storable"] = True
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("is_specimen"):
            vals = dict(vals, tracking="serial", is_storable=True)
        return super().write(vals)
