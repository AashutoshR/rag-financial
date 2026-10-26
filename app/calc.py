"""Minimal deterministic calculation engine with lineage [CALC-01, 03, 05, 06, 07, 08].

This is the first-session version: enough to produce gold artifacts. Phase 3 replaces it with the
typed calculation DSL; the record format below is what that version must keep producing.
"""
from dataclasses import dataclass, field
from decimal import ROUND_HALF_EVEN, Decimal, getcontext

getcontext().prec = 28
ENGINE = "calc@0.1.0"


@dataclass
class Input:
    name: str
    value: Decimal          # in base units (e.g. USD, not millions)
    unit: str
    period: str
    citation_id: str
    unit_id: str


@dataclass
class Calc:
    calc_id: str
    formula: str
    inputs: list[Input]
    result: Decimal | None
    result_unit: str
    display: str
    notes: list[str] = field(default_factory=list)

    def record(self) -> dict:
        return {
            "id": self.calc_id,
            "formula": self.formula,
            "inputs": [{"name": i.name, "value": format(i.value, "f"), "unit": i.unit, "period": i.period,
                        "citation_id": i.citation_id, "unit_id": i.unit_id} for i in self.inputs],
            "result": {"value": None if self.result is None else format(self.result, "f"),
                       "unit": self.result_unit, "display": self.display},
            "rounding": "ROUND_HALF_EVEN for display only; result kept at full precision",
            "notes": self.notes,
            "engine": ENGINE,
        }


def from_cell(name: str, cell: dict, citation_id: str) -> Input:
    ix = cell["ixbrl"]
    period = f"{ix['period']['start']}..{ix['period']['end'] or ix['period']['instant']}"
    return Input(name, Decimal(ix["value"]), ix["unit"].upper(), period, citation_id, cell["unit_id"])


def _q(x: Decimal, places: str) -> Decimal:
    return x.quantize(Decimal(places), rounding=ROUND_HALF_EVEN)


def ratio(calc_id: str, num: Input, den: Input, label: str) -> Calc:
    if num.unit != den.unit:
        raise TypeError(f"unit mismatch {num.unit} vs {den.unit}")
    if num.period != den.period:
        raise TypeError(f"period mismatch {num.period} vs {den.period}")
    if den.value <= 0:
        return Calc(calc_id, f"{num.name} / {den.name}", [num, den], None, "ratio", "not meaningful",
                    ["denominator <= 0"])
    r = num.value / den.value
    return Calc(calc_id, f"{label} = {num.name} / {den.name}", [num, den], r, "ratio", f"{_q(r * 100, '0.01')}%")


def pct_change(calc_id: str, new: Input, old: Input, label: str) -> Calc:
    if new.unit != old.unit:
        raise TypeError(f"unit mismatch {new.unit} vs {old.unit}")
    if old.value <= 0:
        return Calc(calc_id, f"({new.name} - {old.name}) / {old.name}", [new, old], None, "ratio",
                    "not meaningful", ["base <= 0"])
    r = (new.value - old.value) / old.value
    return Calc(calc_id, f"{label} = ({new.name} - {old.name}) / {old.name}", [new, old], r, "ratio",
                f"{'+' if r >= 0 else ''}{_q(r * 100, '0.01')}%")


def pp_change(calc_id: str, new: Calc, old: Calc, label: str) -> Calc:
    """Change between two ratios, in percentage points (and basis points)."""
    d = new.result - old.result
    pp = d * 100
    return Calc(calc_id, f"{label} = {new.calc_id} - {old.calc_id}", [], d, "ratio_difference",
                f"{'+' if pp >= 0 else ''}{_q(pp, '0.01')} pp ({'+' if pp >= 0 else ''}{_q(pp * 100, '1')} bps)",
                [f"inputs are calculations {new.calc_id} and {old.calc_id}"])


def margin_decomposition(calc_id: str, rev_new: Input, rev_old: Input,
                         lines: list[tuple[str, Input, Input, int]]) -> tuple[Calc, list[dict]]:
    """Δ operating margin = Σ sign_i × Δ(line_i / revenue). sign = -1 for costs, +1 for income items."""
    contributions, inputs, total = [], [rev_new, rev_old], Decimal(0)
    for name, new, old, sign in lines:
        share_new = new.value / rev_new.value
        share_old = old.value / rev_old.value
        contrib = sign * (share_new - share_old)
        total += contrib
        inputs += [new, old]
        contributions.append({
            "line": name,
            "share_of_revenue_new": format(share_new, "f"),
            "share_of_revenue_old": format(share_old, "f"),
            "contribution_to_margin_change_pp": format(_q(contrib * 100, "0.001"), "f"),
            "direction": "lowered margin" if contrib < 0 else "raised margin",
        })
    pp = total * 100
    calc = Calc(calc_id, "Δmargin = Σ sign_i × (line_i,new / revenue_new − line_i,old / revenue_old); "
                         "sign = −1 for expenses, +1 for income items", inputs, total, "ratio_difference",
                f"{'+' if pp >= 0 else ''}{_q(pp, '0.01')} pp", [])
    return calc, contributions
