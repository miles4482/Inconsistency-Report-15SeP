#!/usr/bin/env python3
"""Signed license check and issuance for ParameterAudit.

The app embeds only the public key. Licenses are Ed25519-signed JSON files.
Default validity is 7 days. The owner extends by re-signing with the private key.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization


PRODUCT = "ParameterAudit"
LICENSE_VERSION = 1
DEFAULT_LICENSE_DAYS = 7
PUBLIC_KEY_HEX = "6548084c272904e8302919e2d65820864237cee65d509f4589b3f8b0f9f19fc9"
LICENSE_FILENAMES = (
    "ParameterAudit.lic",
    "ParameterAudit.json",
    "ParameterAudit.txt",
    "ParameterAudit.lic.txt",
    "license.lic",
    "license.json",
    "license.txt",
)
LICENSE_SUFFIXES = {".lic", ".json", ".txt"}
SKIP_LICENSE_NAMES = {"readme.txt", "how_to_use.txt", "readme.md"}
PRIVATE_KEY_FILENAMES = ("parameter_audit_private.key", "ParameterAudit.key")
CLOCK_SKEW = timedelta(hours=24)


class LicenseError(Exception):
    """Raised when the app must not run."""


@dataclass
class LicenseInfo:
    path: Path | None
    license_id: str
    issued_to: str
    issued_at: datetime
    expires_at: datetime
    active: bool
    message: str
    payload: dict

    @property
    def days_remaining(self) -> int:
        now = _utcnow()
        if self.expires_at <= now:
            return 0
        return max(0, int((self.expires_at - now).total_seconds() // 86400))


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _parse_dt(value) -> datetime:
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _fmt_dt(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def runtime_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _load_hex_key(text: str) -> bytes:
    cleaned = "".join(line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#"))
    cleaned = cleaned.replace(" ", "")
    return bytes.fromhex(cleaned)


def public_key() -> Ed25519PublicKey:
    return Ed25519PublicKey.from_public_bytes(bytes.fromhex(PUBLIC_KEY_HEX))


def load_private_key(path: Path | None = None) -> Ed25519PrivateKey:
    found = Path(path) if path else find_private_key_path()
    if found is None:
        raise LicenseError(
            "License private key not found. Keep parameter_audit_private.key in secrets/ "
            "or next to ParameterAudit.exe (owner only)."
        )
    raw = _load_hex_key(Path(found).read_text(encoding="utf-8"))
    if len(raw) != 32:
        raise LicenseError(f"Private key must be 32 bytes, got {len(raw)} from {found}")
    return Ed25519PrivateKey.from_private_bytes(raw)


def find_private_key_path() -> Path | None:
    env = os.environ.get("PARAMETER_AUDIT_PRIVATE_KEY", "").strip()
    candidates = []
    if env:
        candidates.append(Path(env).expanduser())
    root = runtime_root()
    home = Path.home() / ".parameter_audit"
    for folder in (root, root / "secrets", root / "LicenseGenerator", Path.cwd(), Path.cwd() / "secrets", home):
        for name in PRIVATE_KEY_FILENAMES:
            candidates.append(folder / name)
    seen = set()
    for path in candidates:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        if path.is_file():
            return path
    return None


def _license_search_folders() -> list[Path]:
    root = runtime_root()
    folders = [
        root,
        root / "License",
        Path.cwd(),
        Path.cwd() / "License",
        Path.home() / ".parameter_audit",
    ]
    # Generator and audit apps may sit in sibling folders after extract.
    parent = root.parent
    folders.extend([parent, parent / "ParameterAudit", parent / "LicenseGenerator"])
    unique = []
    seen = set()
    for folder in folders:
        try:
            key = folder.resolve()
        except OSError:
            key = folder
        if key in seen:
            continue
        seen.add(key)
        unique.append(folder)
    return unique


def _looks_like_license_name(path: Path) -> bool:
    name = path.name.lower()
    if name in SKIP_LICENSE_NAMES:
        return False
    if path.suffix.lower() not in LICENSE_SUFFIXES:
        return False
    if name in {n.lower() for n in LICENSE_FILENAMES}:
        return True
    return "license" in name or "parameteraudit" in name or name.startswith("owner_")


def iter_license_candidates(explicit: Path | None = None) -> list[Path]:
    ordered = []
    seen = set()

    def add(path: Path | None):
        if path is None:
            return
        path = Path(path).expanduser()
        if not path.is_file():
            return
        key = str(path.resolve()) if path.exists() else str(path)
        if key in seen:
            return
        seen.add(key)
        ordered.append(path)

    if explicit:
        add(Path(explicit))
        return ordered
    env = os.environ.get("PARAMETER_AUDIT_LICENSE", "").strip()
    if env:
        add(Path(env))
    for folder in _license_search_folders():
        if not folder.exists() or not folder.is_dir():
            continue
        for name in LICENSE_FILENAMES:
            add(folder / name)
        try:
            extra = sorted(folder.iterdir(), key=lambda p: p.name.lower())
        except OSError:
            extra = []
        for path in extra:
            if path.is_file() and _looks_like_license_name(path):
                add(path)
    return ordered


def find_license_path(explicit: Path | None = None) -> Path | None:
    last_existing = None
    for path in iter_license_candidates(explicit):
        last_existing = path
        try:
            verify_license_file(path, update_clock=False)
            return path
        except LicenseError:
            continue
    return last_existing


def read_license_text(path: Path) -> str:
    raw = Path(path).read_bytes()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16")
    encodings = ("utf-8-sig", "utf-8", "utf-16", "utf-16-le", "cp1252")
    for enc in encodings:
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def parse_license_json(text: str) -> dict:
    cleaned = text.strip().lstrip("\ufeff")
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        cleaned = cleaned[start : end + 1]
    return json.loads(cleaned)


def _canonical_payload(data: dict) -> bytes:
    body = {k: v for k, v in data.items() if k != "signature"}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _state_path() -> Path:
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
        folder = base / "ParameterAudit"
    else:
        folder = Path.home() / ".parameter_audit"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "license_state.json"


def _check_clock(now: datetime) -> None:
    """Record last seen time. Do not reject the license if the PC clock shifted."""
    path = _state_path()
    last = None
    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            last = _parse_dt(payload.get("last_seen"))
        except Exception:
            last = None
    stamp = now
    if last is not None and last > now + CLOCK_SKEW:
        stamp = last
    elif last is not None and last > now:
        stamp = last
    path.write_text(json.dumps({"last_seen": _fmt_dt(stamp)}, indent=2) + "\n", encoding="utf-8")


def verify_license_file(path: Path, update_clock: bool = True) -> LicenseInfo:
    try:
        data = parse_license_json(read_license_text(path))
    except Exception as exc:
        raise LicenseError(f"License file is not valid JSON: {path.name}") from exc
    signature = data.get("signature")
    if not signature:
        raise LicenseError("License file has no signature.")
    if data.get("product") != PRODUCT:
        raise LicenseError("License is not for ParameterAudit.")
    try:
        public_key().verify(bytes.fromhex(str(signature)), _canonical_payload(data))
    except (InvalidSignature, ValueError) as exc:
        raise LicenseError("License signature is invalid. This license was not issued for this software.") from exc
    issued_to = str(data.get("issued_to") or "").strip() or "(unnamed)"
    issued_at = _parse_dt(data.get("issued_at"))
    expires_at = _parse_dt(data.get("expires_at"))
    now = _utcnow()
    if update_clock:
        _check_clock(now)
    if now + CLOCK_SKEW < issued_at:
        raise LicenseError(f"License is not valid until {issued_at.date().isoformat()}.")
    if now > expires_at:
        raise LicenseError(
            f"License expired on {expires_at.date().isoformat()} (issued to {issued_to}). "
            "Ask the issuer to extend it."
        )
    remaining = expires_at - now
    days = max(0, remaining.days)
    hours = int(remaining.seconds // 3600)
    return LicenseInfo(
        path=Path(path).resolve(),
        license_id=str(data.get("license_id") or ""),
        issued_to=issued_to,
        issued_at=issued_at,
        expires_at=expires_at,
        active=True,
        message=f"Licensed to {issued_to} until {expires_at.date().isoformat()} ({days}d {hours}h remaining).",
        payload=data,
    )


def license_status(explicit: Path | None = None) -> LicenseInfo:
    last_error = "No license file found. Put a .lic / .json / .txt license next to ParameterAudit.exe, or click Load license."
    last_path = None
    for path in iter_license_candidates(explicit):
        last_path = path
        try:
            return verify_license_file(path)
        except LicenseError as exc:
            last_error = str(exc)
            continue
    return LicenseInfo(
        path=last_path,
        license_id="",
        issued_to="",
        issued_at=_utcnow(),
        expires_at=_utcnow(),
        active=False,
        message=last_error,
        payload={},
    )


def install_license(source: Path, dest_dir: Path | None = None) -> LicenseInfo:
    """Verify any license file and save a clean ParameterAudit.lic/.json/.txt next to the app."""
    info = verify_license_file(source)
    dest_dir = Path(dest_dir) if dest_dir else runtime_root()
    write_license_bundle(info.payload, dest_dir)
    info.path = (dest_dir / "ParameterAudit.lic").resolve()
    return info


def write_license_bundle(payload: dict, dest_dir: Path, stem: str = "ParameterAudit") -> Path:
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2) + "\n"
    for suffix in (".lic", ".json", ".txt"):
        (dest_dir / f"{stem}{suffix}").write_text(text, encoding="utf-8", newline="\n")
    return dest_dir / f"{stem}.lic"


def require_active_license(explicit: Path | None = None) -> LicenseInfo:
    info = license_status(explicit)
    if not info.active:
        raise LicenseError(info.message)
    return info


def issue_license(
    issued_to: str,
    days: int = DEFAULT_LICENSE_DAYS,
    expires_at: datetime | None = None,
    private_key_path: Path | None = None,
    license_id: str | None = None,
    issued_at: datetime | None = None,
) -> dict:
    if days is None or days <= 0:
        days = DEFAULT_LICENSE_DAYS
    now = _utcnow().replace(microsecond=0)
    issued_at = issued_at or now
    if expires_at is None:
        expires_at = now + timedelta(days=days)
    payload = {
        "v": LICENSE_VERSION,
        "product": PRODUCT,
        "license_id": license_id or str(uuid.uuid4()),
        "issued_to": (issued_to or "").strip() or "licensed user",
        "issued_at": _fmt_dt(issued_at),
        "expires_at": _fmt_dt(expires_at),
        "default_period_days": DEFAULT_LICENSE_DAYS,
    }
    key = load_private_key(private_key_path)
    payload["signature"] = key.sign(_canonical_payload(payload)).hex()
    return payload


def extend_license(
    path: Path,
    days: int | None = None,
    until: datetime | None = None,
    private_key_path: Path | None = None,
) -> dict:
    data = parse_license_json(read_license_text(path))
    current_expiry = _parse_dt(data.get("expires_at"))
    now = _utcnow().replace(microsecond=0)
    if until is not None:
        new_expiry = until
    else:
        period = days if days and days > 0 else DEFAULT_LICENSE_DAYS
        base = current_expiry if current_expiry > now else now
        new_expiry = base + timedelta(days=period)
    if new_expiry <= now:
        raise LicenseError("New expiration must be in the future.")
    issued_at = _parse_dt(data.get("issued_at")) if data.get("issued_at") else now
    payload = issue_license(
        issued_to=str(data.get("issued_to") or "licensed user"),
        expires_at=new_expiry,
        private_key_path=private_key_path,
        license_id=str(data.get("license_id") or uuid.uuid4()),
        issued_at=issued_at,
    )
    payload["extended_at"] = _fmt_dt(now)
    payload["previous_expires_at"] = data.get("expires_at")
    # Re-sign after adding extension metadata.
    key = load_private_key(private_key_path)
    payload["signature"] = key.sign(_canonical_payload(payload)).hex()
    return payload


def write_license(payload: dict, dest: Path) -> Path:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return dest


def _parse_until(text: str) -> datetime:
    text = text.strip()
    if "T" in text or " " in text:
        return _parse_dt(text.replace(" ", "T"))
    day = datetime.strptime(text, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return day.replace(hour=23, minute=59, second=59)


def build_issuer_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Issue or extend a ParameterAudit license (owner only).")
    parser.add_argument("--to", dest="issued_to", help="Person or company the license is issued to")
    parser.add_argument("--days", type=int, default=DEFAULT_LICENSE_DAYS, help="Validity in days (default 7)")
    parser.add_argument("--until", help="Absolute expiration YYYY-MM-DD (overrides --days for new licenses)")
    parser.add_argument("-o", "--output", type=Path, help="License file to write")
    parser.add_argument("--extend", type=Path, help="Existing license file to extend")
    parser.add_argument("--key", type=Path, help="Path to parameter_audit_private.key")
    parser.add_argument("--status", type=Path, nargs="?", const=True, help="Show license status and exit")
    return parser


def issuer_main(argv=None) -> int:
    parser = build_issuer_parser()
    args = parser.parse_args(argv)
    if args.status is not None:
        path = None if args.status is True else Path(args.status)
        info = license_status(path)
        print(info.message)
        if info.path:
            print(f"File: {info.path}")
        if info.active:
            print(f"Expires: {info.expires_at.isoformat()}")
        return 0 if info.active else 3
    try:
        until = _parse_until(args.until) if args.until else None
        if args.extend:
            payload = extend_license(args.extend, days=args.days, until=until, private_key_path=args.key)
            dest = args.output or args.extend
        else:
            payload = issue_license(
                issued_to=args.issued_to or "licensed user",
                days=args.days,
                expires_at=until,
                private_key_path=args.key,
            )
            dest = args.output or (runtime_root() / "ParameterAudit.lic")
        write_license(payload, dest)
        print(f"Wrote {dest}")
        print(f"Issued to: {payload['issued_to']}")
        print(f"Expires:   {payload['expires_at']}")
        return 0
    except LicenseError as exc:
        print(exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(issuer_main())
