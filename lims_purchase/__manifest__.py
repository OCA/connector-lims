{
    "name": "LIMS Purchase Integration",
    "version": "18.0.1.0.0",
    "depends": ["purchase", "lims"],
    "author": "Hardik-OSI",
    "website": "https://github.com/OCA/connector-lims",
    "category": "LIMS",
    "summary": "Link LIMS orders and Purchase Orders; Smart buttons for navigation",
    "license": "AGPL-3",
    "data": [
        "views/purchase_order_views.xml",
        "views/lims_order_views.xml",
    ],
    "installable": True,
    "application": False,
}
