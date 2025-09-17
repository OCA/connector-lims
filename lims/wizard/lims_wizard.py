# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class LIMSWizard(models.TransientModel):
    """
    A wizard to convert a res.partner record to a lims record
    """

    _name = "lims.wizard"
    _description = "LIMS Record Conversion"

    lims_record_type = fields.Selection(
        [("operator", "Operator"), ("laboratory", "Laboratory")], "Record Type"
    )

    def action_convert(self):
        partners = self.env["res.partner"].browse(self._context.get("active_ids", []))
        for partner in partners:
            if self.lims_record_type == "operator":
                self.action_convert_operator(partner)
            if self.lims_record_type == "laboratory":
                self.action_convert_laboratory(partner)
        return {"type": "ir.actions.act_window_close"}

    def action_convert_laboratory(self, partner):
        lims_model = self.env["lims.laboratory"]
        if lims_model.search_count([("partner_id", "=", partner.id)]) == 0:
            lims_model.create({"partner_id": partner.id})
            partner.write({"lims_laboratory": True})
        else:
            raise UserError(_("A laboratory related to that partner already exists."))

    def action_convert_operator(self, partner):
        lims_model = self.env["lims.operator"]
        if lims_model.search_count([("partner_id", "=", partner.id)]) == 0:
            lims_model.create({"partner_id": partner.id})
            partner.write({"lims_operator": True})
        else:
            raise UserError(
                _("A LIMS operator related to that partner already exists.")
            )
