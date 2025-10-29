# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.lims.tests.common import LIMSCommon


class TestLimsInstrument(LIMSCommon):
    def setUp(self):
        super().setUp()
        self.equipment = self.env["maintenance.equipment"].create(
            {"name": "Body Tube Change"}
        )
        self.instrument.write({"equipment_id": self.equipment.id})

    def test_link_instrument_equipment(self):
        self.assertTrue(self.instrument.equipment_id)
