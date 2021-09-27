# Copyright 2021 - Manuel Calero <https://xtendoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_product_sample = fields.Boolean(
        string="Is a product sample",
        default=False,
    )

    @api.constrains("is_product_sample", "type")
    def _check_is_product_sample(self):
        if self.is_product_sample and self.type != "product":
            raise ValidationError(
                _("You can only create sample products if they are storable.")
            )
