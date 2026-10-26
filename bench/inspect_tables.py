"""Manual table inspection + automatic cross-check of extracted cells against the SEC XBRL API.

Writes docs/table_inspection.md. Usage: python -m bench.inspect_tables
"""
import json
from decimal import Decimal

from app.config import DATA, MANIFEST, ROOT
from app.extract import load_units

INSPECT = {  # (document_id, heading substring) — the tables checked by hand this session
    "sbux_10k_fy2024": ["CONSOLIDATED STATEMENTS OF EARNINGS", "Note 17: Segment Reporting", "Note 7: Supplemental"],
    "sbux_10q_q2fy2025": ["CONSOLIDATED STATEMENTS OF EARNINGS"],
}


def companyfacts_index(cik: str) -> dict:
    cf = json.loads((DATA / "raw" / f"companyfacts_CIK{cik}.json").read_text(encoding="utf-8"))
    index = {}
    for taxonomy, concepts in cf["facts"].items():
        for concept, body in concepts.items():
            for unit, values in body["units"].items():
                for v in values:
                    key = (f"{taxonomy}:{concept}", v["accn"], v.get("start"), v["end"])
                    index[key] = Decimal(str(v["val"]))
    return index


def main() -> None:
    records = [json.loads(l) for l in MANIFEST.read_text(encoding="utf-8").splitlines() if l.strip()]
    out = ["# Table inspection — first working session", ""]
    out.append("Automatic check: every extracted cell with a non-dimensional iXBRL fact is compared with the "
               "value the SEC company-facts API reports for the same concept, accession and period.\n")
    out.append("| Document | Cells checked | Match | Mismatch | Not in API |")
    out.append("|---|---|---|---|---|")
    mismatches, index_cache = [], {}
    for rec in records:
        units = load_units(rec)
        idx = index_cache.setdefault(rec["cik"], companyfacts_index(rec["cik"]))
        checked = match = missing = 0
        for u in units:
            ix = u.get("ixbrl")
            if u["kind"] != "cell" or not ix or ix["dims"] or ix["value"] is None:
                continue
            p = ix["period"]
            key = (ix["concept"], rec["accession"], p["start"], p["end"] or p["instant"])
            checked += 1
            if key not in idx:
                missing += 1
            elif idx[key] == Decimal(ix["value"]):
                match += 1
            else:
                mismatches.append((u["unit_id"], ix["concept"], ix["value"], str(idx[key])))
        out.append(f"| {rec['document_id']} | {checked} | {match} | {checked - match - missing} | {missing} |")
    out.append("")
    if mismatches:
        out.append("## Mismatches\n")
        out += [f"- `{m[0]}` {m[1]}: extracted {m[2]}, API {m[3]}" for m in mismatches[:30]]
        out.append("")

    out.append("## Tables inspected by hand\n")
    for rec in records:
        if rec["document_id"] not in INSPECT:
            continue
        units = load_units(rec)
        by_id = {u["unit_id"]: u for u in units}
        for wanted in INSPECT[rec["document_id"]]:
            table = next((u for u in units if u["kind"] == "table" and wanted.lower() in (u["caption"] or "").lower()), None)
            if table is None:
                out.append(f"### {rec['document_id']} — `{wanted}`: **NOT FOUND**\n")
                continue
            cells = [by_id[i] for i in table["cell_ids"]]
            out.append(f"### {rec['document_id']} — {table['caption']}")
            out.append(f"`{table['unit_id']}` · {table['section']} · HTML page {table['html_page']} "
                       f"(printed {table['printed_page']}) · scale hint: {table['scale_hint']}\n")
            out.append("| Row | Column | Raw | Scale | Neg. shown | iXBRL concept | Period | Dims | Value |")
            out.append("|---|---|---|---|---|---|---|---|---|")
            for c in cells[:40]:
                ix = c.get("ixbrl") or {}
                period = ix.get("period") or {}
                per = f"{period.get('start') or ''}→{period.get('end') or period.get('instant') or ''}" if ix else ""
                dims = ", ".join(v.split(":")[-1] for v in (ix.get("dims") or {}).values())
                out.append(f"| {' > '.join(c['row_path'])} | {c['col_header']} | {c['raw_text']} | {c['scale_hint']} | "
                           f"{'yes' if c['negative_display'] else ''} | {ix.get('concept', '—')} | {per} | {dims} | {ix.get('value', '')} |")
            if len(cells) > 40:
                out.append(f"\n…{len(cells) - 40} more cells")
            out.append("")
    path = ROOT / "docs" / "table_inspection.md"
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {path}  mismatches={len(mismatches)}")


if __name__ == "__main__":
    from app.config import utf8_stdio

    utf8_stdio()
    main()
