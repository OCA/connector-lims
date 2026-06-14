# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class LimsAdvancedCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Customer"})
        cls.laboratory = cls.env["res.partner"].create(
            {"name": "Main Lab", "is_laboratory": True}
        )
        cls.operator = cls.env["res.partner"].create(
            {"name": "Lab Tech", "is_lims_operator": True}
        )
        cls.physician = cls.env["res.partner"].create(
            {"name": "Dr. Smith", "is_physician": True}
        )
        cls.sample_type = cls.env["lims.sample.type"].create({"name": "Blood"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Glucose",
                "laboratory_ok": True,
                "type": "service",
            }
        )
        cls.test = cls.env["lims.test"].create(
            {
                "name": "Glucose",
                "product_tmpl_id": cls.product.product_tmpl_id.id,
            }
        )
        cls.team = cls.env["lims.team"].create({"name": "Chemistry"})
        # Sample stages
        cls.stage_registered = cls.env.ref("lims.lims_stage_sample_registered")
        cls.stage_due = cls.env.ref("lims.lims_stage_sample_due")
        cls.stage_received = cls.env.ref("lims.lims_stage_sample_received")
        cls.stage_to_be_verified = cls.env.ref("lims.lims_stage_sample_to_be_verified")
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
        # Batch stages
        cls.stage_batch_new = cls.env.ref("lims_advanced.lims_stage_batch_new")
        cls.stage_batch_completed = cls.env.ref(
            "lims_advanced.lims_stage_batch_completed"
        )
        cls.stage_batch_cancelled = cls.env.ref(
            "lims_advanced.lims_stage_batch_cancelled"
        )
        # Groups
        cls.env.user.groups_id |= cls.env.ref("lims.group_lims_analyst") | cls.env.ref(
            "lims.group_lims_verifier"
        )

    def _create_sample(self, stage=None, team=None):
        vals = {
            "customer_id": self.partner.id,
            "sample_type_id": self.sample_type.id,
        }
        if stage:
            vals["stage_id"] = stage.id
        if team:
            vals["team_id"] = team.id
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
