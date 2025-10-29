Once configured, you can link each **LIMS Instrument** to its corresponding **Maintenance Equipment** record.

---

## Linking Instruments to Maintenance Equipment

1. Go to **LIMS → Instruments**.
2. Open any instrument record.
3. In the **Maintenance** section, choose a record from the *Maintenance Equipment* dropdown.
4. Save the instrument record.

The instrument is now linked to the selected maintenance equipment.

---

## Viewing Linked Equipment

- Open the instrument form.
- The linked **Maintenance Equipment** appears in the *Maintenance* section.
- You can click on the linked record to open the full Maintenance Equipment form.

---

## Example Workflow

1. The laboratory maintains several instruments (e.g., Spectrometer, HPLC, pH Meter).
2. Each instrument exists in both **LIMS Instruments** and **Maintenance Equipment**.
3. After installing `lims_maintenance`, link each LIMS instrument to its Maintenance Equipment.
4. Maintenance operations and scheduling are now traceable directly from LIMS.

---

## Unlinking
To unlink an instrument from maintenance:
1. Edit the instrument record.
2. Clear the *Maintenance Equipment* field.
3. Save the record.
