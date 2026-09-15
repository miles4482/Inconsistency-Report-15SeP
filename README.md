# Parameter Inconsistency Audit

One tool: **select files or a folder on your PC → save the report to a folder on your PC**.
Input and output stay local. There is no upload and no file-size limit.

## Windows app

Download `packages/ParameterAudit_Windows.rar`, extract the folder, then run `ParameterAudit.exe`.

In the app:

1. **Select files from this PC** or **Select input folder from this PC**
   (Reference + 4G dump + 5G dump, any size, any drive).
2. **Browse this PC** for the output folder (default: `Documents\ParameterAudit_Reports`).
3. **Generate Report**.

Windows Defender may still warn because the app is unsigned. Choose **More info → Run anyway**, or add the extracted folder as an exclusion. Use the extracted **folder** (not a single packed exe) — that is less often blocked.

To rebuild locally:

```bat
build_exe.bat
```

Then run `dist\ParameterAudit\ParameterAudit.exe`.

Command line (local files, local output):

```bash
python3 scripts/parameter_audit_app.py file1.xlsx file2.xlsb file3.xlsb -o "C:\Users\You\Documents\ParameterAudit_Reports"
```

## Folder drop (no GUI)

1. Copy new dumps into `input/`.
2. Run `./run_audit.sh` or `run_audit.bat`.

Latest copies:

- `reports/latest/Parameter_Inconsistency_Report.xlsx`
- `reports/run_history.csv`

## What the tool expects

| Role | Typical file | Compared with |
|---|---|---|
| Baseline | `Reference Parameter*.xlsx` (`NR Performance`, `NR Anchor`) | recommend values |
| 4G dump | `4G_ConfigurationData*.xlsb` / `.xlsx` | NR Anchor |
| 5G dump | `5G_ConfigurationData*.xlsb` / `.xlsx` | NR Performance |

Files can be named differently; the tool also looks inside the workbook if needed.

## Report contents

1. Overall report
2. All parameter-wise report (function wise)
3. Sheet-wise report
4. Final summary

## Sample result (15 Sep 2026 dumps)

- `reports/Parameter_Inconsistency_Report_15Sep26.xlsx`
- `reports/Parameter_Inconsistency_Report_15Sep26.md`
