# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestLimsPurchaseOrder(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create({"name": "LIMS Vendor"})
        cls.sample_type = cls.env["lims.sample.type"].create({"name": "Blood"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Lab Reagent",
                "type": "consu",
                "purchase_ok": True,
                "list_price": 10,
            }
        )
        cls.sample = cls.env["lims.sample"].create(
            {
                "sample_type_id": cls.sample_type.id,
                "partner_id": cls.partner.id,
            }
        )

    def _create_purchase_order(self, lims_sample=None):
        vals = {
            "partner_id": self.partner.id,
            "order_line": [
                Command.create(
                    {
                        "product_id": self.product.id,
                        "product_qty": 1,
                    }
                )
            ],
        }
        if lims_sample:
            vals["lims_sample_id"] = lims_sample.id
        return self.env["purchase.order"].create(vals)

    def test_link_purchase_order_to_sample(self):
        order = self._create_purchase_order(self.sample)
        self.assertEqual(order.lims_sample_id, self.sample)
        self.assertEqual(self.sample.purchase_order_count, 1)
        self.assertIn(order, self.sample.purchase_order_ids)

        action = self.sample.action_view_purchase_orders()
        self.assertEqual(action["res_model"], "purchase.order")
        self.assertEqual(action["res_id"], order.id)
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["context"]["default_lims_sample_id"], self.sample.id)
        self.assertEqual(action["context"]["default_partner_id"], self.partner.id)

        sample_action = order.action_open_linked_lims_sample()
        self.assertEqual(sample_action["res_id"], self.sample.id)
        self.assertEqual(sample_action["res_model"], "lims.sample")

    def test_multiple_purchase_orders_list_action(self):
        order1 = self._create_purchase_order(self.sample)
        order2 = self._create_purchase_order(self.sample)
        self.assertEqual(self.sample.purchase_order_count, 2)
        action = self.sample.action_view_purchase_orders()
        self.assertEqual(action["view_mode"], "list,form")
        self.assertEqual(action["domain"], [("lims_sample_id", "=", self.sample.id)])
        self.assertNotIn("res_id", action)
        self.assertEqual(
            set(self.sample.purchase_order_ids.ids), {order1.id, order2.id}
        )

    def test_open_sample_without_link(self):
        order = self._create_purchase_order()
        self.assertFalse(order.lims_sample_id)
        self.assertFalse(order.action_open_linked_lims_sample())

    def test_sample_without_purchase_orders_opens_create_form(self):
        self.assertEqual(self.sample.purchase_order_count, 0)
        action = self.sample.action_view_purchase_orders()
        self.assertEqual(action["view_mode"], "form")
        self.assertNotIn("res_id", action)
        self.assertEqual(action["context"]["default_lims_sample_id"], self.sample.id)
        self.assertEqual(action["context"]["default_partner_id"], self.partner.id)

    def test_prepare_context_without_partner(self):
        sample = self.env["lims.sample"].create({"sample_type_id": self.sample_type.id})
        action = sample.action_view_purchase_orders()
        self.assertEqual(action["context"]["default_lims_sample_id"], sample.id)
        self.assertNotIn("default_partner_id", action["context"])
