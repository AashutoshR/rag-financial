"""Build, validate and render investigation artifacts (requirements §10)."""
import json
from datetime import datetime, timezone

import jsonschema

from app import facts
from app.config import ROOT

SCHEMA = json.loads((ROOT / "app" / "schemas" / "artifact.schema.json").read_text(encoding="utf-8"))


def snapshot() -> dict:
    """First-session stand-in for a CSN: the manifest length (append-only, so monotonic)."""
    recs = facts.manifest()
    lines = [l for l in (ROOT / "corpus" / "manifest.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    return {"csn": len(lines),
            "versions": [{"document_id": r["document_id"], "version": r["version"], "sha256": r["sha256"]}
                         for r in recs.values()]}


def as_of_block(date: str | None) -> dict | None:
    if not date:
        return None
    return {"date": date, "interpretation": f"published_at <= {date}T23:59:59-04:00 (America/New_York, EDT)",
            "mode": "world"}


def citation(cid: str, unit: dict) -> dict:
    rec = facts.manifest()[unit["document_id"]]
    loc = {k: unit.get(k) for k in ("section", "heading", "html_page", "printed_page", "dom_anchor")}
    if unit["kind"] == "cell":
        table = facts.all_units()[unit["table_id"]]
        loc.update({"table_id": unit["table_id"], "table_caption": table.get("caption"),
                    "row": " > ".join(unit["row_path"]), "column": unit["col_header"],
                    "ixbrl_element_id": (unit.get("ixbrl") or {}).get("element_id")})
    elif unit.get("element_id"):
        loc["element_id"] = unit["element_id"]
    out = {
        "id": cid,
        "unit_id": unit["unit_id"],
        "kind": unit["kind"],
        "document_id": unit["document_id"],
        "form_type": rec["form_type"],
        "accession": rec["accession"],
        "version_sha256": unit["sha256"],
        "published_at": rec["published_at"],
        "locator": loc,
        "quote": unit["raw_text"] if unit["kind"] == "cell" else unit["text"][:600],
    }
    if unit["kind"] == "cell":
        ix = unit.get("ixbrl") or {}
        out.update({"scale": unit["scale_hint"], "currency": (ix.get("unit") or "").upper() or None,
                    "xbrl_concept": ix.get("concept"), "xbrl_period": ix.get("period"), "xbrl_value": ix.get("value")})
    return out


def new_artifact(artifact_id: str, question: str, principal: str, as_of: str | None) -> dict:
    return {
        "schema_version": "1.0", "artifact_id": artifact_id, "question": question, "principal": principal,
        "as_of": as_of_block(as_of), "snapshot": snapshot(), "outcome": "answer", "answer_summary": "",
        "claims": [], "citations": [], "calculations": [], "conflicts": [], "definition_checks": [],
        "limitations": [], "abstentions": [], "security_flags": [], "trace": {}, "versions": {},
        "status": "valid", "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def structural_errors(art: dict) -> list[str]:
    """Schema validation plus the checks in requirements §10 that a schema can't express."""
    errors = [e.message for e in jsonschema.Draft202012Validator(SCHEMA).iter_errors(art)]
    cites = {c["id"]: c for c in art.get("citations", [])}
    calcs = {k["id"] for k in art.get("calculations", [])}
    units = facts.all_units()
    for c in cites.values():
        u = units.get(c["unit_id"])
        if u is None or u["sha256"] != c["version_sha256"]:
            errors.append(f"citation {c['id']} does not resolve to {c['unit_id']} in the recorded version")
    for cl in art.get("claims", []):
        for cid in cl["citation_ids"]:
            if cid not in cites:
                errors.append(f"claim {cl['id']} cites missing citation {cid}")
        for kid in cl["calculation_ids"]:
            if kid not in calcs:
                errors.append(f"claim {cl['id']} references missing calculation {kid}")
        if cl["type"] != "system_inference" and not cl["citation_ids"] and not cl["calculation_ids"]:
            errors.append(f"material claim {cl['id']} has no citation or calculation")
    return errors


def render_markdown(art: dict) -> str:
    out = [f"# Artifact `{art['artifact_id']}`", "", f"**Question:** {art['question']}", "",
           f"**Principal:** {art['principal']} · **As of:** "
           f"{art['as_of']['interpretation'] if art['as_of'] else 'none (latest available)'} · "
           f"**Snapshot CSN:** {art['snapshot']['csn']} · **Outcome:** {art['outcome']} · **Status:** {art['status']}",
           "", "## Answer", "", art["answer_summary"], "", "## Claims", "",
           "| # | Type | Support | Claim | Citations | Calcs |", "|---|---|---|---|---|---|"]
    for c in art["claims"]:
        out.append(f"| {c['id']} | {c['type']} | {c['support']} | {c['text']} | {', '.join(c['citation_ids'])} | "
                   f"{', '.join(c['calculation_ids'])} |")
    out += ["", "## Calculations", ""]
    for k in art["calculations"]:
        out.append(f"**{k['id']}** `{k['formula']}` → **{k['result']['display']}**")
        for i in k["inputs"]:
            out.append(f"- {i['name']} = {i['value']} {i['unit']} ({i['period']}) [{i['citation_id']}]")
        for n in k.get("notes", []):
            out.append(f"- note: {n}")
        if "contributions" in k:
            out.append("")
            out.append("| Line | Share FY-new | Share FY-old | Contribution (pp) |")
            out.append("|---|---|---|---|")
            for row in k["contributions"]:
                out.append(f"| {row['line']} | {float(row['share_of_revenue_new']):.4%} | "
                           f"{float(row['share_of_revenue_old']):.4%} | {row['contribution_to_margin_change_pp']} |")
        out.append("")
    out += ["## Citations", ""]
    for c in art["citations"]:
        loc = c["locator"]
        where = " · ".join(str(x) for x in [c["form_type"], loc.get("section"), loc.get("table_caption") or loc.get("heading"),
                                             loc.get("row"), loc.get("column"),
                                             f"printed p.{loc.get('printed_page')}" if loc.get("printed_page") else None] if x)
        out.append(f"- **{c['id']}** `{c['unit_id']}` — {where} — published {c['published_at']}\n  > {c['quote'][:300]}")
    for title, key in [("Conflicts", "conflicts"), ("Definition checks", "definition_checks"),
                       ("Abstentions", "abstentions"), ("Security flags", "security_flags")]:
        if art[key]:
            out += ["", f"## {title}", ""] + [f"- {json.dumps(x, ensure_ascii=False)}" for x in art[key]]
    if art["limitations"]:
        out += ["", "## Limitations", ""] + [f"- {x}" for x in art["limitations"]]
    out += ["", "## Trace and versions", "", f"```json\n{json.dumps({'trace': art['trace'], 'versions': art['versions']}, indent=2)}\n```"]
    return "\n".join(out)
