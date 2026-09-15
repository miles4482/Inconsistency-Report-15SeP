# Parameter Inconsistency Audit

One tool: **select several input files → get the inconsistency report**.

## EXE / desktop tool

1. Build once:

Windows:
```bat
build_exe.bat
```

Linux:
```bash
./build_exe.sh
```

2. Run `dist/ParameterAudit.exe` (Windows) or `dist/ParameterAudit` (Linux).

3. Click **Select input files…** and pick all of these together (any order):
   - Reference Parameter workbook
   - 4G configuration dump
   - 5G configuration dump

4. Click **Generate Report**. Output is written to the chosen folder (`reports/` by default):
   - `Parameter_Inconsistency_Report.xlsx`
   - `all_parameters.csv`
   - `Parameter_Inconsistency_Report.md`

Command line (same tool, several files then output folder):

```bash
./dist/ParameterAudit \
  "Reference Parameter_v1.0.xlsx" \
  4G_ConfigurationData_15Sep26.xlsb \
  5G_ConfigurationData_15Sep26.xlsb \
  -o reports
```

Or without building an exe:

```bash
python3 scripts/parameter_audit_app.py
python3 scripts/parameter_audit_app.py file1.xlsx file2.xlsb file3.xlsb -o reports
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
