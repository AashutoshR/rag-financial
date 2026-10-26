"""Resolve benchmark evidence specs to evidence-unit IDs.

A requirement is a list of alternative specs; it is satisfied if any unit matching any alternative is found.
Cell matches also count their parent table, and paragraph matches count their parent passage, because
retrieval returns tables and passages.
"""
import json
import re

from app.config import ROOT
from app import facts

ITEMS_DIR = ROOT / "bench" / "items"


def load_items() -> list[dict]:
    """All benchmark items, Core (dev_first20) first, then Frontier (dev_frontier)."""
    items = []
    for path in sorted(ITEMS_DIR.glob("*.json"), key=lambda p: (p.name != "dev_first20.json", p.name)):
        items += json.loads(path.read_text(encoding="utf-8"))["items"]
    return items


def resolve_spec(spec: dict) -> set[str]:
    if "concept" in spec:
        cells = facts.find_cells(spec["doc"], spec["concept"], spec["start"], spec["end"], spec.get("dims"))
        return {c["unit_id"] for c in cells} | {c["table_id"] for c in cells}
    kinds = tuple(spec.get("kinds", ["paragraph"]))
    hits = facts.find_text(spec["doc"], spec["text"], kinds)
    ids = {u["unit_id"] for u in hits}
    for p in facts.units(spec["doc"]):
        if p["kind"] == "passage" and ids & set(p.get("paragraph_ids", [])):
            ids.add(p["unit_id"])
    return ids


def resolve_requirement(alternatives: list[dict]) -> set[str]:
    ids = set()
    for spec in alternatives:
        ids |= resolve_spec(spec)
    return ids


if __name__ == "__main__":
    from app.config import utf8_stdio

    utf8_stdio()
    bad = 0
    for item in load_items():
        for k, req in enumerate(item["expected"].get("required_evidence", [])):
            ids = resolve_requirement(req)
            status = "ok " if ids else "MISSING"
            bad += not ids
            print(f"{item['id']} req{k}: {status} {len(ids):3d} units  e.g. {sorted(ids)[:2]}")
    print("unresolved requirements:", bad)
