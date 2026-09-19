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

`Parameter Name` is the dump display name and is used first to find the field. `Parameter ID` may be `SwitchName@Attribute` — before `@` is the switch/bit, after `@` is the parameter.

Band/group conditions in Proposed/Recommended Value are applied per cell, for example:

- `L9:1` / `L18:20` / `L21:20` / `L26:35`
- `(InterFreqHoGroupId=1)=>L09=-108`
- `(InterRatHoCommGroupId=1)=>L18=-112`

