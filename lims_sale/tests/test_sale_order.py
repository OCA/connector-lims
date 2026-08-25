# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestLimsSaleOrder(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create({"name": "LIMS Customer"})
        cls.sample_type = cls.env["lims.sample.type"].create({"name": "Blood"})
        cls.analyte = cls.env["lims.analyte"].create(
            {
                "name": "pH",
                "code": "pH",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.analyte_2 = cls.env["lims.analyte"].create(
            {
                "name": "Glucose",
                "code": "GLU",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.product_order = cls.env["product.product"].create(
            {
                "name": "CBC Panel (per order)",
                "type": "service",
                "list_price": 100,
                "lims_tracking": "order",
                "lims_sample_type_id": cls.sample_type.id,
                "lims_analyte_ids": [Command.set(cls.analyte.ids)],
            }
        )
        cls.product_line = cls.env["product.product"].create(
            {
                "name": "WBC Panel (per line)",
                "type": "service",
                "list_price": 50,
                "lims_tracking": "line",
                "lims_sample_type_id": cls.sample_type.id,
                "lims_analyte_ids": [Command.set((cls.analyte | cls.analyte_2).ids)],
            }
        )
        cls.product_qty = cls.env["product.product"].create(
            {
                "name": "RBC Panel (per qty)",
                "type": "service",
                "list_price": 50,
                "lims_tracking": "quantity",
                "lims_sample_type_id": cls.sample_type.id,
                "lims_analyte_ids": [Command.set(cls.analyte.ids)],
            }
        )
        cls.product_no = cls.env["product.product"].create(
            {
                "name": "Non-LIMS Service",
                "type": "service",
                "list_price": 10,
                "lims_tracking": "no",
            }
        )

    def _create_sale_order(self, lines):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": qty,
                            "lims_analyte_ids": [Command.set(analytes.ids)]
                            if analytes
                            else [Command.clear()],
                        }
                    )
                    for product, qty, analytes in lines
                ],
            }
        )

    def test_confirm_creates_samples_for_mixed_tracking(self):
        order = self._create_sale_order(
            [
                (self.product_order, 1, self.analyte),
                (self.product_line, 1, self.analyte | self.analyte_2),
                (self.product_qty, 3, self.analyte),
                (self.product_no, 1, self.env["lims.analyte"]),
            ]
        )
        self.assertEqual(order.lims_sample_count, 0)
        order.action_confirm()
        samples = self.env["lims.sample"].search([("sale_order_id", "=", order.id)])
        # 1 (order) + 1 (line) + 3 (quantity)
        self.assertEqual(len(samples), 5)
        self.assertEqual(order.lims_sample_count, 5)
        self.assertTrue(all(s.partner_id == self.partner for s in samples))
        self.assertTrue(all(s.sample_type_id == self.sample_type for s in samples))

        # The "line" sample has 2 analytes; all others have only pH.
        line_sample = samples.filtered(lambda s: len(s.analysis_ids) == 2)
        self.assertEqual(len(line_sample), 1)
        self.assertEqual(
            line_sample.analysis_ids.analyte_id,
            self.analyte | self.analyte_2,
        )

        other_samples = samples - line_sample
        self.assertEqual(len(other_samples), 4)
        self.assertEqual(other_samples.analysis_ids.analyte_id, self.analyte)

        action = order.action_view_lims_samples()
        self.assertEqual(action["res_model"], "lims.sample")
        self.assertEqual(action["domain"], [("sale_order_id", "=", order.id)])

        sample_action = samples[0].action_open_sale_order()
        self.assertEqual(sample_action["res_id"], order.id)

    def test_order_tracking_creates_single_sample_per_product(self):
        order = self._create_sale_order(
            [
                (self.product_order, 1, self.analyte),
                (self.product_order, 1, self.analyte),
            ]
        )
        order.action_confirm()
        samples = self.env["lims.sample"].search([("sale_order_id", "=", order.id)])
        self.assertEqual(len(samples), 1)

    def test_line_tracking_creates_sample_with_multiple_analytes(self):
        order = self._create_sale_order(
            [(self.product_line, 1, self.analyte | self.analyte_2)]
        )
        order.action_confirm()
        sample = self.env["lims.sample"].search([("sale_order_id", "=", order.id)])
        self.assertEqual(len(sample), 1)
        self.assertEqual(sample.sale_origin, order.name)
        self.assertEqual(len(sample.analysis_ids), 2)
        self.assertEqual(sample.analysis_ids.analyte_id, self.analyte | self.analyte_2)

    def test_quantity_tracking_sets_origin_suffix(self):
        order = self._create_sale_order([(self.product_qty, 2, self.analyte)])
        order.action_confirm()
        samples = self.env["lims.sample"].search(
            [("sale_order_id", "=", order.id)], order="id"
        )
        self.assertEqual(len(samples), 2)
        self.assertEqual(
            samples.mapped("sale_origin"),
            [f"{order.name}-1", f"{order.name}-2"],
        )

    def test_quantity_zero_creates_no_sample(self):
        order = self._create_sale_order([(self.product_qty, 0, self.analyte)])
        order.action_confirm()
        samples = self.env["lims.sample"].search([("sale_order_id", "=", order.id)])
        self.assertFalse(samples)

    def test_line_without_analytes_creates_no_sample(self):
        order = self._create_sale_order(
            [(self.product_line, 1, self.env["lims.analyte"])]
        )
        order.action_confirm()
        samples = self.env["lims.sample"].search([("sale_order_id", "=", order.id)])
        self.assertFalse(samples)

    def test_prepare_vals_and_skip_unconfigured(self):
        product = self.product_order.product_tmpl_id
        order = self._create_sale_order([(self.product_order, 1, self.analyte)])
        vals = product._prepare_lims_sample_vals(order, analytes=self.analyte)
        self.assertEqual(vals["sale_order_id"], order.id)
        self.assertEqual(len(vals["analysis_ids"]), 1)

        bare = self.env["product.template"].create(
            {
                "name": "No type",
                "type": "service",
                "lims_tracking": "line",
            }
        )
        self.assertFalse(bare._create_lims_sample(order, self.analyte))

    def test_open_sale_order_without_link(self):
        sample = self.env["lims.sample"].create(
            {
                "sample_type_id": self.sample_type.id,
                "partner_id": self.partner.id,
            }
        )
        self.assertFalse(sample.action_open_sale_order())
