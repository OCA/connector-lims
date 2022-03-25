# Copyright 2023 Dixmit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    laboratory_ok = fields.Boolean(string="Can be used on Lab")
    is_lab_template = fields.Boolean()
    laboratory_uom_id = fields.Many2one("uom.uom")
