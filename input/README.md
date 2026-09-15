# Drop new dumps here

For each regular audit, copy the latest files into this folder:

1. `Reference Parameter_vX.X.xlsx` (only if the baseline changed)
2. `4G_ConfigurationData_*.xlsb` or `.xlsx`
3. `5G_ConfigurationData_*.xlsb` or `.xlsx`

Then from the repo root run:

```bash
./run_audit.sh
```

Windows:

```bat
run_audit.bat
```

The tool picks the **newest matching file** from `input/` first, then the repo root.
The original dumps at the repo root still work if `input/` is empty.
