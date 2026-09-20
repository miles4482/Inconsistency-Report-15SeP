# Parameter Inconsistency Audit

One tool, three local folders on your PC:

| Folder | What goes in it |
|---|---|
| **Input Folder** | Configuration dumps in `Input/5G`, `Input/4G`, `Input/3G`, `Input/2G`. Tick those networks in the tool; only those folders are searched. |
| **Reference Folder** | Recommended / plan values. Any names. Several files (2, 3, 4…). Every file is analyzed against the selected Input folders. |
| **Output Folder** | All inconsistency reports. |

Files stay on this PC. There is no upload and no file-size limit from the app.

## License (required)

The app will not run without an active signed license. Default validity is **7 days**.

You can drop **`.lic`, `.json`, or `.txt`** next to `ParameterAudit.exe` — no rename needed — or click **Load license file…**.

### Owner: generate a license on Windows

1. Open `LicenseGenerator.exe`.
2. Type **Days of license** (example: `7`).
3. Click **Generate license**.
4. Copy the generated `ParameterAudit.lic` (also saved as `.json` and `.txt`) next to `ParameterAudit.exe`.

```bash
python3 scripts/issue_license.py --to "Site A" --days 7 -o SiteA.lic
python3 scripts/license_generator_app.py
```

## Windows app

Download [`packages/ParameterAudit_Windows_v1.8.0.rar`](packages/ParameterAudit_Windows_v1.8.0.rar) (also [`ParameterAudit_Windows.rar`](packages/ParameterAudit_Windows.rar)), extract the folder, then run `ParameterAudit.exe`. The window title shows **v1.8.0**.

The extracted folder already contains `Input`, `Reference`, and `Output`. Drop files in, then Generate Report — or Browse this PC to other folders.

Windows Defender may still warn because the app is unsigned. Choose **More info → Run anyway**, or add the extracted folder as an exclusion. Use the extracted **folder** (not a single packed exe).

To rebuild locally:

```bat
build_exe.bat
```

Then run `dist\ParameterAudit\ParameterAudit.exe`.

Command line (local folders):

```bash
python3 scripts/compare_reference_parameters.py --input-folder "./input" --reference-folder "./reference" --output-folder "./reports" --rats 4G,5G
```

## Folder drop (no GUI)

1. Copy dumps into `input/`.
2. Copy reference workbooks into `reference/`.
3. Run `./run_audit.sh` or `run_audit.bat`.

Latest copies:

- `reports/latest/Parameter_Inconsistency_Report.xlsx`
- `reports/run_history.csv`

## Matching rules

- Tick **5G / 4G / 3G / 2G** so only those `Input` subfolders are searched.
- Input sheet names that match an MO / MML Object name are treated as that object.
- Huawei dumps with a `MAPPING DEF` sheet are mapped by MOC and attribute.
- **MML Object**, **Parameter ID**, and **Parameter Name** are the three columns used to find each parameter in the dump. Other reference columns (Proposed / Recommended / Plan value, bands, groups) are detected automatically.
- `Parameter ID` of the form `SwitchName@Attribute`: before `@` is the switch/bit, after `@` is the parameter (column).
- Recommended / proposed values are either a **direct** parameter value (`1`, `ON`, `-108`) or **named switches/bits** inside that parameter (`GeranCsftbSwitch-1`, or several joined by `&`). Named switches are looked up inside the dump **Parameter Name** column; other options packed in the same cell are ignored.
- `Parameter Name` is the dump display name and is matched first.
- 4G `Cell` maps `Local cell ID` to band families (L9 = L09 = L900 = Frequency Band 8; L18 = L1800 = Band 3; L21 = L2100 = Band 1; L26 = L2600 = Band 41/7). 5G `NRDUCELL` maps `NR DU Cell ID` (N41 → L26). Only those two sheets are read for the band map.
- Proposed values such as `L9:-74 L18:-118 L21:-118 L26:-115` or `(InterFreqHoGroupId=1)=>L09=-108` are applied only to cells where that band/group applies. Group ID is taken from the current MO row when present.
- Built-in name thinking (aliases + fuzzy match) corrects mistyped MO / parameter / sheet names. No cloud AI is used.
- Other workbooks are matched by sheet name and column name.
- Every reference parameter is searched in **every selected** input file.

## Limits (note)

Microsoft Excel allows **1,048,576 rows** and **16,384 columns** per sheet. This tool does not add a lower cap on files, sheets, or columns. Very large dumps use more RAM and take longer. Excel 97-2003 `.xls` is not read; save as `.xlsx`.

## Report contents

1. Overall report
2. All parameter-wise report (function wise)
3. Sheet-wise report
4. Final summary

## Sample result (15 Sep 2026 dumps)

- [`reports/Parameter_Inconsistency_Report_15Sep26.xlsx`](reports/Parameter_Inconsistency_Report_15Sep26.xlsx)
- [`reports/Parameter_Inconsistency_Report_15Sep26.md`](reports/Parameter_Inconsistency_Report_15Sep26.md)
- [`reports/all_parameters_15Sep26.csv`](reports/all_parameters_15Sep26.csv)

Headline from the three-folder run on the 15 Sep 2026 dumps: **256** parameters, **79** inconsistent (5 full, 74 mixed), **85** consistent, **92** no recommend, **0** not found. Auditable rate **48.2%**.
