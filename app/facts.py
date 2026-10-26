"""Look up evidence units by iXBRL fact or by text, across the extracted corpus."""
import json
import re
from functools import lru_cache

from app.config import MANIFEST
from app.extract import load_units


@lru_cache(maxsize=1)
def manifest() -> dict[str, dict]:
    """Latest manifest record per document."""
    out = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            out[rec["document_id"]] = rec
    return out


@lru_cache(maxsize=None)
def units(document_id: str) -> tuple[dict, ...]:
    return tuple(load_units(manifest()[document_id]))


@lru_cache(maxsize=1)
def all_units() -> dict[str, dict]:
    return {u["unit_id"]: u for doc in manifest() for u in units(doc)}


def find_cells(document_id: str, concept: str, start: str | None, end: str, dims: dict | None = None,
               heading: str | None = None) -> list[dict]:
    """Cells tagged with an iXBRL fact matching concept, period and dimensions (default: no dimensions)."""
    dims = dims or {}
    found = []
    for u in units(document_id):
        ix = u.get("ixbrl")
        if u["kind"] != "cell" or not ix or ix["concept"] != concept or ix["dims"] != dims:
            continue
        p = ix["period"]
        if p["start"] == start and (p["end"] or p["instant"]) == end:
            if heading is None or heading.lower() in (u["heading"] or "").lower():
                found.append(u)
    return found


def cell(document_id: str, concept: str, start: str | None, end: str, dims: dict | None = None,
         heading: str | None = None) -> dict:
    found = find_cells(document_id, concept, start, end, dims, heading)
    if not found:
        raise LookupError(f"no cell for {document_id} {concept} {start}..{end} {dims}")
    return found[0]


def find_text(document_id: str, pattern: str, kinds=("paragraph",)) -> list[dict]:
    rx = re.compile(pattern, re.I)
    return [u for u in units(document_id) if u["kind"] in kinds and rx.search(u["text"])]
