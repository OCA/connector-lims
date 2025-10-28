==========================
LIMS Sale Integration
==========================
This module integrates **Odoo LIMS** with **Sales Orders**, allowing laboratories
to sell LIMS services directly as products.  
When a sale order is confirmed, corresponding LIMS Orders are automatically created
based on the configuration defined on each product.

The module supports multiple creation strategies for LIMS Orders via the field
``lims_tracking`` on the product template.

* **No** – No LIMS order is created.
* **Per Sales Order** – One LIMS order is created for the whole sale order.
* **Per Sales Order Line** – One LIMS order is created for each sale order line.
* **Per Quantity** – One LIMS order is created per quantity unit in the sale line.

Each LIMS Order is generated using the selected **LIMS Template**, carrying details
such as categories, operator, and test configurations defined within the template.

This module extends the `lims` and `sale` modules.