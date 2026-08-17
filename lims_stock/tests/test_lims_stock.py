# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestLimsStock(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create({"name": "LIMS Stock Partner"})
        cls.sample_type = cls.env["lims.sample.type"].create({"name": "Blood"})
        cls.product_tmpl = cls.env["product.template"].create(
            {
                "name": "Test Specimen Product",
                "type": "consu",
            }
        )
        cls.product = cls.product_tmpl.product_variant_ids[:1]
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

    def _create_sample(self, **extra):
        vals = {
            "sample_type_id": self.sample_type.id,
            "partner_id": self.partner.id,
        }
        vals.update(extra)
        return self.env["lims.sample"].create(vals)

    def test_is_specimen_sets_serial_tracking_on_create(self):
        tmpl = self.env["product.template"].create(
            {
                "name": "Created Specimen",
                "type": "consu",
                "is_specimen": True,
            }
        )
        self.assertTrue(tmpl.is_storable)
        self.assertEqual(tmpl.tracking, "serial")

    def test_is_specimen_sets_serial_tracking_on_write(self):
        self.assertNotEqual(self.product_tmpl.tracking, "serial")
        self.product_tmpl.write({"is_specimen": True})
        self.assertTrue(self.product_tmpl.is_storable)
        self.assertEqual(self.product_tmpl.tracking, "serial")

    def test_assign_product_and_lot(self):
        lot = self.env["stock.lot"].create(
            {
                "name": "LOT-ASSIGN",
                "product_id": self.product.id,
                "company_id": self.env.company.id,
            }
        )
        sample = self._create_sample(product_id=self.product.id, lot_id=lot.id)
        self.assertEqual(sample.product_id, self.product)
        self.assertEqual(sample.lot_id, lot)

    def test_auto_create_lot_for_specimen_product(self):
        self.product_tmpl.write({"is_specimen": True})
        sample = self._create_sample(product_id=self.product.id)
        self.assertTrue(sample.lot_id)
        self.assertEqual(sample.lot_id.product_id, self.product)
        self.assertEqual(sample.lot_id.name, sample.identifier)

    def test_auto_create_lot_for_serial_tracked_product(self):
        self.product_tmpl.write({"tracking": "serial", "is_storable": True})
        sample = self._create_sample(product_id=self.product.id)
        self.assertTrue(sample.lot_id)
        self.assertEqual(sample.lot_id.product_id, self.product)

    def test_lot_product_mismatch_raises(self):
        other = self.env["product.product"].create(
            {
                "name": "Other Product",
                "type": "consu",
                "is_storable": True,
                "tracking": "serial",
            }
        )
        lot = self.env["stock.lot"].create(
            {
                "name": "LOT-OTHER",
                "product_id": other.id,
                "company_id": self.env.company.id,
            }
        )
        with self.assertRaises(ValidationError):
            self._create_sample(product_id=self.product.id, lot_id=lot.id)

    def test_location_from_quant(self):
        self.product_tmpl.write({"is_specimen": True})
        sample = self._create_sample(product_id=self.product.id)
        self.assertFalse(sample.location_id)
        self.env["stock.quant"]._update_available_quantity(
            self.product,
            self.stock_location,
            1,
            lot_id=sample.lot_id,
        )
        sample.invalidate_recordset(["location_id"])
        self.assertEqual(sample.location_id, self.stock_location)

    def test_action_open_lot(self):
        self.product_tmpl.write({"is_specimen": True})
        sample = self._create_sample(product_id=self.product.id)
        action = sample.action_open_lot()
        self.assertEqual(action["res_model"], "stock.lot")
        self.assertEqual(action["res_id"], sample.lot_id.id)

    def test_action_open_lot_without_lot(self):
        sample = self._create_sample()
        self.assertFalse(sample.action_open_lot())

    def test_write_product_triggers_lot_ensure(self):
        sample = self._create_sample()
        self.assertFalse(sample.lot_id)
        self.product_tmpl.write({"is_specimen": True})
        sample.write({"product_id": self.product.id})
        self.assertTrue(sample.lot_id)

    def test_sample_without_product_skips_lot(self):
        sample = self._create_sample()
        self.assertFalse(sample.product_id)
        self.assertFalse(sample.lot_id)
        self.assertFalse(sample.location_id)

    def test_write_non_stock_fields_keeps_lot(self):
        sample = self._create_sample()
        sample.write({"external_identifier": "EXT-1"})
        self.assertEqual(sample.external_identifier, "EXT-1")
        self.assertFalse(sample.lot_id)

    def test_location_empty_with_lot_but_no_quant(self):
        self.product_tmpl.write({"is_specimen": True})
        sample = self._create_sample(product_id=self.product.id)
        self.assertTrue(sample.lot_id)
        self.assertFalse(sample.location_id)

    def test_move_line_count_without_lot(self):
        sample = self._create_sample()
        self.assertEqual(sample.move_line_count, 0)
        self.assertFalse(sample.action_view_stock_moves())

    def test_action_view_stock_moves(self):
        self.product_tmpl.write({"is_specimen": True})
        sample = self._create_sample(product_id=self.product.id)
        self.assertEqual(sample.move_line_count, 0)
        supplier = self.env.ref("stock.stock_location_suppliers")
        self.env["stock.move.line"].create(
            {
                "product_id": self.product.id,
                "lot_id": sample.lot_id.id,
                "location_id": supplier.id,
                "location_dest_id": self.stock_location.id,
                "quantity": 1,
                "company_id": self.env.company.id,
            }
        )
        sample.invalidate_recordset(["move_line_count"])
        self.assertEqual(sample.move_line_count, 1)
        action = sample.action_view_stock_moves()
        self.assertEqual(action["res_model"], "stock.move.line")
        self.assertEqual(action["domain"], [("lot_id", "=", sample.lot_id.id)])
        self.assertEqual(action["view_mode"], "list,form")
