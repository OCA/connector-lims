# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.lims.tests.common import LIMSCommon


class LIMSCommon(LIMSCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cbc_product, cls.wbc_product, cls.rbc_product = cls.env[
            "product.template"
        ].create(
            [
                {
                    "name": "Complete Blood Count (CBC)",
                    "type": "service",
                    "lims_tracking": "order",
                    "list_price": 100,
                    "lims_template_id": cls.lims_template.id,
                },
                {
                    "name": "White blood cells (WBC)",
                    "type": "service",
                    "lims_tracking": "line",
                    "list_price": 50,
                    "lims_template_id": cls.lims_template.id,
                },
                {
                    "name": "Red blood cells (RBC)",
                    "type": "service",
                    "lims_tracking": "quantity",
                    "list_price": 50,
                    "lims_template_id": cls.lims_template.id,
                },
            ]
        )
