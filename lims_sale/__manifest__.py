# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Laboratory Information Management System (LIMS) Sales",
    "summary": "Manage LIMS Instruments, Analysis and Tests Sales Integration",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "category": "LIMS",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/connector-lims",
    "depends": ["lims", "sale"],
    "data": [
        "views/product_template_views.xml",
        "views/sale_order_views.xml",
        "views/lms_order_view.xml",
    ],
    "application": False,
    "development_status": "Beta",
    "maintainers": ["max3903", "jasiel-osi", "Hardik-OSI"],
}
