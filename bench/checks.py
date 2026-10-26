"""Answer-level scoring: values, direction of change, approximation, and per-item checks.

Everything here looks only at the answer text, its outcome and the documents it cites, so it can be tested
on hand-written answers (bench/scorer_fixtures.json) as well as on system artifacts.

Item fields used (all under item["expected"]):
  values            [{name, value, unit, tol_abs, direction?, approximate?}]
                    direction: "increase" | "decrease" — the answer must state it (sign or wording)
                    approximate: true — the answer must hedge the number or give a range containing it
  forbidden_values  values that must not appear (e.g. post-cutoff figures, tempting wrong derivations)
  checks            [{id, type, pattern | doc, why}]
                    type: mentions | not_mentions | cites_doc | not_cites_doc
                          | mentions_near_value (pattern must occur in a sentence that states the named value)
"""
import re
from dataclasses import dataclass

NUM_RE = re.compile(
    r"(?<![\w.])(-|−|\+)?\$?(\d[\d,]*(?:\.\d+)?)\s*(billion|million|%|percentage points?|percent|pp|basis points|bps)?",
    re.I)
RANGE_RE = re.compile(
    r"\$?(\d[\d,]*(?:\.\d+)?)\s*(billion|million)?\s*(?:–|—|-|to)\s*\$?(\d[\d,]*(?:\.\d+)?)\s*(billion|million)?", re.I)
DECREASE_RE = re.compile(r"declin|decreas|\bfell\b|\bfall|contract|lower|\bdown\b|drop|reduc|compress|shr[iu]nk|negative", re.I)
INCREASE_RE = re.compile(r"increas|\brose\b|\brise|\bgrew\b|\bgrow|expan|higher|improv|\bup\b|positive", re.I)
HEDGE_RE = re.compile(r"approximately|approx\.|about|around|roughly|~|≈|estimated|an estimate|on the order of", re.I)
CLAUSE_BREAK = re.compile(r"[.;:!?]\s|\n")
SENTENCE_BREAK = re.compile(r"[.!?]\s|\n")


@dataclass
class Number:
    value: float          # signed as written
    unit: str             # lower-cased unit word, '' if none
    places: int           # decimal places as written
    sign: str             # '-', '+' or ''
    start: int
    end: int


def numbers_in(text: str) -> list[Number]:
    out = []
    for m in NUM_RE.finditer(text):
        sign, num, unit = m.group(1) or "", m.group(2), (m.group(3) or "").lower()
        v = float(num.replace(",", ""))
        places = len(num.split(".")[1]) if "." in num else 0
        out.append(Number(-v if sign in ("-", "−") else v, unit, places, "-" if sign == "−" else sign, m.start(), m.end()))
    return out


def _magnitude_matches(expected: dict, n: Number) -> bool:
    target, unit, tol = abs(expected["value"]), expected["unit"], expected["tol_abs"]
    v = abs(n.value)
    if unit == "USD_millions":
        if n.unit == "billion":  # correct rounding at the precision written, e.g. $5.4 billion for 5,355.3
            return abs(v * 1000 - target) <= max(tol, 0.5 * 10 ** -n.places * 1000) + 1e-9
        return n.unit in ("", "million") and abs(v - target) <= tol
    if unit == "%":
        return n.unit in ("%", "percent") and abs(v - target) <= tol
    if unit == "pp":
        if n.unit in ("pp", "percentage point", "percentage points"):
            return abs(v - target) <= tol
        return n.unit in ("basis points", "bps") and abs(v / 100 - target) <= tol
    if unit == "count":
        return n.unit == "" and abs(v - target) <= tol
    return False


def find_value(expected: dict, text: str) -> list[Number]:
    return [n for n in numbers_in(text) if _magnitude_matches(expected, n)]


def _clause(text: str, n: Number, before: int = 160, after: int = 60) -> tuple[str, int]:
    """Text of the clause around a number, and the number's offset inside it."""
    lo = max(0, n.start - before)
    breaks = list(CLAUSE_BREAK.finditer(text, lo, n.start))
    if breaks:
        lo = breaks[-1].end()
    hi = min(len(text), n.end + after)
    nxt = CLAUSE_BREAK.search(text, n.end, hi)
    if nxt:
        hi = nxt.start()
    return text[lo:hi], n.start - lo


def sentence_of(text: str, n: Number) -> str:
    starts = [m.end() for m in SENTENCE_BREAK.finditer(text, 0, n.start)]
    nxt = SENTENCE_BREAK.search(text, n.end)
    return text[starts[-1] if starts else 0: nxt.start() if nxt else len(text)]


def direction_of(text: str, n: Number) -> str | None:
    """'decrease' / 'increase' from an explicit sign, else from the direction word nearest the number."""
    if n.sign == "-":
        return "decrease"
    if n.sign == "+":
        return "increase"
    clause, pos = _clause(text, n)
    cues = [(abs(m.start() - pos), "decrease") for m in DECREASE_RE.finditer(clause)]
    cues += [(abs(m.start() - pos), "increase") for m in INCREASE_RE.finditer(clause)]
    return min(cues)[1] if cues else None


def _scaled(num: str, unit: str | None, other_unit: str | None) -> float:
    v = float(num.replace(",", ""))
    return v * 1000 if (unit or other_unit or "").lower() == "billion" else v


def range_contains(expected: dict, text: str) -> bool:
    """A stated range ("$4,619–4,684 million") that contains the value and isn't absurdly wide."""
    target, tol = abs(expected["value"]), expected["tol_abs"]
    for m in RANGE_RE.finditer(text):
        lo = _scaled(m.group(1), m.group(2), m.group(4))
        hi = _scaled(m.group(3), m.group(4), m.group(2))
        if lo <= target <= hi and hi - lo <= 4 * tol:
            return True
    return False


def is_approximate(expected: dict, text: str, matches: list[Number]) -> bool:
    """A hedged point estimate within tolerance, or a range containing the value."""
    for n in matches:
        clause, pos = _clause(text, n, before=60, after=10)
        if HEDGE_RE.search(clause[:pos + 1]):
            return True
    return range_contains(expected, text)


def answer_failures(item: dict, text: str, cited_docs: list[str], outcome: str) -> list[str]:
    """All answer-level failures for one item. Empty list = the answer passes every answer-level check."""
    exp = item["expected"]
    failures = []
    if exp["outcome"] == "abstention" and outcome != "abstention":
        failures.append("answered_instead_of_abstaining")
    if exp["outcome"] != "abstention" and outcome == "abstention":
        failures.append("false_abstention")
    calc_needed = any(c in item["category"] for c in ("calculation", "decomposition"))
    for v in exp.get("values", []):
        matches = find_value(v, text)
        if not matches and not (v.get("approximate") and range_contains(v, text)):
            failures.append(("missing_or_wrong_calculation" if calc_needed else "wrong_or_missing_value") + f":{v['name']}")
            continue
        if v.get("direction"):
            dirs = {direction_of(text, n) for n in matches}
            if v["direction"] not in dirs:
                failures.append(("direction_unstated" if dirs == {None} else "wrong_direction") + f":{v['name']}")
        if v.get("approximate") and not is_approximate(v, text, matches):
            failures.append(f"approximation_not_stated:{v['name']}")
    for v in exp.get("forbidden_values", []):
        if find_value(v, text):
            failures.append(f"forbidden_value_stated:{v['value']}")
    for c in exp.get("checks", []):
        t = c["type"]
        if t == "mentions" and not re.search(c["pattern"], text, re.I):
            failures.append(f"check_failed:{c['id']}")
        elif t == "not_mentions" and re.search(c["pattern"], text, re.I):
            failures.append(f"check_failed:{c['id']}")
        elif t == "cites_doc" and c["doc"] not in cited_docs:
            failures.append(f"check_failed:{c['id']}")
        elif t == "not_cites_doc" and c["doc"] in cited_docs:
            failures.append(f"check_failed:{c['id']}")
        elif t == "mentions_near_value":
            value = next(v for v in exp["values"] if v["name"] == c["value"])
            if not any(re.search(c["pattern"], sentence_of(text, n), re.I) for n in find_value(value, text)):
                failures.append(f"check_failed:{c['id']}")
    return failures
