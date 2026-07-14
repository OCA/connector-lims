# Copyright 2026 Dixmit
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.exceptions import AccessDenied
from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase


class TestLims(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analyte_01 = cls.env["lims.analyte"].create(
            {
                "name": "Analyte 01",
                "code": "AN01",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.analyte_02 = cls.env["lims.analyte"].create(
            {
                "name": "Analyte 02",
                "code": "AN02",
                "uom_id": cls.env.ref("uom.product_uom_millimeter").id,
            }
        )
        cls.sample_type = cls.env["lims.sample.type"].create(
            {
                "name": "Blood Sample",
            }
        )
        cls.analyst = new_test_user(
            cls.env,
            name="Because I am an analyst",
            login="analyst",
            password="analyst",
            email="analyst@test.com",
            groups="lims.group_lims_analyst",
            company_id=cls.env.company.id,
        )
        cls.analyst_verifier = new_test_user(
            cls.env,
            name="Because I am an analyst and a verifier",
            login="analyst_verifier",
            password="analyst_verifier",
            email="analyst_verifier@test.com",
            groups="lims.group_lims_analyst,lims.group_lims_verifier",
            company_id=cls.env.company.id,
        )
        cls.verifier = new_test_user(
            cls.env,
            name="Because I am a verifier",
            login="verifier",
            password="verifier",
            email="verifier@test.com",
            groups="lims.group_lims_verifier",
            company_id=cls.env.company.id,
        )

    def test_flow_01(self):
        """
        Lims Sample with 2 analytes
        - Create sample with 2 analyses
        - Receive sample
        - Analyze both analyses
        - Verify both analyses
        """
        sample = self.env["lims.sample"].create(
            {
                "external_identifier": "Sample 01",
                "sample_type_id": self.sample_type.id,
            }
        )
        self.assertEqual(sample.progress, 0)
        analysis_01 = self.env["lims.analysis"].create(
            {
                "sample_id": sample.id,
                "analyte_id": self.analyte_01.id,
            }
        )
        analysis_02 = self.env["lims.analysis"].create(
            {
                "sample_id": sample.id,
                "analyte_id": self.analyte_02.id,
            }
        )
        self.assertEqual(sample.progress, 0)
        self.assertEqual(analysis_01.progress, 0)
        self.assertEqual(analysis_02.progress, 0)
        self.assertEqual(analysis_01.uom_id, self.analyte_01.uom_id)
        self.assertEqual(analysis_02.uom_id, self.analyte_02.uom_id)
        self.assertEqual(analysis_01.state, "registered")
        self.assertEqual(analysis_02.state, "registered")
        self.assertEqual(sample.state, "due")
        sample.receive_sample_action()
        self.assertEqual(sample.state, "received")
        self.assertEqual(analysis_01.state, "to_analyze")
        self.assertEqual(analysis_02.state, "to_analyze")
        self.assertEqual(sample.progress, 0)
        self.assertEqual(analysis_01.progress, 0)
        self.assertEqual(analysis_02.progress, 0)
        analysis_01.with_user(self.analyst.id).analyze_action()
        self.assertEqual(analysis_01.state, "to_be_verified")
        self.assertEqual(analysis_01.analyst_id, self.analyst)
        self.assertEqual(analysis_02.state, "to_analyze")
        self.assertEqual(sample.state, "received")
        analysis_02.with_user(self.analyst.id).analyze_action()
        self.assertEqual(analysis_02.state, "to_be_verified")
        self.assertEqual(sample.state, "to_be_verified")
        self.assertEqual(sample.progress, 50)
        self.assertEqual(analysis_01.progress, 50)
        self.assertEqual(analysis_02.progress, 50)
        analysis_01.with_user(self.verifier.id).verify_action()
        self.assertEqual(analysis_01.state, "verified")
        self.assertEqual(sample.state, "to_be_verified")
        analysis_02.with_user(self.verifier.id).verify_action()
        self.assertEqual(analysis_02.state, "verified")
        self.assertEqual(sample.state, "verified")
        self.assertEqual(sample.progress, 100)
        self.assertEqual(analysis_01.progress, 100)
        self.assertEqual(analysis_02.progress, 100)

    def test_flow_02(self):
        """
        Lims Sample with 2 analytes
        - Create sample with 2 analyses
        - Receive sample
        - Analyze first analysis and verify it
        - Analyze second analysis and verify it
        """
        sample = self.env["lims.sample"].create(
            {
                "external_identifier": "Sample 01",
                "sample_type_id": self.sample_type.id,
            }
        )
        analysis_01 = self.env["lims.analysis"].create(
            {
                "sample_id": sample.id,
                "analyte_id": self.analyte_01.id,
            }
        )
        analysis_02 = self.env["lims.analysis"].create(
            {
                "sample_id": sample.id,
                "analyte_id": self.analyte_02.id,
            }
        )
        self.assertEqual(analysis_01.uom_id, self.analyte_01.uom_id)
        self.assertEqual(analysis_02.uom_id, self.analyte_02.uom_id)
        self.assertEqual(analysis_01.state, "registered")
        self.assertEqual(analysis_02.state, "registered")
        self.assertEqual(sample.state, "due")
        sample.receive_sample_action()
        self.assertEqual(sample.state, "received")
        self.assertEqual(analysis_01.state, "to_analyze")
        self.assertEqual(analysis_02.state, "to_analyze")
        self.assertEqual(sample.progress, 0)
        self.assertEqual(analysis_01.progress, 0)
        self.assertEqual(analysis_02.progress, 0)
        analysis_01.with_user(self.analyst.id).analyze_action()
        self.assertEqual(analysis_01.state, "to_be_verified")
        self.assertEqual(analysis_01.analyst_id, self.analyst)
        self.assertEqual(analysis_02.state, "to_analyze")
        self.assertEqual(sample.state, "received")
        analysis_01.with_user(self.verifier.id).verify_action()
        self.assertEqual(analysis_01.state, "verified")
        self.assertEqual(sample.state, "received")
        self.assertEqual(sample.progress, 50)
        self.assertEqual(analysis_01.progress, 100)
        self.assertEqual(analysis_02.progress, 0)
        analysis_02.with_user(self.analyst.id).analyze_action()
        self.assertEqual(analysis_02.state, "to_be_verified")
        self.assertEqual(sample.state, "to_be_verified")
        analysis_02.with_user(self.verifier.id).verify_action()
        self.assertEqual(analysis_02.state, "verified")
        self.assertEqual(sample.state, "verified")
        self.assertEqual(sample.progress, 100)
        self.assertEqual(analysis_01.progress, 100)
        self.assertEqual(analysis_02.progress, 100)

    def test_permissions(self):
        """
        Lims Sample with 1 analyte
        - Create sample with 1 analysis
        - Try to analyze and verify with a user that is analyzer and verifier
        - Analyze and verify with the correct users
        """
        sample = self.env["lims.sample"].create(
            {
                "external_identifier": "Sample 01",
                "sample_type_id": self.sample_type.id,
            }
        )
        analysis = self.env["lims.analysis"].create(
            {
                "sample_id": sample.id,
                "analyte_id": self.analyte_01.id,
            }
        )
        sample.receive_sample_action()
        with self.assertRaises(AccessDenied):
            analysis.with_user(self.verifier.id).analyze_action()
        analysis.with_user(self.analyst_verifier.id).analyze_action()
        self.assertEqual(analysis.state, "to_be_verified")
        analysis.with_user(self.analyst_verifier.id).verify_action()
        # We try to verify, but the system does nothing as the analyst can't verify it
        self.assertEqual(analysis.state, "to_be_verified")
        with self.assertRaises(AccessDenied):
            analysis.with_user(self.analyst.id).verify_action()
        # We try to retract, but the system does nothing as the analyst can't retract it
        with self.assertRaises(AccessDenied):
            analysis.with_user(self.analyst.id).retract_action()
        analysis.with_user(self.verifier.id).verify_action()
        self.assertEqual(analysis.state, "verified")

    def test_retraction(self):
        """
        Lims Sample with 1 analyte
        - Create sample with 1 analysis
        - Receive sample
        - Analyze the analysis
        - Retract the sample and check that the analysis is also retracted
        """
        sample = self.env["lims.sample"].create(
            {
                "external_identifier": "Sample 01",
                "sample_type_id": self.sample_type.id,
            }
        )
        analysis = self.env["lims.analysis"].create(
            {
                "sample_id": sample.id,
                "analyte_id": self.analyte_01.id,
            }
        )
        sample.receive_sample_action()
        analysis.with_user(self.analyst.id).analyze_action()
        self.assertEqual(analysis.state, "to_be_verified")
        self.assertEqual(sample.state, "to_be_verified")
        analysis.with_user(self.verifier.id).retract_action()
        self.assertEqual(analysis.state, "to_analyze")
