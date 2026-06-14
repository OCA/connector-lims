# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from .common import LimsAdvancedCommon


@tagged("post_install", "-at_install")
class TestLimsAnalysisAdvanced(LimsAdvancedCommon):
    def test_sync_result_creates_result_from_value(self):
        sample = self._create_sample(stage=self.stage_received)
        analysis = self._create_analysis(sample, stage=self.stage_analysis_to_analyze)
        analysis.value = "5.4"
        analysis._sync_result_from_value()
        self.assertEqual(len(analysis.result_ids), 1)
        self.assertAlmostEqual(analysis.result_ids.result_value, 5.4)

    def test_sync_result_updates_existing_result(self):
        sample = self._create_sample(stage=self.stage_received)
        analysis = self._create_analysis(sample, stage=self.stage_analysis_to_analyze)
        analysis.value = "5.4"
        analysis._sync_result_from_value()
        analysis.value = "6.0"
        analysis._sync_result_from_value()
        self.assertEqual(len(analysis.result_ids), 1)
        self.assertAlmostEqual(analysis.result_ids.result_value, 6.0)

    def test_sync_result_skipped_when_no_value(self):
        sample = self._create_sample()
        analysis = self._create_analysis(sample)
        analysis._sync_result_from_value()
        self.assertFalse(analysis.result_ids)

    def test_create_with_value_auto_syncs_result(self):
        sample = self._create_sample()
        analysis = self.env["lims.analysis"].create(
            {
                "sample_id": sample.id,
                "product_id": self.product.id,
                "name": self.product.name,
                "value": "7.2",
            }
        )
        self.assertEqual(len(analysis.result_ids), 1)

    def test_analyze_action_syncs_result(self):
        sample = self._create_sample(stage=self.stage_received)
        analysis = self._create_analysis(sample, stage=self.stage_analysis_to_analyze)
        analysis.value = "4.8"
        analysis.analyze_action()
        self.assertTrue(analysis.result_ids)
        self.assertAlmostEqual(analysis.result_ids[0].result_value, 4.8)

    def test_onchange_product_sets_test(self):
        analysis = self.env["lims.analysis"].new(
            {
                "sample_id": self._create_sample().id,
                "product_id": self.product.id,
                "name": self.product.name,
            }
        )
        analysis._onchange_product_id_lims_advanced()
        self.assertEqual(analysis.test_id, self.test)
