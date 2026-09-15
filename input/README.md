# Input Folder

Put configuration dumps here. They are used for comparing.

- Any file names (4G dump, 5G dump, 2G dump, or any other name)
- More than one file; no file-count limit
- Any number of sheets; any number of columns
- Sheet names that match an MO / MML Object are treated as that object
- Every file is checked against every reference file

Supported: `.xlsx` `.xlsb` `.xlsm`

Then from the repo root:

```bash
./run_audit.sh
```

Windows:

```bat
run_audit.bat
```
