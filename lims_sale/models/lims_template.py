from odoo import fields, models


class LimsTemplate(models.Model):
    _inherit = "lims.template"

    def create_lims_order_from_template(self, sale_order=None, sale_line=None):
        """Generate a lims.order record based on this
        template and optionally link it to Sale Order."""
        self.ensure_one()

        test_commands = []
        for test in self.test_ids:
            if hasattr(test, "_prepare_order_test_values"):
                values = test._prepare_order_test_values()
            else:
                values = {
                    "name": test.name,
                    "instrument_id": getattr(test, "instrument_id", False)
                    and test.instrument_id.id
                    or False,
                    "company_id": test.company_id.id
                    if test.company_id
                    else self.company_id.id,
                }

            if self.operator_id:
                values["operator_id"] = self.operator_id.id

            test_commands.append(fields.Command.create(values))

        vals = {
            "name": f"{self.name} - {fields.Date.today()}",
            "template_id": self.id,
            "operator_id": self.operator_id.id if self.operator_id else False,
            "company_id": self.company_id.id or self.env.company.id,
            "category_ids": [(6, 0, self.category_ids.ids)],
            "test_ids": test_commands,
        }

        if sale_order:
            vals.update(
                {
                    "sale_order_id": sale_order.id,
                    "partner_id": sale_order.partner_id.id,
                }
            )
        if sale_line:
            vals.update(
                {
                    "sale_line_id": sale_line.id,
                    "partner_id": sale_order.partner_id.id,
                }
            )

        return self.env["lims.order"].create(vals)
