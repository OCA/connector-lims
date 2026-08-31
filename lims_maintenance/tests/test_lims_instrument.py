# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import ast

from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestLimsInstrument(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.instrument = cls.env["maintenance.equipment"].create(
            {"name": "HPLC System", "is_lims_instrument": True}
        )
        cls.plain_equipment = cls.env["maintenance.equipment"].create(
            {"name": "Office Printer"}
        )

    def test_is_lims_instrument_flag(self):
        self.assertTrue(self.instrument.is_lims_instrument)
        self.assertFalse(self.plain_equipment.is_lims_instrument)

    def test_action_domain_filters_instruments(self):
        action = self.env.ref("lims_maintenance.action_lims_instrument")
        domain = ast.literal_eval(action.domain)
        self.assertEqual(domain, [("is_lims_instrument", "=", True)])
        instruments = self.env["maintenance.equipment"].search(domain)
        self.assertIn(self.instrument, instruments)
        self.assertNotIn(self.plain_equipment, instruments)

    def test_action_context_defaults_flag(self):
        action = self.env.ref("lims_maintenance.action_lims_instrument")
        ctx = ast.literal_eval(action.context)
        self.assertTrue(ctx.get("default_is_lims_instrument"))
