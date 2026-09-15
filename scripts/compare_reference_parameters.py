#!/usr/bin/env python3
"""Compare Reference Parameter_v1.0 against 4G and 5G configuration dumps."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from pyxlsb import open_workbook

ROOT = Path("/workspace")
REF_PATH = ROOT / "Reference Parameter_v1.0.xlsx"
CFG_4G = ROOT / "4G_ConfigurationData_15Sep26.xlsb"
CFG_5G = ROOT / "5G_ConfigurationData_15Sep26.xlsb"
OUT_DIR = ROOT / "reports"
OUT_XLSX = OUT_DIR / "Parameter_Inconsistency_Report_15Sep26.xlsx"
OUT_MD = OUT_DIR / "Parameter_Inconsistency_Report_15Sep26.md"

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
    with open_workbook(str(path)) as wb:
        with wb.get_sheet("MAPPING DEF") as sheet:
            rows = [[c.v for c in row] for row in sheet.rows()]
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

    def get(self, sheet_name: str):
        if sheet_name in self.cache:
            return self.cache[sheet_name]
        with open_workbook(str(self.path)) as wb:
            if sheet_name not in wb.sheets:
                self.cache[sheet_name] = None
                return None
            with wb.get_sheet(sheet_name) as sheet:
                rows = [[c.v for c in row] for row in sheet.rows()]
        if len(rows) < 2:
            self.cache[sheet_name] = None
            return None
        headers = [clean_text(h) if h is not None else f"col_{i}" for i, h in enumerate(rows[1])]
        header_index = {h: i for i, h in enumerate(headers)}
        header_norm = {norm_key(h): i for i, h in enumerate(headers)}
        records = []
        for row in rows[2:]:
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
            "Recommend is band name N41, but DlArfcn in dump is numeric ARFCN 528990 "
            "(n41 channel). Frequency Band column on the same MO is N41."
        )
    elif pid == "FREQUENCYBAND" and out["status"] == "Inconsistent":
        out["remark"] = (
            "Recommend NULL but Frequency Band is N41 on all records. "
            "Additional Frequency Band is NULL; reference may have intended that field."
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


def load_reference():
    wb = load_workbook(REF_PATH, data_only=True)
    params = []
    for sheet_name in ["NR Performance", "NR Anchor"]:
        ws = wb[sheet_name]
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            func, mml, pid, rec = (list(row) + [None, None, None, None])[:4]
            if is_empty(mml) and is_empty(pid):
                continue
            params.append(
                {
                    "ref_sheet": sheet_name,
                    "ref_row": row_idx,
                    "function": clean_text(func) or "Unspecified",
                    "mml": clean_text(mml),
                    "pid": clean_text(pid),
                    "recommend": rec if not is_empty(rec) else None,
                    "network": "5G" if sheet_name == "NR Performance" else "4G",
                }
            )
    return params


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
        summary[p["ref_sheet"]][bucket] += 1
        summary["ALL"][bucket] += 1
        func_summary[p["ref_sheet"]][p["function"]][bucket] += 1
        func_summary[p["ref_sheet"]][p["function"]]["total"] += 1
        summary[p["ref_sheet"]]["total"] += 1
        summary["ALL"]["total"] += 1
        if bucket in {"full_inconsistent", "mixed"}:
            summary[p["ref_sheet"]]["inconsistent"] += 1
            summary["ALL"]["inconsistent"] += 1
            func_summary[p["ref_sheet"]][p["function"]]["inconsistent"] += 1
    return summary, func_summary


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


def write_excel(params, summary, func_summary):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
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
    ws["A2"] = (
        "Reference: Reference Parameter_v1.0.xlsx | "
        "Compared with 4G_ConfigurationData_15Sep26.xlsb (NR Anchor) and "
        "5G_ConfigurationData_15Sep26.xlsb (NR Performance)"
    )
    ws.merge_cells("A2:G2")

    ws["A4"] = "1.1 Overall Summary (both reference sheets)"
    ws["A4"].font = section_font
    headers = [
        "Reference Sheet",
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

    rows = [
        ("NR Performance", "5G", summary["NR Performance"]),
        ("NR Anchor", "4G", summary["NR Anchor"]),
        ("BOTH SHEETS", "4G+5G", summary["ALL"]),
    ]
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
            if idx == 8:
                cell.font = Font(bold=True)
            if col == 4 and counter["inconsistent"]:
                cell.fill = PatternFill("solid", fgColor="FFC7CE")

    ws["A10"] = "Notes"
    ws["A10"].font = section_font
    ws["A11"] = (
        "Auditable parameters = parameters that have a Recommend Value and were found in configuration. "
        "Inconsistent (total) = Full Inconsistent + Mixed/Partial. "
        "Full Inconsistent = every object differs from recommend. "
        "Mixed/Partial = some cells/sites match and others do not. "
        "Parameters with empty Recommend Value are listed but not counted as inconsistency."
    )
    ws.merge_cells("A11:J12")
    ws["A11"].alignment = Alignment(wrap_text=True, vertical="top")

    ws["A14"] = "1.2 Function-wise Summary for individual sheet"
    ws["A14"].font = section_font
    func_headers = [
        "Reference Sheet",
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
        cell = ws.cell(16, col, title)
        cell.fill = header_fill
        cell.font = header_font
    r = 17
    for sheet_name in ["NR Performance", "NR Anchor"]:
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
        "Reference Sheet",
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
            p["ref_sheet"],
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
        "Reference Sheet",
        "Network",
        "Function",
        "MML Object",
        "Parameter ID",
        "Recommend Value",
        "Status",
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
        key=lambda p: (p["ref_sheet"], p["function"], p["mml"], p["pid"]),
    )
    r = 4
    for p in ordered:
        res = p["result"]
        resolved = p["resolved"]
        match_pct = ""
        if res["objects_checked"] and not is_empty(p["recommend"]):
            match_pct = f"{res['match_count'] / res['objects_checked']:.1%}"
        values = [
            p["ref_sheet"],
            p["network"],
            p["function"],
            p["mml"],
            p["pid"],
            "" if p["recommend"] is None else p["recommend"],
            res["status"],
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
            if col == 7:
                cell.fill = status_fill(res["status"])
        r += 1
    ws2.freeze_panes = "A4"
    ws2.auto_filter.ref = f"A3:Q{r-1}"
    autosize(ws2, 36)
    ws2.column_dimensions["E"].width = 42
    ws2.column_dimensions["O"].width = 50
    ws2.column_dimensions["P"].width = 45

    # 3. Sheet wise
    ws3 = wb.create_sheet("3_Sheet_Wise_Report")
    ws3["A1"] = "Sheet-wise Report"
    ws3["A1"].font = title_font
    row = 3
    for sheet_name, network, cfg_name in [
        ("NR Performance", "5G", "5G_ConfigurationData_15Sep26.xlsb"),
        ("NR Anchor", "4G", "4G_ConfigurationData_15Sep26.xlsb"),
    ]:
        counter = summary[sheet_name]
        ws3.cell(row, 1, f"{sheet_name}  ({network})").font = section_font
        row += 1
        ws3.cell(row, 1, f"Source configuration: {cfg_name}")
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
            ["Function", "MML Object", "Parameter ID", "Recommend", "Status", "Actual (top)", "Mismatch Count"],
            start=1,
        ):
            cell = ws3.cell(row, col, title)
            cell.fill = header_fill
            cell.font = header_font
        row += 1
        sheet_params = [
            p
            for p in ordered
            if p["ref_sheet"] == sheet_name and is_inconsistent(p["result"]["status"])
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
    nrp = summary["NR Performance"]
    nra = summary["NR Anchor"]
    inconsistent_params = [p for p in ordered if is_inconsistent(p["result"]["status"])]
    consistent_params = [p for p in ordered if p["result"]["status"] == "Consistent"]
    not_found = [p for p in ordered if p["result"]["status"] == "Not Found in Configuration"]
    no_rec = [p for p in ordered if p["result"]["status"] == "No Recommend Value"]

    lines = [
        "Audit date: 15 Sep 2026",
        "Baseline: Reference Parameter_v1.0.xlsx (sheets NR Performance, NR Anchor)",
        "Live data: 4G_ConfigurationData_15Sep26.xlsb and 5G_ConfigurationData_15Sep26.xlsb",
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
        f"- NR Performance (5G): {nrp['total']} parameters; {nrp['inconsistent']} inconsistent; "
        f"{nrp['consistent']} consistent; {nrp['not_found']} not found; {nrp['no_recommend']} no recommend; "
        f"auditable rate {auditable_rate(nrp)}",
        f"- NR Anchor (4G): {nra['total']} parameters; {nra['inconsistent']} inconsistent; "
        f"{nra['consistent']} consistent; {nra['not_found']} not found; {nra['no_recommend']} no recommend; "
        f"auditable rate {auditable_rate(nra)}",
        "",
        "FUNCTION HOTSPOTS",
    ]
    hotspots = []
    for sheet_name in ["NR Performance", "NR Anchor"]:
        for func, c in func_summary[sheet_name].items():
            if c["inconsistent"]:
                hotspots.append((c["inconsistent"], sheet_name, func, c["total"]))
    hotspots.sort(reverse=True)
    for count, sheet_name, func, total in hotspots[:12]:
        lines.append(f"- {sheet_name} / {func}: {count} inconsistent of {total} parameters")

    lines += [
        "",
        "INTERPRETATION",
        "- NR Performance is compared against the 5G configuration workbook (gNodeB / NR DU cell MOs).",
        "- NR Anchor is compared against the 4G configuration workbook (eNodeB NSA anchoring / SCG / ANR MOs).",
        "- Switch bits (ParameterID format BIT@Attribute or Attribute@BIT) are extracted from Huawei bit-pack strings (NAME-1&NAME-0).",
        "- Mixed / Partial means some cells or sites match the recommend value and others do not; these are counted as inconsistency.",
        "- Empty Recommend Value in the reference file cannot be judged; they are excluded from the inconsistency rate.",
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

    wb.save(OUT_XLSX)
    return {
        "inconsistent_params": inconsistent_params,
        "consistent_params": consistent_params,
        "not_found": not_found,
        "no_rec": no_rec,
        "hotspots": hotspots,
    }


def write_markdown(params, summary, func_summary, extras):
    def rate(counter):
        auditable = counter["inconsistent"] + counter["consistent"]
        if not auditable:
            return "N/A"
        return f"{counter['inconsistent'] / auditable:.1%}"

    all_c = summary["ALL"]
    nrp = summary["NR Performance"]
    nra = summary["NR Anchor"]
    lines = []
    lines.append("# Parameter Inconsistency Report (15 Sep 2026)")
    lines.append("")
    lines.append("Baseline: `Reference Parameter_v1.0.xlsx`")
    lines.append("Compared with: `4G_ConfigurationData_15Sep26.xlsb` and `5G_ConfigurationData_15Sep26.xlsb`")
    lines.append("")
    lines.append("## 1. Overall Report")
    lines.append("")
    lines.append("### 1.1 How many parameter inconsistencies from both sheets")
    lines.append("")
    lines.append("| Reference Sheet | Network | Total | Inconsistent | Full | Mixed | Consistent | Not Found | No Recommend | Auditable Inconsistency Rate |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for name, net, c in [
        ("NR Performance", "5G", nrp),
        ("NR Anchor", "4G", nra),
        ("BOTH SHEETS", "4G+5G", all_c),
    ]:
        lines.append(
            f"| {name} | {net} | {c['total']} | {c['inconsistent']} | {c['full_inconsistent']} | {c['mixed']} | "
            f"{c['consistent']} | {c['not_found']} | {c['no_recommend']} | {rate(c)} |"
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
    for sheet_name in ["NR Performance", "NR Anchor"]:
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
            f"| {p['ref_sheet']} | {p['function']} | `{p['pid']}` | {rec} | {res['status']} | "
            f"{res['mismatch_count']}/{res['objects_checked']} | {mismatch_pct:.1%} | {actual} |"
        )
    lines.append("")

    lines.append("## 2. All Parameter-wise Report (function wise)")
    lines.append("")
    lines.append("Full line-by-line table is in `reports/Parameter_Inconsistency_Report_15Sep26.xlsx` sheet `2_All_Parameter_Report`.")
    lines.append("Below: every parameter grouped by reference sheet and function.")
    lines.append("")
    ordered = sorted(params, key=lambda p: (p["ref_sheet"], p["function"], p["mml"], p["pid"]))
    current = None
    for p in ordered:
        key = (p["ref_sheet"], p["function"])
        if key != current:
            current = key
            lines.append(f"### {p['ref_sheet']} — {p['function']}")
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
    for sheet_name, network in [("NR Performance", "5G"), ("NR Anchor", "4G")]:
        c = summary[sheet_name]
        lines.append(f"### {sheet_name} ({network})")
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
            if p["ref_sheet"] == sheet_name and is_inconsistent(p["result"]["status"])
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
    lines.append(
        f"The reference file contains **{all_c['total']}** parameters across two sheets. "
        f"**{all_c['inconsistent']}** parameters are inconsistent against live 4G/5G configuration "
        f"({all_c['full_inconsistent']} fully mismatched, {all_c['mixed']} mixed). "
        f"NR Performance / 5G: {nrp['inconsistent']} inconsistent of {nrp['total']}. "
        f"NR Anchor / 4G: {nra['inconsistent']} inconsistent of {nra['total']}. "
        f"**{all_c['consistent']}** parameters fully match the recommend value. "
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
    lines.append("Detailed workbook: `reports/Parameter_Inconsistency_Report_15Sep26.xlsx`")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main():
    print("Loading reference parameters...")
    params = load_reference()
    print(f"  {len(params)} parameters")
    print("Loading mapping definitions...")
    maps = {
        "5G": load_mapping(CFG_5G),
        "4G": load_mapping(CFG_4G),
    }
    caches = {
        "5G": SheetCache(CFG_5G),
        "4G": SheetCache(CFG_4G),
    }
    print("Resolving and comparing...")
    for i, param in enumerate(params, start=1):
        mapping = maps[param["network"]]
        resolved = resolve_parameter(param, mapping)
        result = compare_param(param, resolved, caches[param["network"]])
        param["resolved"] = resolved
        param["result"] = result
        if i % 40 == 0:
            print(f"  {i}/{len(params)}")
    summary, func_summary = summarize(params)
    print("Writing Excel and Markdown...")
    extras = write_excel(params, summary, func_summary)
    write_markdown(params, summary, func_summary, extras)
    print("DONE")
    print(f"Excel: {OUT_XLSX}")
    print(f"Markdown: {OUT_MD}")
    print("ALL", dict(summary["ALL"]))
    print("NR Performance", dict(summary["NR Performance"]))
    print("NR Anchor", dict(summary["NR Anchor"]))
    print("Not found:")
    for p in extras["not_found"]:
        print(" ", p["ref_sheet"], p["mml"], p["pid"], p["result"]["remark"])


if __name__ == "__main__":
    main()
