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
        samples = order.lims_sample_ids
        # 1 (order) + 1 (line) + 3 (quantity)
        self.assertEqual(len(samples), 5)
        self.assertEqual(order.lims_sample_count, 5)
        self.assertTrue(all(s.partner_id == self.partner for s in samples))
        self.assertTrue(all(s.sample_type_id == self.sample_type for s in samples))
        self.assertTrue(all(order in s.sale_order_ids for s in samples))

        line_sample = samples.filtered(lambda s: len(s.analysis_ids) == 2)
        self.assertEqual(len(line_sample), 1)
        self.assertEqual(
            line_sample.analysis_ids.analyte_id,
            self.analyte | self.analyte_2,
        )
        self.assertEqual(
            line_sample.analysis_ids.sale_order_line_id,
            order.order_line.filtered(
                lambda line: line.product_id == self.product_line
            ),
        )

        action = order.action_view_lims_samples()
        self.assertEqual(action["res_model"], "lims.sample")
        self.assertEqual(action["domain"], [("sale_order_ids", "in", order.ids)])

        sample_action = samples[0].action_open_sale_orders()
        self.assertEqual(sample_action["res_id"], order.id)

    def test_order_tracking_merges_analytes_from_sibling_lines(self):
        order = self._create_sale_order(
            [
                (self.product_order, 1, self.analyte),
                (self.product_order, 1, self.analyte | self.analyte_2),
            ]
        )
        order.action_confirm()
        samples = order.lims_sample_ids
        self.assertEqual(len(samples), 1)
        self.assertEqual(
            samples.analysis_ids.analyte_id,
            self.analyte | self.analyte_2,
        )
        # Duplicate analyte on second line is skipped; pH keeps the first line.
        ph_analysis = samples.analysis_ids.filtered(
            lambda a: a.analyte_id == self.analyte
        )
        glu_analysis = samples.analysis_ids.filtered(
            lambda a: a.analyte_id == self.analyte_2
        )
        self.assertEqual(len(ph_analysis), 1)
        self.assertEqual(ph_analysis.sale_order_line_id, order.order_line[0])
        self.assertEqual(glu_analysis.sale_order_line_id, order.order_line[1])

    def test_line_tracking_creates_sample_with_multiple_analytes(self):
        order = self._create_sale_order(
            [(self.product_line, 1, self.analyte | self.analyte_2)]
        )
        order.action_confirm()
        sample = order.lims_sample_ids
        self.assertEqual(len(sample), 1)
        self.assertEqual(sample.sale_origin, order.name)
        self.assertEqual(len(sample.analysis_ids), 2)
        self.assertEqual(sample.analysis_ids.analyte_id, self.analyte | self.analyte_2)
        self.assertEqual(sample.analysis_ids.sale_order_line_id, order.order_line)

    def test_quantity_tracking_sets_origin_suffix(self):
        order = self._create_sale_order([(self.product_qty, 2, self.analyte)])
        order.action_confirm()
        samples = order.lims_sample_ids.sorted("id")
        self.assertEqual(len(samples), 2)
        self.assertEqual(
            samples.mapped("sale_origin"),
            [f"{order.name}-1", f"{order.name}-2"],
        )

    def test_quantity_zero_creates_no_sample(self):
        order = self._create_sale_order([(self.product_qty, 0, self.analyte)])
        order.action_confirm()
        self.assertFalse(order.lims_sample_ids)

    def test_line_without_analytes_creates_no_sample(self):
        order = self._create_sale_order(
            [(self.product_line, 1, self.env["lims.analyte"])]
        )
        order.action_confirm()
        self.assertFalse(order.lims_sample_ids)

    def test_onchange_product_sets_default_analytes(self):
        line = self.env["sale.order.line"].new({"product_id": self.product_line.id})
        line._onchange_product_id_lims_analytes()
        self.assertEqual(
            set(line.lims_analyte_ids.ids),
            set((self.analyte | self.analyte_2).ids),
        )

        line.product_id = self.product_no
        line._onchange_product_id_lims_analytes()
        self.assertFalse(line.lims_analyte_ids.ids)

    def test_prepare_vals_and_skip_unconfigured(self):
        product = self.product_order.product_tmpl_id
        order = self._create_sale_order([(self.product_order, 1, self.analyte)])
        commands = order.order_line._prepare_lims_analysis_commands()
        vals = product._prepare_lims_sample_vals(order, analysis_commands=commands)
        self.assertEqual(vals["sale_order_ids"], [Command.set(order.ids)])
        self.assertEqual(len(vals["analysis_ids"]), 1)

        bare = self.env["product.template"].create(
            {
                "name": "No type",
                "type": "service",
                "lims_tracking": "line",
            }
        )
        self.assertFalse(bare._create_lims_sample(order, commands))

    def test_open_sale_orders_without_link(self):
        sample = self.env["lims.sample"].create(
            {
                "sample_type_id": self.sample_type.id,
                "partner_id": self.partner.id,
            }
        )
        self.assertFalse(sample.action_open_sale_orders())

    def test_open_sale_orders_multiple(self):
        order1 = self._create_sale_order([(self.product_line, 1, self.analyte)])
        order2 = self._create_sale_order([(self.product_line, 1, self.analyte)])
        order1.action_confirm()
        order2.action_confirm()
        sample = order1.lims_sample_ids
        sample.sale_order_ids = order1 | order2
        action = sample.action_open_sale_orders()
        self.assertEqual(action["view_mode"], "list,form")
        self.assertEqual(action["domain"], [("id", "in", (order1 | order2).ids)])
