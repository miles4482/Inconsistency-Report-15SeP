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

# Plan-file names L9/L09/L900 are the SAME family as dump Frequency Band 8, etc.
# L26/L2600 is 2600 MHz (3GPP 41 / 7 / 38). Frequency Band 3 is L18/1800, not L26.
BAND_FAMILIES = {
    "L900": frozenset({
        "L9", "L09", "L090", "L900", "L0900", "900", "900M", "900MHZ",
        "B8", "BAND8", "NB8", "N8", "8",
    }),
    "L1800": frozenset({
        "L18", "L180", "L1800", "1800", "1800M", "1800MHZ",
        "B3", "BAND3", "NB3", "N3", "3",
    }),
    "L2100": frozenset({
        "L21", "L210", "L2100", "2100", "2100M", "2100MHZ",
        "B1", "BAND1", "NB1", "N1", "1",
    }),
    "L2600": frozenset({
        "L26", "L260", "L2600", "2600", "2600M", "2600MHZ",
        "B41", "BAND41", "NB41", "N41", "NR41", "41",
        "B7", "BAND7", "NB7", "N7", "7",
        "B38", "BAND38", "N38", "38",
    }),
}

EARFCN_TO_FAMILY = {
    "8": "L900",
    "3": "L1800",
    "1": "L2100",
    "41": "L2600",
    "7": "L2600",
    "38": "L2600",
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
    "FREQUENCYBANDINDICATOR",
    "FREQBAND",
    "DLBAND",
    "EUTRANBAND",
    "NRBAND",
    "BAND",
    "BANDIND",
    "OPERATINGBAND",
    "OPERATINGBANDINDEX",
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

BAND_TOKEN = r"(?:L0?9(?:00)?|L18(?:00)?|L21(?:00)?|L26(?:00)?|N\d{1,3}|B\d{1,3})"
BAND_TOKEN_RE = re.compile(rf"\b({BAND_TOKEN})\b", re.I)
BAND_EMBEDDED_RE = re.compile(
    r"(L900|L0900|L090|L09|L9(?!\d)|L1800|L18(?!\d)|L2100|L21(?!\d)|L2600|L26(?!\d)|NR41|N41)",
    re.I,
)
FREQ_BAND_PHRASE_RE = re.compile(
    r"(?:FREQUENCY\s*BAND|FREQ(?:UENCY)?\s*BAND|BAND\s*IND(?:ICATOR)?|"
    r"E-?UTRA(?:N)?\s*BAND|OPERATING\s*BAND)[\s:=_-]*(\d{1,3})(?:\.0+)?",
    re.I,
)
BAND_VALUE_RE = re.compile(
    rf"\b({BAND_TOKEN})(?:\s*/\s*{BAND_TOKEN})*\s*[:=\uff1a]\s*(.+?)"
    rf"(?=\s+{BAND_TOKEN}\s*[:=\uff1a]|$|\n|;|,)",
    re.I,
)
BAND_SPLIT_RE = re.compile(
    rf"(?<=\S)[\s,]+(?=({BAND_TOKEN})(?:\s*/\s*{BAND_TOKEN})*\s*[:=\uff1a])",
    re.I,
)
METRIC_DISC_RE = re.compile(r"\b([AB]\d+)\b", re.I)
UNIT_PARENS_RE = re.compile(r"\([^)]*\)")
UNIT_TAIL_RE = re.compile(r"(DBM|DB|MHZ|KHZ|MS|MIN|SEC)$")
GROUP_LINE_RE = re.compile(
    r"\(\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*([^)]+?)\s*\)\s*(?:=>|=)?\s*(.*)$",
)
# Reference Conditions column: "Interfreq handover group ID=0" or
# "Interfreq handover group ID (INTERFREQHOGROUPID)=1". Excel wrap is collapsed.
CONDITION_EQ_RE = re.compile(r"^\s*(.+?)\s*(?:=|==|:)\s*(.+?)\s*$")
SHORT_IN_PARENS_RE = re.compile(r"^(.*?)\s*\(([^)]+)\)\s*$")
CONDITION_HEADER_RE = re.compile(
    r"^(CONDITION(?:S)?(?:COLUMN|COL)?|ROWCONDITION(?:S)?|FILTERCONDITION(?:S)?)(\d*)$"
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


def header_match_key(value) -> str:
    """Normalize a header so 'A1 RSRP Threshold' matches 'A1 RSRP Threshold(dBm)'."""
    text = UNIT_PARENS_RE.sub("", clean_text(value))
    key = norm_key(text)
    return UNIT_TAIL_RE.sub("", key)


def metric_discs(value) -> set[str]:
    """A1 vs A2 (and B1 vs B2) so fuzzy match cannot pick the neighbour column."""
    return {m.group(1).upper() for m in METRIC_DISC_RE.finditer(clean_text(value))}


def closest_name(query: str, candidates: Iterable[str], *, cutoff: float = 0.78):
    """Return (match, score, reason) or (None, 0, '')."""
    q = clean_text(query)
    if not q:
        return None, 0.0, ""
    qn = norm_key(q)
    qh = header_match_key(q)
    q_disc = metric_discs(q)
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
    if q_disc:
        filtered = [c for c in unique if not metric_discs(c) or metric_discs(c) == q_disc]
        if filtered:
            unique = filtered
    for cand in unique:
        if norm_key(cand) == qn or header_match_key(cand) == qh:
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


def _coerce_band_text(raw) -> str:
    """Excel/pyxlsb often stores Frequency band as 8.0; treat that as 8."""
    return canon_id_value(raw)


def canon_id_value(raw) -> str:
    """0, 0.0, '0' → '0' so Interfreq handover group ID matches Excel numbers."""
    if raw is None:
        return ""
    if isinstance(raw, bool):
        return "1" if raw else "0"
    if isinstance(raw, float):
        if raw.is_integer():
            return str(int(raw))
        return str(raw)
    if isinstance(raw, int):
        return str(raw)
    text = clean_text(raw)
    if re.fullmatch(r"-?\d+\.0+", text):
        return text.split(".", 1)[0]
    return text


def _alias_map() -> dict:
    """Built once: L9/L09/L900/8 → L900, etc."""
    cached = getattr(_alias_map, "_map", None)
    if cached is not None:
        return cached
    mapping = dict(EARFCN_TO_FAMILY)
    for family, tokens_set in BAND_FAMILIES.items():
        mapping[norm_key(family)] = family
        mapping[family.upper()] = family
        for tok in tokens_set:
            mapping[norm_key(tok)] = family
            mapping[str(tok).upper().replace(" ", "")] = family
    _alias_map._map = mapping
    return mapping


def family_for_band(raw) -> str | None:
    """L9, L09, L900, Band 8, Frequency Band 8, 8, and 8.0 are the same family."""
    text = _coerce_band_text(raw)
    if not text:
        return None
    aliases = _alias_map()
    key = norm_key(text)
    if key in aliases:
        return aliases[key]
    compact = text.upper().replace(" ", "")
    if compact in aliases:
        return aliases[compact]
    if compact.startswith("N") and compact[1:].isdigit():
        if compact[1:] in aliases:
            return aliases[compact[1:]]

    embedded = BAND_EMBEDDED_RE.search(text)
    if embedded:
        found = aliases.get(norm_key(embedded.group(1)))
        if found:
            return found

    phrase = FREQ_BAND_PHRASE_RE.search(text)
    if phrase:
        num = phrase.group(1).lstrip("0") or phrase.group(1)
        return aliases.get(num) or aliases.get(norm_key(num))
    return None


def tokens_for_family(family: str | None, raw=None) -> set[str]:
    out = set()
    if family:
        out.add(norm_key(family))
        out.add(family)
        if family in BAND_FAMILIES:
            out |= {norm_key(t) for t in BAND_FAMILIES[family]}
    if raw is not None and not is_empty(raw):
        text = _coerce_band_text(raw)
        if text:
            out.add(norm_key(text))
        found = family_for_band(raw)
        if found:
            out.add(norm_key(found))
            out.add(found)
    return {t for t in out if t}


def band_matches(rule_band: str, cell_tokens: set[str]) -> bool:
    """True when recommend L9/L09/L900 and dump Frequency Band 8 (same family)."""
    rule_family = family_for_band(rule_band)
    if not rule_family:
        return False
    aliases = _alias_map()
    wanted = norm_key(rule_family)
    for raw in cell_tokens:
        if not raw:
            continue
        token = raw if isinstance(raw, str) else str(raw)
        key = token if token.isupper() and token.isalnum() else norm_key(token)
        if key == wanted or token == rule_family:
            return True
        fam = aliases.get(key)
        if fam == rule_family:
            return True
    return False


def combined_cell_key(site, cell_id) -> str:
    return f"{clean_text(site)}+{clean_text(cell_id)}"


@dataclass
class ConditionClause:
    """One dump-column filter from the Reference Conditions column."""

    display_name: str
    short_name: str | None = None
    value: str = ""
    raw: str = ""

    def labels(self) -> list[str]:
        out = []
        if self.display_name:
            out.append(self.display_name)
        if self.short_name:
            out.append(self.short_name)
        return out


def condition_header_slot(header) -> int | None:
    """Conditions1 → 1, Conditions 2 → 2, Conditions / Condition Column → 1."""
    key = norm_key(header)
    if not key:
        return None
    match = CONDITION_HEADER_RE.fullmatch(key)
    if not match:
        return None
    num = match.group(2)
    return int(num) if num else 1


def condition_header_is_numbered(header) -> bool:
    key = norm_key(header)
    match = CONDITION_HEADER_RE.fullmatch(key)
    return bool(match and match.group(2))


def parse_conditions(value) -> list[ConditionClause]:
    """Parse Conditions such as Interfreq handover group ID (INTERFREQHOGROUPID)=0.

    Empty Conditions means no row filter. Several clauses (semicolon / AND)
    must all match. Excel wrap/newlines inside the name are collapsed to spaces.
    Short name in brackets is the dump Parameter ID.
    """
    raw = clean_text(value)
    if not raw:
        return []
    blob = raw.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
    blob = " ".join(blob.split())
    chunks = [chunk for chunk in re.split(r"\s*;\s+|\s+\bAND\b\s+", blob, flags=re.I) if clean_text(chunk)]
    if not chunks:
        chunks = [blob]
    clauses: list[ConditionClause] = []
    for chunk in chunks:
        clause = _parse_one_condition(clean_text(chunk))
        if clause:
            clauses.append(clause)
    if not clauses:
        clause = _parse_one_condition(blob)
        if clause:
            clauses.append(clause)
    return clauses


def _parse_one_condition(text: str) -> ConditionClause | None:
    match = CONDITION_EQ_RE.match(text)
    if not match:
        return None
    name, val = clean_text(match.group(1)), canon_id_value(match.group(2))
    if not name or val == "":
        return None
    short = None
    paren = SHORT_IN_PARENS_RE.match(name)
    if paren:
        name = clean_text(paren.group(1))
        short = clean_text(paren.group(2)) or None
        if not name:
            name = short or ""
            short = None
    if not name:
        return None
    return ConditionClause(display_name=name, short_name=short, value=val, raw=text)


def condition_name_keys(clause: ConditionClause) -> list[str]:
    """Normalized dump-header keys for a Conditions clause, including group-ID aliases."""
    keys: list[str] = []
    seen: set[str] = set()

    def add(item: str):
        nk = norm_key(item)
        if nk and nk not in seen:
            keys.append(nk)
            seen.add(nk)

    for label in clause.labels():
        add(label)
        add(header_match_key(label))
        for canonical, alts in GROUP_NAME_ALIASES.items():
            bag = {canonical, *{norm_key(a) for a in alts}}
            if norm_key(label) in bag:
                for item in bag:
                    add(item)
    for gkey in GROUP_HEADER_KEYS:
        gn = norm_key(gkey)
        if gn in seen:
            continue
        if any(k in gn or gn in k for k in list(seen) if len(k) >= 6):
            add(gn)
    return keys


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
    blob = blob.replace("\u2212", "-").replace("\u2013", "-").replace("\uff1a", ":")
    blob = blob.replace(")(", ")\n(")
    blob = BAND_SPLIT_RE.sub("\n", blob)
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
    if re.search(rf"\b{BAND_TOKEN}\b", text, re.I) and re.search(r"-?\d", text):
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


def header_index_from_norm(header_norm: dict, keys: Iterable[str], fuzzy: bool = False):
    """Resolve a header index. Fuzzy is opt-in and must not run per dump row."""
    for key in keys:
        nk = norm_key(key)
        if nk in header_norm:
            return header_norm[nk]
    if not fuzzy:
        return None
    for key in keys:
        match, score, _reason = closest_name(key, header_norm.keys(), cutoff=0.92)
        if match is not None:
            return header_norm[match]
    return None


def identity_indexes(header_norm: dict, fuzzy: bool = False) -> dict:
    """Look up site/cell/band/group columns once per sheet."""
    group_idxs = []
    for gkey in GROUP_HEADER_KEYS:
        idx = header_index_from_norm(header_norm, [gkey], fuzzy=False)
        if idx is not None:
            group_idxs.append((gkey, idx))
    return {
        "site": header_index_from_norm(header_norm, SITE_HEADER_KEYS, fuzzy=fuzzy),
        "cell_id": header_index_from_norm(header_norm, CELL_ID_HEADER_KEYS, fuzzy=fuzzy),
        "cell_name": header_index_from_norm(header_norm, CELL_NAME_HEADER_KEYS, fuzzy=False),
        "band": header_index_from_norm(header_norm, BAND_HEADER_KEYS, fuzzy=False),
        "groups": group_idxs,
    }


def cell_from_row(headers, header_norm, row, indexes=None) -> RowContext:
    def value_at(idx):
        if idx is None or row is None or idx >= len(row):
            return ""
        return clean_text(row[idx])

    indexes = indexes or identity_indexes(header_norm, fuzzy=False)
    site = value_at(indexes.get("site"))
    cell_id = value_at(indexes.get("cell_id"))
    cell_name = value_at(indexes.get("cell_name"))
    band_idx = indexes.get("band")
    band_raw_orig = None
    if band_idx is not None and row is not None and band_idx < len(row):
        band_raw_orig = row[band_idx]
    band_raw = _coerce_band_text(band_raw_orig) if band_raw_orig is not None else value_at(indexes.get("band"))
    groups = {}
    for gkey, idx in indexes.get("groups") or []:
        raw = value_at(idx)
        if raw:
            groups.setdefault(gkey, set()).add(raw)
    family = family_for_band(band_raw_orig if band_raw_orig is not None else band_raw)
    if family is None and cell_name:
        embedded = BAND_EMBEDDED_RE.search(cell_name)
        if embedded:
            family = family_for_band(embedded.group(1))
    band_tokens = set()
    if family:
        band_tokens.add(family)
        band_tokens.add(norm_key(family))
    if band_raw:
        band_tokens.add(norm_key(band_raw))
    return RowContext(
        site=site,
        cell_id=cell_id,
        cell_name=cell_name,
        cell_key=combined_cell_key(site, cell_id) if site and cell_id else "",
        band_raw=band_raw,
        band_family=family,
        band_tokens=band_tokens,
        groups=groups,
    )


def is_new_style_ref_headers(header_row) -> bool:
    keys = {norm_key(c) for c in (header_row or [])}
    if "PROPOSEDVALUE" in keys or "DEFAULTVALUE" in keys:
        return True
    if "MONAME" in keys and "MMLOBJECT" not in keys and "MMLOBJECTNAME" not in keys:
        return True
    return False
