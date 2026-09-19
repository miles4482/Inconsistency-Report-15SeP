#!/usr/bin/env python3
"""License gate tests."""

from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import license_control as lic  # noqa: E402
import compare_reference_parameters as audit  # noqa: E402


def main() -> int:
    key = lic.find_private_key_path()
    assert key is not None, "private key must exist for owner tests"
    with tempfile.TemporaryDirectory() as raw:
        folder = Path(raw)
        good = folder / "good.lic"
        payload = lic.issue_license("Test User", days=7, private_key_path=key)
        lic.write_license(payload, good)
        info = lic.verify_license_file(good)
        assert info.active
        assert info.issued_to == "Test User"
        assert info.days_remaining >= 6

        status = lic.license_status(good)
        assert status.active

        expired = folder / "expired.lic"
        past = datetime.now(timezone.utc) - timedelta(days=1)
        old = lic.issue_license("Expired", expires_at=past, private_key_path=key)
        lic.write_license(old, expired)
        try:
            lic.verify_license_file(expired)
            raise SystemExit("expired license must not verify")
        except lic.LicenseError as exc:
            assert "expired" in str(exc).lower()

        tampered = folder / "tampered.lic"
        data = json.loads(good.read_text(encoding="utf-8"))
        data["issued_to"] = "Hacker"
        tampered.write_text(json.dumps(data), encoding="utf-8")
        try:
            lic.verify_license_file(tampered)
            raise SystemExit("tampered license must not verify")
        except lic.LicenseError as exc:
            assert "invalid" in str(exc).lower()

        extended = lic.extend_license(good, days=7, private_key_path=key)
        lic.write_license(extended, good)
        again = lic.verify_license_file(good)
        assert again.days_remaining >= 13

        until = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(days=30)
        dated = lic.extend_license(good, until=until, private_key_path=key)
        lic.write_license(dated, good)
        dated_info = lic.verify_license_file(good)
        assert dated_info.days_remaining >= 29

        txt = folder / "Owner_ParameterAudit_7day.txt"
        txt.write_text(good.read_text(encoding="utf-8"), encoding="utf-8")
        assert lic.verify_license_file(txt).active
        utf16 = folder / "utf16.txt"
        utf16.write_bytes(good.read_text(encoding="utf-8").encode("utf-16"))
        assert lic.verify_license_file(utf16).active
        installed = lic.install_license(txt, folder)
        assert (folder / "ParameterAudit.lic").is_file()
        assert (folder / "ParameterAudit.json").is_file()
        assert (folder / "ParameterAudit.txt").is_file()
        assert installed.active

        missing = folder / "missing.lic"
        info_missing = lic.license_status(missing)
        assert not info_missing.active

        try:
            audit.execute_folder_audit(
                output_dir=folder / "out",
                input_files=[folder / "nope.xlsx"],
                reference_files=[folder / "nope.xlsx"],
                license_file=expired,
            )
            raise SystemExit("audit must refuse expired license")
        except lic.LicenseError:
            pass

        print("license tests ok")
        print(f"sample expiry after extend-until: {dated_info.expires_at.isoformat()}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
