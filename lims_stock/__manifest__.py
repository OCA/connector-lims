{
    "name": "LIMS Stock",
    "version": "18.0.1.0.0",
    "summary": "Track specimens using stock (lots/location) for LIMS",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/connector-lims",
    "license": "AGPL-3",
    "category": "LIMS",
    "depends": ["lims", "stock", "product"],
    "data": [
        "views/product_template_views.xml",
        "views/lims_specimen_views.xml",
    ],
    "installable": True,
    "application": False,
}
