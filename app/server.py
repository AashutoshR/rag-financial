"""Reviewer web console: ask questions, inspect artifacts down to the source cell, browse benchmark results.

Run:  python -m uvicorn app.server:app --port 8000
"""
import json
import os
import queue
import re
import threading
import time
import uuid
from datetime import date
from functools import lru_cache

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import facts, store
from app.baseline import (BLOCK_CHARS, GENERATORS, K, OLLAMA_FIRST_TOKEN_S, OLLAMA_MODEL, OLLAMA_NUM_GPU,
                          OLLAMA_TOKEN_GAP_S, OLLAMA_URL, GenerationStopped, RunControl, run)
from app.config import EXTRACTED, PARSER_VERSION, ROOT, RUNS
from app.extract import anchor_ids
from bench.evidence import load_items
from bench.run_b0 import metrics, score

WEB = ROOT / "web"
WEB_RUNS = RUNS / "web"
REPORTS = ROOT / "bench" / "reports"
GOLD = ROOT / "bench" / "gold"
SAFE_ID = re.compile(r"^[A-Za-z0-9_.:\-]+$")

app = FastAPI(title="Financial Investigation Console")
app.mount("/static", StaticFiles(directory=WEB), name="static")


@app.middleware("http")
async def no_stale_assets(request, call_next):
    """Revalidate the page and its assets on every load, so an edited console never runs against stale JS/CSS."""
    response = await call_next(request)
    if request.url.path == "/" or request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache"
    return response


# ---- generator availability -------------------------------------------------------------------
def ollama_status() -> dict:
    try:
        tags = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2).json()
        names = [m["name"] for m in tags.get("models", [])]
        return {"available": OLLAMA_MODEL in names, "model": OLLAMA_MODEL, "installed": names,
                "detail": None if OLLAMA_MODEL in names else f"model {OLLAMA_MODEL} not pulled"}
    except requests.RequestException:
        return {"available": False, "model": OLLAMA_MODEL, "installed": [], "detail": f"no Ollama server at {OLLAMA_URL}"}


def generators() -> dict:
    o = ollama_status()
    key = bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))
    return {
        "extractive": {"available": True, "label": "Extractive (no model)", "detail": "deterministic lower bound"},
        "ollama": {"available": o["available"], "label": f"Ollama · {o['model']}", "detail": o["detail"] or "local, runs on this machine"},
        "llm": {"available": key, "label": "Claude API", "detail": None if key else "set ANTHROPIC_API_KEY to enable"},
    }


# ---- job queue: one investigation at a time (the local model saturates the CPU) ----------------
class Jobs:
    def __init__(self):
        self.jobs: dict[str, dict] = {}
        self.order: list[str] = []
        self.q: queue.Queue[str] = queue.Queue()
        self.controls: dict[str, RunControl] = {}
        self.lock = threading.Lock()
        threading.Thread(target=self._worker, daemon=True).start()

    def submit(self, req: dict) -> str:
        jid = uuid.uuid4().hex[:10]
        with self.lock:
            self.jobs[jid] = {"id": jid, "status": "queued", "stage": "queued", "request": req,
                              "created": time.time(), "started": None, "finished": None,
                              "artifact": None, "score": None, "error": None, "progress": {}}
            self.order.append(jid)
        self.q.put(jid)
        return jid

    def view(self, jid: str) -> dict:
        with self.lock:
            job = self.jobs.get(jid)
            if job is None:
                raise KeyError(jid)
            ahead = [j for j in self.order if self.jobs[j]["status"] == "queued" and self.jobs[j]["created"] < job["created"]]
            out = dict(job, queue_position=len(ahead) if job["status"] == "queued" else 0)
        now = job["finished"] or time.time()
        out["elapsed_s"] = round(now - (job["started"] or job["created"]), 1)
        return out

    def recent(self, n: int = 15) -> list[dict]:
        with self.lock:
            return [{k: self.jobs[j][k] for k in ("id", "status", "created")} | {"question": self.jobs[j]["request"]["question"],
                    "generator": self.jobs[j]["request"]["generator"]} for j in reversed(self.order[-n:])]

    def _set(self, jid: str, **kw):
        with self.lock:
            self.jobs[jid].update(kw)

    def cancel(self, jid: str) -> dict:
        """Cancel a queued job outright; for a running one, cut the model connection (the worker then reports it)."""
        with self.lock:
            job = self.jobs.get(jid)
            if job is None:
                raise KeyError(jid)
            if job["status"] == "queued":
                job.update(status="cancelled", stage="cancelled", error="cancelled by the reviewer", finished=time.time())
            control = self.controls.get(jid) if job["status"] == "running" else None
        if control:
            control.cancel()
        return self.view(jid)

    def _worker(self):
        while True:
            jid = self.q.get()
            if self.jobs[jid]["status"] == "cancelled":
                continue
            req = self.jobs[jid]["request"]
            control = RunControl(progress=lambda stage, _jid=jid, **info: self._set(_jid, stage=stage, progress=info))
            with self.lock:
                self.controls[jid] = control
            self._set(jid, status="running", stage="retrieving", started=time.time())
            try:
                item = req["item"] or {"id": f"adhoc_{jid}", "question": req["question"], "principal": "analyst_public",
                                       "as_of": req["as_of"]}
                art = run(item, req["generator"], control)
                art["artifact_id"] = f"web_{req['generator']}_{jid}"
                WEB_RUNS.mkdir(parents=True, exist_ok=True)
                (WEB_RUNS / f"{art['artifact_id']}.json").write_text(json.dumps(art, indent=2, ensure_ascii=False), encoding="utf-8")
                sc = score(req["item"], art) if req["item"] else None
                self._set(jid, status="done", stage="done", artifact=art, score=sc, finished=time.time())
            except GenerationStopped as exc:
                cancelled = str(exc) == "cancelled by the reviewer"
                self._set(jid, status="cancelled" if cancelled else "error", stage="cancelled" if cancelled else "error",
                          error=str(exc), finished=time.time())
            except Exception as exc:  # surfaced to the reviewer; the queue keeps running
                self._set(jid, status="error", stage="error", error=f"{type(exc).__name__}: {exc}", finished=time.time())
            finally:
                with self.lock:
                    self.controls.pop(jid, None)


JOBS = Jobs()


class InvestigationRequest(BaseModel):
    question: str = Field(default="", max_length=2000)
    as_of: str | None = None
    generator: str = "extractive"
    item_id: str | None = None


# ---- API ----------------------------------------------------------------------------------------
@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


@app.get("/api/status")
def status():
    lines = [l for l in (ROOT / "corpus" / "manifest.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    return {"generators": generators(), "csn": len(lines), "documents": len(facts.manifest()),
            "parser": PARSER_VERSION, "retriever": f"BM25 top-{K}, no filters (baseline B0)",
            "evidence_chars_per_block": BLOCK_CHARS,
            "ollama": {"num_gpu": OLLAMA_NUM_GPU or "auto", "first_token_limit_s": OLLAMA_FIRST_TOKEN_S,
                       "token_gap_limit_s": OLLAMA_TOKEN_GAP_S}}


@app.get("/api/questions")
def questions():
    return [{"id": i["id"], "question": i["question"], "as_of": i.get("as_of"), "category": i["category"],
             "family": i.get("family"), "expected_outcome": i["expected"]["outcome"],
             "expected_values": i["expected"].get("values", []), "checks": i["expected"].get("checks", []),
             "flags": i["expected"].get("expected_flags", [])} for i in load_items()]


@app.post("/api/investigations")
def create_investigation(req: InvestigationRequest):
    gens = generators()
    if req.generator not in GENERATORS:
        raise HTTPException(400, f"unknown generator {req.generator}")
    if not gens[req.generator]["available"]:
        raise HTTPException(400, f"{gens[req.generator]['label']} is not available: {gens[req.generator]['detail']}")
    item = None
    if req.item_id:
        item = next((i for i in load_items() if i["id"] == req.item_id), None)
        if item is None:
            raise HTTPException(404, f"no benchmark item {req.item_id}")
    question = item["question"] if item else req.question.strip()
    if not question:
        raise HTTPException(400, "question is empty")
    as_of = item.get("as_of") if item else req.as_of
    if as_of:
        try:
            date.fromisoformat(as_of)
        except ValueError:
            raise HTTPException(400, "as_of must be YYYY-MM-DD")
    jid = JOBS.submit({"question": question, "as_of": as_of, "generator": req.generator, "item": item})
    return {"id": jid}


@app.get("/api/investigations")
def list_investigations():
    return JOBS.recent()


@app.post("/api/investigations/{jid}/cancel")
def cancel_investigation(jid: str):
    try:
        job = JOBS.cancel(jid)
    except KeyError:
        raise HTTPException(404, "no such investigation")
    return {"id": jid, "status": job["status"]}


@app.get("/api/investigations/{jid}")
def get_investigation(jid: str):
    try:
        job = JOBS.view(jid)
    except KeyError:
        raise HTTPException(404, "no such investigation")
    job["request"] = {k: v for k, v in job["request"].items() if k != "item"} | {"item_id": (job["request"]["item"] or {}).get("id")}
    return job


def doc_meta(doc_id: str) -> dict:
    r = facts.manifest()[doc_id]
    return {k: r[k] for k in ("document_id", "form_type", "fiscal_label", "period_end", "published_at", "ingested_at",
                              "accession", "origin_url", "role", "sha256", "version")}


@app.get("/api/units/{unit_id:path}")
def get_unit(unit_id: str):
    u = facts.all_units().get(unit_id)
    if u is None:
        raise HTTPException(404, "no such evidence unit")
    out = {"unit": u, "document": doc_meta(u["document_id"])}
    units = facts.all_units()
    if u["kind"] in ("cell", "table"):
        table = u if u["kind"] == "table" else units[u["table_id"]]
        out["table"] = {"unit_id": table["unit_id"], "caption": table.get("caption"), "scale_hint": table.get("scale_hint"),
                        "cells": [{k: units[c].get(k) for k in ("unit_id", "row_path", "col_header", "raw_text")}
                                  for c in table["cell_ids"]]}
    if u["kind"] == "passage":
        out["paragraphs"] = [{"unit_id": p, "text": units[p]["text"]} for p in u.get("paragraph_ids", [])]
    return out


@app.get("/api/documents")
def documents():
    out = []
    for doc_id, r in facts.manifest().items():
        rep_path = EXTRACTED / doc_id / f"v{r['version']}" / "report.json"
        rep = json.loads(rep_path.read_text(encoding="utf-8")) if rep_path.exists() else {}
        out.append(doc_meta(doc_id) | {"units": rep.get("units"), "ixbrl_linked": rep.get("ixbrl_facts_linked_to_cells"),
                                       "ixbrl_total": rep.get("ixbrl_numeric_facts_in_document")})
    return out


@lru_cache(maxsize=8)
def anchored_html(doc_id: str) -> str:
    """The original filing with the extractor's positional anchors added as ids (cached per document)."""
    html = store.path_for(facts.manifest()[doc_id]["sha256"]).read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    for el, anchor in anchor_ids(soup):
        if not el.get("id"):
            el["id"] = anchor
        elif el["id"] != anchor:
            el["data-anchor"] = anchor
            el.insert(0, soup.new_tag("a", attrs={"id": anchor}))
    return str(soup)


@app.get("/source/{doc_id}")
def source(doc_id: str, el: str | None = None):
    """Serve an original filing for the evidence viewer. Filings are untrusted: no scripts, no external loads."""
    if doc_id not in facts.manifest():
        raise HTTPException(404, "no such document")
    targets = [t for t in (el or "").split(",") if t and SAFE_ID.match(t)][:2]
    css = ":root{color-scheme:light}html,body{background:#fff!important;color:#000}" + "".join(f'[id="{t}"]{{outline:3px solid #d97706!important;outline-offset:2px;background:#fef3c7!important;'
                  f'scroll-margin-top:40vh}}' for t in targets)
    html = anchored_html(doc_id).replace("</head>", f"<style>{css}</style></head>", 1)
    headers = {"Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; img-src data:; sandbox",
               "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer"}
    return Response(html, media_type="text/html; charset=utf-8", headers=headers)


@app.get("/api/reports")
def reports():
    out = []
    for path in sorted(REPORTS.glob("b0_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        generator = path.stem.removeprefix("b0_")
        out.append({"generator": generator, "run_id": data["run_id"], "metrics": metrics(data["rows"]), "rows": data["rows"]})
    return out


def find_artifact(artifact_id: str) -> dict | None:
    if not SAFE_ID.match(artifact_id):
        return None
    for d in [GOLD, WEB_RUNS, *sorted(RUNS.glob("b0_*/artifacts"), reverse=True)]:
        p = d / f"{artifact_id}.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return None


@app.get("/api/runs/{run_id}/artifacts/{artifact_id}")
def run_artifact(run_id: str, artifact_id: str):
    if not (SAFE_ID.match(run_id) and SAFE_ID.match(artifact_id)):
        raise HTTPException(400, "bad id")
    p = RUNS / run_id / "artifacts" / f"{artifact_id}.json"
    if not p.exists():
        raise HTTPException(404, "no such artifact")
    return json.loads(p.read_text(encoding="utf-8"))


@app.get("/api/artifacts/{artifact_id}")
def get_artifact(artifact_id: str):
    art = find_artifact(artifact_id)
    if art is None:
        raise HTTPException(404, "no such artifact")
    return art


@app.get("/api/gold")
def gold():
    return [{"artifact_id": p.stem, "question": json.loads(p.read_text(encoding="utf-8"))["question"]}
            for p in sorted(GOLD.glob("*.json"))]
