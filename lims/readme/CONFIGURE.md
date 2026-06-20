## Settings

Go to *LIMS > Configuration > Settings* to:

- Enable **LIMS Advanced** for the full feature set (orders, batches, instruments, teams, LOINC codes, and integrations).
- Enable **Units of Measure** to display a UOM column on analysis lines.

## Roles

Assign roles to users from *Settings > Users & Companies > Users* by setting their **LIMS** role in the user form.

### Sampler

Creates samples, adds analyses, and receives physical samples (advances the sample from *Sample due* to *Received*).

### Analyst

Enters result values on analysis lines and submits them for verification. Cannot verify their own results (double-verification rule).

### Verifier

Verifies submitted analyses and retracts them back to *To Analyze* when corrections are needed. Must be a different user than the analyst unless the Manager override is active.

### Publisher

Publishes verified samples (advances to *Published*).

### Manager

Has all of the above permissions. Can also:

- Access *LIMS > Configuration* (sample types, departments, stages, settings).
- Override the double-verification rule (configurable via the `lims.unforce_double_verification_manager` system parameter).

Administrators (the Odoo admin and root users) are automatically placed in the Manager role.

## Role hierarchy

```
Manager
├── Sampler
├── Analyst
├── Verifier
└── Publisher
```
