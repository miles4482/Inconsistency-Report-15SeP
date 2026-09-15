#!/usr/bin/env python3
"""Parameter Inconsistency Audit tool.

Select local files or a local folder on this PC (no upload, no size limit).
Write the report to a local output folder on this PC.
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


FILETYPES = [
    ("Excel workbooks", "*.xlsx *.xlsb *.xlsm"),
    ("All files", "*.*"),
]
WORKBOOK_SUFFIXES = {".xlsx", ".xlsb", ".xlsm"}


def open_path(path: Path):
    path = Path(path)
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


def default_output_dir() -> Path:
    docs = Path.home() / "Documents" / "ParameterAudit_Reports"
    return docs


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


def collect_workbooks(folder: Path) -> list[Path]:
    files = []
    if not folder.is_dir():
        return files
    for path in folder.iterdir():
        if path.is_file() and path.suffix.lower() in WORKBOOK_SUFFIXES:
            files.append(path)
    return files


def launch_gui(preselected=None):
    import tkinter as tk
    from tkinter import filedialog, messagebox

    root = tk.Tk()
    root.title("Parameter Inconsistency Audit")
    root.geometry("860x640")
    root.minsize(760, 580)

    selected: list[Path] = list(preselected or [])
    output_var = tk.StringVar(value=str(default_output_dir()))
    ref_var = tk.StringVar(value="(not selected)")
    g4_var = tk.StringVar(value="(not selected)")
    g5_var = tk.StringVar(value="(not selected)")
    status_var = tk.StringVar(
        value="All files stay on this PC. Select local input files/folder, then a local output folder."
    )
    last_report = {"path": None}

    def refresh_classification():
        result = audit.classify_input_files(selected)
        ref_var.set(
            f"{result['reference'].name}  ({format_size(result['reference'])})  [{result['reference']}]"
            if result["reference"]
            else "(not selected)"
        )
        g4_var.set(
            f"{result['cfg_4g'].name}  ({format_size(result['cfg_4g'])})  [{result['cfg_4g']}]"
            if result["cfg_4g"]
            else "(not selected)"
        )
        g5_var.set(
            f"{result['cfg_5g'].name}  ({format_size(result['cfg_5g'])})  [{result['cfg_5g']}]"
            if result["cfg_5g"]
            else "(not selected)"
        )
        file_list.delete(0, tk.END)
        for path in selected:
            role = audit.guess_file_role(path)
            file_list.insert(tk.END, f"{role.upper():<10} {format_size(path):>10}   {path}")
        unknown = result["unknown"]
        if unknown:
            status_var.set(
                f"{len(unknown)} local file(s) not classified. Use Reference/4G/5G in the file name if needed."
            )
        elif result["reference"] and result["cfg_4g"] and result["cfg_5g"]:
            status_var.set("Local inputs detected. Choose output folder on this PC, then Generate Report.")
        else:
            status_var.set("Select one Reference, one 4G dump, and one 5G dump from this PC (any size).")
        return result

    def add_paths(paths):
        for item in paths:
            path = Path(item)
            if path not in selected:
                selected.append(path)
        refresh_classification()

    def add_files():
        paths = filedialog.askopenfilenames(
            title="Select files from this PC (Reference + 4G + 5G). No size limit.",
            filetypes=FILETYPES,
        )
        add_paths(paths)

    def add_folder():
        folder = filedialog.askdirectory(
            title="Select a folder on this PC that contains the workbooks"
        )
        if not folder:
            return
        found = collect_workbooks(Path(folder))
        if not found:
            messagebox.showwarning(
                "No workbooks",
                "No .xlsx / .xlsb / .xlsm files in that folder.\nFiles are read from your PC only.",
            )
            return
        add_paths(found)

    def pick_one(kind: str):
        title = {
            "reference": "Select Reference Parameter file from this PC",
            "4g": "Select 4G configuration dump from this PC",
            "5g": "Select 5G configuration dump from this PC",
        }[kind]
        path = filedialog.askopenfilename(title=title, filetypes=FILETYPES)
        if not path:
            return
        path = Path(path)
        remaining = []
        for existing in selected:
            if audit.guess_file_role(existing) == kind:
                continue
            remaining.append(existing)
        remaining.append(path)
        selected.clear()
        selected.extend(remaining)
        refresh_classification()

    def clear_files():
        selected.clear()
        refresh_classification()

    def choose_output():
        folder = filedialog.askdirectory(
            title="Select output folder on this PC (report will be saved here)",
            initialdir=output_var.get() or str(Path.home()),
        )
        if folder:
            output_var.set(folder)

    def set_buttons(state):
        for btn in action_buttons:
            btn.config(state=state)

    def generate():
        classified = refresh_classification()
        missing = []
        if not classified["reference"]:
            missing.append("Reference Parameter")
        if not classified["cfg_4g"]:
            missing.append("4G configuration")
        if not classified["cfg_5g"]:
            missing.append("5G configuration")
        if missing:
            messagebox.showerror("Missing input", "Select from this PC:\n- " + "\n- ".join(missing))
            return
        output_dir = Path(output_var.get()).expanduser()
        if not str(output_var.get()).strip():
            messagebox.showerror("Missing output", "Select an output folder on this PC.")
            return
        output_dir.mkdir(parents=True, exist_ok=True)
        set_buttons(tk.DISABLED)
        log_box.delete("1.0", tk.END)
        log_box.insert(
            tk.END,
            "Reading files from your PC (not uploaded).\n"
            f"Reference: {classified['reference']}\n"
            f"4G: {classified['cfg_4g']}\n"
            f"5G: {classified['cfg_5g']}\n"
            f"Output folder: {output_dir}\n\n",
        )
        status_var.set("Running audit on local files...")
        messages: queue.Queue = queue.Queue()

        def progress(msg: str):
            messages.put(("log", str(msg)))

        def worker():
            try:
                run, summary, _extras = audit.execute_audit(
                    classified["reference"],
                    classified["cfg_4g"],
                    classified["cfg_5g"],
                    output_dir,
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

    header = tk.Frame(root, bg="#1F4E79", height=84)
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
        text="Input and output are folders/files on THIS PC. Files are not uploaded. No size limit.",
        fg="#D6E3F0",
        bg="#1F4E79",
        font=("Segoe UI", 10),
    ).pack(anchor="w", padx=16, pady=(0, 12))

    body = tk.Frame(root, padx=16, pady=12)
    body.pack(fill=tk.BOTH, expand=True)

    btns = tk.Frame(body)
    btns.pack(fill=tk.X)
    add_btn = tk.Button(btns, text="Select files from this PC…", command=add_files, width=26)
    add_btn.pack(side=tk.LEFT)
    folder_btn = tk.Button(btns, text="Select input folder from this PC…", command=add_folder, width=30)
    folder_btn.pack(side=tk.LEFT, padx=8)
    tk.Button(btns, text="Clear", command=clear_files, width=10).pack(side=tk.LEFT)

    one = tk.Frame(body)
    one.pack(fill=tk.X, pady=(8, 0))
    tk.Button(one, text="Reference…", command=lambda: pick_one("reference"), width=14).pack(side=tk.LEFT)
    tk.Button(one, text="4G dump…", command=lambda: pick_one("4g"), width=14).pack(side=tk.LEFT, padx=8)
    tk.Button(one, text="5G dump…", command=lambda: pick_one("5g"), width=14).pack(side=tk.LEFT)

    tk.Label(body, text="Local files (full path on your PC)", font=("Segoe UI", 10, "bold")).pack(
        anchor="w", pady=(12, 4)
    )
    file_list = tk.Listbox(body, height=6)
    file_list.pack(fill=tk.X)

    detect = tk.Frame(body)
    detect.pack(fill=tk.X, pady=8)
    for label, var in (
        ("Reference", ref_var),
        ("4G dump", g4_var),
        ("5G dump", g5_var),
    ):
        row = tk.Frame(detect)
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text=f"{label}:", width=12, anchor="w", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        tk.Label(row, textvariable=var, anchor="w", wraplength=680, justify="left").pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )

    out_row = tk.Frame(body)
    out_row.pack(fill=tk.X, pady=(8, 4))
    tk.Label(out_row, text="Output folder on this PC:", width=22, anchor="w", font=("Segoe UI", 10, "bold")).pack(
        side=tk.LEFT
    )
    tk.Entry(out_row, textvariable=output_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
    out_btn = tk.Button(out_row, text="Browse this PC…", command=choose_output, width=16)
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

    action_buttons = [add_btn, folder_btn, generate_btn, out_btn, folder_out_btn]

    tk.Label(body, textvariable=status_var, anchor="w", wraplength=800, justify="left").pack(fill=tk.X, pady=(4, 4))
    log_box = tk.Text(body, height=8, wrap=tk.WORD)
    log_box.pack(fill=tk.BOTH, expand=True)

    if selected:
        refresh_classification()

    root.mainloop()


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--gui" in argv:
        argv = [a for a in argv if a != "--gui"]
        args = audit.parse_args(argv)
        preselected = list(args.files)
        launch_gui(preselected)
        return 0
    if not argv:
        launch_gui()
        return 0
    return audit.main(argv)


if __name__ == "__main__":
    sys.exit(main())
