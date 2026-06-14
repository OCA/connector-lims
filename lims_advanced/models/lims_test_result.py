# Copyright (C) 2025 Gray Matter Logic
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LimsTestResult(models.Model):
    _name = "lims.test.result"
    _description = "LIMS Test Result Definition"
    _order = "test_id, sequence, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    description = fields.Char()
    result_min = fields.Float(string="Min")
    result_max = fields.Float(string="Max")
    uom_id = fields.Many2one("uom.uom", string="Unit")
    test_id = fields.Many2one(
        "lims.test",
        string="Test",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        index=True,
    )
