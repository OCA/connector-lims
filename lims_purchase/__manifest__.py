# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "LIMS Purchase",
    "summary": "Link LIMS samples and purchase orders with smart buttons",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "category": "Inventory/Purchase",
    "author": "Open Source Integrators, Gray Matter Logic, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/connector-lims",
    "depends": ["lims", "purchase"],
    "data": [
        "views/purchase_order_views.xml",
        "views/lims_sample_views.xml",
    ],
    "demo": [
        "demo/res_partner.xml",
        "demo/product_product.xml",
        "demo/lims_sample.xml",
        "demo/purchase_order.xml",
        "demo/purchase_order_line.xml",
    ],
    "application": False,
    "development_status": "Beta",
    "maintainers": ["max3903"],
}
