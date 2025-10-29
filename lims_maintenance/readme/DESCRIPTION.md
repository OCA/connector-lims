This module integrates the **LIMS (Laboratory Information Management System)** with Odoo’s **Maintenance** application.

It allows each **LIMS Instrument** to be linked to a **Maintenance Equipment** record, providing traceability and centralized management of laboratory instruments and their maintenance schedules.

### Key Features
- Adds a field `equipment_id` on the `lims.instrument` model.
- Links each instrument with an equipment record from the Maintenance module.
- Displays the associated Maintenance Equipment directly on the instrument form.
- Enables maintenance tracking, scheduling, and reporting for laboratory instruments.
