# Advanced LIMS

[![Beta](https://img.shields.io/badge/maturity-Beta-yellow.png)](https://odoo-community.org/page/development-status)
[![License: LGPL-3](https://img.shields.io/badge/licence-LGPL--3-blue.png)](http://www.gnu.org/licenses/lgpl-3.0-standalone.html)
[![OCA/connector-lims](https://img.shields.io/badge/github-OCA%2Fconnector--lims-lightgray.png?logo=github)](https://github.com/OCA/connector-lims/tree/18.0/lims_advanced)
[![Translate me on Weblate](https://img.shields.io/badge/weblate-Translate%20me-F47D42.png)](https://translation.odoo-community.org/projects/connector-lims-18-0/connector-lims-18-0-lims_advanced)
[![Try me on Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/connector-lims&target_branch=18.0)

Extends the base `lims` module with advanced laboratory workflow features:

- **LOINC codes** — link products to standard LOINC test identifiers.
- **Configurable stages** — define and reorder workflow stages for specimens, orders,
  batches, instruments, and results.
- **Teams & operators** — organise staff into teams; assign operators and physicians to
  samples.
- **Categories & tags** — classify samples and analyses for reporting.
- **Sample & order templates** — define reusable analysis panels.
- **Instruments & methods** — track laboratory equipment and analytical methods.
- **Batches** — group analyses for bulk processing.
- **Specimens** — manage physical specimen records linked to samples.
- **Detailed results** — store structured numeric results alongside free-text values.
- **Analysis orders** — manage full order-to-invoice workflows bridging samples and
  analyses.
- **Multi-company** — separate record rules per company.
- **Optional integrations** — Sales, Purchase, Accounting, Stock, Maintenance,
  Bromatology, and HL7v2 (enabled per-company from Settings).

**Table of contents**

- [Configuration](#configuration)
- [Bug Tracker](#bug-tracker)
- [Credits](#credits)

## Configuration

After installing, go to _LIMS > Configuration > Settings_ and enable the features you
need.

### Laboratories

Enable **Manage Multiple Laboratories** to assign samples and orders to specific partner
records marked as laboratories.

### Instruments

Enable **Manage Instruments** to track laboratory equipment and link analyses to
specific instruments. Enable **Manage Maintenance** (requires Instruments) to create
Odoo maintenance requests directly from an instrument record.

### Operators & teams

- **Manage Teams** — group operators into teams; use the team dashboard to monitor
  workload.
- **Manage Categories** / **Manage Tags** — classify samples and analyses for filtering
  and reporting.

### Analysis workflow

- **Manage Batches** — group analyses into batches for bulk processing and reporting.
- **Manage Templates** — define reusable analysis panels (sets of tests) that can be
  applied to a sample in one step.
- **Invoice your analysis** — link analysis orders to customer invoices and vendor bills
  (_requires_ `lims_account`).
- **Manage Logistics** — track specimens using Odoo stock lots and locations (_requires_
  `lims_stock`).
- **Bromatology** — food-science specimen tracking (_requires_ Logistics).
- **Sell analysis** — generate sales quotations from analysis orders (_requires_
  `lims_sale`).

### Integrations

Enable **HL7** to exchange HL7v2 messages with connected instruments or external LIS
systems (_requires_ `lims_hl7`).

## Bug Tracker

Bugs are tracked on [GitHub Issues](https://github.com/OCA/connector-lims/issues). In
case of trouble, please check there if your issue has already been reported. If you
spotted it first, help us smash it by providing a detailed and welcomed
[feedback](https://github.com/OCA/connector-lims/issues/new?body=module:%20lims_advanced%0Aversion:%2018.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**).

Do not contact contributors directly about support or help with technical issues.

## Credits

### Authors

- Gray Matter Logic
- Odoo Community Association (OCA)

### Contributors

- [Gray Matter Logic](https://www.graymatterlogic.com)
  - Maxime Chambreuil \<mchambreuil@opensourceintegrators.com\>

### Maintainers

This module is maintained by the OCA.

[![Odoo Community Association](https://odoo-community.org/logo.png)](https://odoo-community.org)

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to
support the collaborative development of Odoo features and promote its widespread use.

Current [maintainer](https://odoo-community.org/page/maintainer-role):
[![max3903](https://github.com/max3903.png?size=40px)](https://github.com/max3903)

This module is part of the
[OCA/connector-lims](https://github.com/OCA/connector-lims/tree/18.0/lims_advanced)
project on GitHub.

You are welcome to contribute. To learn how please visit
<https://odoo-community.org/page/Contribute>.
