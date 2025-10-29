from odoo import fields, models


class LimsStage(models.Model):
    _inherit = "lims.stage"

    stage_type = fields.Selection(
        selection_add=[("bromatology", "Bromatology")],
        ondelete={"bromatology": "cascade"},
    )
