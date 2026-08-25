# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "LIMS Sale",
    "summary": "Create LIMS samples from sales order confirmation",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "category": "Sales/Sales",
    "author": "Open Source Integrators, Gray Matter Logic, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/connector-lims",
    "depends": ["lims", "sale"],
    "data": [
        "views/product_template_views.xml",
        "views/sale_order_views.xml",
        "views/lims_sample_views.xml",
    ],
    "application": False,
    "development_status": "Beta",
    "maintainers": ["max3903"],
}
