# Laboratory Information Management System (LIMS)

[![Beta](https://img.shields.io/badge/maturity-Beta-yellow.png)](https://odoo-community.org/page/development-status)
[![License: LGPL-3](https://img.shields.io/badge/licence-LGPL--3-blue.png)](http://www.gnu.org/licenses/lgpl-3.0-standalone.html)
[![OCA/connector-lims](https://img.shields.io/badge/github-OCA%2Fconnector--lims-lightgray.png?logo=github)](https://github.com/OCA/connector-lims/tree/18.0/lims)
[![Translate me on Weblate](https://img.shields.io/badge/weblate-Translate%20me-F47D42.png)](https://translation.odoo-community.org/projects/connector-lims-18-0/connector-lims-18-0-lims)
[![Try me on Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/connector-lims&target_branch=18.0)

Base Laboratory Information Management System (LIMS) module for Odoo.

Manages samples and their analyses through a configurable, stage-based workflow — from
sample registration to result publication — with role-based access control for samplers,
analysts, verifiers, and publishers.

**Table of contents**

- [Usage](#usage)
- [Configuration](#configuration)
- [Roadmap](#roadmap)
- [Bug Tracker](#bug-tracker)
- [Credits](#credits)

## Usage

### Samples

1. A **sampler** creates a sample from _LIMS > Samples_:

   - Set the customer, sample type, and collection date.
   - Add the analyses to perform on the sample.
   - Click **Receive** when the physical sample arrives, or use **Next Stage** to
     advance the sample manually.

2. An **analyst** enters the result value on each analysis line and clicks ✓ (Analyze)
   to submit it for verification.

3. A **verifier** (different from the analyst by default) clicks ● (Verify) on each
   submitted analysis. Once all analyses are verified the sample advances to _Verified_
   automatically.

### Sample stage workflow

```
Registered → Scheduled Sampling → Sample due → Received
           → To be verified → Verified → Published
                                        → Cancelled
                                        → Invalid
```

### Analysis stage workflow

```
Registered → To Analyze → To be Verified → Verified
                                          → Rejected (terminal)
```

The **Receive** button moves the sample from _Sample due_ to _Received_ and
simultaneously advances all its analyses from _Registered_ to _To Analyze_.

## Configuration

### Settings

Go to _LIMS > Configuration > Settings_ to:

- Enable **LIMS Advanced** for the full feature set (orders, batches, instruments,
  teams, LOINC codes, and integrations).
- Enable **Units of Measure** to display a UOM column on analysis lines.

### Roles

Assign roles to users from _Settings > Users & Companies > Users_ by setting their
**LIMS** role in the user form.

#### Sampler

Creates samples, adds analyses, and receives physical samples (advances the sample from
_Sample due_ to _Received_).

#### Analyst

Enters result values on analysis lines and submits them for verification. Cannot verify
their own results (double-verification rule).

#### Verifier

Verifies submitted analyses and retracts them back to _To Analyze_ when corrections are
needed. Must be a different user than the analyst unless the Manager override is active.

#### Publisher

Publishes verified samples (advances to _Published_).

#### Manager

Has all of the above permissions. Can also:

- Access _LIMS > Configuration_ (sample types, departments, stages, settings).
- Override the double-verification rule (configurable via the
  `lims.unforce_double_verification_manager` system parameter).

Administrators (the Odoo admin and root users) are automatically placed in the Manager
role.

#### Role hierarchy

```
Manager
├── Sampler
├── Analyst
├── Verifier
└── Publisher
```

## Roadmap

- Worklist view for bulk result entry
- Device / instrument integration
- Calculated results (formulas across analyses)
- Quality control rules and reference ranges
- Sample storage location tracking

## Bug Tracker

Bugs are tracked on [GitHub Issues](https://github.com/OCA/connector-lims/issues). In
case of trouble, please check there if your issue has already been reported. If you
spotted it first, help us smash it by providing a detailed and welcomed
[feedback](https://github.com/OCA/connector-lims/issues/new?body=module:%20lims%0Aversion:%2018.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**).

Do not contact contributors directly about support or help with technical issues.

## Credits

### Authors

- Dixmit
- Creu Blanca
- Gray Matter Logic
- Odoo Community Association (OCA)

### Contributors

- [Dixmit](https://dixmit.com)
  - Enric Tobella \<etobella@dixmit.com\>
- [Gray Matter Logic](https://www.graymatterlogic.com)
  - Maxime Chambreuil \<mchambreuil@opensourceintegrators.com\>

### Maintainers

This module is maintained by the OCA.

[![Odoo Community Association](https://odoo-community.org/logo.png)](https://odoo-community.org)

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to
support the collaborative development of Odoo features and promote its widespread use.

This module is part of the
[OCA/connector-lims](https://github.com/OCA/connector-lims/tree/18.0/lims) project on
GitHub.

You are welcome to contribute. To learn how please visit
<https://odoo-community.org/page/Contribute>.
