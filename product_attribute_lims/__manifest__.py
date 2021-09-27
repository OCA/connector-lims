# Copyright 2021 - Manuel Calero <https://xtendoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product LIMS attribute",
    "summary": "Product attributes for LIMS",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "author": "Xtendoo, Odoo Community Association (OCA)",
    "category": "Warehouse",
    "website": "https://github.com/OCA/connector-lims",
    "depends": [
        "base",
        "sale",
        "purchase",
        "stock",
        "product",
    ],
    "data": ["views/product_view.xml"],
    "installable": True,
}
