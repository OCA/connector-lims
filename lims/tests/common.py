# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import TransactionCase


class LIMSCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # === Partners ===
        cls.partner_specimen = cls.env.ref(
            "base.res_partner_10", raise_if_not_found=False
        )
        cls.partner_admin = cls.env.ref("base.partner_admin", raise_if_not_found=False)
        cls.partner_laboratory = cls.env.ref(
            "base.res_partner_1", raise_if_not_found=False
        )
        cls.partner_operator = cls.env.ref(
            "base.res_partner_2", raise_if_not_found=False
        )
        cls.partner_operator_4 = cls.env.ref(
            "base.res_partner_4", raise_if_not_found=False
        )
        cls.partner_physician = cls.env.ref(
            "base.res_partner_3", raise_if_not_found=False
        )

        # Assign LIMS role flags for partners
        cls.partner_admin.write(
            {
                "is_laboratory": True,
                "is_lims_operator": True,
                "is_physician": True,
            }
        )
        cls.partner_laboratory.write(
            {
                "is_laboratory": True,
                "is_lims_operator": False,
                "is_physician": False,
            }
        )
        cls.partner_operator.write(
            {
                "is_laboratory": False,
                "is_lims_operator": True,
                "is_physician": False,
            }
        )
        cls.partner_operator_4.write(
            {
                "is_laboratory": False,
                "is_lims_operator": True,
                "is_physician": False,
            }
        )
        cls.partner_physician.write(
            {
                "is_laboratory": False,
                "is_lims_operator": False,
                "is_physician": True,
            }
        )

        # === LIMS Entities ===
        cls.test_id = cls.env.ref(
            "lims.lims_test_microbiology_parasitic_studies", raise_if_not_found=False
        )

        # Category
        cls.lims_category = cls.env["lims.category"].create(
            {
                "name": "Test Category",
                "description": "Functional test category",
            }
        )

        # Team
        cls.lims_team = cls.env["lims.team"].create(
            {
                "name": "Test Team",
                "description": "Functional test team",
            }
        )

        # Tag
        cls.lims_tag = cls.env["lims.tag"].create(
            {
                "name": "Test Tag",
            }
        )

        # Specimen
        cls.lims_specimen = cls.env["lims.specimen"].create(
            {
                "name": "Test/Blood/007",
                "partner_id": cls.partner_specimen.id,
                "collection_date": fields.Date.today(),
            }
        )

        # Template
        cls.lims_template = cls.env["lims.template"].create(
            {
                "name": "Test/TMP/007",
                "physician_id": cls.partner_physician.id,
                "operator_id": cls.partner_operator_4.id,
                "tag_ids": [(6, 0, [cls.lims_tag.id])],
                "category_ids": [(6, 0, [cls.lims_category.id])],
                "test_ids": [(6, 0, [cls.test_id.id])],
            }
        )

        # Instrument
        cls.instrument = cls.env["lims.instrument"].create(
            {
                "name": "Microscope",
                "operator_id": cls.partner_operator.id,
                "notes": """Used for viewing samples at a cellular level,
            such as blood and tissue.""",
                "laboratory_id": cls.partner_laboratory.id,
            }
        )
