# Parameter Inconsistency Report (15 Sep 2026)

Compare **Reference Parameter_v1.0** against live 4G and 5G configuration dumps.

## Input files

- `Reference Parameter_v1.0.xlsx` — baseline recommend values (`NR Performance` = 5G, `NR Anchor` = 4G)
- `4G_ConfigurationData_15Sep26.xlsb`
- `5G_ConfigurationData_15Sep26.xlsb`

## Output

- `reports/Parameter_Inconsistency_Report_15Sep26.xlsx` — workbook with Overall, All-parameter, Sheet-wise, and Final Summary sheets
- `reports/Parameter_Inconsistency_Report_15Sep26.md` — same content in Markdown

## How to regenerate

```bash
python3 scripts/compare_reference_parameters.py
```

Requires `openpyxl` and `pyxlsb`.
