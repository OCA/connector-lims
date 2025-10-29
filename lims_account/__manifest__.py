# Copyright (C) 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Laboratory Information Management System (LIMS) Account",
    "summary": "Allows invoicing LIMS orders and linking invoices to LIMS orders",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "category": "Accounting",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/connector-lims",
    "depends": ["lims", "account"],
    "data": [
        "views/account_move_views.xml",
        "views/lims_order_views.xml",
    ],
    "application": False,
    "development_status": "Beta",
    "maintainers": ["max3903", "jasiel-osi", "Nikul-OSI"],
}
