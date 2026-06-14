# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from .common import LimsAdvancedCommon


@tagged("post_install", "-at_install")
class TestLimsResult(LimsAdvancedCommon):
    def _create_result(self, analysis, **kwargs):
        return self.env["lims.result"].create({"analysis_id": analysis.id, **kwargs})

    def test_result_name_auto_generated_from_sequence(self):
        sample = self._create_sample()
        analysis = self._create_analysis(sample)
        result = self._create_result(analysis)
        self.assertNotEqual(result.name, "New")
        self.assertTrue(result.name)

    def test_result_partner_computed_from_sample_customer(self):
        sample = self._create_sample()
        analysis = self._create_analysis(sample)
        result = self._create_result(analysis)
        self.assertEqual(result.partner_id, self.partner)

    def test_result_partner_false_when_no_sample(self):
        sample = self._create_sample()
        analysis = self._create_analysis(sample)
        result = self._create_result(analysis)
        analysis.sample_id = False
        result.invalidate_recordset(["partner_id"])
        self.assertFalse(result.partner_id)

    def test_result_team_computed_from_sample(self):
        sample = self._create_sample(team=self.team)
        analysis = self._create_analysis(sample)
        result = self._create_result(analysis)
        self.assertEqual(result.team_id, self.team)

    def test_result_range_from_test_result_definition(self):
        test = self.env["lims.test"].create(
            {
                "name": "Glucose Range",
                "product_tmpl_id": self.product.product_tmpl_id.id,
            }
        )
        test_result_def = self.env["lims.test.result"].create(
            {
                "name": "Adult",
                "test_id": test.id,
                "result_min": 3.9,
                "result_max": 6.1,
            }
        )
        sample = self._create_sample()
        analysis = self._create_analysis(sample)
        analysis.test_id = test
        result = self._create_result(analysis, test_result_id=test_result_def.id)
        self.assertAlmostEqual(result.result_min, 3.9)
        self.assertAlmostEqual(result.result_max, 6.1)

    def test_result_range_from_product_when_no_test_result(self):
        product = self.env["product.product"].create(
            {
                "name": "Hemoglobin",
                "laboratory_ok": True,
                "type": "service",
                "normal_range_min": 120.0,
                "normal_range_max": 160.0,
            }
        )
        sample = self._create_sample()
        analysis = self.env["lims.analysis"].create(
            {
                "sample_id": sample.id,
                "product_id": product.id,
                "name": product.name,
            }
        )
        result = self._create_result(analysis)
        self.assertAlmostEqual(result.result_min, 120.0)
        self.assertAlmostEqual(result.result_max, 160.0)

    def test_result_default_stage_assigned(self):
        sample = self._create_sample()
        analysis = self._create_analysis(sample)
        result = self._create_result(analysis)
        self.assertTrue(result.stage_id)
        self.assertEqual(result.stage_id.stage_type, "result")
