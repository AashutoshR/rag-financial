"""Run B0 on the first-session dev questions, score each metric separately, and write a report.

Usage: python -m bench.run_b0 [--generator extractive|ollama|llm]
Outputs: data/runs/<run_id>/artifacts/*.json, bench/reports/b0_<generator>.md, bench/reports/b0_<generator>.json
"""
import argparse
import json
from collections import Counter
from datetime import datetime, timezone

from app import facts
from app.artifact import structural_errors
from app.baseline import run
from app.config import ROOT, RUNS
from app.retrieval import default_index
from bench.checks import answer_failures
from bench.evidence import load_items, resolve_requirement

def equivalent_units(req_ids: set[str]) -> set[str]:
    """Strict ids plus retrievable units in the same document whose text repeats a required cell's displayed value
    next to its row label (e.g. an untagged MD&A table showing the same figure)."""
    out = set(req_ids)
    all_units = facts.all_units()
    for uid in req_ids:
        u = all_units[uid]
        if u["kind"] != "cell" or not u["raw_text"] or len(u["raw_text"]) < 4:
            continue
        label = u["row_path"][-1].lower() if u["row_path"] else ""
        for v in facts.units(u["document_id"]):
            if v["kind"] in ("table", "passage") and u["raw_text"] in v["text"] and label[:20] in v["text"].lower():
                out.add(v["unit_id"])
    return out


def published_after(doc_id: str, as_of: str) -> bool:
    return facts.manifest()[doc_id]["published_at"][:10] > as_of  # UTC date vs cutoff date: conservative enough here


def score(item: dict, art: dict) -> dict:
    exp = item["expected"]
    exposed = art["trace"]["exposed_unit_ids"]
    cited = [c["unit_id"] for c in art["citations"]]
    deep, _ = default_index().search(item["question"], k=20)
    deep_ids = [h["unit"]["unit_id"] for h in deep]
    reqs = [resolve_requirement(r) for r in exp.get("required_evidence", [])]
    r_at_k = [bool(set(exposed) & r) for r in reqs]
    r_at_20 = [bool(set(deep_ids) & r) for r in reqs]
    equiv = [equivalent_units(r) for r in reqs]
    e_at_k = [bool(set(exposed) & e) for e in equiv]
    text = answer_text(art)
    cited_docs = sorted({c["document_id"] for c in art["citations"]})
    outcome_ok = (art["outcome"] == "abstention") == (exp["outcome"] == "abstention")
    future_exposed = future_cited = []
    if item.get("as_of"):
        future_exposed = sorted({u.split(":")[0] for u in exposed if published_after(u.split(":")[0], item["as_of"])})
        future_cited = sorted({d for d in cited_docs if published_after(d, item["as_of"])})
    all_req = set().union(*reqs) if reqs else set()
    cite_hits_required = bool(set(cited) & all_req) if reqs else None
    struct = structural_errors(art)

    answer_level = answer_failures(item, text, cited_docs, art["outcome"])
    failures = []
    if reqs and not all(r_at_k):
        failures.append("retrieval_miss")
    if future_cited:
        failures.append("temporal_leakage:cited_post_cutoff")
    if reqs and cite_hits_required is False and art["outcome"] != "abstention":
        failures.append("citation_not_supporting")
    if struct:
        failures.append("artifact_structure")
    failures += answer_level
    value_names = [v["name"] for v in exp.get("values", [])]
    bad_values = {f.split(":", 1)[1] for f in answer_level
                  if f.split(":")[0] in ("missing_or_wrong_calculation", "wrong_or_missing_value")}
    bad_dir = {f.split(":", 1)[1] for f in answer_level if f.split(":")[0] in ("wrong_direction", "direction_unstated")}
    dir_names = [v["name"] for v in exp.get("values", []) if v.get("direction")]
    n_dir = len(dir_names)
    dir_ok = sum(1 for n in dir_names if n not in bad_values and n not in bad_dir)  # unstated values don't count
    checks = exp.get("checks", [])
    failed_checks = {f.split(":", 1)[1] for f in answer_level if f.startswith("check_failed:")}

    return {
        "id": item["id"], "category": item["category"], "outcome": art["outcome"], "outcome_ok": outcome_ok,
        "requirements": len(reqs), "req_hit_at_k": sum(r_at_k), "req_hit_at_20": sum(r_at_20),
        "req_equiv_at_k": sum(e_at_k),
        "complete_at_k": all(r_at_k) if reqs else None, "complete_at_20": all(r_at_20) if reqs else None,
        "values_expected": len(value_names), "values_correct": len(value_names) - len(bad_values),
        "directions_expected": n_dir, "directions_correct": dir_ok,
        "checks_expected": len(checks), "checks_passed": len(checks) - len(failed_checks),
        "forbidden_value_stated": any(f.startswith("forbidden_value_stated") for f in answer_level),
        "future_docs_exposed": future_exposed, "future_docs_cited": future_cited,
        "citations": len(cited), "citation_hits_required": cite_hits_required, "structural_errors": struct,
        "latency_ms": art["trace"]["latency_ms"], "cost_usd": art["trace"]["cost_usd"],
        "answer": art["answer_summary"][:220], "failures": failures,
    }


def answer_text(art: dict) -> str:
    return art["answer_summary"] + " " + " ".join(c["text"] for c in art["claims"])


def pct(n: int, d: int) -> str:
    return f"{n}/{d} ({100 * n / d:.0f}%)" if d else "n/a"


def metrics(rows: list[dict]) -> list[tuple[str, str]]:
    """(metric, result) pairs, each measured separately. Shared by the Markdown report and the web console."""
    reqs = sum(r["requirements"] for r in rows)
    with_reqs = [r for r in rows if r["requirements"]]
    vals = sum(r["values_expected"] for r in rows)
    answerable = [r for r in rows if "should_abstain" not in r["category"]]
    abstain = [r for r in rows if "should_abstain" in r["category"]]
    temporal = [r for r in rows if "temporal" in r["category"]]
    lat = sorted(r["latency_ms"] for r in rows)
    return [
        ("Required-evidence recall@8 (what B0 used)", pct(sum(r["req_hit_at_k"] for r in rows), reqs)),
        ("Required-evidence recall@8, value-equivalent units also accepted", pct(sum(r["req_equiv_at_k"] for r in rows), reqs)),
        ("Required-evidence recall@20", pct(sum(r["req_hit_at_20"] for r in rows), reqs)),
        ("Complete evidence set @8", pct(sum(bool(r["complete_at_k"]) for r in with_reqs), len(with_reqs))),
        ("Complete evidence set @20", pct(sum(bool(r["complete_at_20"]) for r in with_reqs), len(with_reqs))),
        ("Numerical accuracy (expected values stated correctly)", pct(sum(r["values_correct"] for r in rows), vals)),
        ("Direction of change stated correctly", pct(sum(r["directions_correct"] for r in rows), sum(r["directions_expected"] for r in rows))),
        ("Item-specific checks passed (premise, basis, source, reason…)", pct(sum(r["checks_passed"] for r in rows), sum(r["checks_expected"] for r in rows))),
        ("Correct outcome on answerable questions", pct(sum(r["outcome_ok"] for r in answerable), len(answerable))),
        ("Correct abstention on unanswerable questions", pct(sum(r["outcome_ok"] for r in abstain), len(abstain))),
        ("Citations hitting required evidence", pct(sum(bool(r["citation_hits_required"]) for r in with_reqs), len(with_reqs))),
        ("Citation resolution (artifact structure valid)", pct(sum(not r["structural_errors"] for r in rows), len(rows))),
        ("As-of questions exposed to post-cutoff documents", pct(sum(bool(r["future_docs_exposed"]) for r in temporal), len(temporal))),
        ("As-of questions citing post-cutoff evidence or stating future values",
         pct(sum(bool(r["future_docs_cited"] or r["forbidden_value_stated"]) for r in temporal), len(temporal))),
        ("Latency p50 / max", f"{lat[len(lat) // 2]:.0f} ms / {lat[-1]:.0f} ms"),
        ("Cost total", f"${sum(r['cost_usd'] for r in rows):.4f}"),
    ]


def report(rows: list[dict], generator: str, run_id: str) -> str:
    fail = Counter(f.split(":")[0] for r in rows for f in r["failures"])
    out = [f"# B0 baseline report — generator `{generator}`", "",
           f"Run `{run_id}` · {len(rows)} dev questions (Starbucks, 5 documents) · BM25 top-8 · no filters", "",
           "## Metrics (each reported separately)", "", "| Metric | Result |", "|---|---|"]
    out += [f"| {m} | {v} |" for m, v in metrics(rows)]
    out += ["", "## Failure categories", "", "| Category | Questions |", "|---|---|"]
    out += [f"| {k} | {v} |" for k, v in fail.most_common()]
    out += ["", "## Per question", "", "| Q | Categories | Outcome | Evidence @8 / @20 | Values | Failures | Answer (truncated) |",
            "|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['id']} | {', '.join(r['category'])} | {r['outcome']}{'' if r['outcome_ok'] else ' ✗'} | "
                   f"{r['req_hit_at_k']}/{r['requirements']} · {r['req_hit_at_20']}/{r['requirements']} | "
                   f"{r['values_correct']}/{r['values_expected']} | {', '.join(r['failures']) or '—'} | "
                   f"{r['answer'].replace('|', '/')} |")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--generator", choices=["extractive", "ollama", "llm"], default="extractive")
    args = ap.parse_args()
    run_id = f"b0_{args.generator}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    out_dir = RUNS / run_id / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for item in load_items():
        art = run(item, args.generator)
        (out_dir / f"{art['artifact_id']}.json").write_text(json.dumps(art, indent=2, ensure_ascii=False), encoding="utf-8")
        rows.append(score(item, art))
        print(f"{item['id']}  {rows[-1]['outcome']:<10}  failures: {', '.join(rows[-1]['failures']) or '—'}")
    reports = ROOT / "bench" / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / f"b0_{args.generator}.md").write_text(report(rows, args.generator, run_id), encoding="utf-8")
    (reports / f"b0_{args.generator}.json").write_text(json.dumps({"run_id": run_id, "rows": rows}, indent=2), encoding="utf-8")
    print(f"report: bench/reports/b0_{args.generator}.md")


if __name__ == "__main__":
    main()
