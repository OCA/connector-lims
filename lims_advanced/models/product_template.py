# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    loinc_code_id = fields.Many2one("loinc.code", string="LOINC Code")
    lims_method_id = fields.Many2one("lims.method", string="Method")
    lims_instrument_id = fields.Many2one("lims.instrument", string="Instrument")
    normal_range_min = fields.Float()
    normal_range_max = fields.Float()
    lims_test_id = fields.Many2one(
        "lims.test",
        string="LIMS Test Profile",
        compute="_compute_lims_test_id",
        inverse="_inverse_lims_test_id",
    )

    def _compute_lims_test_id(self):
        Test = self.env["lims.test"]
        for template in self:
            template.lims_test_id = Test.search(
                [("product_tmpl_id", "=", template.id)], limit=1
            )

    def _inverse_lims_test_id(self):
        for template in self:
            if template.lims_test_id:
                template.lims_test_id.product_tmpl_id = template.id
