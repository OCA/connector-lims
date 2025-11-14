# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.fields import Command

from odoo.addons.lims.tests.common import LIMSCommon


class TestLIMSPurchaseOrder(LIMSCommon):
    def setUp(self):
        super().setUp()
        self.LimsOrder = self.env["lims.order"]

        # Sample partner for test orders
        self.partner_id = self.env.ref("base.res_partner_12", raise_if_not_found=False)
        self.stage_new = self.env.ref(
            "lims.lims_stage_order_new", raise_if_not_found=False
        )
        self.service_product = self.env["product.product"].search([], limit=1)

        # Create LIMS order
        self.lims_order = self.LimsOrder.create(
            {
                "name": "Test Order",
                "stage_id": self.stage_new.id,
                "company_id": self.env.company.id,
                "laboratory_id": self.partner_laboratory.id,
                "team_id": self.lims_team.id,
                "partner_id": self.partner_id.id,
                "tag_ids": [(6, 0, [self.lims_tag.id])],
                "description": "Test Order For UT",
                "operator_id": self.partner_operator.id,
                "physician_id": self.partner_physician.id,
                "specimen_id": self.lims_specimen.id,
                "scheduled_date": fields.Date.today(),
                "date": fields.Date.today(),
                "test_ids": [
                    Command.create(
                        {
                            "test_id": self.test_id.id,
                            "operator_id": self.partner_operator.id,
                            "scheduled_date": fields.Date.today(),
                            "date": fields.Date.today(),
                            "todo": "Test TODO",
                        }
                    )
                ],
                "purchase_order_ids": [
                    Command.create(
                        {
                            "partner_id": self.partner_id.id,
                            "order_line": [
                                Command.create(
                                    {
                                        "product_id": self.service_product.id,
                                        "product_uom_qty": 1,
                                    }
                                ),
                            ],
                        }
                    )
                ],
            }
        )

    def test_01_purchase_order_linkage(self):
        """Ensure purchase order is correctly linked to LIMS order."""
        lims_order = self.lims_order

        self.assertTrue(
            lims_order.purchase_order_ids,
            "LIMS order should have linked purchase orders.",
        )

        # Simulate UI action from purchase order to open related LIMS order
        lims_order.purchase_order_ids.action_open_linked_lims_order()

        # Compute and verify the purchase order count
        lims_order._compute_purchase_order_count()
        self.assertTrue(
            lims_order.purchase_order_count,
            "LIMS order should correctly compute the purchase_order_count field.",
        )

        # Simulate action to open purchase orders from LIMS order
        lims_order.action_view_purchase_orders()
