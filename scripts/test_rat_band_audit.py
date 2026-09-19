#!/usr/bin/env python3
"""RAT folders, band/group recommend rules, Parameter Name, and smart matching."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from openpyxl import Workbook

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import compare_reference_parameters as audit  # noqa: E402
import license_control as lic  # noqa: E402
import smart_match as smart  # noqa: E402


def _write_sheet(wb, name, rows):
    ws = wb.create_sheet(name)
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row, start=1):
            ws.cell(r, c, val)
    return ws


def _save(wb, path: Path):
    if "Sheet" in wb.sheetnames and len(wb.sheetnames) > 1:
        del wb["Sheet"]
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def test_rats_and_split():
    assert smart.normalize_rats("4g, nr") == ["4G", "5G"]
    assert smart.split_parameter_id("SpectralETBasedLoadEvalSw@EnhancedMlbAlgoSwitch") == (
        "EnhancedMlbAlgoSwitch",
        "SpectralETBasedLoadEvalSw",
    )
    assert smart.split_parameter_id("InterFreqIdleMlbUeNumThd") == ("InterFreqIdleMlbUeNumThd", None)
    attr, bit = smart.split_parameter_id("CaUserLoadTransferSw@EnhancedMlbAlgoSwitch")
    assert attr == "EnhancedMlbAlgoSwitch"
    assert bit == "CaUserLoadTransferSw"


def test_band_families():
    assert smart.family_for_band(8) == "L900"
    assert smart.family_for_band("3") == "L1800"
    assert smart.family_for_band(1) == "L2100"
    assert smart.family_for_band(41) == "L2600"
    assert smart.family_for_band("N41") == "L2600"
    assert smart.band_matches("L09", smart.tokens_for_family("L900", 8))
    assert smart.band_matches("L9", smart.tokens_for_family("L900", 8))
    assert smart.band_matches("L26", smart.tokens_for_family("L2600", "N41"))
    assert not smart.band_matches("L18", smart.tokens_for_family("L900", 8))


def test_recommend_parser():
    spec = smart.parse_recommend("L9: 1\nL18: 20\nL21:20\nL26: 35")
    assert spec.has_conditional
    ctx = smart.RowContext(band_family="L1800", band_tokens=smart.tokens_for_family("L1800", 3))
    value, note = smart.select_recommend(spec, ctx)
    assert value == "20"
    assert "L18" in note

    ctx900 = smart.RowContext(band_family="L900", band_tokens=smart.tokens_for_family("L900", 8))
    value, _note = smart.select_recommend(spec, ctx900)
    assert value == "1"

    grouped = smart.parse_recommend(
        "(InterFreqHoGroupId=1)=>L09=-108\n"
        "(InterFreqHoGroupId=1)=>L18=-108\n"
        "(InterFreqHoGroupId=1)=>640ms\n"
        "(InterRatHoCommGroupId=1)=>L09=-112\n"
        "(InterRatHoCommGroupId=1)=>L26=-110\n"
        "(InterRatHoCommGroupId=2)"
    )
    ctx = smart.RowContext(
        band_family="L900",
        band_tokens=smart.tokens_for_family("L900", 8),
        groups={"INTERFREQHOGROUPID": {"1"}, "INTERRATHOCOMMGROUPID": {"1"}},
    )
    value, note = smart.select_recommend(grouped, ctx)
    assert value == "-108"
    ctx_ms = smart.RowContext(
        band_tokens=set(),
        groups={"INTERFREQHOGROUPID": {"1"}},
    )
    value, _note = smart.select_recommend(grouped, ctx_ms)
    assert value == "640ms"
    ctx_ir = smart.RowContext(
        band_family="L2600",
        band_tokens=smart.tokens_for_family("L2600", 41),
        groups={"INTERRATHOCOMMGROUPID": {"1"}},
    )
    value, _note = smart.select_recommend(grouped, ctx_ir)
    assert value == "-110"


def test_three_identity_columns():
    headers = ["MML Object", "Parameter ID", "Parameter Name", "Golden"]
    mapping = audit.detect_ref_header_map(headers)
    assert mapping["mml"] == 0
    assert mapping["pid"] == 1
    assert mapping["param_name"] == 2
    assert mapping["recommend"] == 3
    assert audit.is_identity_ref_header(mapping)

    odd = ["MO Name", "Param ID", "Param Name", "Default Value", "Target Value"]
    mapping2 = audit.detect_ref_header_map(odd)
    assert "mml" in mapping2 and "pid" in mapping2 and "param_name" in mapping2
    assert "recommend" in mapping2
    # Default Value must not be treated as the recommend/proposed value
    assert mapping2["recommend"] == 4


def test_fuzzy_names():
    hit, score, why = smart.closest_name("CelAlgoSwitch", ["CellAlgoSwitch", "CellMLB"], cutoff=0.8)
    assert hit == "CellAlgoSwitch"
    hit, score, why = smart.closest_name("NRDU CEL", ["NRDUCell", "Cell"], cutoff=0.8)
    assert smart.norm_key(hit) == "NRDUCELL"


def test_simple_compare_is_fast():
    """Simple recommend values must not scan Cell/band context on every row."""
    import time

    rows = [["MODIND", "ENODEBNAME", "LOCALCELLID", "SOMEPARAM"]]
    rows.append(["*eNodeB Name", "*eNodeB Name", "*Local cell ID", "Some Param"])
    for i in range(4000):
        rows.append([None, "SITE1", i, 1])
    payload_headers = ["*eNodeB Name", "*eNodeB Name", "*Local cell ID", "Some Param"]
    header_norm = {smart.norm_key(h): i for i, h in enumerate(payload_headers)}
    sheet = {
        "headers": payload_headers,
        "header_index": {h: i for i, h in enumerate(payload_headers)},
        "header_norm": header_norm,
        "rows": rows[2:],
        "identity_idx": smart.identity_indexes(header_norm, fuzzy=False),
    }

    class FakeCache:
        def get(self, _name):
            return sheet

    param = {
        "pid": "SomeParam",
        "param_name": "Some Param",
        "recommend": "1",
        "mml": "CellAlgoSwitch",
    }
    resolved = {
        "reason": "OK",
        "sheet": "CellAlgoSwitch",
        "column": "Some Param",
        "bit": None,
        "smart_note": "",
    }
    t0 = time.perf_counter()
    out = audit.compare_param(param, resolved, FakeCache(), cell_index=None)
    elapsed = time.perf_counter() - t0
    assert out["status"] == "Consistent"
    assert out["objects_checked"] == 4000
    assert elapsed < 1.5, f"simple compare too slow: {elapsed:.2f}s"


HO_ALLOWED_PACK = (
    "SnBasedInterFreqHoSw-0&GeranSepOpMobilitySwitch-0&UtranCsftbSwitch-0"
    "&GeranCsftbSwitch-1&UtranFlashCsftbSwitch-0&GeranFlashCsftbSwitch-0"
    "&CsftbAdaptiveBlindHoSwitch-1"
)


def _switch_sheet(rows):
    headers = ["*eNodeB Name", "*Local cell ID", "Handover Allowed Switch"]
    header_norm = {smart.norm_key(h): i for i, h in enumerate(headers)}
    return {
        "headers": headers,
        "header_index": {h: i for i, h in enumerate(headers)},
        "header_norm": header_norm,
        "rows": rows,
        "identity_idx": smart.identity_indexes(header_norm, fuzzy=False),
    }


def test_switch_bits_inside_parameter_column():
    """Recommend GeranCsftbSwitch-1 must be looked up inside the packed dump column."""
    assert audit.parse_switch_recommend("1") is None
    assert audit.parse_switch_recommend("ON") is None
    assert audit.parse_switch_recommend("-108") is None
    assert audit.parse_switch_recommend("L9:1") is None
    geran = audit.parse_switch_recommend("GeranCsftbSwitch-1")
    assert geran == [("GeranCsftbSwitch", "1")]
    multi = audit.parse_switch_recommend("GeranCsftbSwitch-1&UtranCsftbSwitch-0")
    assert multi == [("GeranCsftbSwitch", "1"), ("UtranCsftbSwitch", "0")]

    packed_ok = HO_ALLOWED_PACK
    packed_off = packed_ok.replace("GeranCsftbSwitch-1", "GeranCsftbSwitch-0")
    sheet = _switch_sheet(
        [
            [None, 11, packed_ok],
            [None, 14, packed_ok],
            [None, 20, packed_ok],
            [None, 74, packed_off],
        ]
    )

    class FakeCache:
        def get(self, _name):
            return sheet

    resolved = {
        "reason": "OK",
        "sheet": "CellAlgoSwitch",
        "column": "Handover Allowed Switch",
        "bit": None,
        "smart_note": "",
    }

    geran_param = {
        "pid": "HoAllowedSwitch",
        "param_name": "Handover Allowed Switch",
        "recommend": "GeranCsftbSwitch-1",
        "mml": "CELLALGOSWITCH",
    }
    out = audit.compare_param(geran_param, dict(resolved), FakeCache(), cell_index=None)
    assert out["status"] == "Mixed / Partial"
    assert out["match_count"] == 3
    assert out["mismatch_count"] == 1
    assert out["objects_checked"] == 4
    actuals = [name for name, _n in out["unique_actuals"]]
    assert "GeranCsftbSwitch-1" in actuals
    assert "GeranCsftbSwitch-0" in actuals
    assert not any("&SnBased" in a or "SnBasedInterFreqHoSw" in a for a in actuals)

    utran0 = dict(geran_param, recommend="UtranCsftbSwitch-0")
    out0 = audit.compare_param(utran0, dict(resolved), FakeCache(), cell_index=None)
    assert out0["status"] == "Consistent"
    assert out0["match_count"] == 4

    utran1 = dict(geran_param, recommend="UtranCsftbSwitch-1")
    out1 = audit.compare_param(utran1, dict(resolved), FakeCache(), cell_index=None)
    assert out1["status"] == "Inconsistent"
    assert out1["match_count"] == 0
    assert out1["mismatch_count"] == 4

    both = dict(geran_param, recommend="GeranCsftbSwitch-1&UtranCsftbSwitch-0")
    out_both = audit.compare_param(both, dict(resolved), FakeCache(), cell_index=None)
    assert out_both["match_count"] == 3
    assert out_both["mismatch_count"] == 1

    # Direct numeric values still compare the whole cell, not bits
    num_sheet = _switch_sheet([[None, 11, 20], [None, 14, 20]])
    num_sheet["headers"] = ["*eNodeB Name", "*Local cell ID", "Some Param"]
    num_sheet["header_index"] = {h: i for i, h in enumerate(num_sheet["headers"])}
    num_sheet["header_norm"] = {smart.norm_key(h): i for i, h in enumerate(num_sheet["headers"])}

    class NumCache:
        def get(self, _name):
            return num_sheet

    num_param = {
        "pid": "SomeParam",
        "param_name": "Some Param",
        "recommend": "20",
        "mml": "CellMLB",
    }
    num_resolved = {
        "reason": "OK",
        "sheet": "CellMLB",
        "column": "Some Param",
        "bit": None,
        "smart_note": "",
    }
    num_out = audit.compare_param(num_param, num_resolved, NumCache(), cell_index=None)
    assert num_out["status"] == "Consistent"
    assert num_out["match_count"] == 2


def test_list_workbooks_rats():
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        audit.ensure_rat_input_folders(root)
        (root / "4G" / "lte.xlsx").write_bytes(b"")  # not a real xlsx, is_workbook checks suffix
        # is_workbook only checks suffix; empty file still counts as workbook by extension
        (root / "5G" / "nr.xlsx").write_bytes(b"")
        (root / "loose.xlsx").write_bytes(b"")
        only_4g = audit.list_workbooks(root, rats=["4G"], use_rat_subfolders=True)
        assert [p.name for p in only_4g] == ["lte.xlsx"]
        only_5g = audit.list_workbooks(root, rats=["5G"], use_rat_subfolders=True)
        assert [p.name for p in only_5g] == ["nr.xlsx"]
        all_rats = audit.list_workbooks(root, rats=["5G", "4G", "3G", "2G"], use_rat_subfolders=True)
        names = {p.name for p in all_rats}
        assert names == {"lte.xlsx", "nr.xlsx", "loose.xlsx"}


def _build_4g_dump(path: Path):
    wb = Workbook()
    _write_sheet(
        wb,
        "Cell",
        [
            ["MODIND", "ENODEBNAME", "LOCALCELLID", "FREQUENCYBAND"],
            ["*eNodeB Name", "*eNodeB Name", "*Local cell ID", "Frequency band"],
            [None, "DHAPT08", 11, 8],
            [None, "DHAPT08", 14, 3],
            [None, "DHAPT08", 20, 1],
            [None, "DHAPT08", 74, 41],
        ],
    )
    _write_sheet(
        wb,
        "CellAlgoSwitch",
        [
            ["MODIND", "ENODEBNAME", "LOCALCELLID", "ENHANCEDMLBALGOSWITCH", "HOALLOWEDSWITCH"],
            [
                "*eNodeB Name",
                "*eNodeB Name",
                "*Local cell ID",
                "Enhanced MLB Algorithm Switch",
                "Handover Allowed Switch",
            ],
            [
                None,
                "DHAPT08",
                11,
                "SpectralETBasedLoadEvalSw-1&OtherSw-0",
                "SnBasedInterFreqHoSw-0&GeranSepOpMobilitySwitch-0&UtranCsftbSwitch-0&GeranCsftbSwitch-1&UtranFlashCsftbSwitch-0&GeranFlashCsftbSwitch-0&CsftbAdaptiveBlindHoSwitch-1",
            ],
            [
                None,
                "DHAPT08",
                14,
                "SpectralETBasedLoadEvalSw-1&OtherSw-0",
                "SnBasedInterFreqHoSw-0&GeranSepOpMobilitySwitch-0&UtranCsftbSwitch-0&GeranCsftbSwitch-1&UtranFlashCsftbSwitch-0&GeranFlashCsftbSwitch-0&CsftbAdaptiveBlindHoSwitch-1",
            ],
            [
                None,
                "DHAPT08",
                20,
                "SpectralETBasedLoadEvalSw-0&OtherSw-0",
                "SnBasedInterFreqHoSw-0&GeranSepOpMobilitySwitch-0&UtranCsftbSwitch-0&GeranCsftbSwitch-1&UtranFlashCsftbSwitch-0&GeranFlashCsftbSwitch-0&CsftbAdaptiveBlindHoSwitch-1",
            ],
            [
                None,
                "DHAPT08",
                74,
                "SpectralETBasedLoadEvalSw-1&OtherSw-0",
                "SnBasedInterFreqHoSw-0&GeranSepOpMobilitySwitch-0&UtranCsftbSwitch-0&GeranCsftbSwitch-0&UtranFlashCsftbSwitch-0&GeranFlashCsftbSwitch-0&CsftbAdaptiveBlindHoSwitch-1",
            ],
        ],
    )
    _write_sheet(
        wb,
        "CellMLB",
        [
            ["MODIND", "ENODEBNAME", "LOCALCELLID", "INTERFREQIDLEMLBUENUMTHD"],
            ["*eNodeB Name", "*eNodeB Name", "*Local cell ID", "Inter-Freq Idle MLB UE Number Threshold"],
            [None, "DHAPT08", 11, 1],
            [None, "DHAPT08", 14, 20],
            [None, "DHAPT08", 20, 20],
            [None, "DHAPT08", 74, 99],
        ],
    )
    _write_sheet(
        wb,
        "InterFreqHoGroup",
        [
            ["MODIND", "ENODEBNAME", "LOCALCELLID", "INTERFREQHOGROUPID", "A3OFFSET"],
            ["*eNodeB Name", "*eNodeB Name", "*Local cell ID", "*Interfreq handover group ID", "A3 Offset"],
            [None, "DHAPT08", 11, 1, -108],
            [None, "DHAPT08", 14, 1, -108],
            [None, "DHAPT08", 20, 1, -100],
            [None, "DHAPT08", 74, 0, -108],
        ],
    )
    _save(wb, path)


def _build_5g_dump(path: Path):
    wb = Workbook()
    _write_sheet(
        wb,
        "NRDUCell",
        [
            ["MODIND", "GNODEBNAME", "NRDUCELLID", "NRDUCELLNAME", "FREQUENCYBAND"],
            ["*gNodeB Name", "*gNodeB Name", "*NR DU Cell ID", "*NR DU Cell Name", "*Frequency Band"],
            [None, "TNMDP05", 102, "TNMDP05N26B", "N41"],
            [None, "GPSDRP7", 101, "GPSDRP7N26A", "N41"],
        ],
    )
    _write_sheet(
        wb,
        "NRDUCellAlgoSwitch",
        [
            ["MODIND", "GNODEBNAME", "NRDUCELLID", "SOMEALGOSWITCH"],
            ["*gNodeB Name", "*gNodeB Name", "*NR DU Cell ID", "Some Algo Switch"],
            [None, "TNMDP05", 102, "DemoSw-1"],
            [None, "GPSDRP7", 101, "DemoSw-1"],
        ],
    )
    _save(wb, path)


def _build_reference(path: Path):
    wb = Workbook()
    _write_sheet(
        wb,
        "MLB Plan",
        [
            ["MO Name", "Parameter ID", "Parameter Name", "Default Value", "Proposed Value"],
            [
                "CellAlgoSwitch",
                "SpectralETBasedLoadEvalSw@EnhancedMlbAlgoSwitch",
                "Enhanced MLB Algorithm Switch",
                "Off",
                "L9: 1\nL18: 1\nL21: 1\nL26: 1",
            ],
            [
                "Cell MLB",  # spaced / informal MO name — smart matching should recover CellMLB
                "InterFreqIdleMlbUeNumThd",
                "Inter-Freq Idle MLB UE Number Threshold",
                "100",
                "L9: 1\nL18: 20\nL21: 20\nL26: 35",
            ],
            [
                "InterFreqHoGroup",
                "A3Offset",
                "A3 Offset",
                "",
                "(InterFreqHoGroupId=1)=>L09=-108\n(InterFreqHoGroupId=1)=>L18=-108\n(InterFreqHoGroupId=1)=>L21=-108",
            ],
        ],
    )
    _write_sheet(
        wb,
        "Missing Name",
        [
            ["MO Name", "Parameter ID", "Default Value", "Proposed Value"],
            ["CellMLB", "Something@OtherSwitch", "Off", "1"],
        ],
    )
    _write_sheet(
        wb,
        "Legacy",
        [
            ["Function", "MML Object", "Parameter ID", "Recommend Value"],
            ["Idle", "CellMLB", "InterFreqIdleMlbUeNumThd", "20"],
        ],
    )
    _write_sheet(
        wb,
        "Three Keys",
        [
            ["MML Object", "Parameter ID", "Parameter Name", "Golden"],
            [
                "CellAlgoSwitch",
                "SpectralETBasedLoadEvalSw@EnhancedMlbAlgoSwitch",
                "Enhanced MLB Algorithm Switch",
                "1",
            ],
            [
                "CELLALGOSWITCH",
                "HoAllowedSwitch",
                "Handover Allowed Switch",
                "GeranCsftbSwitch-1",
            ],
            [
                "CELLALGOSWITCH",
                "HoAllowedSwitch",
                "Handover Allowed Switch",
                "UtranCsftbSwitch-0",
            ],
            [
                "CELLALGOSWITCH",
                "HoAllowedSwitch",
                "Handover Allowed Switch",
                "UtranCsftbSwitch-1",
            ],
        ],
    )
    _save(wb, path)


def test_end_to_end_audit():
    key = lic.find_private_key_path()
    assert key is not None, "private key required for licensed audit test"
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        input_dir = root / "Input"
        ref_dir = root / "Reference"
        out_dir = root / "Output"
        _build_4g_dump(input_dir / "4G" / "lte_dump.xlsx")
        _build_5g_dump(input_dir / "5G" / "nr_dump.xlsx")
        _build_reference(ref_dir / "plan.xlsx")
        license_path = root / "test.lic"
        lic.write_license(lic.issue_license("Test", days=7, private_key_path=key), license_path)

        only_4g = audit.list_workbooks(input_dir, rats=["4G"], use_rat_subfolders=True)
        assert [p.name for p in only_4g] == ["lte_dump.xlsx"]
        only_5g = audit.list_workbooks(input_dir, rats=["5G"], use_rat_subfolders=True)
        assert [p.name for p in only_5g] == ["nr_dump.xlsx"]

        run, summary, _extras = audit.execute_folder_audit(
            output_dir=out_dir,
            input_folder=input_dir,
            reference_folder=ref_dir,
            license_file=license_path,
            rats=["4G"],
            progress=lambda *_a, **_k: None,
        )
        params = _params_from_csv(run.out_csv)
        mlb_switch = next(p for p in params if "SpectralETBasedLoadEvalSw" in p["parameter_id"])
        assert mlb_switch["status"] in {"Mixed / Partial", "Inconsistent"}
        # L21 cell (local 20) has bit 0, others 1 → mixed
        assert int(mlb_switch["mismatch_count"]) >= 1
        assert int(mlb_switch["match_count"]) >= 1

        thd = next(p for p in params if p["parameter_id"] == "InterFreqIdleMlbUeNumThd" and p["reference_sheet"] == "MLB Plan")
        assert thd["status"] in {"Mixed / Partial", "Inconsistent"}
        # L26 cell 74 has 99 vs expected 35
        assert int(thd["mismatch_count"]) >= 1

        missing = next(p for p in params if p["reference_sheet"] == "Missing Name")
        assert missing["status"] == "No Recommend Value"
        assert "Parameter Name" in missing["remark"]

        group = next(p for p in params if p["parameter_id"] == "A3Offset")
        assert int(group["objects_checked"]) >= 1
        # group 0 cell skipped; L21 group 1 has -100 vs -108
        assert int(group["mismatch_count"]) >= 1

        legacy = next(p for p in params if p["reference_sheet"] == "Legacy")
        assert legacy["status"] in {"Mixed / Partial", "Inconsistent", "Consistent"}

        three = next(p for p in params if p["reference_sheet"] == "Three Keys" and "SpectralETBasedLoadEvalSw" in p["parameter_id"])
        assert three["parameter_name"] == "Enhanced MLB Algorithm Switch"
        assert three["status"] in {"Mixed / Partial", "Inconsistent", "Consistent"}
        assert int(three["objects_checked"]) >= 1

        geran = next(
            p
            for p in params
            if p["reference_sheet"] == "Three Keys" and p["recommend_value"] == "GeranCsftbSwitch-1"
        )
        assert geran["status"] == "Mixed / Partial"
        assert int(geran["match_count"]) == 3
        assert int(geran["mismatch_count"]) == 1
        assert "GeranCsftbSwitch" in (geran.get("bit_name") or "")

        utran_off = next(
            p
            for p in params
            if p["reference_sheet"] == "Three Keys" and p["recommend_value"] == "UtranCsftbSwitch-0"
        )
        assert utran_off["status"] == "Consistent"
        assert int(utran_off["match_count"]) == 4

        utran_on = next(
            p
            for p in params
            if p["reference_sheet"] == "Three Keys" and p["recommend_value"] == "UtranCsftbSwitch-1"
        )
        assert utran_on["status"] == "Inconsistent"
        assert int(utran_on["match_count"]) == 0
        assert int(utran_on["mismatch_count"]) == 4

        assert run.out_xlsx.exists()
        assert "4G" in ",".join(run.selected_rats)


def _params_from_csv(path: Path):
    import csv

    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    test_rats_and_split()
    test_band_families()
    test_recommend_parser()
    test_three_identity_columns()
    test_fuzzy_names()
    test_simple_compare_is_fast()
    test_switch_bits_inside_parameter_column()
    test_list_workbooks_rats()
    test_end_to_end_audit()
    print("rat-band-smart-audit tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
