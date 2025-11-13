# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command

from odoo.addons.lims.tests.common import LIMSCommon


class TestLIMSOrder(LIMSCommon):
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

    def test_create_lims_order(self):
        """Ensure a LIMS order is created correctly with default values."""
        order = self.lims_order

        self.assertTrue(order, "Order should be successfully created.")
        self.assertEqual(
            order.stage_id, self.stage_new, "Order should start in 'New' stage."
        )
        self.assertNotEqual(
            order.name,
            "New",
            "Order name should be auto-generated or custom, not 'New'.",
        )
        self.assertTrue(
            order.can_unlink(), "A new order should be deletable in the draft stage."
        )
        order.stage_id.team_ids = [(6, 0, [order.team_id.id])]
        stages = order.with_context(
            **{"default_team_id": order.team_id.id}
        )._read_group_stage_ids(order.stage_id, domain=[])
        self.assertIn(order.stage_id, stages)

    def test_action_complete_sets_completed_stage(self):
        """Verify that completing an order updates its stage and locks deletion."""
        order = self.lims_order
        order.action_complete()

        self.assertEqual(
            order.stage_id,
            self.stage_completed,
            "Order should move to 'Completed' stage after completion.",
        )
        self.assertFalse(
            order.can_unlink(), "Completed orders should not be deletable."
        )

        # Attempt to unlink should raise a ValidationError
        with self.assertRaises(
            ValidationError,
            msg="Deleting a completed order must raise a ValidationError.",
        ):
            order.unlink()

    def test_action_cancel_sets_cancelled_stage(self):
        """Confirm that cancelling an order changes its stage to 'Cancelled'."""
        order = self.lims_order
        order.action_cancel()

        self.assertEqual(
            order.stage_id,
            self.stage_cancelled,
            "Order should move to 'Cancelled' stage after cancellation.",
        )

    def test_write_restrict_completed_stage_directly(self):
        """Prevent direct transition to 'Completed' stage from Kanban view."""
        with self.assertRaises(
            UserError,
            msg="Direct Kanban move to completed stage should raise a UserError.",
        ):
            self.lims_order.with_context(default_stage_id=self.stage_new.id).write(
                {"stage_id": self.stage_completed.id}
            )

    def test_onchange_template_id_updates_related_fields(self):
        """Ensure that selecting a template updates operator, categories, and tests."""
        order = self.lims_order
        self.assertFalse(order.template_id, "Template should initially be empty.")

        # Apply template and trigger onchange
        order.write({"template_id": self.lims_template.id})
        order._onchange_template_id()

        # Validate updated fields
        self.assertTrue(
            order.template_id, "Template ID should be set after assignment."
        )
        self.assertTrue(
            order.category_ids, "Categories should be populated from the template."
        )
        self.assertNotEqual(
            order.operator_id,
            self.partner_operator,
            "Operator should change when applying a template.",
        )
