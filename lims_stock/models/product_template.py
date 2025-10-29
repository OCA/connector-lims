# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_specimen = fields.Boolean(
        string="Is Specimen",
        default=False,
        help="If checked, this product's variants will be tracked by serial number for specimens.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        # set tracking='serial' on variants if is_specimen true
        to_update = recs.filtered(lambda r: r.is_specimen)
        if to_update:
            for tmpl in to_update:
                if tmpl.product_variant_ids:
                    tmpl.product_variant_ids.sudo().write({"tracking": "serial", "is_storable": True})
        return recs

    def write(self, vals):
        res = super().write(vals)
        # if is_specimen changed to True on any template, enforce variant tracking
        if "is_specimen" in vals:
            templates = self.filtered(lambda t: t.is_specimen)
            for tmpl in templates:
                if tmpl.product_variant_ids:
                    tmpl.product_variant_ids.sudo().write({"tracking": "serial", "is_storable": True})
        return res
