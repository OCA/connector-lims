# Copyright 2023 Dixmit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class LimsSampleType(models.Model):
    _name = "lims.sample.type"
    _description = "Sample Type"

    name = fields.Char(required=True)
    description = fields.Text()
    hazardous = fields.Boolean()
    active = fields.Boolean(default=True)
