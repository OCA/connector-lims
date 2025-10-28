# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Command

from odoo.addons.lims_sale.tests.common import LIMSCommon


class TestLIMSSaleOrder(LIMSCommon):
    def setUp(self):
        super().setUp()
        # Sample partner for test orders
        self.partner_id = self.env.ref("base.res_partner_12", raise_if_not_found=False)

        # Create a test Sale Order with multiple products
        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_id.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.cbc_product.product_variant_ids.id}
                    ),
                    Command.create(
                        {"product_id": self.wbc_product.product_variant_ids.id}
                    ),
                    Command.create(
                        {"product_id": self.rbc_product.product_variant_ids.id}
                    ),
                ],
            }
        )

    def test_01_sale_order_confirmation_creates_lims_orders(self):
        """Verify that confirming a Sale Order
        automatically creates related LIMS Orders."""
        sale_order = self.sale_order

        # Initially no linked LIMS orders
        self.assertFalse(
            sale_order.lims_order_count,
            "Sale Order should not have linked LIMS Orders before confirmation.",
        )

        # Confirm sale order → should trigger LIMS Order creation
        sale_order.action_confirm()
        sale_order._compute_lims_order_count()

        self.assertTrue(
            sale_order.lims_order_count,
            "Sale Order confirmation should create related LIMS Orders.",
        )

        # Test the action returning the LIMS Orders view
        sale_order.action_view_lims_orders()

        # Validate LIMS Orders linkage
        lims_orders = self.env["lims.order"].search(
            [("sale_order_id", "=", sale_order.id)]
        )
        self.assertTrue(
            lims_orders, "LIMS Orders should exist and be linked to the Sale Order."
        )

        # Check reverse linkage from LIMS Order to Sale Order
        lims_orders[0].action_open_sale_order()

    def test_02_sale_order_with_multiple_quantities_creates_multiple_lims_orders(self):
        product_uom_qty = 5

        sale_order_multi_qty = self.env["sale.order"].create(
            {
                "partner_id": self.partner_id.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.rbc_product.product_variant_ids.id,
                            "product_uom_qty": product_uom_qty,
                        }
                    ),
                ],
            }
        )

        # Before confirmation — lims_order_count should not match qty
        self.assertNotEqual(
            sale_order_multi_qty.lims_order_count,
            product_uom_qty,
            "Before confirmation, LIMS order count should not match ordered quantity.",
        )

        # After confirmation — should create LIMS Orders equal to ordered quantity
        sale_order_multi_qty.action_confirm()
        sale_order_multi_qty._compute_lims_order_count()

        self.assertEqual(
            sale_order_multi_qty.lims_order_count,
            product_uom_qty,
            "After confirmation, LIMS Orders count should match ordered quantity.",
        )
