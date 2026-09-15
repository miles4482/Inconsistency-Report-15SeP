# Parameter Inconsistency Audit

One tool, three local folders on your PC:

| Folder | What goes in it |
|---|---|
| **Input Folder** | Configuration dumps used for comparing. Any names (4G dump, 5G dump, 2G dump, …). More than one file. No file-count limit. Any number of sheets and columns. Every file is checked. |
| **Reference Folder** | Recommended / plan values. Any names. Several files (2, 3, 4…). Every file is analyzed against the Input Folder. |
| **Output Folder** | All inconsistency reports. |

Files stay on this PC. There is no upload and no file-size limit from the app.

## Windows app

Download [`packages/ParameterAudit_Windows.rar`](packages/ParameterAudit_Windows.rar), extract the folder, then run `ParameterAudit.exe`.

The extracted folder already contains `Input`, `Reference`, and `Output`. Drop files in, then Generate Report — or Browse this PC to other folders.

Windows Defender may still warn because the app is unsigned. Choose **More info → Run anyway**, or add the extracted folder as an exclusion. Use the extracted **folder** (not a single packed exe).

To rebuild locally:

```bat
build_exe.bat
```

Then run `dist\ParameterAudit\ParameterAudit.exe`.

Command line (local folders):

```bash
python3 scripts/compare_reference_parameters.py --input-folder "./input" --reference-folder "./reference" --output-folder "./reports"
```

## Folder drop (no GUI)

1. Copy dumps into `input/`.
2. Copy reference workbooks into `reference/`.
3. Run `./run_audit.sh` or `run_audit.bat`.

Latest copies:

- `reports/latest/Parameter_Inconsistency_Report.xlsx`
- `reports/run_history.csv`

## Matching rules

- Input sheet names that match an MO / MML Object name are treated as that object.
- Huawei dumps with a `MAPPING DEF` sheet are mapped by MOC and attribute.
- Other workbooks are matched by sheet name and column name.
- Every reference parameter is searched in **every** input file.

## Limits (note)

Microsoft Excel allows **1,048,576 rows** and **16,384 columns** per sheet. This tool does not add a lower cap on files, sheets, or columns. Very large dumps use more RAM and take longer. Excel 97-2003 `.xls` is not read; save as `.xlsx`.

## Report contents

1. Overall report
2. All parameter-wise report (function wise)
3. Sheet-wise report
4. Final summary

## Sample result (15 Sep 2026 dumps)

- `reports/Parameter_Inconsistency_Report_15Sep26.xlsx` ([download](https://github.com/miles4482/Inconsistency-Report-15SeP/raw/cursor/parameter-inconsistency-report-0dac/reports/Parameter_Inconsistency_Report_15Sep26.xlsx))
- `reports/Parameter_Inconsistency_Report_15Sep26.md` ([download](https://github.com/miles4482/Inconsistency-Report-15SeP/raw/cursor/parameter-inconsistency-report-0dac/reports/Parameter_Inconsistency_Report_15Sep26.md))

Headline from the three-folder run on the 15 Sep 2026 dumps: **256** parameters, **79** inconsistent (5 full, 74 mixed), **85** consistent, **92** no recommend, **0** not found. Auditable rate **48.2%**.
