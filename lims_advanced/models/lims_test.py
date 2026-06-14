# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class LIMSTest(models.Model):
    _name = "lims.test"
    _description = "LIMS Test"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True)
    product_tmpl_id = fields.Many2one("product.template", string="Product")
    product_id = fields.Many2one(
        "product.product",
        string="Product Variant",
        compute="_compute_product_id",
        store=True,
    )
    loinc_code_id = fields.Many2one("loinc.code")
    description = fields.Text()
    method_id = fields.Many2one("lims.method")
    instrument_id = fields.Many2one("lims.instrument")
    test_result_ids = fields.One2many(
        "lims.test.result",
        "test_id",
        string="Result Definitions",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        index=True,
        help="Company related to this test",
    )

    @api.depends("product_tmpl_id")
    def _compute_product_id(self):
        for test in self:
            test.product_id = test.product_tmpl_id.product_variant_id

    def _prepare_analysis_values(self):
        self.ensure_one()
        return {
            "product_id": self.product_id.id,
            "name": self.name,
            "test_id": self.id,
            "instrument_id": self.instrument_id.id,
            "uom_id": self.product_id.laboratory_uom_id.id
            if self.product_id
            else False,
        }
