# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import LimsAdvancedCommon


@tagged("post_install", "-at_install")
class TestLimsBatch(LimsAdvancedCommon):
    def _create_batch(self, **kwargs):
        vals = {"laboratory_id": self.laboratory.id, **kwargs}
        return self.env["lims.batch"].create(vals)

    def test_batch_links_analysis(self):
        sample = self.env["lims.sample"].create(
            {
                "sample_type_id": self.sample_type.id,
                "customer_id": self.partner.id,
                "analysis_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "test_id": self.test.id,
                        },
                    )
                ],
            }
        )
        analysis = sample.analysis_ids
        batch = self._create_batch(test_id=self.test.id)
        analysis.batch_id = batch.id
        self.assertIn(analysis, batch.analysis_ids)

    def test_batch_complete_raises_if_analyses_pending(self):
        sample = self._create_sample()
        analysis = self._create_analysis(sample, stage=self.stage_analysis_to_analyze)
        batch = self._create_batch(test_id=self.test.id)
        analysis.batch_id = batch.id
        with self.assertRaises(ValidationError):
            batch.action_complete()

    def test_batch_complete_succeeds_when_all_closed(self):
        sample = self._create_sample()
        analysis = self._create_analysis(sample, stage=self.stage_analysis_verified)
        batch = self._create_batch(test_id=self.test.id)
        analysis.batch_id = batch.id
        batch.action_complete()
        self.assertEqual(batch.stage_id, self.stage_batch_completed)

    def test_batch_complete_succeeds_with_no_analyses(self):
        batch = self._create_batch()
        batch.action_complete()
        self.assertEqual(batch.stage_id, self.stage_batch_completed)

    def test_batch_cancel_moves_to_cancelled_stage(self):
        batch = self._create_batch()
        batch.action_cancel()
        self.assertEqual(batch.stage_id, self.stage_batch_cancelled)

    def test_batch_cannot_unlink_when_not_in_default_stage(self):
        batch = self._create_batch()
        batch.stage_id = self.stage_batch_completed
        with self.assertRaises(ValidationError):
            batch.unlink()

    def test_batch_can_unlink_in_default_stage(self):
        batch = self._create_batch()
        self.assertTrue(batch.can_unlink())
        batch.unlink()
        self.assertFalse(batch.exists())
