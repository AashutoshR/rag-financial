"""Build the three hand-written gold artifacts (q01, q04, q07).

The claim wording, claim types and support judgements are written by hand. Every number is computed by
app.calc from cited cells, so a wrong lookup fails loudly instead of producing a plausible gold answer.
Usage: python -m bench.make_gold
"""
import json
from decimal import Decimal

from app import calc, facts
from app.artifact import citation, new_artifact, render_markdown, structural_errors
from app.config import ROOT

OUT = ROOT / "bench" / "gold"
K24, K23 = "sbux_10k_fy2024", "sbux_10k_fy2023"
FY24 = ("2023-10-02", "2024-09-29")
FY23 = ("2022-10-03", "2023-10-01")
IS = "CONSOLIDATED STATEMENTS OF EARNINGS"


class Builder:
    def __init__(self, art: dict):
        self.art = art
        self.by_unit: dict[str, str] = {}

    def cite(self, unit: dict) -> str:
        if unit["unit_id"] not in self.by_unit:
            cid = f"e{len(self.by_unit) + 1}"
            self.by_unit[unit["unit_id"]] = cid
            self.art["citations"].append(citation(cid, unit))
        return self.by_unit[unit["unit_id"]]

    def fact(self, name: str, concept: str, period: tuple, doc: str = K24, heading: str | None = IS) -> calc.Input:
        c = facts.cell(doc, concept, period[0], period[1], heading=heading)
        return calc.from_cell(name, c, self.cite(c))

    def para(self, doc: str, pattern: str) -> str:
        hits = facts.find_text(doc, pattern)
        if not hits:
            raise LookupError(pattern)
        return self.cite(hits[0])

    def claim(self, ctype: str, text: str, support: str, cites=(), calcs=(), note: str | None = None) -> None:
        c = {"id": f"c{len(self.art['claims']) + 1}", "type": ctype, "text": text, "support": support,
             "citation_ids": list(cites), "calculation_ids": list(calcs)}
        if note:
            c["verification_note"] = note
        self.art["claims"].append(c)

    def add_calc(self, k: calc.Calc, **extra) -> calc.Calc:
        rec = k.record()
        rec.update(extra)
        self.art["calculations"].append(rec)
        return k


def finish(art: dict) -> dict:
    art["trace"] = {"author": "hand-written gold", "steps": None, "tokens": 0, "cost_usd": 0}
    art["versions"] = {"calc_engine": calc.ENGINE, "parser": facts.manifest()[K24]["parser_version"]}
    return art


def gold_q01() -> dict:
    b = Builder(new_artifact("gold_q01", "What were Starbucks' total net revenues for fiscal 2024?", "analyst_public", None))
    rev = b.fact("revenue_fy2024", "us-gaap:Revenues", FY24)
    later = facts.cell("sbux_10k_fy2025", "us-gaap:Revenues", *FY24, heading=IS)
    b.claim("reported_fact", "Starbucks reported total net revenues of $36,176.2 million for fiscal 2024 "
            "(52 weeks ended September 29, 2024).", "supported", [rev.citation_id])
    b.claim("reported_fact", "The fiscal 2025 Form 10-K reports the same fiscal 2024 figure ($36,176.2 million) "
            "as its prior-year comparative, so the figure has not been restated.", "supported", [b.cite(later)])
    assert Decimal(later["ixbrl"]["value"]) == rev.value
    b.art["answer_summary"] = "Fiscal 2024 total net revenues were $36,176.2 million."
    return finish(b.art)


def gold_q04() -> dict:
    b = Builder(new_artifact("gold_q04", "By how many percentage points did Starbucks' operating margin change from "
                             "fiscal 2023 to fiscal 2024?", "analyst_public", None))
    r24, r23 = b.fact("revenue_fy2024", "us-gaap:Revenues", FY24), b.fact("revenue_fy2023", "us-gaap:Revenues", FY23)
    o24 = b.fact("operating_income_fy2024", "us-gaap:OperatingIncomeLoss", FY24)
    o23 = b.fact("operating_income_fy2023", "us-gaap:OperatingIncomeLoss", FY23)
    m24 = b.add_calc(calc.ratio("k1", o24, r24, "operating_margin_fy2024"))
    m23 = b.add_calc(calc.ratio("k2", o23, r23, "operating_margin_fy2023"))
    d = b.add_calc(calc.pp_change("k3", m24, m23, "operating_margin_change"))
    mgmt = b.para(K24, r"Fiscal 2024 operating margin was 15\.0% compared to 16\.3%")
    b.claim("calculated", f"Operating margin was {m23.display} in fiscal 2023 and {m24.display} in fiscal 2024.",
            "supported", [o23.citation_id, r23.citation_id, o24.citation_id, r24.citation_id], ["k1", "k2"])
    b.claim("calculated", f"Operating margin changed by {d.display} from fiscal 2023 to fiscal 2024.", "supported",
            [], ["k3"])
    b.claim("management_assertion", "Management reports operating margins of 16.3% and 15.0%, a contraction of "
            "130 basis points.", "supported", [mgmt],
            note="Management's 130 bps is the difference of margins rounded to one decimal; the unrounded change is "
                 "137 bps. This is a rounding difference, not a conflict in the underlying figures.")
    b.art["conflicts"].append({"type": "rounding_difference", "fact": "FY2024 operating margin change",
                               "values": {"management (rounded margins)": "-130 bps", "calculated (k3)": d.display},
                               "citations": [mgmt], "resolution": "Report the calculated value; note the stated figure."})
    b.art["definition_checks"].append({"metric": "operating margin", "finding": "GAAP operating income / total net "
                                       "revenues, same basis and 52-week periods in both years", "citations": [o24.citation_id]})
    b.art["answer_summary"] = (f"Starbucks' GAAP operating margin fell from {m23.display} to {m24.display}, a change "
                               f"of {d.display}. Management describes this as a 130 bps contraction, using rounded margins.")
    return finish(b.art)


def gold_q07() -> dict:
    b = Builder(new_artifact("gold_q07", "What reasons did management give for Starbucks' fiscal 2024 operating margin "
                             "decline, and do the reported cost lines support those reasons?", "analyst_public", None))
    r24, r23 = b.fact("revenue_fy2024", "us-gaap:Revenues", FY24), b.fact("revenue_fy2023", "us-gaap:Revenues", FY23)
    lines = [  # (label, concept, sign: -1 expense / +1 income)
        ("Product and distribution costs", "us-gaap:ProductionAndDistributionCosts", -1),
        ("Store operating expenses", "sbux:StoreOperatingExpenses", -1),
        ("Other operating expenses", "us-gaap:OtherCostAndExpenseOperating", -1),
        ("Depreciation and amortization expenses", "us-gaap:DepreciationAndAmortization", -1),
        ("General and administrative expenses", "us-gaap:GeneralAndAdministrativeExpense", -1),
        ("Restructuring and impairments", "us-gaap:RestructuringSettlementAndImpairmentProvisions", -1),
        ("Income from equity investees", "us-gaap:IncomeLossFromEquityMethodInvestments", +1),
        ("Gain from sale of assets", "us-gaap:GainLossOnDispositionOfAssets1", +1),
    ]
    rows = [(label, b.fact(f"{label} FY2024", concept, FY24), b.fact(f"{label} FY2023", concept, FY23), sign)
            for label, concept, sign in lines]
    decomp, contributions = calc.margin_decomposition("k1", r24, r23, rows)
    b.add_calc(decomp, contributions=contributions)
    o24 = b.fact("operating_income_fy2024", "us-gaap:OperatingIncomeLoss", FY24)
    o23 = b.fact("operating_income_fy2023", "us-gaap:OperatingIncomeLoss", FY23)
    m24, m23 = calc.ratio("k2", o24, r24, "operating_margin_fy2024"), calc.ratio("k3", o23, r23, "operating_margin_fy2023")
    b.add_calc(m24), b.add_calc(m23)
    check = b.add_calc(calc.pp_change("k4", m24, m23, "operating_margin_change"))
    assert abs(check.result - decomp.result) < Decimal("1e-12"), "decomposition must sum to the margin change"

    mgmt = b.para(K24, r"Operating margin contraction of 130 basis points was primarily due to")
    stated = [("wages and benefits investment", -140), ("deleverage", -130), ("promotional activity", -100),
              ("pricing", 180), ("in-store operational efficiencies", 130)]
    drivers = [calc.Input(n, Decimal(v), "bps", "FY2024 vs FY2023", mgmt, "") for n, v in stated]
    net = sum(i.value for i in drivers)
    b.art["calculations"].append({
        "id": "k5", "formula": "sum of management-stated driver impacts (bps)",
        "inputs": [{"name": i.name, "value": str(i.value), "unit": "bps", "period": i.period,
                    "citation_id": mgmt, "unit_id": facts.find_text(K24, r"Operating margin contraction of 130")[0]["unit_id"]}
                   for i in drivers],
        "result": {"value": str(net), "unit": "bps", "display": f"{net} bps"},
        "notes": ["Driver values are management estimates ('approximately'); methodology not disclosed."],
        "engine": calc.ENGINE})

    wb24 = b.fact("wages_and_benefits_fy2024", "us-gaap:LaborAndRelatedExpense", FY24, heading="Note 7")
    wb23 = b.fact("wages_and_benefits_fy2023", "us-gaap:LaborAndRelatedExpense", FY23, heading="Note 7")
    s24 = b.add_calc(calc.ratio("k6", wb24, r24, "wages_benefits_share_fy2024"))
    s23 = b.add_calc(calc.ratio("k7", wb23, r23, "wages_benefits_share_fy2023"))
    ws = b.add_calc(calc.pp_change("k8", s24, s23, "wages_benefits_share_change"))

    by = {c["line"]: c for c in contributions}
    store, gain = by["Store operating expenses"], by["Gain from sale of assets"]
    pd = by["Product and distribution costs"]
    b.claim("management_assertion", "Management attributes the 130 bps operating-margin contraction primarily to "
            "investments in store partner wages and benefits (~140 bps), deleverage (~130 bps) and increased "
            "promotional activity (~100 bps), partially offset by pricing (~180 bps) and in-store operational "
            "efficiencies (~130 bps).", "supported", [mgmt],
            note="'Supported' here means the filing says this; whether the evidence supports the explanation is c6.")
    b.claim("calculated", f"Operating margin fell {check.display.replace('-', '')}, from {m23.display} to {m24.display}.",
            "supported", [o23.citation_id, o24.citation_id, r23.citation_id, r24.citation_id], ["k2", "k3", "k4"])
    b.claim("calculated", f"Management's quantified drivers net to {net} bps, so about {abs(-130 - int(net))} bps of the "
            "stated 130 bps contraction is not accounted for by the listed items.", "supported", [mgmt], ["k5"])
    b.claim("calculated", f"Store operating expenses rose from {float(store['share_of_revenue_old']):.2%} to "
            f"{float(store['share_of_revenue_new']):.2%} of total net revenues, lowering margin by "
            f"{store['contribution_to_margin_change_pp'].lstrip('-')} pp — the largest single contributor. Product "
            f"and distribution costs fell as a share of revenue, raising margin by {pd['contribution_to_margin_change_pp']} pp.",
            "supported", [rows[1][1].citation_id, rows[1][2].citation_id, rows[0][1].citation_id, rows[0][2].citation_id], ["k1"])
    b.claim("calculated", f"Fiscal 2023 included a $91.3 million gain from sale of assets with no fiscal 2024 "
            f"equivalent; its absence lowered the margin comparison by {gain['contribution_to_margin_change_pp'].lstrip('-')} pp. "
            "Management's driver list does not mention it.", "supported", [rows[7][2].citation_id, mgmt], ["k1"])
    b.claim("system_inference", "Management's explanation is only partially supported. Its direction — store-level "
            "cost pressure — is consistent with the rise in store operating expenses. But the size of individual "
            f"drivers can't be verified from reported line items: total wages and benefits moved only {ws.display} "
            "as a share of revenue, against a stated ~140 bps impact. The attribution is likely measured before the "
            "offsetting efficiencies, on a basis the filing does not disclose. The filing can't establish that these "
            "factors caused the whole decline.", "partially_supported",
            [mgmt, wb24.citation_id, wb23.citation_id], ["k1", "k5", "k8"])

    b.art["conflicts"].append({"type": "internal_inconsistency", "fact": "FY2024 operating margin drivers",
                               "values": {"stated total": "-130 bps", "sum of stated drivers (k5)": f"{net} bps",
                                          "calculated change (k4)": check.display},
                               "citations": [mgmt],
                               "resolution": "Not resolvable from the filing; reported as a limitation."})
    b.art["definition_checks"].append({"metric": "operating income", "finding": "Starbucks' GAAP operating income "
                                       "includes income from equity investees and gains from asset sales; both are "
                                       "included in the decomposition as income items.", "citations": [rows[6][1].citation_id]})
    b.art["limitations"] += [
        "Driver impacts are management estimates with an undisclosed methodology; they can't be reconciled to line items.",
        "'Wages and benefits' in Note 7 covers store operating expenses only; labor in other lines is not broken out.",
        "Segment-level drivers (North America, International) are not analyzed in this artifact.",
    ]
    b.art["answer_summary"] = (
        f"Operating margin fell {check.display.replace('-', '')} ({m23.display} → {m24.display}). Management cites wage and benefit "
        "investments, deleverage and promotions, partly offset by pricing and efficiencies, but its quantified drivers "
        f"net to only {net} bps. The income statement shows store operating expenses as the largest drag "
        f"({store['contribution_to_margin_change_pp']} pp). The non-recurrence of a fiscal 2023 asset-sale gain "
        f"({gain['contribution_to_margin_change_pp']} pp) goes unmentioned. Wages and benefits barely moved as a share "
        f"of revenue ({ws.display}). The explanation is therefore only partially supported.")
    return finish(b.art)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for build in (gold_q01, gold_q04, gold_q07):
        art = build()
        errors = structural_errors(art)
        (OUT / f"{art['artifact_id']}.json").write_text(json.dumps(art, indent=2, ensure_ascii=False), encoding="utf-8")
        (OUT / f"{art['artifact_id']}.md").write_text(render_markdown(art), encoding="utf-8")
        print(f"{art['artifact_id']}: {len(art['claims'])} claims, {len(art['citations'])} citations, "
              f"{len(art['calculations'])} calcs, structural errors: {errors or 'none'}")


if __name__ == "__main__":
    from app.config import utf8_stdio

    utf8_stdio()
    main()
