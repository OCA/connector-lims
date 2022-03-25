# Copyright 2023 Dixmit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Lims",
    "summary": """
        Laboratory Information Management System""",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "author": "Dixmit, Creu Blanca,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/connector-lims",
    "depends": ["product"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/menu.xml",
        "views/lims_department.xml",
        "views/lims_sample_type.xml",
        "views/lims_sample.xml",
        "views/lims_analysis.xml",
        "views/product_template.xml",
    ],
    "demo": ["demo/demo.xml"],
}
