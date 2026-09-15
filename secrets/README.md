# Owner secrets (do not commit keys)

Put `parameter_audit_private.key` in this folder. It is the only file that can
issue or extend licenses. The public key is already embedded in the app.

The private key is gitignored. Store a backup somewhere only you can access.

Issue or extend:

```bash
python scripts/issue_license.py --to "Name" --days 7 -o ParameterAudit.lic
python scripts/issue_license.py --extend ParameterAudit.lic --days 7
python scripts/issue_license.py --extend ParameterAudit.lic --until 2026-12-31
```

You can also copy the private key next to `ParameterAudit.exe`. The app then
shows a License Admin panel so you can issue and extend without the command line.
