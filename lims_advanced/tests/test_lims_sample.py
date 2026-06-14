# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from .common import LimsAdvancedCommon


@tagged("post_install", "-at_install")
class TestLimsSampleAdvanced(LimsAdvancedCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stage_due = cls.env.ref("lims.lims_stage_sample_due")
        cls.stage_received = cls.env.ref("lims.lims_stage_sample_received")
        cls.stage_to_be_verified = cls.env.ref("lims.lims_stage_sample_to_be_verified")
        cls.stage_invalid = cls.env.ref("lims.lims_stage_sample_invalid")

    def test_next_stage_advances_to_next(self):
        sample = self._create_sample(stage=self.stage_due)
        sample.action_next_workflow_stage()
        self.assertEqual(sample.stage_id, self.stage_received)

    def test_next_stage_advances_multiple_steps(self):
        sample = self._create_sample(stage=self.stage_received)
        sample.action_next_workflow_stage()
        self.assertEqual(sample.stage_id, self.stage_to_be_verified)

    def test_next_stage_no_advance_at_last_stage(self):
        sample = self._create_sample(stage=self.stage_invalid)
        sample.action_next_workflow_stage()
        self.assertEqual(sample.stage_id, self.stage_invalid)

    def test_next_stage_no_op_without_stage(self):
        sample = self._create_sample()
        sample.stage_id = False
        sample.action_next_workflow_stage()
        self.assertFalse(sample.stage_id)

    def test_sample_team_assigned(self):
        sample = self._create_sample(team=self.team)
        self.assertEqual(sample.team_id, self.team)

    def test_sample_operator_assigned(self):
        sample = self._create_sample()
        sample.operator_id = self.operator
        self.assertEqual(sample.operator_id, self.operator)

    def test_sample_physician_assigned(self):
        sample = self._create_sample()
        sample.physician_id = self.physician
        self.assertEqual(sample.physician_id, self.physician)
