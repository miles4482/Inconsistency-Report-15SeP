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
    root.geometry("920x720")
    root.minsize(820, 640)

    input_var = tk.StringVar(value=str(defaults["input"]))
    reference_var = tk.StringVar(value=str(defaults["reference"]))
    output_var = tk.StringVar(value=str(defaults["output"]))
    status_var = tk.StringVar(
        value="Select Input Folder, Reference Folder, and Output Folder on this PC. Files are not uploaded."
    )
    last_report = {"path": None}

    def folder_listing(folder_text: str) -> list[Path]:
        folder = Path(folder_text).expanduser()
        return audit.list_workbooks(folder)

    def refresh_lists():
        input_list.delete(0, tk.END)
        ref_list.delete(0, tk.END)
        inputs = folder_listing(input_var.get())
        refs = folder_listing(reference_var.get())
        if inputs:
            for path in inputs:
                input_list.insert(tk.END, f"{format_size(path):>10}   {path.name}")
        else:
            input_list.insert(tk.END, "(no .xlsx / .xlsb / .xlsm files yet)")
        if refs:
            for path in refs:
                ref_list.insert(tk.END, f"{format_size(path):>10}   {path.name}")
        else:
            ref_list.insert(tk.END, "(no .xlsx / .xlsb / .xlsm files yet)")
        status_var.set(
            f"Input: {len(inputs)} file(s)  |  Reference: {len(refs)} file(s)  |  "
            "Every input file is compared with every reference file."
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
        inputs, refs = refresh_lists()
        if len(inputs) < 1:
            messagebox.showerror(
                "Input Folder empty",
                "Put at least one configuration dump in the Input Folder.\n"
                "Names can be anything (4G dump, 5G dump, 2G dump, ...).\n"
                "Any number of files and sheets is allowed.",
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
            f"Input Folder ({len(inputs)} files): {input_var.get()}\n"
            + "".join(f"  - {p.name}\n" for p in inputs)
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
                        status_var.set("Audit failed.")
                        messagebox.showerror("Audit failed", item[1][:1500])
                        return
                    elif item[0] == "done":
                        run, summary = item[1], item[2]
                        last_report["path"] = run.out_xlsx
                        set_buttons(tk.NORMAL)
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
        text="Three folders on THIS PC: Input (dumps) · Reference (plan values) · Output (reports). No upload. No file-count limit.",
        fg="#D6E3F0",
        bg="#1F4E79",
        font=("Segoe UI", 10),
    ).pack(anchor="w", padx=16, pady=(0, 12))

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
        "Select Input Folder — configuration dumps (4G, 5G, 2G, any names)",
        "Any file names. More than one file. Any number of sheets and columns. "
        "Sheet names that match an MO / MML Object are treated as that object. Every file is checked.",
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
