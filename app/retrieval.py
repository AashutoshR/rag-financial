"""Lexical BM25 retrieval baseline over passages and linearized tables [RET-01, RET-07].

Deliberately naive, as B0 requires: no time, permission or metadata filters.
"""
import re
import time
from functools import lru_cache

from rank_bm25 import BM25Okapi

from app import facts

STOP = set("""a an and are as at be by did do does for from had has have how in is it its of on or that the
their this to was were what when which while who why with within using only information available""".split())
TOKEN_RE = re.compile(r"\d[\d,]*(?:\.\d+)?|[a-z][a-z\-']*")
RETRIEVABLE = ("passage", "table")


def tokenize(text: str) -> list[str]:
    out = []
    for t in TOKEN_RE.findall(text.lower().replace("’", "'")):
        t = t.replace(",", "")
        if t not in STOP and len(t) > 1 or t.isdigit():
            out.append(t)
    return out


class Index:
    def __init__(self, units: list[dict]):
        self.units = units
        self.bm25 = BM25Okapi([tokenize(self._doc_text(u)) for u in units])

    @staticmethod
    def _doc_text(u: dict) -> str:
        return " ".join(filter(None, [u.get("section"), u.get("heading"), u.get("caption"), u["text"]]))

    def search(self, query: str, k: int = 8) -> tuple[list[dict], dict]:
        t0 = time.perf_counter()
        scores = self.bm25.get_scores(tokenize(query))
        order = sorted(range(len(scores)), key=lambda i: -scores[i])[:k]
        hits = [{"rank": r + 1, "score": round(float(scores[i]), 4), "unit": self.units[i]} for r, i in enumerate(order)]
        log = {"query": query, "k": k, "filters": None, "strategy": "bm25",
               "results": [(h["unit"]["unit_id"], h["score"]) for h in hits],
               "latency_ms": round((time.perf_counter() - t0) * 1000, 1)}
        return hits, log


@lru_cache(maxsize=1)
def default_index() -> Index:
    units = [u for doc in facts.manifest() for u in facts.units(doc) if u["kind"] in RETRIEVABLE]
    return Index(units)
