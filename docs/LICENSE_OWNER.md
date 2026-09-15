# Owner: issuing and extending licenses

Default license period is **7 days**. You can extend any license at any time.

1. Keep `secrets/parameter_audit_private.key` (or a copy next to `ParameterAudit.exe`) **secret**.
2. Issue:

```bash
python3 scripts/issue_license.py --to "Name or company" --days 7 -o Name.lic
```

3. Send `Name.lic` to the user. They copy it next to `ParameterAudit.exe` as `ParameterAudit.lic`.
4. Extend (adds 7 more days from the current expiry, or from today if already expired):

```bash
python3 scripts/issue_license.py --extend Name.lic --days 7
python3 scripts/issue_license.py --extend Name.lic --until 2026-12-31
```

5. Send the updated `.lic` file. The app will not generate reports with a missing, expired, or forged license.

GUI: copy the private key next to the exe to show **License Admin**.
