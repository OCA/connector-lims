# Copyright 2021 - Manuel Calero <https://xtendoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProductAttribute(TransactionCase):
    def setUp(self):
        super(TestProductAttribute, self).setUp()

    def test_create_sample_product(self):
        product = self.env["product.product"].create(
            {
                "name": "Sample Product A",
                "is_product_sample": True,
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
            }
        )
        self.assertEqual(product.name, "Sample Product A")

    def test_error_create_sample_product(self):
        with self.assertRaises(ValidationError):
            self.env["product.product"].create(
                {
                    "name": "Sample Product B",
                    "is_product_sample": True,
                    "type": "service",
                    "categ_id": self.env.ref("product.product_category_all").id,
                }
            )
