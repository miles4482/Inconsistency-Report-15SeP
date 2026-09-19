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
            ["MODIND", "ENODEBNAME", "LOCALCELLID", "ENHANCEDMLBALGOSWITCH"],
            ["*eNodeB Name", "*eNodeB Name", "*Local cell ID", "Enhanced MLB Algorithm Switch"],
            [
                None,
                "DHAPT08",
                11,
                "SpectralETBasedLoadEvalSw-1&OtherSw-0",
            ],
            [
                None,
                "DHAPT08",
                14,
                "SpectralETBasedLoadEvalSw-1&OtherSw-0",
            ],
            [
                None,
                "DHAPT08",
                20,
                "SpectralETBasedLoadEvalSw-0&OtherSw-0",
            ],
            [
                None,
                "DHAPT08",
                74,
                "SpectralETBasedLoadEvalSw-1&OtherSw-0",
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

        three = next(p for p in params if p["reference_sheet"] == "Three Keys")
        assert three["parameter_name"] == "Enhanced MLB Algorithm Switch"
        assert three["status"] in {"Mixed / Partial", "Inconsistent", "Consistent"}
        assert int(three["objects_checked"]) >= 1

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
    test_list_workbooks_rats()
    test_end_to_end_audit()
    print("rat-band-smart-audit tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
