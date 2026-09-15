#!/usr/bin/env python3
"""One-file Parameter Inconsistency Audit tool.

Select several input workbooks (Reference + 4G + 5G, any order).
The tool classifies them and writes the Excel/CSV/Markdown report.
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


def open_path(path: Path):
    path = Path(path)
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


def launch_gui(preselected=None):
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    root = tk.Tk()
    root.title("Parameter Inconsistency Audit")
    root.geometry("760x560")
    root.minsize(680, 520)

    selected: list[Path] = list(preselected or [])
    default_out = audit.ROOT / "output" if getattr(sys, "frozen", False) else audit.DEFAULT_OUTPUT_DIR
    output_var = tk.StringVar(value=str(default_out))
    ref_var = tk.StringVar(value="(not detected)")
    g4_var = tk.StringVar(value="(not detected)")
    g5_var = tk.StringVar(value="(not detected)")
    status_var = tk.StringVar(value="Select the Reference, 4G and 5G files, then Generate.")
    last_report = {"path": None}

    def refresh_classification():
        result = audit.classify_input_files(selected)
        ref_var.set(result["reference"].name if result["reference"] else "(not detected)")
        g4_var.set(result["cfg_4g"].name if result["cfg_4g"] else "(not detected)")
        g5_var.set(result["cfg_5g"].name if result["cfg_5g"] else "(not detected)")
        file_list.delete(0, tk.END)
        for path in selected:
            role = audit.guess_file_role(path)
            file_list.insert(tk.END, f"{role.upper():<10}  {path}")
        unknown = result["unknown"]
        if unknown:
            status_var.set(f"{len(unknown)} file(s) could not be classified. Keep Reference/4G/5G in the names if needed.")
        elif result["reference"] and result["cfg_4g"] and result["cfg_5g"]:
            status_var.set("All three inputs detected. Click Generate Report.")
        else:
            status_var.set("Need one Reference file, one 4G dump, and one 5G dump.")
        return result

    def add_files():
        paths = filedialog.askopenfilenames(
            title="Select Reference, 4G and 5G files",
            filetypes=FILETYPES,
        )
        for item in paths:
            path = Path(item)
            if path not in selected:
                selected.append(path)
        refresh_classification()

    def clear_files():
        selected.clear()
        refresh_classification()
        status_var.set("Select the Reference, 4G and 5G files, then Generate.")

    def choose_output():
        folder = filedialog.askdirectory(title="Select output folder", initialdir=output_var.get())
        if folder:
            output_var.set(folder)

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
            messagebox.showerror("Missing input", "Please add:\n- " + "\n- ".join(missing))
            return
        output_dir = Path(output_var.get()).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)
        generate_btn.config(state=tk.DISABLED)
        add_btn.config(state=tk.DISABLED)
        log_box.delete("1.0", tk.END)
        status_var.set("Running audit...")
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
                        generate_btn.config(state=tk.NORMAL)
                        add_btn.config(state=tk.NORMAL)
                        status_var.set("Audit failed.")
                        messagebox.showerror("Audit failed", item[1][:1500])
                        return
                    elif item[0] == "done":
                        run, summary = item[1], item[2]
                        last_report["path"] = run.out_xlsx
                        generate_btn.config(state=tk.NORMAL)
                        add_btn.config(state=tk.NORMAL)
                        open_btn.config(state=tk.NORMAL)
                        all_c = summary["ALL"]
                        status_var.set(
                            f"Done. Inconsistent {all_c['inconsistent']} / {all_c['total']}. "
                            f"Report: {run.out_xlsx.name}"
                        )
                        if messagebox.askyesno(
                            "Report ready",
                            f"Inconsistent parameters: {all_c['inconsistent']} of {all_c['total']}\n\n"
                            f"Open Excel report now?\n{run.out_xlsx}",
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

    header = tk.Frame(root, bg="#1F4E79", height=72)
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
        text="Input: several files (Reference + 4G + 5G)   →   Output: inconsistency report",
        fg="#D6E3F0",
        bg="#1F4E79",
        font=("Segoe UI", 10),
    ).pack(anchor="w", padx=16, pady=(0, 12))

    body = tk.Frame(root, padx=16, pady=12)
    body.pack(fill=tk.BOTH, expand=True)

    btns = tk.Frame(body)
    btns.pack(fill=tk.X)
    add_btn = tk.Button(btns, text="1. Select input files…", command=add_files, width=22)
    add_btn.pack(side=tk.LEFT)
    tk.Button(btns, text="Clear", command=clear_files, width=10).pack(side=tk.LEFT, padx=8)

    tk.Label(body, text="Selected files", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 4))
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
        tk.Label(row, textvariable=var, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)

    out_row = tk.Frame(body)
    out_row.pack(fill=tk.X, pady=(8, 4))
    tk.Label(out_row, text="Output folder:", width=12, anchor="w", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
    tk.Entry(out_row, textvariable=output_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
    tk.Button(out_row, text="Browse…", command=choose_output, width=10).pack(side=tk.LEFT)

    action = tk.Frame(body)
    action.pack(fill=tk.X, pady=8)
    generate_btn = tk.Button(action, text="2. Generate Report", command=generate, width=22, bg="#1F4E79", fg="white")
    generate_btn.pack(side=tk.LEFT)
    open_btn = tk.Button(action, text="Open last report", command=open_report, width=16, state=tk.DISABLED)
    open_btn.pack(side=tk.LEFT, padx=8)

    tk.Label(body, textvariable=status_var, anchor="w").pack(fill=tk.X, pady=(4, 4))
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
