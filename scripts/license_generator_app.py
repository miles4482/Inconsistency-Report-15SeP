#!/usr/bin/env python3
"""Simple Windows app to generate ParameterAudit licenses.

Enter the number of days, click Generate. A license file is written next to
this app (and next to ParameterAudit.exe if that folder is found).
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import license_control as lic  # noqa: E402


def save_targets() -> list[Path]:
    root = lic.runtime_root()
    targets = [root]
    parent = root.parent
    for candidate in (
        root,
        parent,
        parent / "ParameterAudit",
        Path.cwd(),
    ):
        if (candidate / "ParameterAudit.exe").is_file() or (candidate / "parameter_audit_app.py").is_file():
            if candidate not in targets:
                targets.append(candidate)
    unique = []
    seen = set()
    for folder in targets:
        key = str(folder.resolve()) if folder.exists() else str(folder)
        if key in seen:
            continue
        seen.add(key)
        unique.append(folder)
    return unique


def generate_license(issued_to: str, days: int) -> tuple[dict, list[Path]]:
    if days <= 0:
        days = lic.DEFAULT_LICENSE_DAYS
    payload = lic.issue_license(issued_to=issued_to, days=days)
    saved = []
    for folder in save_targets():
        saved.append(lic.write_license_bundle(payload, folder))
    return payload, saved


def launch_gui():
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.title("ParameterAudit License Generator")
    root.geometry("560x340")
    root.minsize(520, 300)

    header = tk.Frame(root, bg="#1F4E79")
    header.pack(fill=tk.X)
    tk.Label(
        header,
        text="License Generator",
        fg="white",
        bg="#1F4E79",
        font=("Segoe UI", 16, "bold"),
    ).pack(anchor="w", padx=16, pady=(12, 0))
    tk.Label(
        header,
        text="Enter days, click Generate. The license is saved as ParameterAudit.lic / .json / .txt",
        fg="#D6E3F0",
        bg="#1F4E79",
        font=("Segoe UI", 10),
    ).pack(anchor="w", padx=16, pady=(0, 12))

    body = tk.Frame(root, padx=16, pady=16)
    body.pack(fill=tk.BOTH, expand=True)

    to_var = tk.StringVar(value="Owner")
    days_var = tk.StringVar(value=str(lic.DEFAULT_LICENSE_DAYS))
    status_var = tk.StringVar(
        value="Private key found." if lic.find_private_key_path() else "Put parameter_audit_private.key next to this app."
    )

    row1 = tk.Frame(body)
    row1.pack(fill=tk.X, pady=6)
    tk.Label(row1, text="Issued to:", width=14, anchor="w", font=("Segoe UI", 11)).pack(side=tk.LEFT)
    tk.Entry(row1, textvariable=to_var, font=("Segoe UI", 11)).pack(side=tk.LEFT, fill=tk.X, expand=True)

    row2 = tk.Frame(body)
    row2.pack(fill=tk.X, pady=6)
    tk.Label(row2, text="Days of license:", width=14, anchor="w", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
    days_entry = tk.Entry(row2, textvariable=days_var, width=10, font=("Segoe UI", 14, "bold"))
    days_entry.pack(side=tk.LEFT)
    tk.Label(row2, text="  (example: 7, 14, 30)", fg="#555").pack(side=tk.LEFT)

    def generate():
        try:
            days = int(str(days_var.get()).strip())
        except ValueError:
            messagebox.showerror("Days required", "Type a whole number of days, for example 7.")
            return
        if days <= 0:
            messagebox.showerror("Days required", "Days must be 1 or more.")
            return
        if not lic.find_private_key_path():
            messagebox.showerror(
                "Owner key missing",
                "Copy parameter_audit_private.key into the LicenseGenerator folder, then try again.",
            )
            return
        try:
            payload, saved = generate_license(to_var.get(), days)
        except Exception as exc:
            messagebox.showerror("Could not generate", str(exc)[:1500])
            return
        first = saved[0]
        status_var.set(
            f"{days}-day license saved. Expires {payload['expires_at'][:10]}. File: {first}"
        )
        messagebox.showinfo(
            "License generated",
            f"Days: {days}\nIssued to: {payload['issued_to']}\nExpires: {payload['expires_at']}\n\n"
            f"Saved:\n"
            + "\n".join(str(p) for p in saved)
            + "\n\nCopy ParameterAudit.lic (or .json / .txt) next to ParameterAudit.exe.",
        )

    tk.Button(
        body,
        text="Generate license",
        command=generate,
        width=22,
        bg="#1F4E79",
        fg="white",
        font=("Segoe UI", 12, "bold"),
    ).pack(pady=16)

    tk.Label(body, textvariable=status_var, wraplength=500, justify="left", anchor="w").pack(fill=tk.X)
    tk.Button(body, text="Open this folder", command=lambda: _open(lic.runtime_root()), width=18).pack(
        anchor="w", pady=(12, 0)
    )
    days_entry.focus_set()
    root.mainloop()


def _open(path: Path):
    import os
    import subprocess

    path = Path(path)
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv:
        return lic.issuer_main(argv)
    launch_gui()
    return 0


if __name__ == "__main__":
    sys.exit(main())
