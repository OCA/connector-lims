# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class LimsAnalysis(models.Model):
    _name = "lims.analysis"
    _description = "Analysis"
    _inherit = ["lims.analysis", "mail.thread", "mail.activity.mixin"]

    test_id = fields.Many2one("lims.test", string="Test Definition")
    instrument_id = fields.Many2one("lims.instrument", string="Instrument")
    batch_id = fields.Many2one(
        "lims.batch",
        string="Batch",
        index=True,
        domain="[('test_id', '=', test_id)]",
    )
    operator_id = fields.Many2one(
        "res.partner",
        string="Assigned Operator",
        domain="[('is_lims_operator', '=', True)]",
    )
    result_ids = fields.One2many(
        "lims.result",
        "analysis_id",
        string="Detailed Results",
    )
    scheduled_date = fields.Datetime()

    @api.onchange("product_id")
    def _onchange_product_id_lims_advanced(self):
        for record in self:
            if not record.product_id:
                continue
            test = self.env["lims.test"].search(
                [("product_id", "=", record.product_id.id)], limit=1
            )
            if test:
                record.test_id = test.id
                record.instrument_id = test.instrument_id.id

    def _analyze_action_vals(self):
        vals = super()._analyze_action_vals()
        vals["capture_date"] = fields.Datetime.now()
        return vals

    def _sync_result_from_value(self):
        Result = self.env["lims.result"]
        for analysis in self.filtered("value"):
            try:
                numeric_value = float(analysis.value)
            except (TypeError, ValueError):
                numeric_value = 0.0
            result = analysis.result_ids[:1]
            vals = {
                "analysis_id": analysis.id,
                "description": analysis.name,
                "result_value": numeric_value,
                "result_date": fields.Date.context_today(analysis),
                "validated_by_user_id": analysis.verified_by.id,
            }
            if result:
                result.write(vals)
            else:
                Result.create(vals)

    def _create_results_from_test(self):
        Result = self.env["lims.result"]
        for analysis in self.filtered("test_id"):
            existing_def_ids = analysis.result_ids.mapped("test_result_id").ids
            for test_result in analysis.test_id.test_result_ids:
                if test_result.id not in existing_def_ids:
                    Result.create(
                        {
                            "analysis_id": analysis.id,
                            "test_result_id": test_result.id,
                            "description": test_result.name,
                        }
                    )

    def write(self, vals):
        res = super().write(vals)
        if "test_id" in vals:
            self._create_results_from_test()
        return res

    def analyze_action(self):
        res = super().analyze_action()
        self._sync_result_from_value()
        return res

    def verify_action(self):
        res = super().verify_action()
        self._sync_result_from_value()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        analyses = super().create(vals_list)
        for analysis, vals in zip(analyses, vals_list, strict=True):
            if vals.get("value"):
                analysis._sync_result_from_value()
            if vals.get("test_id"):
                analysis._create_results_from_test()
        return analyses
