# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.fields import Command

from odoo.addons.lims.tests.common import LIMSCommon


class TestAccountMove(LIMSCommon):
    """Tests for LIMS order and account move integration."""

    def setUp(self):
        """Set up reusable records for all test methods."""
        super().setUp()
        self.LimsOrder = self.env["lims.order"]

        self.partner_id = self.env.ref("base.res_partner_12", raise_if_not_found=False)
        self.stage_new = self.env.ref(
            "lims.lims_stage_order_new", raise_if_not_found=False
        )
        self.service_product = self.env["product.product"].search([], limit=1)

        # Create a LIMS Order with related account move and test lines
        self.lims_order = self.LimsOrder.create(
            {
                "name": "Test Order",
                "stage_id": self.stage_new.id,
                "company_id": self.env.company.id,
                "laboratory_id": self.partner_laboratory.id,
                "team_id": self.lims_team.id,
                "partner_id": self.partner_id.id,
                "tag_ids": [(6, 0, [self.lims_tag.id])],
                "description": "Unit test for Account Move linkage",
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
                "account_move_ids": [
                    Command.create(
                        {
                            "partner_id": self.partner_id.id,
                            "move_type": "out_invoice",
                            "invoice_line_ids": [
                                Command.create(
                                    {
                                        "name": "Test Invoice Line",
                                        "quantity": 1.0,
                                        "price_unit": 1000.0,
                                    }
                                )
                            ],
                        }
                    )
                ],
            }
        )

    def test_01_compute_and_open_account_moves(self):
        """Test that LIMS order correctly computes and opens related account moves."""
        lims_order = self.lims_order
        lims_order._compute_account_move_count()
        lims_order.action_open_account_moves()

        self.assertTrue(
            lims_order.account_move_count,
            "LIMS order should have at least one linked account move.",
        )

    def test_02_compute_and_open_lims_orders_from_account_move(self):
        """Test that account moves correctly compute and open related LIMS orders."""
        account_move = self.lims_order.account_move_ids
        account_move._compute_lims_order_count()
        account_move.action_open_lims_orders()

        self.assertTrue(
            account_move.lims_order_count,
            "Account move should be linked to at least one LIMS order.",
        )
