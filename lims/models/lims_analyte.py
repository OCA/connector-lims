# Copyright 2026 Dixmit
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models

OPERATORS = [
    ("lt", "<"),
    ("lte", "<="),
    ("gte", ">="),
    ("gt", ">"),
]


class LimsAnalyte(models.Model):
    _name = "lims.analyte"
    _description = "Lims Analyte"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    description = fields.Html(translate=True)
    active = fields.Boolean(default=True)
    uom_id = fields.Many2one("uom.uom")
    specification_ids = fields.One2many("lims.analyte.specs", inverse_name="analyte_id")
    result_type = fields.Selection(
        [
            ("float", "Numeric"),
            ("char", "String"),
            ("text", "Text"),
            ("boolean", "Boolean"),
            ("selection", "Selection"),
            ("multiselection", "Multi-selection"),
            ("multiselection-check", "Multi-selection with checks"),
            ("date", "Date"),
            ("datetime", "Datetime"),
        ],
        required=True,
        default="float",
    )
    autoverify = fields.Boolean(
        help="Whether the analysis can be verified by the user if he is a verifier."
    )
    precision_digits = fields.Integer(
        help="""Number of decimals to consider when comparing numeric results with
        specifications. Ignored for other result types.""",
        default=2,
    )
    option_ids = fields.One2many("lims.analyte.option", inverse_name="analyte_id")
    _code_unique = models.Constraint("unique(code)", "Code must be unique.")

    def _get_default_value(self, sample_type):
        if not self:
            return {}
        self.ensure_one()
        value = {"value": False, "result_type": self.result_type}
        if self.result_type in ("selection", "multiselection"):
            value["selection"] = self.option_ids.mapped("value")
        if self.result_type == "multiselection":
            value["value"] = []
        if self.result_type == "multiselection-check":
            value["value"] = {option.value: False for option in self.option_ids}
        if self.result_type == "float":
            value["digits"] = self.precision_digits
            specs = self.specification_ids.filtered(
                lambda s: s.sample_type_id == sample_type
            )
            if specs and specs.min_operator:
                value["min"] = specs.min_value
                value["min_warning"] = specs.min_warning_value
                value["min_operator"] = specs.min_operator
            if specs and specs.max_operator:
                value["max"] = specs.max_value
                value["max_warning"] = specs.max_warning_value
                value["max_operator"] = specs.max_operator
        return value


class LimsAnalyteOption(models.Model):
    _name = "lims.analyte.option"
    _description = "Lims Analyte Option"
    _order = "sequence, id"

    analyte_id = fields.Many2one("lims.analyte", required=True)
    sequence = fields.Integer(required=True, default=10)
    value = fields.Char(required=True)


class LimsAnalyteSpecs(models.Model):
    _name = "lims.analyte.specs"
    _description = "Lims Analyte Specs"

    analyte_id = fields.Many2one("lims.analyte", required=True)
    sample_type_id = fields.Many2one("lims.sample.type", required=True)
    min_operator = fields.Selection(OPERATORS, default="lt")
    min_value = fields.Float()
    min_warning_value = fields.Float()
    max_value = fields.Float()
    max_warning_value = fields.Float()
    max_operator = fields.Selection(OPERATORS, default="gt")
