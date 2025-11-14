# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.lims.tests.common import LIMSCommon


class TestLimsSpecimen(LIMSCommon):
    def setUp(self):
        super().setUp()
        self.LimsSpecimen = self.env["lims.specimen"]
        self.ProductTemplate = self.env["product.template"]
        self.StockLot = self.env["stock.lot"]

        self.stock_location = self.env.ref(
            "stock.stock_location_stock", raise_if_not_found=False
        )

        # Create a specimen product
        self.specimen_product = self.ProductTemplate.create(
            {
                "name": "Test Specimen Product",
                "type": "consu",
            }
        )
        self.product_variant = self.specimen_product.product_variant_ids

        # Create an initial LIMS Specimen
        self.lims_specimen = self.LimsSpecimen.create(
            {
                "name": "Test/Blood/007",
                "partner_id": self.partner_specimen.id,
                "collection_date": fields.Date.today(),
            }
        )

        # Create a lot for testing
        self.lot_final = self.StockLot.create(
            {
                "name": "lot_final",
                "product_id": self.product_variant.id,
            }
        )

    def test_01_specimen_product_tracking(self):
        """Ensure that setting is_specimen updates product tracking to 'serial'."""
        self.assertEqual(
            self.product_variant.tracking, "none", "Default tracking must be 'none'."
        )
        self.specimen_product.write({"is_specimen": True})
        self.assertEqual(
            self.product_variant.tracking,
            "serial",
            "Product tracking should update to 'serial' when marked as specimen.",
        )

    def test_02_assign_product_and_lot_to_specimen(self):
        """Check that LIMS Specimen can be linked with product and lot."""
        self.lims_specimen.write(
            {
                "product_id": self.product_variant.id,
                "lot_id": self.lot_final.id,
            }
        )
        self.assertEqual(self.lims_specimen.product_id, self.product_variant)
        self.assertEqual(self.lims_specimen.lot_id, self.lot_final)

    def test_03_auto_create_lot_for_specimen(self):
        """Verify that lot is automatically created when
        specimen product is a specimen."""
        self.specimen_product.write({"is_specimen": True})
        lims_specimen = self.LimsSpecimen.create(
            {
                "name": "Test/Blood/008",
                "partner_id": self.partner_specimen.id,
                "collection_date": fields.Date.today(),
                "product_id": self.product_variant.id,
            }
        )
        self.assertTrue(
            lims_specimen.lot_id,
            "A lot record should be automatically created for specimen products.",
        )
        lims_specimen.action_open_lot()
        lims_specimen._compute_location_id()
