# Copyright 2023 Dixmit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Laboratory Information Management System (LIMS)",
    "category": "Laboratories",
    "summary": "Manage your laboratories, samples and analysis.",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "author": "Dixmit, Creu Blanca, Gray Matter Logic,"
    " Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/connector-lims",
    "depends": ["product"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/lims_stage.xml",
        "views/res_config_settings.xml",
        "views/lims_department.xml",
        "views/lims_sample_type.xml",
        "views/lims_sample.xml",
        "views/lims_analysis.xml",
        "views/product_template.xml",
        "views/menu.xml",
    ],
    "demo": ["demo/demo.xml"],
    "maintainers": ["etobella", "max3903"],
    "development_status": "Beta",
    "application": True,
    "installable": True,
}
