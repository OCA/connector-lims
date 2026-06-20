# Copyright (C) 2025 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import tagged

from .common import LimsCommon


@tagged("post_install", "-at_install")
class TestLimsSample(LimsCommon):
    def test_default_stage_is_registered(self):
        sample = self._create_sample()
        self.assertEqual(sample.stage_id, self.stage_registered)

    def test_receive_advances_to_received(self):
        sample = self._create_sample()
        self._create_analysis(sample)
        sample.receive_sample_action()
        self.assertEqual(sample.stage_id, self.stage_received)

    def test_receive_sets_received_date(self):
        sample = self._create_sample()
        self.assertFalse(sample.received_date)
        sample.receive_sample_action()
        self.assertTrue(sample.received_date)

    def test_receive_moves_analyses_to_to_analyze(self):
        sample = self._create_sample()
        analysis = self._create_analysis(sample)
        self.assertEqual(analysis.stage_id, self.stage_analysis_registered)
        sample.receive_sample_action()
        self.assertEqual(analysis.stage_id, self.stage_analysis_to_analyze)

    def test_receive_does_not_reprocess_already_received(self):
        sample = self._create_sample()
        sample.receive_sample_action()
        self.assertEqual(sample.stage_id, self.stage_received)
        sample.receive_sample_action()
        self.assertEqual(sample.stage_id, self.stage_received)

    def test_analyze_auto_advances_sample_to_to_be_verified(self):
        sample = self._create_sample(stage=self.stage_received)
        analysis = self._create_analysis(sample, stage=self.stage_analysis_to_analyze)
        analysis.analyze_action()
        self.assertEqual(sample.stage_id, self.stage_to_be_verified)

    def test_verify_auto_advances_sample_to_verified(self):
        sample = self._create_sample(stage=self.stage_to_be_verified)
        analysis = self._create_analysis(
            sample, stage=self.stage_analysis_to_be_verified
        )
        analysis.write({"analyst_id": False})
        analysis.verify_action()
        self.assertEqual(sample.stage_id, self.stage_verified)

    def test_check_to_verify_blocked_when_analyses_pending(self):
        sample = self._create_sample(stage=self.stage_received)
        self._create_analysis(sample, stage=self.stage_analysis_to_analyze)
        self._create_analysis(sample, stage=self.stage_analysis_to_be_verified)
        sample.check_to_verify()
        self.assertEqual(sample.stage_id, self.stage_received)

    def test_check_verify_blocked_when_analyses_pending(self):
        sample = self._create_sample(stage=self.stage_to_be_verified)
        self._create_analysis(sample, stage=self.stage_analysis_to_be_verified)
        sample.check_verify()
        self.assertEqual(sample.stage_id, self.stage_to_be_verified)

    def test_is_closed_related_field(self):
        stage_published = self.env.ref("lims.lims_stage_sample_published")
        sample = self._create_sample(stage=stage_published)
        self.assertTrue(sample.is_closed)
        sample2 = self._create_sample(stage=self.stage_received)
        self.assertFalse(sample2.is_closed)

    def test_next_stage_sets_received_date(self):
        sample = self._create_sample(stage=self.stage_due)
        self.assertFalse(sample.received_date)
        sample.action_next_workflow_stage()
        self.assertEqual(sample.stage_id, self.stage_received)
        self.assertTrue(sample.received_date)

    def test_next_stage_advances_to_next(self):
        sample = self._create_sample(stage=self.stage_due)
        sample.action_next_workflow_stage()
        self.assertEqual(sample.stage_id, self.stage_received)

    def test_next_stage_advances_multiple_steps(self):
        sample = self._create_sample(stage=self.stage_received)
        sample.action_next_workflow_stage()
        self.assertEqual(sample.stage_id, self.stage_to_be_verified)

    def test_next_stage_no_advance_at_closed_stage(self):
        sample = self._create_sample(stage=self.stage_invalid)
        sample.action_next_workflow_stage()
        self.assertEqual(sample.stage_id, self.stage_invalid)

    def test_next_stage_no_op_without_stage(self):
        sample = self._create_sample()
        sample.stage_id = False
        sample.action_next_workflow_stage()
        self.assertFalse(sample.stage_id)
