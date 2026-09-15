# Parameter Inconsistency Audit

Compare a **Reference Parameter** workbook with live **4G** and **5G** configuration dumps.
Use this whenever new configuration exports arrive.

## Regular run

1. Copy the new dumps into `input/` (keep the reference file there too if it changed).
2. Run one command:

```bash
./run_audit.sh
```

Windows:

```bat
run_audit.bat
```

3. Open the newest report:

- `reports/latest/Parameter_Inconsistency_Report.xlsx`
- `reports/latest/Parameter_Inconsistency_Report.md`
- `reports/latest/all_parameters.csv`
- `reports/run_history.csv` — one row per run, for trend tracking

Each run is also kept under `reports/runs/<timestamp>/`.

## What the tool expects

| Role | Sheets / files | Network |
|---|---|---|
| Baseline | `Reference Parameter*.xlsx` sheets `NR Performance`, `NR Anchor` | 5G / 4G |
| 4G dump | `4G_ConfigurationData*.xlsb` or `.xlsx` | compared with `NR Anchor` |
| 5G dump | `5G_ConfigurationData*.xlsb` or `.xlsx` | compared with `NR Performance` |

Files are auto-detected from `input/` first, then the repo root. The newest matching file wins.

## Optional arguments

```bash
# Show which files would be used
./run_audit.sh --list-inputs

# Point at explicit files
./run_audit.sh --reference "Reference Parameter_v1.0.xlsx" \
  --config-4g 4G_ConfigurationData_15Sep26.xlsb \
  --config-5g 5G_ConfigurationData_15Sep26.xlsb

# Fail (exit code 1) if any auditable parameter is inconsistent
./run_audit.sh --fail-on-inconsistent
```

## First-time setup

```bash
python3 -m pip install -r requirements.txt
```

`run_audit.sh` / `run_audit.bat` install the packages automatically if they are missing.

## Report contents

1. Overall report — counts from both sheets, function-wise summary, material gaps
2. All parameter-wise report — every parameter by function
3. Sheet-wise report — NR Performance (5G) and NR Anchor (4G)
4. Final summary

## Sample result (15 Sep 2026 dumps)

The first audit against the files in this repo is saved as:

- `reports/Parameter_Inconsistency_Report_15Sep26.xlsx`
- `reports/Parameter_Inconsistency_Report_15Sep26.md`
