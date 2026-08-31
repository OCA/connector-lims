# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestLimsAccount(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create({"name": "LIMS Customer"})
        cls.sample_type = cls.env["lims.sample.type"].create({"name": "Blood"})
        cls.analyte = cls.env["lims.analyte"].create(
            {
                "name": "pH",
                "code": "pH",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.analyte_2 = cls.env["lims.analyte"].create(
            {
                "name": "Glucose",
                "code": "GLU",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.sample = cls.env["lims.sample"].create(
            {
                "sample_type_id": cls.sample_type.id,
                "partner_id": cls.partner.id,
            }
        )

    def _create_invoice(self, samples=None, analytes=None):
        line_vals = {
            "name": "Lab analysis",
            "quantity": 1.0,
            "price_unit": 100.0,
        }
        if analytes:
            line_vals["lims_analyte_ids"] = [Command.set(analytes.ids)]
        vals = {
            "partner_id": self.partner.id,
            "move_type": "out_invoice",
            "invoice_line_ids": [Command.create(line_vals)],
        }
        if samples:
            vals["lims_sample_ids"] = [Command.set(samples.ids)]
        return self.env["account.move"].create(vals)

    def test_link_invoice_to_sample(self):
        invoice = self._create_invoice(self.sample)
        self.assertIn(self.sample, invoice.lims_sample_ids)
        self.assertEqual(invoice.lims_sample_count, 1)
        self.assertEqual(self.sample.account_move_count, 1)
        self.assertIn(invoice, self.sample.account_move_ids)

        sample_action = invoice.action_open_lims_samples()
        self.assertEqual(sample_action["res_model"], "lims.sample")
        self.assertEqual(sample_action["res_id"], self.sample.id)
        self.assertEqual(sample_action["view_mode"], "form")

        invoice_action = self.sample.action_open_account_moves()
        self.assertEqual(invoice_action["res_model"], "account.move")
        self.assertEqual(invoice_action["res_id"], invoice.id)
        self.assertEqual(invoice_action["view_mode"], "form")

    def test_invoice_line_carries_analytes(self):
        invoice = self._create_invoice(
            self.sample, analytes=self.analyte | self.analyte_2
        )
        line = invoice.invoice_line_ids[0]
        self.assertEqual(line.lims_analyte_ids, self.analyte | self.analyte_2)

    def test_multiple_samples_list_action(self):
        sample2 = self.env["lims.sample"].create(
            {
                "sample_type_id": self.sample_type.id,
                "partner_id": self.partner.id,
            }
        )
        invoice = self._create_invoice(self.sample | sample2)
        self.assertEqual(invoice.lims_sample_count, 2)
        action = invoice.action_open_lims_samples()
        self.assertEqual(action["view_mode"], "list,form")
        self.assertEqual(action["domain"], [("id", "in", invoice.lims_sample_ids.ids)])
        self.assertNotIn("res_id", action)

    def test_multiple_invoices_list_action(self):
        invoice1 = self._create_invoice(self.sample)
        invoice2 = self._create_invoice(self.sample)
        self.assertEqual(self.sample.account_move_count, 2)
        action = self.sample.action_open_account_moves()
        self.assertEqual(action["view_mode"], "list,form")
        self.assertEqual(
            action["domain"], [("id", "in", self.sample.account_move_ids.ids)]
        )
        self.assertNotIn("res_id", action)
        self.assertEqual(
            set(self.sample.account_move_ids.ids), {invoice1.id, invoice2.id}
        )

    def test_sample_without_invoices_opens_create_form(self):
        self.assertEqual(self.sample.account_move_count, 0)
        action = self.sample.action_open_account_moves()
        self.assertEqual(action["view_mode"], "form")
        self.assertNotIn("res_id", action)
        self.assertEqual(action["context"]["default_partner_id"], self.partner.id)
        self.assertEqual(
            action["context"]["default_lims_sample_ids"],
            [(6, 0, [self.sample.id])],
        )

    def test_invoice_without_samples(self):
        invoice = self._create_invoice()
        self.assertEqual(invoice.lims_sample_count, 0)
        action = invoice.action_open_lims_samples()
        self.assertEqual(action["view_mode"], "list,form")
        self.assertEqual(action["domain"], [("id", "in", [])])
