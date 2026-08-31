# Copyright (C) 2025 Open Source Integrators
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "LIMS Maintenance",
    "summary": "Manage LIMS instruments as maintenance equipment",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "category": "Manufacturing/Maintenance",
    "author": "Open Source Integrators, Gray Matter Logic, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/connector-lims",
    "depends": ["lims", "maintenance"],
    "data": [
        "views/maintenance_equipment_views.xml",
        "views/menu.xml",
    ],
    "demo": ["demo/maintenance_equipment.xml"],
    "application": False,
    "development_status": "Beta",
    "maintainers": ["max3903"],
}
