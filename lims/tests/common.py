# Copyright (C) 2025 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase


class LimsCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Patient A"})
        cls.sample_type = cls.env["lims.sample.type"].create({"name": "Blood"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Glucose",
                "laboratory_ok": True,
                "type": "service",
            }
        )
        # Sample stages
        cls.stage_registered = cls.env.ref("lims.lims_stage_sample_registered")
        cls.stage_due = cls.env.ref("lims.lims_stage_sample_due")
        cls.stage_received = cls.env.ref("lims.lims_stage_sample_received")
        cls.stage_to_be_verified = cls.env.ref("lims.lims_stage_sample_to_be_verified")
        cls.stage_verified = cls.env.ref("lims.lims_stage_sample_verified")
        cls.stage_invalid = cls.env.ref("lims.lims_stage_sample_invalid")
        # Analysis stages
        cls.stage_analysis_registered = cls.env.ref(
            "lims.lims_stage_analysis_registered"
        )
        cls.stage_analysis_to_analyze = cls.env.ref(
            "lims.lims_stage_analysis_to_analyze"
        )
        cls.stage_analysis_to_be_verified = cls.env.ref(
            "lims.lims_stage_analysis_to_be_verified"
        )
        cls.stage_analysis_verified = cls.env.ref("lims.lims_stage_analysis_verified")
        cls.stage_analysis_rejected = cls.env.ref("lims.lims_stage_analysis_rejected")

        cls.analyst_group = cls.env.ref("lims.group_lims_analyst")
        cls.verifier_group = cls.env.ref("lims.group_lims_verifier")
        cls.env.user.groups_id |= cls.analyst_group | cls.verifier_group

    def _create_sample(self, stage=None):
        vals = {
            "customer_id": self.partner.id,
            "sample_type_id": self.sample_type.id,
        }
        if stage:
            vals["stage_id"] = stage.id
        return self.env["lims.sample"].create(vals)

    def _create_analysis(self, sample, stage=None):
        vals = {
            "sample_id": sample.id,
            "product_id": self.product.id,
            "name": self.product.name,
        }
        analysis = self.env["lims.analysis"].create(vals)
        if stage:
            analysis.write({"stage_id": stage.id})
        return analysis
