# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.fields import Command

from odoo.addons.lims.tests.common import LIMSCommon


class TestLIMSOrderTest(LIMSCommon):
    def setUp(self):
        super().setUp()
        self.LimsOrder = self.env["lims.order"]
        # Reference order stages
        self.stage_new = self.env.ref(
            "lims.lims_stage_order_new", raise_if_not_found=False
        )
        self.stage_completed = self.env.ref(
            "lims.lims_stage_order_completed", raise_if_not_found=False
        )
        self.stage_cancelled = self.env.ref(
            "lims.lims_stage_order_cancelled", raise_if_not_found=False
        )
        # Sample partner for test orders
        self.partner_id = self.env.ref("base.res_partner_12", raise_if_not_found=False)

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
                "scheduled_date": fields.Date.today() + timedelta(days=5),
                "date": fields.Date.today(),
                "test_ids": [
                    Command.create(
                        {
                            "test_id": self.test_id.id,
                            "operator_id": self.partner_operator.id,
                            "scheduled_date": fields.Date.today() + timedelta(days=5),
                            "date": fields.Date.today(),
                            "todo": "Test TODO",
                        }
                    )
                ],
            }
        )

    def test_create_and_read_group_stage_ids(self):
        """Test creation and _read_group_stage_ids filtering by team."""
        order_test = self.lims_order.test_ids

        # Assign stage team for filtering
        order_test.stage_id.team_ids = [(6, 0, [order_test.team_id.id])]

        # Apply context and test filtering
        stages = order_test.with_context(
            default_team_id=order_test.team_id.id
        )._read_group_stage_ids(order_test.stage_id, domain=[])

        self.assertIn(order_test.stage_id, stages)
        self.assertNotEqual(order_test.name, "New")
        self.assertTrue(order_test.can_unlink())

        order_test.team_id._compute_order_count()
        order_test.team_id._compute_order_need_assign_count()
        order_test.team_id._compute_order_need_schedule_count()

    def test_action_complete_changes_to_completed_stage(self):
        """Test completing order test moves it to completed stage."""
        order_test = self.lims_order.test_ids
        order_test.action_complete()

        self.assertEqual(order_test.stage_id, self.stage_completed)
        self.assertFalse(order_test.can_unlink())

        with self.assertRaises(ValidationError):
            order_test.unlink()

    def test_action_cancel_changes_to_cancelled_stage(self):
        """Test cancelling order test moves it to cancelled stage."""
        order_test = self.lims_order.test_ids
        order_test.action_cancel()
        self.assertEqual(order_test.stage_id, self.stage_cancelled)
