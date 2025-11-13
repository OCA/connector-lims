# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.fields import Command

from odoo.addons.lims.tests.common import LIMSCommon


class TestLIMSBatch(LIMSCommon):
    def setUp(self):
        super().setUp()
        self.LimsOrder = self.env["lims.order"]
        self.LimsBatch = self.env["lims.batch"]
        # Reference order stages
        self.stage_new = self.env.ref(
            "lims.lims_stage_order_new", raise_if_not_found=False
        )
        self.stage_completed = self.env.ref(
            "lims.lims_stage_batch_completed", raise_if_not_found=False
        )
        self.stage_cancelled = self.env.ref(
            "lims.lims_stage_batch_cancelled", raise_if_not_found=False
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
        # Create LIMS batch
        self.lims_batch = self.LimsBatch.create(
            {
                "laboratory_id": self.partner_laboratory.id,
                "description": "Test Order For UT",
                "operator_id": self.partner_operator.id,
                "team_id": self.lims_team.id,
                "test_id": self.test_id.id,
                "scheduled_date": fields.Date.today() + timedelta(days=5),
                "test_ids": [(6, 0, self.lims_order.test_ids.ids)],
            }
        )

    def test_create_and_read_group_stage_ids(self):
        """Test batch creation and _read_group_stage_ids filtering by team."""
        batch = self.lims_batch
        batch.stage_id.team_ids = [(6, 0, [batch.team_id.id])]

        stages = batch.with_context(
            default_team_id=batch.team_id.id
        )._read_group_stage_ids(batch.stage_id, domain=[])

        self.assertIn(batch.stage_id, stages)
        self.assertNotEqual(batch.name, "New")
        self.assertTrue(batch.can_unlink())

    def test_action_complete_changes_to_completed_stage(self):
        """Test batch completion moves it to completed stage."""
        batch = self.lims_batch

        # Batch cannot complete if tests are not completed
        with self.assertRaises(ValidationError):
            batch.action_complete()
        self.assertNotEqual(batch.stage_id, self.stage_completed)

        # Complete linked tests, then complete batch
        batch.test_ids.action_complete()
        batch.action_complete()

        self.assertEqual(batch.stage_id, self.stage_completed)
        self.assertFalse(batch.can_unlink())

        with self.assertRaises(ValidationError):
            batch.unlink()

    def test_action_cancel_changes_to_cancelled_stage(self):
        """Test cancelling batch moves it to cancelled stage."""
        batch = self.lims_batch
        batch.action_cancel()
        self.assertEqual(batch.stage_id, self.stage_cancelled)

    def test_onchange_test_ids_populates_fields(self):
        """Test onchange_test_ids executes without errors."""
        batch = self.lims_batch
        batch._onchange_test_ids()
