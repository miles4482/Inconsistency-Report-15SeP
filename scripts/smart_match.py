#!/usr/bin/env python3
"""Local 'AI thinking' helpers for Parameter Audit.

No cloud model is used. The EXE identifies mistyped MO / parameter / band
names with aliases, tokenization, and fuzzy matching.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Iterable


RAT_FOLDERS = ("5G", "4G", "3G", "2G")
RAT_ALIASES = {
    "5G": ("5G", "5g", "NR", "nr", "NSA"),
    "4G": ("4G", "4g", "LTE", "lte", "EUTRAN"),
    "3G": ("3G", "3g", "UMTS", "umts", "WCDMA"),
    "2G": ("2G", "2g", "GSM", "gsm"),
}

# LTE EARFCN / NR operating-band → the L09/L18/L21/L26 families used in plan files.
BAND_FAMILIES = {
    "L900": frozenset({"L9", "L09", "L090", "L900", "B8", "BAND8", "NB8", "8", "900"}),
    "L1800": frozenset({"L18", "L1800", "B3", "BAND3", "NB3", "3", "1800"}),
    "L2100": frozenset({"L21", "L2100", "B1", "BAND1", "NB1", "1", "2100"}),
    "L2600": frozenset({"L26", "L2600", "B41", "BAND41", "NB41", "N41", "NR41", "41", "2600"}),
}

EARFCN_TO_FAMILY = {
    "8": "L900",
    "3": "L1800",
    "1": "L2100",
    "41": "L2600",
}

SHEET_ALIASES = {
    "CELL": ("CELL", "EUTRANCELL", "EUTRANCELLFDD", "EUTRANCELLTDD", "LTECELL"),
    "NRDUCELL": ("NRDUCELL", "NRDU CEL", "NRDUCELL", "GNBDUCELL", "GNODEBDUCELL"),
    "INTERFREQHOGROUP": ("INTERFREQHOGROUP", "INTERFREQHOCOMMGROUP", "INTERFREQHO"),
    "INTERRATHOCOMM": ("INTERRATHOCOMM", "INTERRATHOCOMMGROUP", "INTERRATHO"),
}

MO_ALIASES = {
    "CELLALGOSWITCH": ("CELALGOSWITCH", "CELLALGO SWITCH", "CELLALGOSW"),
    "CELLMLB": ("CELL MLB", "CELMLB"),
    "NRDUCELL": ("NRDU CELL", "NR DU CELL", "NRDUCEL"),
}

GROUP_NAME_ALIASES = {
    "INTERFREQHOGROUPID": (
        "INTERFREQHOGROUPID",
        "INTERFREQHANDOVERGROUPID",
        "INTERFREQHOGROUP",
        "COMMGROUPID",
    ),
    "INTERRATHOCOMMGROUPID": (
        "INTERRATHOCOMMGROUPID",
        "INTERRATHOCOMMGROUP",
        "INTERRATCOMMGROUPID",
        "COMMGROUPID",
    ),
}

SITE_HEADER_KEYS = (
    "ENODEBNAME",
    "GNODEBNAME",
    "NENAME",
    "NODEBNAME",
    "BTSNAME",
    "ENBNAME",
    "GNBNAME",
)
CELL_ID_HEADER_KEYS = (
    "LOCALCELLID",
    "NRDUCELLID",
    "CELLID",
    "LCELLID",
)
CELL_NAME_HEADER_KEYS = (
    "NRDUCELLNAME",
    "CELLNAME",
    "LOCALCELLNAME",
)
BAND_HEADER_KEYS = (
    "FREQUENCYBAND",
    "FREQBAND",
    "BAND",
    "BANDIND",
    "OPERATINGBAND",
)
GROUP_HEADER_KEYS = (
    "INTERFREQHOGROUPID",
    "INTERFREQHANDOVERGROUPID",
    "INTERRATHOCOMMGROUPID",
    "INTERRATHOGROUPID",
    "COMMGROUPID",
    "GROUPID",
)

TRUE_SET = {"1", "1.0", "ON", "TRUE", "YES", "ENABLE", "ENABLED"}
FALSE_SET = {"0", "0.0", "OFF", "FALSE", "NO", "DISABLE", "DISABLED"}
UNIT_RE = re.compile(r"^(-?\d+(?:\.\d+)?)(MS|S|DBM|DB|MHZ|KHZ|MIN|DAY)?$", re.I)
NON_ALNUM = re.compile(r"[^A-Z0-9]+")

BAND_TOKEN_RE = re.compile(
    r"\b(L0?9(?:00)?|L18(?:00)?|L21(?:00)?|L26(?:00)?|N\d{1,3}|B\d{1,3})\b",
    re.I,
)
BAND_VALUE_RE = re.compile(
    r"\b(L0?9(?:00)?|L18(?:00)?|L21(?:00)?|L26(?:00)?|N\d{1,3}|B\d{1,3})"
    r"(?:\s*/\s*(?:L0?9(?:00)?|L18(?:00)?|L21(?:00)?|L26(?:00)?|N\d{1,3}|B\d{1,3}))*"
    r"\s*[:=]\s*([^\n;]+)",
    re.I,
)
GROUP_LINE_RE = re.compile(
    r"\(\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*([^)]+?)\s*\)\s*(?:=>|=)?\s*(.*)$",
)


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


def tokens(value: str) -> list[str]:
    compact = NON_ALNUM.sub(" ", clean_text(value).upper())
    return [t for t in compact.split() if t]


def similarity(left: str, right: str) -> float:
    a, b = norm_key(left), norm_key(right)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if a in b or b in a:
        shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
        if len(shorter) >= 4:
            return max(0.82, len(shorter) / len(longer))
    ratio = SequenceMatcher(None, a, b).ratio()
    ta, tb = set(tokens(left)), set(tokens(right))
    if ta and tb:
        overlap = len(ta & tb) / max(len(ta | tb), 1)
        ratio = max(ratio, 0.55 * ratio + 0.45 * overlap)
    return ratio


def closest_name(query: str, candidates: Iterable[str], *, cutoff: float = 0.78):
    """Return (match, score, reason) or (None, 0, '')."""
    q = clean_text(query)
    if not q:
        return None, 0.0, ""
    qn = norm_key(q)
    unique = []
    seen = set()
    for raw in candidates:
        text = clean_text(raw)
        if not text:
            continue
        key = norm_key(text)
        if key in seen:
            continue
        seen.add(key)
        unique.append(text)
    for cand in unique:
        if norm_key(cand) == qn:
            return cand, 1.0, "exact"
    alias_hit = _alias_lookup(qn)
    if alias_hit:
        for cand in unique:
            if norm_key(cand) == alias_hit or alias_hit in SHEET_ALIASES.get(norm_key(cand), ()):
                return cand, 0.96, f"alias:{alias_hit}"
            if norm_key(cand) in MO_ALIASES.get(alias_hit, ()):
                return cand, 0.96, f"alias:{alias_hit}"
            if alias_hit == norm_key(cand):
                return cand, 0.96, f"alias:{alias_hit}"
    best = None
    best_score = 0.0
    for cand in unique:
        score = similarity(q, cand)
        if score > best_score:
            best, best_score = cand, score
    if best is not None and best_score >= cutoff:
        return best, best_score, f"fuzzy:{best_score:.2f}"
    return None, best_score, ""


def _alias_lookup(qn: str) -> str | None:
    for canonical, alts in {**SHEET_ALIASES, **MO_ALIASES}.items():
        bag = {canonical, *{norm_key(a) for a in alts}}
        if qn in bag:
            return canonical
    return None


def normalize_rats(rats) -> list[str]:
    if rats is None:
        return list(RAT_FOLDERS)
    if isinstance(rats, str):
        rats = re.split(r"[,\s]+", rats)
    out = []
    seen = set()
    for raw in rats:
        text = clean_text(raw).upper().replace(" ", "")
        if not text:
            continue
        mapped = None
        if text in {"5G", "NR", "NSA"}:
            mapped = "5G"
        elif text in {"4G", "LTE", "EUTRAN"}:
            mapped = "4G"
        elif text in {"3G", "UMTS", "WCDMA"}:
            mapped = "3G"
        elif text in {"2G", "GSM"}:
            mapped = "2G"
        if mapped and mapped not in seen:
            out.append(mapped)
            seen.add(mapped)
    return out


def rat_subfolder_names(rat: str) -> tuple[str, ...]:
    return RAT_ALIASES.get(rat, (rat,))


def split_parameter_id(pid: str) -> tuple[str | None, str | None]:
    """Before @ = switch / bit name; after @ = Parameter ID (attribute)."""
    text = clean_text(pid)
    if not text:
        return None, None
    if "@" not in text:
        return text, None
    left, right = text.split("@", 1)
    switch_name = clean_text(left) or None
    attr_name = clean_text(right) or None
    return attr_name, switch_name


def family_for_band(raw) -> str | None:
    text = clean_text(raw)
    if not text:
        return None
    compact = text.upper().replace(" ", "")
    if compact.startswith("N") and compact[1:].isdigit():
        if compact in {"N41", "NR41"} or compact[1:] == "41":
            return "L2600"
        return compact
    key = norm_key(text)
    if key in EARFCN_TO_FAMILY:
        return EARFCN_TO_FAMILY[key]
    for family, tokens_set in BAND_FAMILIES.items():
        if compact in tokens_set or key in {norm_key(t) for t in tokens_set}:
            return family
    match = BAND_TOKEN_RE.search(text)
    if match:
        return family_for_band(match.group(1))
    return None


def tokens_for_family(family: str | None, raw=None) -> set[str]:
    out = set()
    if family and family in BAND_FAMILIES:
        out |= {norm_key(t) for t in BAND_FAMILIES[family]}
        out.add(norm_key(family))
    if family and family not in BAND_FAMILIES:
        out.add(norm_key(family))
    if raw is not None and not is_empty(raw):
        out.add(norm_key(raw))
        tok = BAND_TOKEN_RE.search(clean_text(raw))
        if tok:
            out.add(norm_key(tok.group(1)))
    return {t for t in out if t}


def band_matches(rule_band: str, cell_tokens: set[str]) -> bool:
    family = family_for_band(rule_band)
    wanted = tokens_for_family(family, rule_band)
    cell = {norm_key(t) for t in cell_tokens if t}
    if not wanted or not cell:
        return False
    return bool(wanted & cell)


def combined_cell_key(site, cell_id) -> str:
    return f"{clean_text(site)}+{clean_text(cell_id)}"


@dataclass
class RecommendRule:
    group_name: str | None = None
    group_id: str | None = None
    band_token: str | None = None
    value: str | None = None
    raw: str = ""


@dataclass
class RecommendSpec:
    raw: str
    simple: str | None
    rules: list = field(default_factory=list)
    has_conditional: bool = False


def _split_recommend_lines(text: str) -> list[str]:
    blob = text.replace("\r\n", "\n").replace("\r", "\n")
    blob = blob.replace(")(", ")\n(")
    parts = []
    for chunk in re.split(r"[\n;]+", blob):
        chunk = chunk.strip().strip(",")
        if chunk:
            parts.append(chunk)
    return parts


def _looks_conditional(text: str) -> bool:
    if "(" in text and "=" in text and ")" in text:
        return True
    if BAND_VALUE_RE.search(text):
        return True
    return False


def parse_recommend(value) -> RecommendSpec:
    raw = clean_text(value)
    if not raw:
        return RecommendSpec(raw="", simple=None, rules=[], has_conditional=False)
    if not _looks_conditional(raw):
        return RecommendSpec(raw=raw, simple=raw, rules=[], has_conditional=False)

    rules: list[RecommendRule] = []
    for line in _split_recommend_lines(raw):
        group_match = GROUP_LINE_RE.match(line)
        if group_match:
            gname, gid, rest = group_match.group(1), clean_text(group_match.group(2)), clean_text(group_match.group(3))
            rest = rest.lstrip("=>").strip()
            if rest:
                band_hits = list(BAND_VALUE_RE.finditer(rest))
                if band_hits:
                    for hit in band_hits:
                        rules.append(
                            RecommendRule(
                                group_name=gname,
                                group_id=gid,
                                band_token=hit.group(1),
                                value=clean_text(hit.group(2)),
                                raw=line,
                            )
                        )
                else:
                    rules.append(
                        RecommendRule(
                            group_name=gname,
                            group_id=gid,
                            band_token=None,
                            value=rest,
                            raw=line,
                        )
                    )
            else:
                rules.append(
                    RecommendRule(
                        group_name=gname,
                        group_id=gid,
                        band_token=None,
                        value=None,
                        raw=line,
                    )
                )
            continue
        band_hits = list(BAND_VALUE_RE.finditer(line))
        if band_hits:
            for hit in band_hits:
                rules.append(
                    RecommendRule(
                        band_token=hit.group(1),
                        value=clean_text(hit.group(2)),
                        raw=line,
                    )
                )
            continue
        rules.append(RecommendRule(value=line, raw=line))

    valued = [r for r in rules if not is_empty(r.value)]
    has_conditional = any(r.band_token or r.group_name for r in rules)
    simple = None if has_conditional else (valued[0].value if len(valued) == 1 else raw)
    return RecommendSpec(raw=raw, simple=simple, rules=rules, has_conditional=has_conditional)


def _group_ids_for(groups: dict, group_name: str) -> set[str]:
    if not groups or not group_name:
        return set()
    wanted = norm_key(group_name)
    aliases = set()
    for canonical, alts in GROUP_NAME_ALIASES.items():
        bag = {canonical, *{norm_key(a) for a in alts}}
        if wanted in bag:
            aliases |= bag
    aliases.add(wanted)
    if "COMMGROUPID" in wanted or wanted.endswith("GROUPID"):
        aliases.add("COMMGROUPID")
    found: set[str] = set()
    for key, ids in groups.items():
        kn = norm_key(key)
        if kn in aliases or wanted in kn or kn in wanted:
            found |= {clean_text(i) for i in ids}
    return found


@dataclass
class RowContext:
    site: str = ""
    cell_id: str = ""
    cell_name: str = ""
    cell_key: str = ""
    band_raw: str = ""
    band_family: str | None = None
    band_tokens: set = field(default_factory=set)
    groups: dict = field(default_factory=dict)


def select_recommend(spec: RecommendSpec, ctx: RowContext | None = None) -> tuple[str | None, str]:
    """Pick the proposed value that applies to this cell / group / band."""
    if spec is None:
        return None, "empty"
    if not spec.has_conditional:
        return spec.simple, "default"
    ctx = ctx or RowContext()
    scored: list[tuple[int, RecommendRule]] = []
    for rule in spec.rules:
        if is_empty(rule.value):
            continue
        score = 0
        if rule.group_name:
            ids = _group_ids_for(ctx.groups, rule.group_name)
            if clean_text(rule.group_id) not in ids:
                continue
            score += 2
        if rule.band_token:
            if not band_matches(rule.band_token, ctx.band_tokens):
                continue
            score += 1
        scored.append((score, rule))
    if not scored:
        return None, "not_applicable"
    scored.sort(key=lambda item: -item[0])
    best_score = scored[0][0]
    best_rules = [rule for score, rule in scored if score == best_score]
    value = best_rules[0].value
    bits = []
    if best_rules[0].band_token:
        bits.append(best_rules[0].band_token)
    if best_rules[0].group_name:
        bits.append(f"{best_rules[0].group_name}={best_rules[0].group_id}")
    return value, "+".join(bits) or "conditional"


def header_index_from_norm(header_norm: dict, keys: Iterable[str]):
    for key in keys:
        nk = norm_key(key)
        if nk in header_norm:
            return header_norm[nk]
    # fuzzy fallback for slightly mistyped dump headers
    for key in keys:
        match, score, _reason = closest_name(key, header_norm.keys(), cutoff=0.9)
        if match is not None:
            return header_norm[match]
    return None


def cell_from_row(headers, header_norm, row) -> RowContext:
    def value_at(idx):
        if idx is None or row is None or idx >= len(row):
            return ""
        return clean_text(row[idx])

    site = value_at(header_index_from_norm(header_norm, SITE_HEADER_KEYS))
    cell_id = value_at(header_index_from_norm(header_norm, CELL_ID_HEADER_KEYS))
    cell_name = value_at(header_index_from_norm(header_norm, CELL_NAME_HEADER_KEYS))
    band_raw = value_at(header_index_from_norm(header_norm, BAND_HEADER_KEYS))
    groups = {}
    for gkey in GROUP_HEADER_KEYS:
        idx = header_index_from_norm(header_norm, [gkey])
        if idx is None:
            continue
        raw = value_at(idx)
        if raw:
            groups.setdefault(gkey, set()).add(raw)
    family = family_for_band(band_raw) if band_raw else None
    ctx = RowContext(
        site=site,
        cell_id=cell_id,
        cell_name=cell_name,
        cell_key=combined_cell_key(site, cell_id) if site and cell_id else "",
        band_raw=band_raw,
        band_family=family,
        band_tokens=tokens_for_family(family, band_raw),
        groups=groups,
    )
    return ctx


def is_new_style_ref_headers(header_row) -> bool:
    keys = {norm_key(c) for c in (header_row or [])}
    if "PROPOSEDVALUE" in keys or "DEFAULTVALUE" in keys:
        return True
    if "MONAME" in keys and "MMLOBJECT" not in keys and "MMLOBJECTNAME" not in keys:
        return True
    return False
