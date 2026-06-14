# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LOINCCode(models.Model):
    _name = "loinc.code"
    _description = "LOINC Codes"
    _rec_name = "loinc_num"

    loinc_num = fields.Char(required=True, index=True, copy=False, help="1975-2")
    long_common_name = fields.Char(
        copy=False, help="Glucose [Mass/volume] in Serum or Plasma"
    )
    short_name = fields.Char(copy=False, help="Glucose SerPl-mCnc")
    component = fields.Char(required=True, index=True, copy=False, help="Glucose")
    property = fields.Char(required=True, index=True, copy=False, help="Mass/volume")
    time_aspect = fields.Char(
        required=True, index=True, copy=False, help="Pt for Point in time"
    )
    system = fields.Char(
        required=True, index=True, copy=False, help="Ser/Plas for Serum or Plasma"
    )
    scale_type = fields.Char(
        required=True, index=True, copy=False, help="Qn for Quantitative"
    )
    method_type = fields.Char(copy=False, help="Colorimetric")
    unit_code = fields.Char(help="mg/dL")
    loinc_class = fields.Char(string="Class", required=True, copy=False, help="CHEM")
    loinc_class_type = fields.Integer(string="Class Type", required=True, copy=False)
    external_copyright_notice = fields.Char(copy=False)
    version_first_released = fields.Char(required=True, copy=False)
    version_last_changed = fields.Char(required=True, copy=False)
    status = fields.Char(
        required=True,
        index=True,
        copy=False,
        help="ACTIVE, DEPRECATED, DISCOURAGED, TRIAL",
    )
