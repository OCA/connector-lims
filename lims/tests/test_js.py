# Copyright 2026 Dixmit
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import odoo

from odoo.addons.web.tests.test_js import WebSuite


@odoo.tests.tagged("post_install", "-at_install")
class TestLimsWebSuite(WebSuite):
    """Test Lims WebSuite"""

    def get_hoot_filters(self):
        self._test_params = [("+", "@lims")]
        return super().get_hoot_filters()

    def test_lims(self):
        self.test_unit_desktop()
