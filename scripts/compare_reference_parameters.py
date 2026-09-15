#!/usr/bin/env python3
"""Compare every reference workbook against every input dump.

Three local folders:
    Input Folder      configuration dumps (any names, any RAT, many files)
    Reference Folder  recommended / plan values (any names, many files)
    Output Folder     inconsistency reports

Regular use:
    python3 scripts/parameter_audit_app.py
    python3 scripts/compare_reference_parameters.py --input-folder ... --reference-folder ... --output-folder ...
    ./run_audit.sh
    run_audit.bat
"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from pyxlsb import open_workbook


WORKBOOK_SUFFIXES = {".xlsx", ".xlsb", ".xlsm"}


def runtime_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


ROOT = runtime_root()
DEFAULT_INPUT_DIR = ROOT / "input"
DEFAULT_REFERENCE_DIR = ROOT / "reference"
DEFAULT_OUTPUT_DIR = ROOT / "reports"
DEFAULT_CONFIG = ROOT / "config" / "audit.json"

REF_PATTERNS = (
    "Reference Parameter*.xlsx",
    "Reference Parameter*.xlsb",
    "*Reference*Parameter*.xlsx",
)
CFG_4G_PATTERNS = (
    "4G_ConfigurationData*.xlsb",
    "4G_ConfigurationData*.xlsx",
    "*4G*Config*.xlsb",
    "*4G*Config*.xlsx",
)
CFG_5G_PATTERNS = (
    "5G_ConfigurationData*.xlsb",
    "5G_ConfigurationData*.xlsx",
    "*5G*Config*.xlsb",
    "*5G*Config*.xlsx",
)

TRUE_SET = {"1", "1.0", "ON", "TRUE", "YES", "ENABLE", "ENABLED"}
FALSE_SET = {"0", "0.0", "OFF", "FALSE", "NO", "DISABLE", "DISABLED"}
UNIT_RE = re.compile(r"^(-?\d+(?:\.\d+)?)(MS|S|DBM|DB|MHZ|KHZ|MIN|DAY)?$", re.I)
META_SHEETS = {
    "SUMMARYRES",
    "FILEIDENTIFICATION",
    "INNERVALIDEDEF",
    "MAPPINGCELLTEMPLATE",
    "PRODUCTTYPE",
    "INNER_VERSION_FOR_VALID",
    "CONTROL INFOR",
    "CONTROL DEF",
    "SHEET DEF",
    "MAPPING DEF",
    "VALID DEF",
    "COMMENTS",
}
SKIP_REF_SHEETS = {
    "TITLE",
    "SUMMARY",
    "COVER",
    "INDEX",
    "README",
    "REVISION",
    "CHANGELOG",
    "HISTORY",
    "NOTES",
}
REF_HEADER_ALIASES = {
    "function": {"FUNCTION", "FEATURE", "CATEGORY", "AREA", "DOMAIN", "GROUP"},
    "mml": {
        "MMLOBJECT",
        "MMLOBJECTNAME",
        "MML",
        "MO",
        "MOC",
        "MONAME",
        "OBJECT",
        "OBJECTNAME",
        "MANAGEDOBJECT",
        "MMLOBJECTNAME",
        "NEOBJECT",
    },
    "pid": {
        "PARAMETERID",
        "PARAMETER",
        "PARAMETERNAME",
        "PARAMID",
        "PARA",
        "PARANAME",
        "ATTR",
        "ATTRIBUTE",
        "ATTRIBUTENAME",
        "PARAM",
    },
    "recommend": {
        "RECOMMENDVALUE",
        "RECOMMENDEDVALUE",
        "RECOMMEND",
        "RECOMMENDED",
        "PLANVALUE",
        "PLANNEDVALUE",
        "TARGETVALUE",
        "EXPECTEDVALUE",
        "BASELINEVALUE",
        "REFVALUE",
        "STANDARDVALUE",
        "GOLDENVALUE",
        "PLAN",
    },
}

# Microsoft Excel worksheet limits. This tool does not impose a lower cap.
EXCEL_MAX_ROWS = 1_048_576
EXCEL_MAX_COLS = 16_384


@dataclass
class RunContext:
    root: Path
    reference: Path
    cfg_4g: Path | None
    cfg_5g: Path | None
    output_dir: Path
    run_id: str
    audit_date: str
    out_xlsx: Path
    out_md: Path
    out_csv: Path
    out_summary: Path
    history_csv: Path
    latest_dir: Path
    input_folder: Path | None = None
    reference_folder: Path | None = None
    input_files: list = field(default_factory=list)
    reference_files: list = field(default_factory=list)


def workbook_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".xlsb":
        return "xlsb"
    if suffix in {".xlsx", ".xlsm"}:
        return "xlsx"
    raise ValueError(f"Unsupported workbook type: {path.name} ({suffix or 'no extension'}). Use .xlsx, .xlsb or .xlsm.")


def is_workbook(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in WORKBOOK_SUFFIXES


def list_workbooks(folder: Path | None) -> list[Path]:
    if folder is None:
        return []
    folder = Path(folder).expanduser()
    if not folder.exists() or not folder.is_dir():
        return []
    files = [p for p in folder.iterdir() if is_workbook(p)]
    files.sort(key=lambda p: p.name.lower())
    return files


def sheet_names(path: Path) -> list[str]:
    if workbook_kind(path) == "xlsb":
        with open_workbook(str(path)) as wb:
            return list(wb.sheets)
    wb = load_workbook(path, read_only=True, data_only=True)
    names = list(wb.sheetnames)
    wb.close()
    return names


def read_sheet_rows(path: Path, sheet_name: str):
    if workbook_kind(path) == "xlsb":
        with open_workbook(str(path)) as wb:
            if sheet_name not in wb.sheets:
                return None
            with wb.get_sheet(sheet_name) as sheet:
                return [[c.v for c in row] for row in sheet.rows()]
    wb = load_workbook(path, read_only=True, data_only=True)
    if sheet_name not in wb.sheetnames:
        wb.close()
        return None
    rows = [list(row) for row in wb[sheet_name].iter_rows(values_only=True)]
    wb.close()
    return rows


def unique_files(paths):
    seen = {}
    for path in paths:
        if path.is_file():
            seen[path.resolve()] = path
    return list(seen.values())


def find_files(search_dirs, patterns) -> list[Path]:
    found = []
    for folder in search_dirs:
        if not folder or not folder.exists():
            continue
        for pattern in patterns:
            found.extend(folder.glob(pattern))
    return unique_files(found)


def newest_file(paths: list[Path]) -> Path | None:
    if not paths:
        return None
    return max(paths, key=lambda p: (p.stat().st_mtime, p.name))


def load_audit_config(path: Path | None) -> dict:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def search_dirs(root: Path, input_dir: Path) -> list[Path]:
    dirs = [input_dir, root]
    unique = []
    seen = set()
    for folder in dirs:
        key = folder.resolve() if folder.exists() else folder
        if key not in seen:
            unique.append(folder)
            seen.add(key)
    return unique


def discover_inputs(root: Path, input_dir: Path, config: dict | None = None) -> dict:
    dirs = search_dirs(root, input_dir)
    patterns = (config or {}).get("file_patterns") or {}
    ref_patterns = tuple(patterns.get("reference") or REF_PATTERNS)
    cfg_4g_patterns = tuple(patterns.get("4G") or CFG_4G_PATTERNS)
    cfg_5g_patterns = tuple(patterns.get("5G") or CFG_5G_PATTERNS)
    return {
        "reference": newest_file(find_files(dirs, ref_patterns)),
        "cfg_4g": newest_file(find_files(dirs, cfg_4g_patterns)),
        "cfg_5g": newest_file(find_files(dirs, cfg_5g_patterns)),
        "search_dirs": dirs,
    }


def _matches_any(name: str, patterns) -> bool:
    return any(fnmatch.fnmatch(name, pat) for pat in patterns)


def guess_file_role(path: Path) -> str:
    name = path.name
    upper = name.upper()
    if _matches_any(name, REF_PATTERNS) or "REFERENCE" in upper:
        return "reference"
    if _matches_any(name, CFG_4G_PATTERNS) or re.search(r"(^|[^0-9])4G([^0-9]|$)", upper):
        return "4g"
    if _matches_any(name, CFG_5G_PATTERNS) or re.search(r"(^|[^0-9])5G([^0-9]|$)", upper):
        return "5g"
    try:
        sheets = [str(s).upper() for s in sheet_names(path)]
    except Exception:
        return "unknown"
    if any(s in {"NR PERFORMANCE", "NR ANCHOR", "TITLE"} for s in sheets) and "MAPPING DEF" not in sheets:
        return "reference"
    if "NR PERFORMANCE" in sheets or "NR ANCHOR" in sheets:
        return "reference"
    blob = " ".join(sheets)
    if "NRCELL" in blob or "GNODEBPARAM" in blob or "GNBX2SONCONFIG" in blob:
        return "5g"
    if "NSADCMGMTCONFIG" in blob or "ENODEBALGOSWITCH" in blob or "CELLALGOSWITCH" in blob:
        return "4g"
    return "unknown"


def classify_input_files(paths) -> dict:
    classified = {"reference": [], "4g": [], "5g": [], "unknown": []}
    for raw in paths:
        path = Path(raw).expanduser().resolve()
        if not path.is_file():
            classified["unknown"].append(path)
            continue
        classified[guess_file_role(path)].append(path)
    picked = {
        "reference": newest_file(classified["reference"]),
        "cfg_4g": newest_file(classified["4g"]),
        "cfg_5g": newest_file(classified["5g"]),
        "unknown": classified["unknown"],
        "all_reference": classified["reference"],
        "all_4g": classified["4g"],
        "all_5g": classified["5g"],
    }
    return picked


def build_run_context(
    root: Path,
    reference: Path,
    cfg_4g: Path | None,
    cfg_5g: Path | None,
    output_dir: Path,
    run_id: str | None = None,
    input_folder: Path | None = None,
    reference_folder: Path | None = None,
    input_files: list | None = None,
    reference_files: list | None = None,
) -> RunContext:
    now = datetime.now()
    run_id = run_id or now.strftime("%Y%m%d_%H%M%S")
    run_dir = output_dir / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    latest_dir = output_dir / "latest"
    latest_dir.mkdir(parents=True, exist_ok=True)
    reference_files = [Path(p) for p in (reference_files or [reference])]
    input_files = [Path(p) for p in (input_files or [p for p in (cfg_4g, cfg_5g) if p])]
    return RunContext(
        root=root,
        reference=Path(reference),
        cfg_4g=Path(cfg_4g) if cfg_4g else None,
        cfg_5g=Path(cfg_5g) if cfg_5g else None,
        output_dir=output_dir,
        run_id=run_id,
        audit_date=now.strftime("%d %b %Y"),
        out_xlsx=run_dir / "Parameter_Inconsistency_Report.xlsx",
        out_md=run_dir / "Parameter_Inconsistency_Report.md",
        out_csv=run_dir / "all_parameters.csv",
        out_summary=run_dir / "run_summary.json",
        history_csv=output_dir / "run_history.csv",
        latest_dir=latest_dir,
        input_folder=Path(input_folder) if input_folder else None,
        reference_folder=Path(reference_folder) if reference_folder else None,
        input_files=input_files,
        reference_files=reference_files,
    )


def copy_latest(run: RunContext):
    for src, name in (
        (run.out_xlsx, "Parameter_Inconsistency_Report.xlsx"),
        (run.out_md, "Parameter_Inconsistency_Report.md"),
        (run.out_csv, "all_parameters.csv"),
        (run.out_summary, "run_summary.json"),
    ):
        if src.exists():
            shutil.copy2(src, run.latest_dir / name)


def norm_key(value) -> str:
    if value is None:
        return ""
    return re.sub(r"[^A-Z0-9]", "", str(value).upper())


def clean_text(value) -> str:
    if value is None:
        return ""
    return str(value).replace("\xa0", " ").strip()


def is_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def canon_value(value):
    if is_empty(value):
        return None
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, float):
        if value.is_integer():
            value = int(value)
        else:
            return str(value)
    if isinstance(value, int):
        return str(value)
    text = clean_text(value)
    compact = text.upper().replace(" ", "")
    unit_match = UNIT_RE.fullmatch(compact)
    if unit_match:
        number = float(unit_match.group(1))
        if number.is_integer():
            return str(int(number))
        return str(number)
    if compact in TRUE_SET:
        return "1"
    if compact in FALSE_SET:
        return "0"
    return re.sub(r"[^A-Z0-9]", "", compact)


def values_match(actual, recommend) -> bool:
    if is_empty(recommend):
        return False
    left = canon_value(actual)
    right = canon_value(recommend)
    if left is None or right is None:
        return False
    return left == right


def parse_bitfield(value):
    if is_empty(value):
        return None
    text = clean_text(value)
    if "&" not in text and not re.search(r"-\s*[01]\b", text):
        return None
    bits = {}
    for part in text.split("&"):
        part = part.strip()
        if not part:
            continue
        name, sep, raw = part.rpartition("-")
        if not sep:
            continue
        bits[norm_key(name)] = raw.strip()
    return bits or None


def extract_bit(value, bit_name):
    bits = parse_bitfield(value)
    if bits is None:
        return None, "not_bitfield"
    key = norm_key(bit_name)
    if key in bits:
        return bits[key], "found"
    return None, "bit_missing"


def load_mapping(path: Path):
    moc_to_sheet = {}
    attrs_by_moc = defaultdict(dict)
    attrs_global = defaultdict(list)
    rows = read_sheet_rows(path, "MAPPING DEF")
    if not rows:
        raise ValueError(f"MAPPING DEF sheet not found in {path}")
    for row in rows[1:]:
        if not row or len(row) < 5:
            continue
        sheet_name, _group, column, moc, attr = row[0], row[1], row[2], row[3], row[4]
        if not sheet_name or not moc or not attr:
            continue
        moc_key = norm_key(moc)
        attr_key = norm_key(attr)
        moc_to_sheet.setdefault(moc_key, sheet_name)
        moc_to_sheet.setdefault(norm_key(sheet_name), sheet_name)
        rec = {
            "sheet": sheet_name,
            "column": column,
            "moc": moc,
            "attr": attr,
        }
        attrs_by_moc[moc_key][attr_key] = rec
        attrs_global[attr_key].append(rec)
        attrs_global[norm_key(column)].append(rec)
    return {
        "path": path,
        "moc_to_sheet": moc_to_sheet,
        "attrs_by_moc": attrs_by_moc,
        "attrs_global": attrs_global,
    }


class SheetCache:
    def __init__(self, path: Path):
        self.path = path
        self.cache = {}
        self._names = None

    def names(self):
        if self._names is None:
            self._names = sheet_names(self.path)
        return self._names

    def get(self, sheet_name: str):
        if sheet_name in self.cache:
            return self.cache[sheet_name]
        if sheet_name not in self.names():
            self.cache[sheet_name] = None
            return None
        rows = read_sheet_rows(self.path, sheet_name)
        if not rows or len(rows) < 1:
            self.cache[sheet_name] = None
            return None
        huawei_mode = any(norm_key(n) == "MAPPINGDEF" for n in self.names())
        if huawei_mode and len(rows) >= 2:
            header_row, data_start = 1, 2
        else:
            header_row, data_start = detect_data_header_row(rows)
        if header_row >= len(rows):
            self.cache[sheet_name] = None
            return None
        raw_headers = rows[header_row]
        headers = [clean_text(h) if h is not None else f"col_{i}" for i, h in enumerate(raw_headers)]
        header_index = {h: i for i, h in enumerate(headers) if h}
        header_norm = {norm_key(h): i for i, h in enumerate(headers) if norm_key(h)}
        if header_row > 0:
            for i, h in enumerate(rows[0]):
                nk = norm_key(h)
                if nk and nk not in header_norm:
                    header_norm[nk] = i
                    text = clean_text(h)
                    if text and text not in header_index:
                        header_index[text] = i
        records = []
        for row in rows[data_start:]:
            if not row or all(is_empty(v) for v in row):
                continue
            records.append(row)
        payload = {
            "headers": headers,
            "header_index": header_index,
            "header_norm": header_norm,
            "rows": records,
        }
        self.cache[sheet_name] = payload
        return payload


def detect_data_header_row(rows) -> tuple[int, int]:
    """Return (header_row_index, first_data_row_index).

    Huawei bulk dumps typically have technical names on row 1 and display
    names on row 2. Generic workbooks use row 1 as headers.
    """
    if len(rows) >= 2:
        first = [norm_key(c) for c in (rows[0] or [])[:12]]
        huawei_markers = {"MODIND", "MOI", "FDN", "NE", "BN", "SN"}
        if any(m in first for m in huawei_markers):
            return 1, 2
        row0_filled = [c for c in (rows[0] or []) if not is_empty(c)]
        row1_filled = [c for c in (rows[1] or []) if not is_empty(c)]
        row1_star = sum(1 for c in row1_filled if str(c).lstrip().startswith("*"))
        if row1_star >= 1 and len(row1_filled) >= len(row0_filled):
            return 1, 2
        if len(row0_filled) <= 3 and len(row1_filled) >= 4:
            return 1, 2
    return 0, 1


def find_attr_record(mapping, moc_name, attr_name):
    moc_key = norm_key(moc_name)
    attr_key = norm_key(attr_name)
    by_moc = mapping["attrs_by_moc"].get(moc_key, {})
    if attr_key in by_moc:
        return by_moc[attr_key]
    for rec in mapping["attrs_global"].get(attr_key, []):
        if norm_key(rec["sheet"]) == moc_key or norm_key(rec["moc"]) == moc_key:
            return rec
    hits = mapping["attrs_global"].get(attr_key, [])
    if len(hits) == 1:
        return hits[0]
    return None


def resolve_parameter(param, mapping):
    mml = clean_text(param["mml"])
    pid = clean_text(param["pid"])
    result = {
        "sheet": None,
        "column": None,
        "attr": None,
        "bit": None,
        "moc": None,
        "reason": "",
    }
    if not mml or not pid:
        result["reason"] = "Missing MML Object or Parameter ID"
        return result

    moc_key = norm_key(mml)
    sheet = mapping["moc_to_sheet"].get(moc_key)
    moc_attrs = mapping["attrs_by_moc"].get(moc_key, {})
    mml_as_attr_hits = mapping["attrs_global"].get(moc_key, [])

    left, right = (pid.split("@", 1) + [None])[:2] if "@" in pid else (pid, None)
    left, right = clean_text(left), clean_text(right) if right else None

    def choose_roles():
        if not right:
            if moc_attrs and norm_key(left) in moc_attrs:
                return left, None
            if mml_as_attr_hits and not moc_attrs:
                return mml, left
            return left, None
        left_is_attr = bool(moc_attrs and norm_key(left) in moc_attrs) or bool(
            find_attr_record(mapping, mml, left)
        )
        right_is_attr = bool(moc_attrs and norm_key(right) in moc_attrs) or bool(
            find_attr_record(mapping, mml, right)
        )
        if right_is_attr and not left_is_attr:
            return right, left
        if left_is_attr and not right_is_attr:
            return left, right
        if right_is_attr and left_is_attr:
            return right, left
        if mml_as_attr_hits and not moc_attrs:
            return mml, left if not right_is_attr else right
        return right, left

    attr_name, bit_name = choose_roles()
    rec = find_attr_record(mapping, mml, attr_name)
    if rec is None and mml_as_attr_hits:
        rec = mml_as_attr_hits[0]
        if bit_name is None:
            bit_name = pid if "@" not in pid else left
        attr_name = rec["attr"]
    if rec is None:
        result["reason"] = f"Attribute not mapped: {mml} / {pid}"
        return result

    result.update(
        {
            "sheet": rec["sheet"],
            "column": rec["column"],
            "attr": rec["attr"],
            "bit": bit_name,
            "moc": rec["moc"],
            "reason": "OK",
        }
    )
    return result


def object_label(row, headers):
    parts = []
    for key in headers[:3]:
        idx = headers.index(key)
        val = row[idx] if idx < len(row) else None
        if not is_empty(val):
            parts.append(f"{key}={val}")
    return " | ".join(parts[:2]) if parts else "row"


def compare_param(param, resolved, cache):
    recommend = param["recommend"]
    out = {
        "status": "",
        "objects_checked": 0,
        "match_count": 0,
        "mismatch_count": 0,
        "missing_count": 0,
        "unique_actuals": [],
        "sample_mismatches": [],
        "remark": resolved.get("reason") or "",
        "actual_source": "",
    }
    if resolved.get("reason") != "OK":
        out["status"] = "Not Found in Configuration"
        return out

    sheet = cache.get(resolved["sheet"])
    if not sheet:
        out["status"] = "Not Found in Configuration"
        out["remark"] = f"Sheet not present: {resolved['sheet']}"
        return out

    col = resolved["column"]
    col_idx = sheet["header_index"].get(col)
    if col_idx is None:
        col_idx = sheet["header_norm"].get(norm_key(col))
    if col_idx is None:
        out["status"] = "Not Found in Configuration"
        out["remark"] = f"Column not present: {col}"
        return out

    out["actual_source"] = f"{resolved['sheet']} / {sheet['headers'][col_idx]}"
    counts = Counter()
    mismatches = []
    for row in sheet["rows"]:
        raw = row[col_idx] if col_idx < len(row) else None
        used = raw
        bit_state = ""
        if resolved.get("bit"):
            bit_val, bit_state = extract_bit(raw, resolved["bit"])
            if bit_state == "found":
                used = bit_val
            elif bit_state == "not_bitfield":
                used = raw
            else:
                used = f"<BIT_MISSING:{resolved['bit']}>"
                bits = parse_bitfield(raw) or {}
                similar = [name for name in bits if resolved["bit"].replace("NSA_", "NR_") in name or name.endswith(norm_key(resolved["bit"])[-16:])]
                if similar and "closest_bit" not in out:
                    out["closest_bit"] = similar[0]
        display = clean_text(used)
        if display == "":
            display = "<EMPTY>"
        counts[display] += 1
        out["objects_checked"] += 1
        if is_empty(recommend):
            continue
        if bit_state == "bit_missing":
            out["missing_count"] += 1
            out["mismatch_count"] += 1
            if len(mismatches) < 8:
                mismatches.append(object_label(row, sheet["headers"]) + f" -> {display}")
            continue
        if values_match(used, recommend):
            out["match_count"] += 1
        else:
            out["mismatch_count"] += 1
            if len(mismatches) < 8:
                mismatches.append(object_label(row, sheet["headers"]) + f" -> {display}")

    out["unique_actuals"] = counts.most_common(12)
    out["sample_mismatches"] = mismatches
    if is_empty(recommend):
        out["status"] = "No Recommend Value"
        out["remark"] = "Reference recommend value is empty; parameter not audited for inconsistency"
        return out
    if out["objects_checked"] == 0:
        out["status"] = "Not Found in Configuration"
        out["remark"] = "No data rows in mapped sheet"
        return out
    if out["mismatch_count"] == 0:
        out["status"] = "Consistent"
    elif out["match_count"] == 0:
        out["status"] = "Inconsistent"
    else:
        out["status"] = "Mixed / Partial"

    pid = str(param.get("pid") or "").upper()
    if pid == "DLARFCN" and out["status"] == "Inconsistent":
        out["remark"] = (
            "Recommend is a band name, but DlArfcn in the dump is a numeric ARFCN. "
            f"Actual: {unique_actual_text(out['unique_actuals'])}. "
            "Check Frequency Band on the same MO."
        )
    elif pid == "FREQUENCYBAND" and out["status"] == "Inconsistent":
        out["remark"] = (
            "Recommend does not match Frequency Band in the dump. "
            f"Actual: {unique_actual_text(out['unique_actuals'])}. "
            "Additional Frequency Band may be the intended NULL field."
        )
    elif out["unique_actuals"] and str(out["unique_actuals"][0][0]).startswith("<BIT_MISSING"):
        extra = ""
        if "closest_bit" in out:
            extra = f" Closest live bit key seen: {out['closest_bit']}."
        out["remark"] = (
            f"Bit {resolved.get('bit')} is not present in the packed switch on "
            f"{resolved.get('sheet')} / {resolved.get('column')} for this software version."
            + extra
        )
    return out


def detect_ref_header_map(header_row) -> dict:
    mapping = {}
    for i, cell in enumerate(header_row or []):
        key = norm_key(cell)
        if not key:
            continue
        for field, aliases in REF_HEADER_ALIASES.items():
            if key in aliases and field not in mapping:
                mapping[field] = i
    return mapping


def is_skipped_ref_sheet(sheet_name: str) -> bool:
    key = norm_key(sheet_name)
    skipped = {norm_key(s) for s in SKIP_REF_SHEETS | META_SHEETS}
    return key in skipped


def guess_network_label(*parts) -> str:
    blob = " ".join(clean_text(p) for p in parts if p).upper()
    if re.search(r"(^|[^0-9])5G([^0-9]|$)", blob) or "NR PERFORMANCE" in blob or "GNODEB" in blob:
        return "5G"
    if re.search(r"(^|[^0-9])4G([^0-9]|$)", blob) or "NR ANCHOR" in blob or re.search(r"\bLTE\b", blob):
        return "4G"
    if re.search(r"(^|[^0-9])2G([^0-9]|$)", blob) or "GSM" in blob or "BSC" in blob:
        return "2G"
    if "3G" in blob or "NODEB" in blob or "RNC" in blob or "UMTS" in blob:
        return "3G"
    return ""


def load_reference_file(ref_path: Path, ref_count: int = 1):
    params = []
    names = sheet_names(ref_path)
    for sheet_name in names:
        if is_skipped_ref_sheet(sheet_name):
            continue
        rows = read_sheet_rows(ref_path, sheet_name)
        if not rows:
            continue
        header_idx = None
        header_map = None
        for i, row in enumerate(rows[:12]):
            candidate = detect_ref_header_map(row)
            if "pid" in candidate and ("recommend" in candidate or "mml" in candidate):
                header_idx = i
                header_map = candidate
                break
        if header_map is None:
            continue
        sheet_as_mo = "mml" not in header_map
        for offset, row in enumerate(rows[header_idx + 1 :], start=header_idx + 2):
            def cell(field):
                idx = header_map.get(field)
                if idx is None or row is None or idx >= len(row):
                    return None
                return row[idx]

            mml = clean_text(cell("mml"))
            pid = clean_text(cell("pid"))
            if is_empty(mml) and is_empty(pid):
                continue
            if is_empty(pid):
                continue
            if is_empty(mml):
                mml = sheet_name
                sheet_as_mo = True
            rec = cell("recommend")
            sheet_key = sheet_name if ref_count <= 1 else f"{ref_path.name} | {sheet_name}"
            params.append(
                {
                    "ref_file": ref_path.name,
                    "ref_path": str(ref_path),
                    "ref_sheet": sheet_name,
                    "sheet_key": sheet_key,
                    "ref_row": offset,
                    "function": clean_text(cell("function")) or "Unspecified",
                    "mml": mml,
                    "pid": pid,
                    "recommend": rec if not is_empty(rec) else None,
                    "network": guess_network_label(ref_path.name, sheet_name),
                    "sheet_is_mo": sheet_as_mo,
                }
            )
    return params


def load_reference(ref_path: Path):
    """Load one reference workbook (any qualifying sheets, not only NR Performance / NR Anchor)."""
    return load_reference_file(Path(ref_path), ref_count=1)


def load_all_references(ref_files: list[Path]):
    params = []
    missing = []
    for path in ref_files:
        loaded = load_reference_file(path, ref_count=len(ref_files))
        if not loaded:
            missing.append(path.name)
            continue
        params.extend(loaded)
    return params, missing


def find_column_index(sheet, name: str):
    if not name or not sheet:
        return None
    idx = sheet["header_index"].get(name)
    if idx is not None:
        return idx
    return sheet["header_norm"].get(norm_key(name))


def resolve_by_sheet_name(param, workbook_names, cache):
    """Treat a matching input sheet name as the MML / MO object."""
    result = {
        "sheet": None,
        "column": None,
        "attr": None,
        "bit": None,
        "moc": None,
        "reason": "",
    }
    mml = clean_text(param.get("mml"))
    pid = clean_text(param.get("pid"))
    if not pid:
        result["reason"] = "Missing Parameter ID"
        return result
    name_index = {norm_key(n): n for n in workbook_names if not is_skipped_ref_sheet(n) and norm_key(n) not in {norm_key(s) for s in META_SHEETS}}
    sheet = name_index.get(norm_key(mml)) if mml else None
    if sheet is None and mml:
        for key, actual in name_index.items():
            if key.endswith(norm_key(mml)) or norm_key(mml).endswith(key):
                if min(len(key), len(norm_key(mml))) >= 6:
                    sheet = actual
                    break
    if sheet is None:
        result["reason"] = f"No input sheet named as MO '{mml}'"
        return result
    payload = cache.get(sheet)
    if not payload:
        result["reason"] = f"Sheet not present: {sheet}"
        return result
    left, right = (pid.split("@", 1) + [None])[:2] if "@" in pid else (pid, None)
    left, right = clean_text(left), clean_text(right) if right else None
    candidates = [c for c in (left, right, pid) if c]
    col_idx = None
    col_name = None
    bit_name = None
    for cand in candidates:
        idx = find_column_index(payload, cand)
        if idx is not None:
            col_idx = idx
            col_name = payload["headers"][idx]
            bit_name = next((c for c in candidates if norm_key(c) != norm_key(cand)), None)
            break
    if col_idx is None and right:
        idx = find_column_index(payload, right)
        if idx is not None:
            col_idx = idx
            col_name = payload["headers"][idx]
            bit_name = left
    if col_idx is None:
        result["reason"] = f"Column not present on sheet {sheet}: {pid}"
        result["sheet"] = sheet
        return result
    result.update(
        {
            "sheet": sheet,
            "column": col_name,
            "attr": col_name,
            "bit": bit_name,
            "moc": mml or sheet,
            "reason": "OK",
        }
    )
    return result


class InputWorkbook:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.cache = SheetCache(self.path)
        self.mapping = None
        names = self.cache.names()
        if any(norm_key(n) == "MAPPINGDEF" for n in names):
            mapping_name = next(n for n in names if norm_key(n) == "MAPPINGDEF")
            try:
                self.mapping = load_mapping(self.path) if mapping_name == "MAPPING DEF" else load_mapping(self.path)
            except Exception:
                try:
                    self.mapping = load_mapping(self.path)
                except Exception:
                    self.mapping = None

    def resolve(self, param) -> dict:
        moc_key = norm_key(param.get("mml"))
        if self.mapping and moc_key:
            mo_known = (
                moc_key in self.mapping["moc_to_sheet"]
                or moc_key in self.mapping["attrs_by_moc"]
                or moc_key in self.mapping["attrs_global"]
            )
            if mo_known:
                resolved = resolve_parameter(param, self.mapping)
                if resolved.get("reason") == "OK":
                    return resolved
        return resolve_by_sheet_name(param, self.cache.names(), self.cache)


class InputStore:
    def __init__(self, files: list[Path]):
        self.workbooks = [InputWorkbook(path) for path in files]

    def compare_param(self, param):
        hits = []
        last_resolved = {
            "sheet": None,
            "column": None,
            "attr": None,
            "bit": None,
            "moc": None,
            "reason": "Not found in any input file",
        }
        for wb in self.workbooks:
            resolved = wb.resolve(param)
            if resolved.get("reason") != "OK":
                last_resolved = resolved
                continue
            result = compare_param(param, resolved, wb.cache)
            if result["status"] == "Not Found in Configuration" and result["objects_checked"] == 0:
                last_resolved = resolved
                last_resolved["reason"] = result.get("remark") or resolved.get("reason")
                continue
            result["input_file"] = wb.path.name
            result["resolved"] = resolved
            hits.append((wb.path, resolved, result))
        if not hits:
            empty = {
                "status": "Not Found in Configuration",
                "objects_checked": 0,
                "match_count": 0,
                "mismatch_count": 0,
                "missing_count": 0,
                "unique_actuals": [],
                "sample_mismatches": [],
                "remark": last_resolved.get("reason") or "Not found in any input file",
                "actual_source": "",
                "input_files": "",
            }
            return last_resolved, empty
        return merge_file_hits(param, hits)


def merge_file_hits(param, hits):
    primary_resolved = hits[0][1]
    merged = {
        "status": "",
        "objects_checked": 0,
        "match_count": 0,
        "mismatch_count": 0,
        "missing_count": 0,
        "unique_actuals": [],
        "sample_mismatches": [],
        "remark": "",
        "actual_source": "",
        "input_files": ", ".join(path.name for path, _, _ in hits),
    }
    counts = Counter()
    remarks = []
    sources = []
    for path, resolved, result in hits:
        merged["objects_checked"] += result["objects_checked"]
        merged["match_count"] += result["match_count"]
        merged["mismatch_count"] += result["mismatch_count"]
        merged["missing_count"] += result.get("missing_count") or 0
        for value, count in result.get("unique_actuals") or []:
            counts[f"{path.name}: {value}"] += count
        for sample in result.get("sample_mismatches") or []:
            if len(merged["sample_mismatches"]) < 12:
                merged["sample_mismatches"].append(f"{path.name} | {sample}")
        if result.get("remark"):
            remarks.append(f"{path.name}: {result['remark']}")
        if result.get("actual_source"):
            sources.append(f"{path.name}: {result['actual_source']}")
        if result.get("closest_bit") and "closest_bit" not in merged:
            merged["closest_bit"] = result["closest_bit"]
    merged["unique_actuals"] = counts.most_common(12)
    merged["remark"] = " | ".join(remarks)
    merged["actual_source"] = " | ".join(sources)
    recommend = param.get("recommend")
    if is_empty(recommend):
        merged["status"] = "No Recommend Value"
        merged["remark"] = merged["remark"] or (
            "Reference recommend value is empty; parameter not audited for inconsistency"
        )
        return primary_resolved, merged
    if merged["objects_checked"] == 0:
        merged["status"] = "Not Found in Configuration"
        return primary_resolved, merged
    if merged["mismatch_count"] == 0:
        merged["status"] = "Consistent"
    elif merged["match_count"] == 0:
        merged["status"] = "Inconsistent"
    else:
        merged["status"] = "Mixed / Partial"
    pid = str(param.get("pid") or "").upper()
    if pid == "DLARFCN" and merged["status"] == "Inconsistent":
        merged["remark"] = (
            "Recommend is a band name, but DlArfcn in the dump is a numeric ARFCN. "
            f"Actual: {unique_actual_text(merged['unique_actuals'])}. "
            "Check Frequency Band on the same MO."
        )
    elif pid == "FREQUENCYBAND" and merged["status"] == "Inconsistent":
        merged["remark"] = (
            "Recommend does not match Frequency Band in the dump. "
            f"Actual: {unique_actual_text(merged['unique_actuals'])}. "
            "Additional Frequency Band may be the intended NULL field."
        )
    elif merged["unique_actuals"] and str(merged["unique_actuals"][0][0]).split(": ", 1)[-1].startswith("<BIT_MISSING"):
        extra = ""
        if "closest_bit" in merged:
            extra = f" Closest live bit key seen: {merged['closest_bit']}."
        merged["remark"] = (
            f"Bit {primary_resolved.get('bit')} is not present in the packed switch on "
            f"{primary_resolved.get('sheet')} / {primary_resolved.get('column')} for this software version."
            + extra
        )
    return primary_resolved, merged


def unique_actual_text(unique_actuals):
    if not unique_actuals:
        return ""
    parts = []
    for value, count in unique_actuals:
        text = str(value)
        if len(text) > 90:
            text = text[:87] + "..."
        parts.append(f"{text} ({count})")
    return " | ".join(parts)


def classify_bucket(status: str) -> str:
    if status == "Inconsistent":
        return "full_inconsistent"
    if status == "Mixed / Partial":
        return "mixed"
    if status == "Consistent":
        return "consistent"
    if status == "No Recommend Value":
        return "no_recommend"
    return "not_found"


def is_inconsistent(status: str) -> bool:
    return classify_bucket(status) in {"full_inconsistent", "mixed"}


def summarize(params):
    summary = defaultdict(lambda: Counter())
    func_summary = defaultdict(lambda: defaultdict(lambda: Counter()))
    for p in params:
        bucket = classify_bucket(p["result"]["status"])
        key = p.get("sheet_key") or p["ref_sheet"]
        summary[key][bucket] += 1
        summary["ALL"][bucket] += 1
        func_summary[key][p["function"]][bucket] += 1
        func_summary[key][p["function"]]["total"] += 1
        summary[key]["total"] += 1
        summary["ALL"]["total"] += 1
        if bucket in {"full_inconsistent", "mixed"}:
            summary[key]["inconsistent"] += 1
            summary["ALL"]["inconsistent"] += 1
            func_summary[key][p["function"]]["inconsistent"] += 1
    return summary, func_summary


def sheet_keys_in_order(params):
    order = []
    seen = set()
    for p in params:
        key = p.get("sheet_key") or p["ref_sheet"]
        if key not in seen:
            seen.add(key)
            order.append(key)
    return order


def network_for_sheet(params, sheet_key):
    for p in params:
        if (p.get("sheet_key") or p["ref_sheet"]) == sheet_key:
            return p.get("network") or ""
    return ""


def files_banner(run: RunContext) -> str:
    refs = ", ".join(p.name for p in run.reference_files) or run.reference.name
    inputs = ", ".join(p.name for p in run.input_files)
    if not inputs:
        names = [p.name for p in (run.cfg_4g, run.cfg_5g) if p]
        inputs = ", ".join(names)
    return f"Reference: {refs} | Input: {inputs} | Run {run.run_id}"


def fill_header(ws, titles, fill, font):
    for col, title in enumerate(titles, start=1):
        cell = ws.cell(1, col, title)
        cell.fill = fill
        cell.font = font
        cell.alignment = Alignment(wrap_text=True, vertical="center")


def autosize(ws, max_width=42):
    for col in ws.columns:
        letter = get_column_letter(col[0].column)
        width = 12
        for cell in col[:80]:
            if cell.value:
                width = min(max_width, max(width, min(len(str(cell.value)) + 2, max_width)))
        ws.column_dimensions[letter].width = width


def status_fill(status):
    colors = {
        "Consistent": "C6EFCE",
        "Inconsistent": "FFC7CE",
        "Mixed / Partial": "FFEB9C",
        "Not Found in Configuration": "F4B183",
        "No Recommend Value": "D9D9D9",
    }
    return PatternFill("solid", fgColor=colors.get(status, "FFFFFF"))


def write_excel(params, summary, func_summary, run: RunContext):
    run.out_xlsx.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    thin = Border(
        left=Side(style="thin", color="B0B0B0"),
        right=Side(style="thin", color="B0B0B0"),
        top=Side(style="thin", color="B0B0B0"),
        bottom=Side(style="thin", color="B0B0B0"),
    )
    header_fill = PatternFill("solid", fgColor="1F4E79")
    header_font = Font(color="FFFFFF", bold=True)
    title_font = Font(bold=True, size=14, color="1F4E79")
    section_font = Font(bold=True, size=12, color="1F4E79")

    # 1. Overall Report
    ws = wb.active
    ws.title = "1_Overall_Report"
    ws["A1"] = "Parameter Inconsistency Overall Report"
    ws["A1"].font = title_font
    ws.merge_cells("A1:G1")
    ws["A2"] = files_banner(run)
    ws.merge_cells("A2:G2")
    if run.input_folder or run.reference_folder:
        ws["A3"] = (
            f"Input Folder: {run.input_folder or '(files)'} | "
            f"Reference Folder: {run.reference_folder or '(files)'} | "
            f"Output Folder: {run.output_dir}"
        )
        ws.merge_cells("A3:J3")

    ws["A4"] = "1.1 Overall Summary (every reference file / sheet vs every input file)"
    ws["A4"].font = section_font
    headers = [
        "Reference File / Sheet",
        "Network",
        "Total Parameters",
        "Inconsistent (total)",
        "Full Inconsistent",
        "Mixed / Partial",
        "Consistent",
        "Not Found in Config",
        "No Recommend Value",
        "Inconsistency Rate (auditable)",
    ]
    for col, title in enumerate(headers, start=1):
        cell = ws.cell(5, col, title)
        cell.fill = header_fill
        cell.font = header_font

    def auditable_rate(counter):
        auditable = counter["inconsistent"] + counter["consistent"]
        if not auditable:
            return "N/A"
        return f"{counter['inconsistent'] / auditable:.1%}"

    keys = sheet_keys_in_order(params)
    rows = [(key, network_for_sheet(params, key), summary[key]) for key in keys]
    rows.append(("ALL FILES / SHEETS", "ALL", summary["ALL"]))
    for idx, (name, net, counter) in enumerate(rows, start=6):
        values = [
            name,
            net,
            counter["total"],
            counter["inconsistent"],
            counter["full_inconsistent"],
            counter["mixed"],
            counter["consistent"],
            counter["not_found"],
            counter["no_recommend"],
            auditable_rate(counter),
        ]
        for col, val in enumerate(values, start=1):
            cell = ws.cell(idx, col, val)
            cell.border = thin
            if name == "ALL FILES / SHEETS":
                cell.font = Font(bold=True)
            if col == 4 and counter["inconsistent"]:
                cell.fill = PatternFill("solid", fgColor="FFC7CE")

    note_row = 6 + len(rows) + 1
    ws.cell(note_row, 1, "Notes").font = section_font
    ws.cell(
        note_row + 1,
        1,
        "Every workbook in the Input Folder is compared against every workbook in the Reference Folder. "
        "Auditable parameters = parameters that have a Recommend Value and were found in configuration. "
        "Inconsistent (total) = Full Inconsistent + Mixed/Partial. "
        "Full Inconsistent = every object differs from recommend. "
        "Mixed/Partial = some cells/sites match and others do not. "
        "Parameters with empty Recommend Value are listed but not counted as inconsistency. "
        f"Excel sheet limit (Microsoft): {EXCEL_MAX_ROWS:,} rows x {EXCEL_MAX_COLS:,} columns. "
        "This tool does not add a lower file, sheet, or column cap.",
    )
    ws.merge_cells(start_row=note_row + 1, start_column=1, end_row=note_row + 2, end_column=10)
    ws.cell(note_row + 1, 1).alignment = Alignment(wrap_text=True, vertical="top")

    func_title_row = note_row + 4
    ws.cell(func_title_row, 1, "1.2 Function-wise Summary for individual sheet").font = section_font
    func_headers = [
        "Reference File / Sheet",
        "Function",
        "Total Parameters",
        "Inconsistent (total)",
        "Full Inconsistent",
        "Mixed / Partial",
        "Consistent",
        "Not Found",
        "No Recommend",
        "Inconsistency Rate (auditable)",
    ]
    for col, title in enumerate(func_headers, start=1):
        cell = ws.cell(func_title_row + 2, col, title)
        cell.fill = header_fill
        cell.font = header_font
    r = func_title_row + 3
    for sheet_name in keys:
        functions = sorted(func_summary[sheet_name].keys())
        for func in functions:
            counter = func_summary[sheet_name][func]
            values = [
                sheet_name,
                func,
                counter["total"],
                counter["inconsistent"],
                counter["full_inconsistent"],
                counter["mixed"],
                counter["consistent"],
                counter["not_found"],
                counter["no_recommend"],
                auditable_rate(counter),
            ]
            for col, val in enumerate(values, start=1):
                cell = ws.cell(r, col, val)
                cell.border = thin
                if counter["inconsistent"]:
                    ws.cell(r, 4).fill = PatternFill("solid", fgColor="FFC7CE")
            r += 1

    r += 2
    ws.cell(r, 1, "1.3 Material inconsistencies (mismatch count >= 10 or 100% mismatch)").font = section_font
    r += 1
    mat_headers = [
        "Reference File / Sheet",
        "Function",
        "Parameter ID",
        "Recommend",
        "Status",
        "Objects",
        "Mismatch Count",
        "Mismatch %",
        "Actual (top)",
        "Remark",
    ]
    for col, title in enumerate(mat_headers, start=1):
        cell = ws.cell(r, col, title)
        cell.fill = header_fill
        cell.font = header_font
    r += 1
    material = []
    for p in params:
        res = p["result"]
        if not is_inconsistent(res["status"]):
            continue
        mismatch_pct = res["mismatch_count"] / res["objects_checked"] if res["objects_checked"] else 0
        if res["status"] == "Inconsistent" or res["mismatch_count"] >= 10:
            material.append((mismatch_pct, p))
    material.sort(key=lambda x: (-x[0], -x[1]["result"]["mismatch_count"]))
    for _, p in material:
        res = p["result"]
        mismatch_pct = res["mismatch_count"] / res["objects_checked"] if res["objects_checked"] else 0
        values = [
            p.get("sheet_key") or p["ref_sheet"],
            p["function"],
            p["pid"],
            "" if p["recommend"] is None else p["recommend"],
            res["status"],
            res["objects_checked"],
            res["mismatch_count"],
            f"{mismatch_pct:.1%}",
            unique_actual_text(res["unique_actuals"]),
            res["remark"],
        ]
        for col, val in enumerate(values, start=1):
            cell = ws.cell(r, col, val)
            cell.border = thin
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            if col == 5:
                cell.fill = status_fill(res["status"])
        r += 1
    autosize(ws)
    ws.row_dimensions[1].height = 22
    ws.freeze_panes = "A6"

    # 2. All parameter wise
    ws2 = wb.create_sheet("2_All_Parameter_Report")
    ws2["A1"] = "All Parameter-wise Report (function wise)"
    ws2["A1"].font = title_font
    param_headers = [
        "Reference File",
        "Reference Sheet",
        "Network",
        "Function",
        "MML Object",
        "Parameter ID",
        "Recommend Value",
        "Status",
        "Input File(s)",
        "Config Sheet",
        "Config Column",
        "Bit Name",
        "Objects Checked",
        "Match Count",
        "Mismatch Count",
        "Match %",
        "Actual Value Distribution (top)",
        "Sample Mismatched Objects",
        "Remark",
    ]
    for col, title in enumerate(param_headers, start=1):
        cell = ws2.cell(3, col, title)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    ws2.row_dimensions[3].height = 32
    ordered = sorted(
        params,
        key=lambda p: (p.get("ref_file") or "", p["ref_sheet"], p["function"], p["mml"], p["pid"]),
    )
    r = 4
    for p in ordered:
        res = p["result"]
        resolved = p["resolved"]
        match_pct = ""
        if res["objects_checked"] and not is_empty(p["recommend"]):
            match_pct = f"{res['match_count'] / res['objects_checked']:.1%}"
        values = [
            p.get("ref_file") or run.reference.name,
            p["ref_sheet"],
            p.get("network") or "",
            p["function"],
            p["mml"],
            p["pid"],
            "" if p["recommend"] is None else p["recommend"],
            res["status"],
            res.get("input_files") or "",
            resolved.get("sheet") or "",
            resolved.get("column") or "",
            resolved.get("bit") or "",
            res["objects_checked"],
            res["match_count"],
            res["mismatch_count"],
            match_pct,
            unique_actual_text(res["unique_actuals"]),
            " || ".join(res["sample_mismatches"]),
            res["remark"],
        ]
        for col, val in enumerate(values, start=1):
            cell = ws2.cell(r, col, val)
            cell.border = thin
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            if col == 8:
                cell.fill = status_fill(res["status"])
        r += 1
    ws2.freeze_panes = "A4"
    ws2.auto_filter.ref = f"A3:S{max(r-1, 3)}"
    autosize(ws2, 36)
    ws2.column_dimensions["F"].width = 42
    ws2.column_dimensions["Q"].width = 50
    ws2.column_dimensions["R"].width = 45

    # 3. Sheet wise
    ws3 = wb.create_sheet("3_Sheet_Wise_Report")
    ws3["A1"] = "Sheet-wise Report"
    ws3["A1"].font = title_font
    row = 3
    for sheet_name in keys:
        network = network_for_sheet(params, sheet_name)
        counter = summary[sheet_name]
        title = f"{sheet_name}" + (f"  ({network})" if network else "")
        ws3.cell(row, 1, title).font = section_font
        row += 1
        ws3.cell(row, 1, f"Compared against all input files: {', '.join(p.name for p in run.input_files)}")
        row += 1
        stats = [
            ("Total reference parameters", counter["total"]),
            ("Inconsistent (incl. Mixed)", counter["inconsistent"]),
            ("Consistent", counter["consistent"]),
            ("Not Found in Configuration", counter["not_found"]),
            ("No Recommend Value", counter["no_recommend"]),
            ("Inconsistency rate of auditable parameters", auditable_rate(counter)),
        ]
        for label, val in stats:
            ws3.cell(row, 1, label)
            ws3.cell(row, 2, val)
            if label.startswith("Inconsistent"):
                ws3.cell(row, 2).fill = PatternFill("solid", fgColor="FFC7CE")
            row += 1
        row += 1
        ws3.cell(row, 1, "Function").font = header_font
        ws3.cell(row, 1).fill = header_fill
        for col, title in enumerate(
            ["Function", "Total", "Inconsistent", "Consistent", "Not Found", "No Recommend", "Rate"],
            start=1,
        ):
            cell = ws3.cell(row, col, title)
            cell.fill = header_fill
            cell.font = header_font
        row += 1
        for func in sorted(func_summary[sheet_name].keys()):
            c = func_summary[sheet_name][func]
            vals = [
                func,
                c["total"],
                c["inconsistent"],
                c["consistent"],
                c["not_found"],
                c["no_recommend"],
                auditable_rate(c),
            ]
            for col, val in enumerate(vals, start=1):
                cell = ws3.cell(row, col, val)
                cell.border = thin
            row += 1
        row += 1
        ws3.cell(row, 1, f"Inconsistent parameters in {sheet_name}").font = section_font
        row += 1
        for col, title in enumerate(
            ["Function", "MML Object", "Parameter ID", "Recommend", "Status", "Actual (top)", "Mismatch Count", "Input File(s)"],
            start=1,
        ):
            cell = ws3.cell(row, col, title)
            cell.fill = header_fill
            cell.font = header_font
        row += 1
        sheet_params = [
            p
            for p in ordered
            if (p.get("sheet_key") or p["ref_sheet"]) == sheet_name and is_inconsistent(p["result"]["status"])
        ]
        if not sheet_params:
            ws3.cell(row, 1, "None")
            row += 1
        for p in sheet_params:
            vals = [
                p["function"],
                p["mml"],
                p["pid"],
                "" if p["recommend"] is None else p["recommend"],
                p["result"]["status"],
                unique_actual_text(p["result"]["unique_actuals"]),
                p["result"]["mismatch_count"],
                p["result"].get("input_files") or "",
            ]
            for col, val in enumerate(vals, start=1):
                cell = ws3.cell(row, col, val)
                cell.border = thin
                cell.alignment = Alignment(wrap_text=True, vertical="top")
                if col == 5:
                    cell.fill = status_fill(p["result"]["status"])
            row += 1
        row += 2
    autosize(ws3, 40)
    ws3.column_dimensions["C"].width = 45
    ws3.column_dimensions["F"].width = 50

    # 4. Final Summary
    ws4 = wb.create_sheet("4_Final_Summary")
    ws4["A1"] = "Final Summary"
    ws4["A1"].font = title_font
    all_c = summary["ALL"]
    inconsistent_params = [p for p in ordered if is_inconsistent(p["result"]["status"])]
    consistent_params = [p for p in ordered if p["result"]["status"] == "Consistent"]
    not_found = [p for p in ordered if p["result"]["status"] == "Not Found in Configuration"]
    no_rec = [p for p in ordered if p["result"]["status"] == "No Recommend Value"]

    ref_names = ", ".join(p.name for p in run.reference_files) or run.reference.name
    in_names = ", ".join(p.name for p in run.input_files)
    lines = [
        f"Audit date: {run.audit_date}",
        f"Run ID: {run.run_id}",
        f"Reference Folder: {run.reference_folder or '(selected files)'}",
        f"Reference files ({len(run.reference_files)}): {ref_names}",
        f"Input Folder: {run.input_folder or '(selected files)'}",
        f"Input files ({len(run.input_files)}): {in_names}",
        f"Output Folder: {run.output_dir}",
        "",
        "HEADLINE",
        f"- Total reference parameters checked: {all_c['total']}",
        f"- Parameter inconsistencies (value mismatch or mixed): {all_c['inconsistent']}",
        f"  of which full inconsistent: {all_c['full_inconsistent']}, mixed/partial: {all_c['mixed']}",
        f"- Consistent parameters: {all_c['consistent']}",
        f"- Not found in configuration dumps: {all_c['not_found']}",
        f"- No recommend value (not audited): {all_c['no_recommend']}",
        f"- Combined auditable inconsistency rate: {auditable_rate(all_c)}",
        "",
        "BY REFERENCE SHEET",
    ]
    for sheet_name in keys:
        c = summary[sheet_name]
        net = network_for_sheet(params, sheet_name)
        net_txt = f" ({net})" if net else ""
        lines.append(
            f"- {sheet_name}{net_txt}: {c['total']} parameters; {c['inconsistent']} inconsistent; "
            f"{c['consistent']} consistent; {c['not_found']} not found; {c['no_recommend']} no recommend; "
            f"auditable rate {auditable_rate(c)}"
        )
    lines += [
        "",
        "FUNCTION HOTSPOTS",
    ]
    hotspots = []
    for sheet_name in keys:
        for func, c in func_summary[sheet_name].items():
            if c["inconsistent"]:
                hotspots.append((c["inconsistent"], sheet_name, func, c["total"]))
    hotspots.sort(reverse=True)
    for count, sheet_name, func, total in hotspots[:12]:
        lines.append(f"- {sheet_name} / {func}: {count} inconsistent of {total} parameters")

    lines += [
        "",
        "INTERPRETATION",
        "- Every reference workbook is fully analyzed. Every input workbook is searched for each parameter.",
        "- Sheet names in input dumps that match an MO / MML Object name are treated as that object.",
        "- Huawei dumps with a MAPPING DEF sheet are mapped by MOC/attribute; other workbooks use sheet and column names.",
        "- Switch bits (ParameterID format BIT@Attribute or Attribute@BIT) are extracted from Huawei bit-pack strings (NAME-1&NAME-0).",
        "- Mixed / Partial means some cells or sites match the recommend value and others do not; these are counted as inconsistency.",
        "- Empty Recommend Value in the reference file cannot be judged; they are excluded from the inconsistency rate.",
        f"- Microsoft Excel limit: {EXCEL_MAX_ROWS:,} rows and {EXCEL_MAX_COLS:,} columns per sheet. This tool does not add a lower cap.",
        "",
        f"See sheet 2_All_Parameter_Report for the full {all_c['total']} parameter lines, "
        f"and sheet 3_Sheet_Wise_Report for the inconsistent list of each reference sheet.",
    ]
    for idx, line in enumerate(lines, start=3):
        ws4.cell(idx, 1, line)
        if line in {"HEADLINE", "BY REFERENCE SHEET", "FUNCTION HOTSPOTS", "INTERPRETATION"}:
            ws4.cell(idx, 1).font = section_font
    ws4.column_dimensions["A"].width = 140
    ws4["A3"].alignment = Alignment(wrap_text=False)

    # helper lists
    ws5 = wb.create_sheet("5_Not_Found_No_Recommend")
    ws5["A1"] = "Parameters not found or with no recommend value"
    ws5["A1"].font = title_font
    for col, title in enumerate(
        ["Category", "Reference Sheet", "Function", "MML Object", "Parameter ID", "Recommend", "Remark"],
        start=1,
    ):
        cell = ws5.cell(3, col, title)
        cell.fill = header_fill
        cell.font = header_font
    r = 4
    for p in not_found + no_rec:
        vals = [
            p["result"]["status"],
            p["ref_sheet"],
            p["function"],
            p["mml"],
            p["pid"],
            "" if p["recommend"] is None else p["recommend"],
            p["result"]["remark"],
        ]
        for col, val in enumerate(vals, start=1):
            cell = ws5.cell(r, col, val)
            cell.border = thin
            if col == 1:
                cell.fill = status_fill(p["result"]["status"])
        r += 1
    autosize(ws5, 40)

    wb.save(run.out_xlsx)
    return {
        "inconsistent_params": inconsistent_params,
        "consistent_params": consistent_params,
        "not_found": not_found,
        "no_rec": no_rec,
        "hotspots": hotspots,
    }


def write_markdown(params, summary, func_summary, extras, run: RunContext):
    def rate(counter):
        auditable = counter["inconsistent"] + counter["consistent"]
        if not auditable:
            return "N/A"
        return f"{counter['inconsistent'] / auditable:.1%}"

    all_c = summary["ALL"]
    keys = sheet_keys_in_order(params)
    ref_names = ", ".join(f"`{p.name}`" for p in run.reference_files) or f"`{run.reference.name}`"
    in_names = ", ".join(f"`{p.name}`" for p in run.input_files)
    lines = []
    lines.append(f"# Parameter Inconsistency Report ({run.audit_date})")
    lines.append("")
    lines.append(f"Run ID: `{run.run_id}`")
    lines.append(f"Reference files: {ref_names}")
    lines.append(f"Input files: {in_names}")
    if run.input_folder:
        lines.append(f"Input Folder: `{run.input_folder}`")
    if run.reference_folder:
        lines.append(f"Reference Folder: `{run.reference_folder}`")
    lines.append(f"Output Folder: `{run.output_dir}`")
    lines.append("")
    lines.append("## 1. Overall Report")
    lines.append("")
    lines.append("### 1.1 How many parameter inconsistencies from all reference sheets")
    lines.append("")
    lines.append("| Reference File / Sheet | Network | Total | Inconsistent | Full | Mixed | Consistent | Not Found | No Recommend | Auditable Inconsistency Rate |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for name in keys:
        net = network_for_sheet(params, name)
        c = summary[name]
        lines.append(
            f"| {name} | {net} | {c['total']} | {c['inconsistent']} | {c['full_inconsistent']} | {c['mixed']} | "
            f"{c['consistent']} | {c['not_found']} | {c['no_recommend']} | {rate(c)} |"
        )
    lines.append(
        f"| ALL FILES / SHEETS | ALL | {all_c['total']} | {all_c['inconsistent']} | {all_c['full_inconsistent']} | {all_c['mixed']} | "
        f"{all_c['consistent']} | {all_c['not_found']} | {all_c['no_recommend']} | {rate(all_c)} |"
    )
    lines.append("")
    lines.append(
        f"**Headline:** {all_c['inconsistent']} of {all_c['total']} reference parameters are inconsistent "
        f"({all_c['full_inconsistent']} full mismatch, {all_c['mixed']} mixed/partial). "
        f"{all_c['consistent']} match the recommend value on all objects. "
        f"{all_c['no_recommend']} have no recommend value and were not audited. "
        f"{all_c['not_found']} could not be located in the configuration dumps."
    )
    lines.append("")
    lines.append("### 1.2 Function-wise Summary for individual sheet")
    lines.append("")
    for sheet_name in keys:
        lines.append(f"#### {sheet_name}")
        lines.append("")
        lines.append("| Function | Total | Inconsistent | Full | Mixed | Consistent | Not Found | No Recommend | Rate |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---|")
        for func in sorted(func_summary[sheet_name].keys()):
            c = func_summary[sheet_name][func]
            lines.append(
                f"| {func} | {c['total']} | {c['inconsistent']} | {c['full_inconsistent']} | {c['mixed']} | "
                f"{c['consistent']} | {c['not_found']} | {c['no_recommend']} | {rate(c)} |"
            )
        lines.append("")

    lines.append("### 1.3 Material inconsistencies")
    lines.append("")
    lines.append("Parameters with 100% mismatch, or at least 10 mismatched objects:")
    lines.append("")
    lines.append("| Sheet | Function | Parameter ID | Recommend | Status | Mismatch | Mismatch % | Actual (top) |")
    lines.append("|---|---|---|---|---|---:|---|---|")
    material = []
    for p in params:
        res = p["result"]
        if not is_inconsistent(res["status"]):
            continue
        mismatch_pct = res["mismatch_count"] / res["objects_checked"] if res["objects_checked"] else 0
        if res["status"] == "Inconsistent" or res["mismatch_count"] >= 10:
            material.append((mismatch_pct, p))
    material.sort(key=lambda x: (-x[0], -x[1]["result"]["mismatch_count"]))
    for _, p in material:
        res = p["result"]
        mismatch_pct = res["mismatch_count"] / res["objects_checked"] if res["objects_checked"] else 0
        rec = "" if p["recommend"] is None else str(p["recommend"])
        actual = unique_actual_text(res["unique_actuals"]).replace("|", "/")
        lines.append(
            f"| {p.get('sheet_key') or p['ref_sheet']} | {p['function']} | `{p['pid']}` | {rec} | {res['status']} | "
            f"{res['mismatch_count']}/{res['objects_checked']} | {mismatch_pct:.1%} | {actual} |"
        )
    lines.append("")

    lines.append("## 2. All Parameter-wise Report (function wise)")
    lines.append("")
    lines.append(f"Full line-by-line table is in `{run.out_xlsx}` sheet `2_All_Parameter_Report`.")
    lines.append("Below: every parameter grouped by reference sheet and function.")
    lines.append("")
    ordered = sorted(params, key=lambda p: (p.get("ref_file") or "", p["ref_sheet"], p["function"], p["mml"], p["pid"]))
    current = None
    for p in ordered:
        key = (p.get("sheet_key") or p["ref_sheet"], p["function"])
        if key != current:
            current = key
            lines.append(f"### {p.get('sheet_key') or p['ref_sheet']} — {p['function']}")
            lines.append("")
            lines.append("| Parameter ID | MML Object | Recommend | Status | Match | Mismatch | Actual (top) |")
            lines.append("|---|---|---|---|---:|---:|---|")
        rec = "" if p["recommend"] is None else str(p["recommend"])
        actual = unique_actual_text(p["result"]["unique_actuals"]).replace("|", "/")
        lines.append(
            f"| `{p['pid']}` | {p['mml']} | {rec} | {p['result']['status']} | "
            f"{p['result']['match_count']} | {p['result']['mismatch_count']} | {actual} |"
        )
    lines.append("")

    lines.append("## 3. Sheet-wise Report")
    lines.append("")
    for sheet_name in keys:
        c = summary[sheet_name]
        network = network_for_sheet(params, sheet_name)
        heading = f"{sheet_name} ({network})" if network else sheet_name
        lines.append(f"### {heading}")
        lines.append("")
        lines.append(f"- Total parameters: **{c['total']}**")
        lines.append(f"- Inconsistent: **{c['inconsistent']}**")
        lines.append(f"- Consistent: **{c['consistent']}**")
        lines.append(f"- Not found: **{c['not_found']}**")
        lines.append(f"- No recommend value: **{c['no_recommend']}**")
        lines.append(f"- Auditable inconsistency rate: **{rate(c)}**")
        lines.append("")
        lines.append("Inconsistent parameters:")
        lines.append("")
        lines.append("| Function | Parameter ID | Recommend | Status | Mismatch Count | Actual (top) |")
        lines.append("|---|---|---|---|---:|---|")
        sheet_incon = [
            p
            for p in ordered
            if (p.get("sheet_key") or p["ref_sheet"]) == sheet_name and is_inconsistent(p["result"]["status"])
        ]
        if not sheet_incon:
            lines.append("| — | — | — | None | 0 | — |")
        for p in sheet_incon:
            rec = "" if p["recommend"] is None else str(p["recommend"])
            actual = unique_actual_text(p["result"]["unique_actuals"]).replace("|", "/")
            lines.append(
                f"| {p['function']} | `{p['pid']}` | {rec} | {p['result']['status']} | "
                f"{p['result']['mismatch_count']} | {actual} |"
            )
        lines.append("")

    lines.append("## 4. Final Summary")
    lines.append("")
    sheet_bits = []
    for sheet_name in keys:
        c = summary[sheet_name]
        sheet_bits.append(f"{sheet_name}: {c['inconsistent']} inconsistent of {c['total']}")
    lines.append(
        f"The reference files contain **{all_c['total']}** parameters. "
        f"**{all_c['inconsistent']}** parameters are inconsistent against the input configuration dumps "
        f"({all_c['full_inconsistent']} fully mismatched, {all_c['mixed']} mixed). "
        + (" ".join(sheet_bits) + ". " if sheet_bits else "")
        + f"**{all_c['consistent']}** parameters fully match the recommend value. "
        f"**{all_c['no_recommend']}** parameters have no recommend value in the reference and were excluded "
        f"from the inconsistency rate. **{all_c['not_found']}** parameters could not be mapped to the dumps."
    )
    lines.append("")
    if extras["hotspots"]:
        lines.append("Largest function-level inconsistency counts:")
        lines.append("")
        for count, sheet_name, func, total in extras["hotspots"][:10]:
            lines.append(f"- **{sheet_name} / {func}**: {count} of {total} parameters inconsistent")
        lines.append("")
    lines.append(f"Detailed workbook: `{run.out_xlsx}`")
    run.out_md.write_text("\n".join(lines), encoding="utf-8")


def write_parameter_csv(params, run: RunContext):
    fieldnames = [
        "run_id",
        "reference_file",
        "reference_sheet",
        "network",
        "function",
        "mml_object",
        "parameter_id",
        "recommend_value",
        "status",
        "input_files",
        "config_sheet",
        "config_column",
        "bit_name",
        "objects_checked",
        "match_count",
        "mismatch_count",
        "actual_top",
        "remark",
    ]
    with run.out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for p in params:
            res = p["result"]
            resolved = p["resolved"]
            writer.writerow(
                {
                    "run_id": run.run_id,
                    "reference_file": p.get("ref_file") or run.reference.name,
                    "reference_sheet": p["ref_sheet"],
                    "network": p.get("network") or "",
                    "function": p["function"],
                    "mml_object": p["mml"],
                    "parameter_id": p["pid"],
                    "recommend_value": "" if p["recommend"] is None else p["recommend"],
                    "status": res["status"],
                    "input_files": res.get("input_files") or "",
                    "config_sheet": resolved.get("sheet") or "",
                    "config_column": resolved.get("column") or "",
                    "bit_name": resolved.get("bit") or "",
                    "objects_checked": res["objects_checked"],
                    "match_count": res["match_count"],
                    "mismatch_count": res["mismatch_count"],
                    "actual_top": unique_actual_text(res["unique_actuals"]),
                    "remark": res["remark"],
                }
            )


def rate_text(counter) -> str:
    auditable = counter["inconsistent"] + counter["consistent"]
    if not auditable:
        return "N/A"
    return f"{counter['inconsistent'] / auditable:.1%}"


def write_run_summary(summary, run: RunContext, param_count: int):
    payload = {
        "run_id": run.run_id,
        "audit_date": run.audit_date,
        "input_folder": str(run.input_folder) if run.input_folder else None,
        "reference_folder": str(run.reference_folder) if run.reference_folder else None,
        "output_folder": str(run.output_dir),
        "reference_files": [str(p) for p in run.reference_files],
        "input_files": [str(p) for p in run.input_files],
        "parameter_count": param_count,
        "overall": dict(summary["ALL"]),
        "sheets": {key: dict(counter) for key, counter in summary.items() if key != "ALL"},
        "auditable_inconsistency_rate": rate_text(summary["ALL"]),
        "excel_limits_note": f"{EXCEL_MAX_ROWS} rows x {EXCEL_MAX_COLS} columns per sheet (Microsoft Excel). No extra cap in this tool.",
        "outputs": {
            "xlsx": str(run.out_xlsx),
            "md": str(run.out_md),
            "csv": str(run.out_csv),
        },
    }
    run.out_summary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def append_history(summary, run: RunContext):
    all_c = summary["ALL"]
    fieldnames = [
        "run_id",
        "audit_date",
        "reference_files",
        "input_files",
        "total",
        "inconsistent",
        "full_inconsistent",
        "mixed",
        "consistent",
        "not_found",
        "no_recommend",
        "auditable_rate",
        "report_xlsx",
    ]
    new_file = not run.history_csv.exists()
    with run.history_csv.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if new_file:
            writer.writeheader()
        try:
            report_path = str(run.out_xlsx.relative_to(run.root))
        except ValueError:
            report_path = str(run.out_xlsx)
        writer.writerow(
            {
                "run_id": run.run_id,
                "audit_date": run.audit_date,
                "reference_files": "; ".join(p.name for p in run.reference_files) or run.reference.name,
                "input_files": "; ".join(p.name for p in run.input_files),
                "total": all_c["total"],
                "inconsistent": all_c["inconsistent"],
                "full_inconsistent": all_c["full_inconsistent"],
                "mixed": all_c["mixed"],
                "consistent": all_c["consistent"],
                "not_found": all_c["not_found"],
                "no_recommend": all_c["no_recommend"],
                "auditable_rate": rate_text(all_c),
                "report_xlsx": report_path,
            }
        )


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Compare every reference workbook with every input dump. "
        "Use three folders (Input, Reference, Output), or launch the GUI with no arguments."
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="Optional workbooks (legacy). Prefer --input-folder and --reference-folder.",
    )
    parser.add_argument("--input-folder", "--input-dir", dest="input_folder", type=Path, default=None, help="Folder of configuration dumps (any names)")
    parser.add_argument("--reference-folder", dest="reference_folder", type=Path, default=None, help="Folder of reference / plan-value workbooks (any names)")
    parser.add_argument("-o", "--output-dir", "--output-folder", dest="output_dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output folder for reports")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Optional JSON config with file patterns")
    parser.add_argument("--reference", type=Path, help="Single reference workbook (legacy)")
    parser.add_argument("--config-4g", type=Path, help="Single 4G dump (legacy)")
    parser.add_argument("--config-5g", type=Path, help="Single 5G dump (legacy)")
    parser.add_argument("--run-id", help="Optional run id; default is timestamp YYYYMMDD_HHMMSS")
    parser.add_argument("--list-inputs", action="store_true", help="Show detected input files and exit")
    parser.add_argument("--gui", action="store_true", help="Open the graphical tool")
    parser.add_argument(
        "--fail-on-inconsistent",
        action="store_true",
        help="Exit with code 1 if any auditable parameter is inconsistent",
    )
    return parser.parse_args(argv)


def resolve_required_file(label: str, explicit: Path | None, discovered: Path | None) -> Path:
    path = explicit or discovered
    if path is None or not path.exists():
        raise FileNotFoundError(
            f"{label} not found. Put the file in input/ or the repo root, or pass an explicit path."
        )
    return path.resolve()


def execute_folder_audit(
    output_dir: Path,
    input_folder: Path | None = None,
    reference_folder: Path | None = None,
    input_files=None,
    reference_files=None,
    run_id=None,
    progress=print,
):
    input_files = [Path(p).expanduser().resolve() for p in (input_files or [])]
    reference_files = [Path(p).expanduser().resolve() for p in (reference_files or [])]
    if not input_files:
        input_files = list_workbooks(input_folder)
    if not reference_files:
        reference_files = list_workbooks(reference_folder)
    if not input_files:
        raise FileNotFoundError(
            "Input Folder has no Excel workbooks (.xlsx / .xlsb / .xlsm). "
            "Put 4G dump, 5G dump, 2G dump, or any other configuration files there."
        )
    if not reference_files:
        raise FileNotFoundError(
            "Reference Folder has no Excel workbooks (.xlsx / .xlsb / .xlsm). "
            "Put every recommended/plan-value file there."
        )

    guessed_4g = next((p for p in input_files if guess_file_role(p) == "4g"), input_files[0])
    guessed_5g = next((p for p in input_files if guess_file_role(p) == "5g"), input_files[-1])
    run = build_run_context(
        root=ROOT,
        reference=reference_files[0],
        cfg_4g=guessed_4g,
        cfg_5g=guessed_5g,
        output_dir=Path(output_dir),
        run_id=run_id,
        input_folder=input_folder,
        reference_folder=reference_folder,
        input_files=input_files,
        reference_files=reference_files,
    )
    progress(f"Run ID: {run.run_id}")
    progress(f"Reference Folder: {run.reference_folder or '(files)'}")
    for path in reference_files:
        progress(f"  REF  {path.name}")
    progress(f"Input Folder: {run.input_folder or '(files)'}")
    for path in input_files:
        progress(f"  IN   {path.name}")
    progress(f"Output Folder: {run.output_dir}")
    progress("Loading reference parameters from every reference workbook...")
    params, missing_ref_sheets = load_all_references(reference_files)
    if missing_ref_sheets:
        progress(
            "  No parameter rows detected in: "
            + ", ".join(missing_ref_sheets)
            + " (need Parameter ID + Recommend Value or MML Object columns)"
        )
    progress(f"  {len(params)} parameters from {len(reference_files)} reference file(s)")
    if not params:
        raise ValueError(
            "No reference parameters found. Each reference sheet needs headers such as "
            "Function / MML Object / Parameter ID / Recommend Value (names can vary)."
        )
    progress("Indexing every input workbook (MAPPING DEF and/or sheet name as MO)...")
    store = InputStore(input_files)
    progress("Resolving and comparing each reference parameter against all input files...")
    for i, param in enumerate(params, start=1):
        resolved, result = store.compare_param(param)
        param["resolved"] = resolved
        param["result"] = result
        if i % 40 == 0:
            progress(f"  {i}/{len(params)}")
    summary, func_summary = summarize(params)
    progress("Writing reports to the Output Folder...")
    extras = write_excel(params, summary, func_summary, run)
    write_markdown(params, summary, func_summary, extras, run)
    write_parameter_csv(params, run)
    write_run_summary(summary, run, len(params))
    append_history(summary, run)
    copy_latest(run)
    progress("DONE")
    progress(f"Excel: {run.out_xlsx}")
    progress(f"Markdown: {run.out_md}")
    progress(f"CSV: {run.out_csv}")
    progress(f"Latest copy: {run.latest_dir}")
    progress("ALL " + str(dict(summary["ALL"])))
    return run, summary, extras


def execute_audit(reference: Path, cfg_4g: Path, cfg_5g: Path, output_dir: Path, run_id=None, progress=print):
    return execute_folder_audit(
        output_dir=output_dir,
        input_files=[cfg_4g, cfg_5g],
        reference_files=[reference],
        run_id=run_id,
        progress=progress,
    )


def main(argv=None):
    args = parse_args(argv)
    cfg = load_audit_config(args.config)
    input_folder = args.input_folder or DEFAULT_INPUT_DIR
    reference_folder = args.reference_folder or DEFAULT_REFERENCE_DIR
    discovered = discover_inputs(ROOT, input_folder, cfg)
    from_files = classify_input_files(args.files) if args.files else None

    if args.list_inputs:
        print("Input Folder:", input_folder)
        for path in list_workbooks(input_folder):
            print(f"  IN   {path}")
        print("Reference Folder:", reference_folder)
        for path in list_workbooks(reference_folder):
            print(f"  REF  {path}")
        print("Search folders (legacy detect):")
        for folder in discovered["search_dirs"]:
            print(f"  {folder}")
        if from_files:
            print("From selected files:")
            print(f"  Reference: {from_files['reference']}")
            print(f"  4G config: {from_files['cfg_4g']}")
            print(f"  5G config: {from_files['cfg_5g']}")
            if from_files["unknown"]:
                print(f"  Unclassified: {from_files['unknown']}")
        print(f"Legacy Reference: {discovered['reference']}")
        print(f"Legacy 4G config: {discovered['cfg_4g']}")
        print(f"Legacy 5G config: {discovered['cfg_5g']}")
        return 0

    folder_inputs = list_workbooks(input_folder)
    folder_refs = list_workbooks(reference_folder)
    use_folders = bool(args.input_folder or args.reference_folder or (folder_inputs and folder_refs))

    try:
        if use_folders and folder_inputs and folder_refs and not args.files and not args.reference:
            run, summary, extras = execute_folder_audit(
                output_dir=args.output_dir,
                input_folder=input_folder,
                reference_folder=reference_folder,
                run_id=args.run_id,
            )
        else:
            extra_inputs = []
            extra_refs = []
            if from_files:
                extra_refs.extend(from_files.get("all_reference") or [])
                extra_inputs.extend(from_files.get("all_4g") or [])
                extra_inputs.extend(from_files.get("all_5g") or [])
                extra_inputs.extend(from_files.get("unknown") or [])
            reference = args.reference
            if reference:
                extra_refs.append(Path(reference))
            if args.config_4g:
                extra_inputs.append(Path(args.config_4g))
            if args.config_5g:
                extra_inputs.append(Path(args.config_5g))
            if not extra_refs:
                extra_refs = folder_refs or ([discovered["reference"]] if discovered["reference"] else [])
            if not extra_inputs:
                extra_inputs = folder_inputs
                if not extra_inputs:
                    extra_inputs = [p for p in (discovered["cfg_4g"], discovered["cfg_5g"]) if p]
            extra_refs = unique_files(extra_refs)
            extra_inputs = unique_files(extra_inputs)
            run, summary, extras = execute_folder_audit(
                output_dir=args.output_dir,
                input_folder=args.input_folder,
                reference_folder=args.reference_folder,
                input_files=extra_inputs,
                reference_files=extra_refs,
                run_id=args.run_id,
            )
    except (FileNotFoundError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 2

    print(f"History: {run.history_csv}")
    for key, counter in summary.items():
        if key != "ALL":
            print(key, dict(counter))
    if extras["not_found"]:
        print("Not found:")
        for p in extras["not_found"]:
            print(" ", p.get("ref_file"), p["ref_sheet"], p["mml"], p["pid"], p["result"]["remark"])
    if args.fail_on_inconsistent and summary["ALL"]["inconsistent"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
