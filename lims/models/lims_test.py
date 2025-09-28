# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LIMSTest(models.Model):
    _name = "lims.test"
    _description = "LIMS Test"

    name = fields.Char(required=True)
    loinc_code_id = fields.Many2one("loinc.code")
    description = fields.Text()
    normal_range_min = fields.Float()
    normal_range_max = fields.Float()
    method_id = fields.Many2one("lims.method")
    instrument_id = fields.Many2one("lims.instrument")
    template_ids = fields.Many2many("lims.template")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        index=True,
        help="Company related to this test",
    )

    def _prepare_order_test_values(self):
        """Give the values to create the corresponding order test.

        :return: `lims.order.test` create values
        :rtype: dict
        """
        self.ensure_one()
        return {
            "name": "New",
            "test_id": self.id,
            "instrument_id": self.instrument_id.id,
        }
