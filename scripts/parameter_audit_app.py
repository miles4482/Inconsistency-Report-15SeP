#!/usr/bin/env python3
"""Parameter Inconsistency Audit tool.

Three local folders on this PC (no upload, no size limit):
    Input Folder      configuration dumps used for comparing
    Reference Folder  recommended / plan values
    Output Folder     inconsistency reports
"""

from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
import traceback
from pathlib import Path

try:
    import tkinter  # bundled by PyInstaller
except Exception:
    tkinter = None

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import compare_reference_parameters as audit  # noqa: E402
import license_control as license_mod  # noqa: E402


def open_path(path: Path):
    path = Path(path)
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


def app_root() -> Path:
    return audit.ROOT


def ensure_default_folders() -> dict[str, Path]:
    root = app_root()
    folders = {
        "input": root / "Input" if (root / "Input").is_dir() else root / "input",
        "reference": root / "Reference" if (root / "Reference").is_dir() else root / "reference",
        "output": root / "Output" if (root / "Output").is_dir() else root / "reports",
    }
    if getattr(sys, "frozen", False):
        folders = {
            "input": root / "Input",
            "reference": root / "Reference",
            "output": root / "Output",
        }
        for path in folders.values():
            path.mkdir(parents=True, exist_ok=True)
    else:
        for path in folders.values():
            path.mkdir(parents=True, exist_ok=True)
    audit.ensure_rat_input_folders(folders["input"])
    return folders


def format_size(path: Path) -> str:
    try:
        n = path.stat().st_size
    except OSError:
        return "?"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            if unit == "B":
                return f"{n} {unit}"
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def launch_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox

    defaults = ensure_default_folders()
    root = tk.Tk()
    root.title("Parameter Inconsistency Audit")
    root.geometry("960x920")
    root.minsize(860, 760)

    input_var = tk.StringVar(value=str(defaults["input"]))
    reference_var = tk.StringVar(value=str(defaults["reference"]))
    output_var = tk.StringVar(value=str(defaults["output"]))
    license_var = tk.StringVar(value="Checking license…")
    issued_to_var = tk.StringVar(value="licensed user")
    days_var = tk.StringVar(value=str(license_mod.DEFAULT_LICENSE_DAYS))
    until_var = tk.StringVar(value="")
    status_var = tk.StringVar(
        value="Select Input Folder (with 5G/4G/3G/2G), Reference Folder, and Output Folder. Files are not uploaded."
    )
    last_report = {"path": None}
    license_state = {"info": license_mod.license_status(), "path": None}

    def current_license_path() -> Path | None:
        info = license_state["info"]
        if info and info.path:
            return Path(info.path)
        found = license_mod.find_license_path()
        return found

    def apply_license_ui():
        info = license_state["info"]
        license_var.set(info.message)
        if info.active:
            license_label.config(fg="#1B5E20", bg="#E8F5E9")
            generate_btn.config(state=tk.NORMAL)
        else:
            license_label.config(fg="#B71C1C", bg="#FFEBEE")
            generate_btn.config(state=tk.DISABLED)
        if info.active and info.issued_to:
            issued_to_var.set(info.issued_to)

    def load_license_file(path: Path | None = None):
        if path is None:
            chosen = filedialog.askopenfilename(
                title="Select license file (.lic / .json / .txt)",
                filetypes=[
                    ("License files", "*.lic *.json *.txt"),
                    ("All files", "*.*"),
                ],
            )
            if not chosen:
                return
            path = Path(chosen)
        try:
            info = license_mod.install_license(path, app_root())
            license_state["info"] = info
            license_state["path"] = info.path
            apply_license_ui()
            messagebox.showinfo("License loaded", info.message)
        except Exception as exc:
            license_state["info"] = license_mod.license_status(path)
            apply_license_ui()
            messagebox.showerror("License not valid", str(exc)[:1500])

    def refresh_license():
        license_state["info"] = license_mod.license_status()
        apply_license_ui()

    def issue_new_license():
        try:
            days = int(days_var.get() or license_mod.DEFAULT_LICENSE_DAYS)
            until = until_var.get().strip()
            payload = license_mod.issue_license(
                issued_to=issued_to_var.get(),
                days=days,
                expires_at=license_mod._parse_until(until) if until else None,
            )
            dest = Path(
                filedialog.asksaveasfilename(
                    title="Save new license",
                    defaultextension=".lic",
                    initialfile="ParameterAudit.lic",
                    filetypes=[("License files", "*.lic"), ("All files", "*.*")],
                )
                or ""
            )
            if not dest:
                return
            license_mod.write_license(payload, dest)
            app_copy = app_root() / "ParameterAudit.lic"
            if dest.resolve() != app_copy.resolve():
                license_mod.write_license(payload, app_copy)
            license_state["info"] = license_mod.verify_license_file(dest)
            apply_license_ui()
            messagebox.showinfo(
                "License issued",
                f"Saved {dest}\nIssued to {payload['issued_to']}\nExpires {payload['expires_at']}",
            )
        except Exception as exc:
            messagebox.showerror("Could not issue license", str(exc)[:1500])

    def extend_current_license():
        path = current_license_path()
        if path is None:
            messagebox.showerror("No license", "Load or issue a license first, then extend it.")
            return
        try:
            days = int(days_var.get() or license_mod.DEFAULT_LICENSE_DAYS)
            until = until_var.get().strip()
            payload = license_mod.extend_license(
                path,
                days=days,
                until=license_mod._parse_until(until) if until else None,
            )
            dest = path
            license_mod.write_license(payload, dest)
            app_copy = app_root() / "ParameterAudit.lic"
            license_mod.write_license(payload, app_copy)
            license_state["info"] = license_mod.verify_license_file(app_copy)
            apply_license_ui()
            messagebox.showinfo(
                "License extended",
                f"Updated {app_copy}\nIssued to {payload['issued_to']}\nNew expiry {payload['expires_at']}",
            )
        except Exception as exc:
            messagebox.showerror("Could not extend license", str(exc)[:1500])

    rat_vars = {rat: tk.BooleanVar(value=True) for rat in audit.smart.RAT_FOLDERS}

    def selected_rats():
        return [rat for rat, var in rat_vars.items() if var.get()]

    def folder_listing(folder_text: str, rats=None) -> list:
        folder = Path(folder_text).expanduser()
        if rats is None:
            return audit.list_workbooks(folder)
        return audit.list_workbooks(folder, rats=rats, use_rat_subfolders=True)

    def refresh_lists():
        input_list.delete(0, tk.END)
        ref_list.delete(0, tk.END)
        rats = selected_rats()
        inputs = folder_listing(input_var.get(), rats=rats)
        refs = folder_listing(reference_var.get())
        if inputs:
            for path in inputs:
                label = audit.workbook_rel_label(path, Path(input_var.get()))
                input_list.insert(tk.END, f"{format_size(path):>10}   {label}")
        else:
            if rats:
                input_list.insert(
                    tk.END,
                    "(no dumps in selected folders: " + ", ".join(f"Input/{r}" for r in rats) + ")",
                )
            else:
                input_list.insert(tk.END, "(select 5G / 4G / 3G / 2G to search those Input folders)")
        if refs:
            for path in refs:
                ref_list.insert(tk.END, f"{format_size(path):>10}   {path.name}")
        else:
            ref_list.insert(tk.END, "(no .xlsx / .xlsb / .xlsm files yet)")
        status_var.set(
            f"Networks: {', '.join(rats) or '(none)'}  |  Input: {len(inputs)} file(s)  |  "
            f"Reference: {len(refs)} file(s)  |  Only selected Input subfolders are searched."
        )
        return inputs, refs

    def pick_folder(var: tk.StringVar, title: str):
        folder = filedialog.askdirectory(
            title=title,
            initialdir=var.get() or str(Path.home()),
        )
        if folder:
            var.set(folder)
            refresh_lists()

    def set_buttons(state):
        for btn in action_buttons:
            btn.config(state=state)

    def generate():
        refresh_license()
        if not license_state["info"].active:
            messagebox.showerror(
                "License required",
                license_state["info"].message
                + "\n\nThis software cannot run without an active license.",
            )
            return
        inputs, refs = refresh_lists()
        rats = selected_rats()
        if not rats:
            messagebox.showerror(
                "Select a network",
                "Tick at least one of 5G / 4G / 3G / 2G.\n"
                "The tool searches only those folders inside Input.",
            )
            return
        if len(inputs) < 1:
            messagebox.showerror(
                "Input Folder empty",
                "Put dumps in the selected network folders inside Input:\n"
                "  Input\\5G   Input\\4G   Input\\3G   Input\\2G\n"
                f"Currently selected: {', '.join(rats)}",
            )
            return
        if len(refs) < 1:
            messagebox.showerror(
                "Reference Folder empty",
                "Put at least one recommended/plan-value workbook in the Reference Folder.\n"
                "Every file in that folder is treated as a reference.",
            )
            return
        output_dir = Path(output_var.get()).expanduser()
        if not str(output_var.get()).strip():
            messagebox.showerror("Missing Output Folder", "Select an Output Folder on this PC.")
            return
        output_dir.mkdir(parents=True, exist_ok=True)
        set_buttons(tk.DISABLED)
        log_box.delete("1.0", tk.END)
        log_box.insert(
            tk.END,
            "Reading folders from your PC (not uploaded).\n"
            f"Networks: {', '.join(rats)}\n"
            f"Input Folder ({len(inputs)} files): {input_var.get()}\n"
            + "".join(f"  - {audit.workbook_rel_label(p, Path(input_var.get()))}\n" for p in inputs)
            + f"Reference Folder ({len(refs)} files): {reference_var.get()}\n"
            + "".join(f"  - {p.name}\n" for p in refs)
            + f"Output Folder: {output_dir}\n\n",
        )
        status_var.set("Running audit on local folders...")
        messages: queue.Queue = queue.Queue()

        def progress(msg: str):
            messages.put(("log", str(msg)))

        def worker():
            try:
                run, summary, _extras = audit.execute_folder_audit(
                    output_dir=output_dir,
                    input_folder=Path(input_var.get()),
                    reference_folder=Path(reference_var.get()),
                    progress=progress,
                    license_file=current_license_path(),
                    rats=rats,
                )
                messages.put(("done", run, summary))
            except Exception as exc:
                messages.put(("error", f"{exc}\n\n{traceback.format_exc()}"))

        def pump():
            try:
                while True:
                    item = messages.get_nowait()
                    if item[0] == "log":
                        log_box.insert(tk.END, item[1] + "\n")
                        log_box.see(tk.END)
                    elif item[0] == "error":
                        set_buttons(tk.NORMAL)
                        apply_license_ui()
                        status_var.set("Audit failed.")
                        messagebox.showerror("Audit failed", item[1][:1500])
                        return
                    elif item[0] == "done":
                        run, summary = item[1], item[2]
                        last_report["path"] = run.out_xlsx
                        set_buttons(tk.NORMAL)
                        apply_license_ui()
                        open_btn.config(state=tk.NORMAL)
                        all_c = summary["ALL"]
                        status_var.set(
                            f"Done. Saved on this PC: {run.out_xlsx}  "
                            f"(inconsistent {all_c['inconsistent']}/{all_c['total']})"
                        )
                        if messagebox.askyesno(
                            "Report saved on this PC",
                            f"Inconsistent parameters: {all_c['inconsistent']} of {all_c['total']}\n\n"
                            f"Saved to:\n{run.out_xlsx}\n\nOpen it now?",
                        ):
                            open_path(run.out_xlsx)
                        return
            except queue.Empty:
                root.after(150, pump)

        threading.Thread(target=worker, daemon=True).start()
        root.after(150, pump)

    def open_report():
        if last_report["path"] and Path(last_report["path"]).exists():
            open_path(last_report["path"])
        else:
            messagebox.showinfo("No report yet", "Generate a report first.")

    header = tk.Frame(root, bg="#1F4E79", height=88)
    header.pack(fill=tk.X)
    tk.Label(
        header,
        text="Parameter Inconsistency Audit",
        fg="white",
        bg="#1F4E79",
        font=("Segoe UI", 16, "bold"),
    ).pack(anchor="w", padx=16, pady=(12, 0))
    tk.Label(
        header,
        text="Three folders on THIS PC: Input (5G/4G/3G/2G dumps) · Reference (plan values) · Output (reports). No upload.",
        fg="#D6E3F0",
        bg="#1F4E79",
        font=("Segoe UI", 10),
    ).pack(anchor="w", padx=16, pady=(0, 12))

    lic_frame = tk.Frame(root, bg="#FFEBEE", padx=16, pady=8)
    lic_frame.pack(fill=tk.X)
    license_label = tk.Label(
        lic_frame,
        textvariable=license_var,
        anchor="w",
        justify="left",
        wraplength=700,
        bg="#FFEBEE",
        fg="#B71C1C",
        font=("Segoe UI", 10, "bold"),
    )
    license_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    tk.Button(lic_frame, text="Load license file…", command=lambda: load_license_file(), width=18).pack(
        side=tk.RIGHT, padx=(8, 0)
    )
    tk.Button(lic_frame, text="Refresh", command=refresh_license, width=10).pack(side=tk.RIGHT)

    if license_mod.find_private_key_path():
        admin = tk.LabelFrame(root, text="License Admin (owner — private key detected)", padx=12, pady=8)
        admin.pack(fill=tk.X, padx=16, pady=(8, 0))
        row = tk.Frame(admin)
        row.pack(fill=tk.X)
        tk.Label(row, text="Issued to:").pack(side=tk.LEFT)
        tk.Entry(row, textvariable=issued_to_var, width=24).pack(side=tk.LEFT, padx=(4, 12))
        tk.Label(row, text="Days (default 7):").pack(side=tk.LEFT)
        tk.Entry(row, textvariable=days_var, width=6).pack(side=tk.LEFT, padx=(4, 12))
        tk.Label(row, text="Or until YYYY-MM-DD:").pack(side=tk.LEFT)
        tk.Entry(row, textvariable=until_var, width=12).pack(side=tk.LEFT, padx=(4, 12))
        tk.Button(row, text="Issue new license…", command=issue_new_license, width=18).pack(side=tk.LEFT)
        tk.Button(row, text="Extend current license", command=extend_current_license, width=20).pack(
            side=tk.LEFT, padx=8
        )
        tk.Label(
            admin,
            text="Issue a 7-day license for a user, or extend the loaded license by more days / to a date. "
            "Send them the .lic file. Keep the private key secret.",
            anchor="w",
            justify="left",
            wraplength=860,
            fg="#333",
        ).pack(fill=tk.X, pady=(6, 0))

    body = tk.Frame(root, padx=16, pady=12)
    body.pack(fill=tk.BOTH, expand=True)

    def folder_row(parent, label, var, browse_title, hint):
        frame = tk.LabelFrame(parent, text=label, padx=8, pady=6)
        frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(frame, text=hint, anchor="w", justify="left", wraplength=840, fg="#333").pack(fill=tk.X)
        row = tk.Frame(frame)
        row.pack(fill=tk.X, pady=(4, 4))
        tk.Entry(row, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        btn = tk.Button(row, text="Browse this PC…", command=lambda: pick_folder(var, browse_title), width=16)
        btn.pack(side=tk.LEFT)
        listing = tk.Listbox(frame, height=4)
        listing.pack(fill=tk.X)
        return btn, listing

    input_btn, input_list = folder_row(
        body,
        "1. Input Folder  (files used for comparing)",
        input_var,
        "Select Input Folder — contains 5G / 4G / 3G / 2G subfolders",
        "Put dumps inside Input\\5G, Input\\4G, Input\\3G, Input\\2G. Any file names. "
        "Tick the networks below; only those folders are searched. Sheet names that match an MO are used as that object.",
    )
    rat_frame = tk.LabelFrame(body, text="Search these networks (Input subfolders)", padx=8, pady=6)
    rat_frame.pack(fill=tk.X, pady=(0, 8))
    tk.Label(
        rat_frame,
        text="Select 5G / 4G / 3G / 2G. The tool looks only in those folders for the inconsistency report.",
        anchor="w",
        fg="#333",
    ).pack(fill=tk.X)
    rat_row = tk.Frame(rat_frame)
    rat_row.pack(fill=tk.X, pady=(4, 0))
    rat_colors = {"5G": "#6A1B9A", "4G": "#1565C0", "3G": "#2E7D32", "2G": "#E65100"}
    for rat in audit.smart.RAT_FOLDERS:
        btn = tk.Checkbutton(
            rat_row,
            text=f"  {rat}  ",
            variable=rat_vars[rat],
            command=refresh_lists,
            indicatoron=True,
            font=("Segoe UI", 11, "bold"),
            fg=rat_colors[rat],
            selectcolor="#E3F2FD",
            padx=8,
        )
        btn.pack(side=tk.LEFT, padx=(0, 12))
    tk.Label(rat_row, text="Folders: Input\\5G  Input\\4G  Input\\3G  Input\\2G", fg="#555").pack(
        side=tk.LEFT, padx=8
    )
    ref_btn, ref_list = folder_row(
        body,
        "2. Reference Folder  (recommended / plan values)",
        reference_var,
        "Select Reference Folder — every workbook is a reference",
        "Any file names (2, 3, 4… files). Different sheet names and many columns. Every file is analyzed against the Input Folder.",
    )
    out_frame = tk.LabelFrame(body, text="3. Output Folder  (inconsistency reports)", padx=8, pady=6)
    out_frame.pack(fill=tk.X, pady=(0, 8))
    tk.Label(
        out_frame,
        text="All Excel / Markdown / CSV reports are written here.",
        anchor="w",
        fg="#333",
    ).pack(fill=tk.X)
    out_row = tk.Frame(out_frame)
    out_row.pack(fill=tk.X, pady=(4, 0))
    tk.Entry(out_row, textvariable=output_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
    out_btn = tk.Button(
        out_row,
        text="Browse this PC…",
        command=lambda: pick_folder(output_var, "Select Output Folder for reports"),
        width=16,
    )
    out_btn.pack(side=tk.LEFT)

    action = tk.Frame(body)
    action.pack(fill=tk.X, pady=8)
    generate_btn = tk.Button(
        action, text="Generate Report", command=generate, width=22, bg="#1F4E79", fg="white"
    )
    generate_btn.pack(side=tk.LEFT)
    open_btn = tk.Button(action, text="Open last report", command=open_report, width=16, state=tk.DISABLED)
    open_btn.pack(side=tk.LEFT, padx=8)
    folder_out_btn = tk.Button(
        action, text="Open output folder", command=lambda: open_path(Path(output_var.get())), width=18
    )
    folder_out_btn.pack(side=tk.LEFT)
    refresh_btn = tk.Button(action, text="Refresh file lists", command=refresh_lists, width=16)
    refresh_btn.pack(side=tk.LEFT, padx=8)

    action_buttons = [input_btn, ref_btn, generate_btn, out_btn, folder_out_btn, refresh_btn]

    tk.Label(
        body,
        text=(
            "Note: Microsoft Excel allows 1,048,576 rows and 16,384 columns per sheet. "
            "This tool does not add a lower limit on files, sheets, or columns. "
            "Very large dumps use more RAM and take longer."
        ),
        anchor="w",
        wraplength=860,
        justify="left",
        fg="#444",
    ).pack(fill=tk.X, pady=(0, 4))
    tk.Label(body, textvariable=status_var, anchor="w", wraplength=860, justify="left").pack(fill=tk.X, pady=(0, 4))
    log_box = tk.Text(body, height=8, wrap=tk.WORD)
    log_box.pack(fill=tk.BOTH, expand=True)

    refresh_lists()
    refresh_license()
    root.mainloop()


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--gui" in argv:
        argv = [a for a in argv if a != "--gui"]
        launch_gui()
        return 0
    if not argv:
        launch_gui()
        return 0
    return audit.main(argv)


if __name__ == "__main__":
    sys.exit(main())
