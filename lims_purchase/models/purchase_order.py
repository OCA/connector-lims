from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    lims_order_id = fields.Many2one(
        "lims.order", string="LIMS Order", ondelete="set null",
        help="Link to the LIMS Order related to this Purchase Order"
    )

    def action_open_linked_lims_order(self):
        """
        Smart-button action: open the related LIMS Order.
        If no lims_order_id is set, return an action to search for none (or raise).
        """
        self.ensure_one()
        if not self.lims_order_id:
            # Best UX: return an empty tree view filtered to nothing
            action = self.env.ref("lims.action_lims_operation_order").read()[0]
            action["domain"] = [("id", "in", [])]
            return action

        # If you want to open the form directly:
        action = self.env.ref("lims.action_lims_operation_order").read()[0]
        # If the action supports views, prefer to open the form for the single record
        action.update({
            "views": [(self.env.ref("lims.lims_order_form").id, "form")] if self.env.ref("lims.lims_order_form", False) else action.get("views"),
            "res_id": self.lims_order_id.id,
            "target": "current",
        })
        return action
