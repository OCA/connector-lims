After installing, go to *LIMS > Configuration > Settings* and enable the features you need.

## Laboratories

Enable **Manage Multiple Laboratories** to assign samples and orders to specific partner records marked as laboratories.

## Instruments

Enable **Manage Instruments** to track laboratory equipment and link analyses to specific instruments. Enable **Manage Maintenance** (requires Instruments) to create Odoo maintenance requests directly from an instrument record.

## Operators & teams

- **Manage Teams** — group operators into teams; use the team dashboard to monitor workload.
- **Manage Categories** / **Manage Tags** — classify samples and analyses for filtering and reporting.

## Analysis workflow

- **Manage Batches** — group analyses into batches for bulk processing and reporting.
- **Manage Templates** — define reusable analysis panels (sets of tests) that can be applied to a sample in one step.
- **Invoice your analysis** — link analysis orders to customer invoices and vendor bills (*requires* `lims_account`).
- **Manage Logistics** — track specimens using Odoo stock lots and locations (*requires* `lims_stock`).
- **Bromatology** — food-science specimen tracking (*requires* Logistics).
- **Sell analysis** — generate sales quotations from analysis orders (*requires* `lims_sale`).

## Integrations

Enable **HL7** to exchange HL7v2 messages with connected instruments or external LIS systems (*requires* `lims_hl7`).
