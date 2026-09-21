# Reference Folder

Put recommended / plan-value workbooks here.

- Any file names
- Several files (2, 3, 4, 5…) — every file is a reference
- Sheet names can differ
- Many columns per sheet
- Every file is analyzed against the Input Folder

Supported: `.xlsx` `.xlsb` `.xlsm`

Typical headers:

- **Required identity columns:** MML Object, Parameter ID, Parameter Name
- Value column (detected automatically): Proposed Value, Recommended Value, Plan Value, …
- Optional **Conditions1**, **Conditions2**, … **ConditionsN** (Mobility): dump Parameter Name and short name in brackets, then `=group ID`. The report adds the same numbered columns. Every filled column must match.

`Parameter Name` is the dump display name and is used first to find the field. `Parameter ID` may be `SwitchName@Attribute` — before `@` is the switch/bit, after `@` is the parameter.

Band conditions in Proposed/Recommended Value are applied per cell, for example:

- `L9:1` / `L18:20` / `L21:20` / `L26:35`

When one Local cell ID has several Interfreq handover group ID rows (0=Data, 1=VoLTE, 2+), put the ID in **Conditions**:

- `Interfreq handover group ID=0`
- `Interfreq handover group ID (INTERFREQHOGROUPID)=1`

The report then includes only dump rows whose group ID matches. Objects Checked is that matching-ID count, not every copy of the cell.

