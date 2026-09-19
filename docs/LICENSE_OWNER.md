# Owner: generate and load licenses

## Windows app (easiest)

1. Open `LicenseGenerator.exe`.
2. Type **Days of license** (example: 7).
3. Click **Generate license**.
4. Copy `ParameterAudit.lic` or `ParameterAudit.txt` or `ParameterAudit.json` next to `ParameterAudit.exe`.

Keep `parameter_audit_private.key` in the LicenseGenerator folder.

## ParameterAudit load (no rename needed)

Drop any of these next to `ParameterAudit.exe`: `.lic`, `.json`, `.txt`.
Or click **Load license file…** and pick the downloaded file.

## Command line

```bash
python3 scripts/issue_license.py --to "Name" --days 7 -o Name.lic
python3 scripts/issue_license.py --extend Name.lic --days 7
python3 scripts/license_generator_app.py
```
