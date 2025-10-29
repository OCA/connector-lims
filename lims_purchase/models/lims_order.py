from odoo import api, fields, models


class LIMSOrder(models.Model):
    _inherit = "lims.order"

    purchase_order_ids = fields.One2many(
        "purchase.order",
        "lims_order_id",
        string="Purchase Orders",
        help="Purchase Orders created/linked for this LIMS Order",
    )

    purchase_order_count = fields.Integer(
        string="PO Count",
        compute="_compute_purchase_order_count",
    )

    purchase_order_m2m_ids = fields.Many2many(
        "purchase.order",
        "lims_order_purchase_rel",
        "lims_order_id",
        "purchase_order_id",
        string="Linked Purchase Orders (M2M)",
        help="Attach existing Purchase Orders that relate to this LIMS Order.",
    )

    def _compute_purchase_order_count(self):
        for rec in self:
            # read_group is faster in bulk but simple search_count is fine here
            rec.purchase_order_count = self.env["purchase.order"].search_count(
                [("lims_order_id", "=", rec.id)]
            )

    def action_view_purchase_orders(self):
        """Open purchase orders linked to this LIMS order."""
        self.ensure_one()
        purchase_orders = self.purchase_order_ids

        # Use the standard Purchase action (the one that lists RFQs/POs)
        action = self.env.ref("purchase.purchase_rfq").read()[0]

        # If no POs, open the empty list
        if not purchase_orders:
            action["domain"] = [("id", "in", [])]
            return action

        # If only one PO → open form view directly
        if len(purchase_orders) == 1:
            form_view = self.env.ref("purchase.purchase_order_form", False)
            action.update(
                {
                    "view_mode": "form",
                    "views": [(form_view.id, "form")] if form_view else [],
                    "res_id": purchase_orders.id,
                    "domain": [],
                }
            )
            return action

        # Multiple → show list view filtered
        action["domain"] = [("id", "in", purchase_orders.ids)]
        return action
