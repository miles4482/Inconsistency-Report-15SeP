#!/usr/bin/env python3
"""Owner tool: issue a new ParameterAudit license or extend an existing one.

Default period is 7 days. Keep parameter_audit_private.key private.

Examples:
    python scripts/issue_license.py --to "Site A" --days 7 -o SiteA.lic
    python scripts/issue_license.py --extend SiteA.lic --days 7
    python scripts/issue_license.py --extend SiteA.lic --until 2026-12-31
    python scripts/issue_license.py --status
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import license_control as lic  # noqa: E402


if __name__ == "__main__":
    sys.exit(lic.issuer_main())
