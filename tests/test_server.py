"""Smoke and safety tests for the web console API. Run: python -m pytest -q"""
import time

import pytest
from fastapi.testclient import TestClient

from app import server

client = TestClient(server.app)


@pytest.fixture(autouse=True)
def isolated_runs(tmp_path, monkeypatch):
    """Artifacts from test investigations go to a temporary folder, not the project's data/runs."""
    monkeypatch.setattr(server, "WEB_RUNS", tmp_path / "web")


def test_status_and_questions():
    s = client.get("/api/status").json()
    assert s["generators"]["extractive"]["available"] is True
    assert s["documents"] == 5
    qs = client.get("/api/questions").json()
    assert {"q01", "h07"} <= {q["id"] for q in qs}


def test_benchmark_investigation_runs_and_is_scored():
    jid = client.post("/api/investigations", json={"item_id": "q06", "generator": "extractive"}).json()["id"]
    for _ in range(100):
        job = client.get(f"/api/investigations/{jid}").json()
        if job["status"] in ("done", "error"):
            break
        time.sleep(0.1)
    assert job["status"] == "done", job.get("error")
    assert job["artifact"]["as_of"]["date"] == "2025-06-30"  # taken from the benchmark item, not the client
    assert job["score"]["id"] == "q06" and "failures" in job["score"]
    assert "item" not in job["request"]  # the full item (expected answers) is not echoed to the browser


def test_rejects_bad_requests(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    assert client.post("/api/investigations", json={"question": "x", "generator": "llm"}).status_code == 400
    assert client.post("/api/investigations", json={"question": "x", "generator": "nope"}).status_code == 400
    assert client.post("/api/investigations", json={"question": " ", "generator": "extractive"}).status_code == 400
    assert client.post("/api/investigations", json={"question": "x", "as_of": "June 30", "generator": "extractive"}).status_code == 400


def test_unit_lookup_includes_table_context():
    data = client.get("/api/units/sbux_10k_fy2024:v1:cell:541").json()
    assert data["unit"]["raw_text"] == "36,176.2"
    assert any(c["unit_id"] == "sbux_10k_fy2024:v1:cell:541" for c in data["table"]["cells"])
    assert client.get("/api/units/does-not-exist").status_code == 404


def test_source_viewer_blocks_scripts_and_drops_unsafe_ids():
    r = client.get('/source/sbux_10k_fy2024?el=u-b-797,"><script>alert(1)</script>')
    assert r.status_code == 200
    csp = r.headers["content-security-policy"]
    assert "default-src 'none'" in csp and "sandbox" in csp
    assert '[id="u-b-797"]' in r.text
    assert "alert(1)" not in r.text
    assert 'id="u-b-797"' in r.text  # positional anchor added to the stored filing


@pytest.mark.parametrize("path", ["/api/artifacts/..%2F..%2Fcorpus%2Fsources", "/api/runs/..%2F..%2F/artifacts/x",
                                  "/source/..%2Fcorpus"])
def test_no_path_traversal(path):
    assert client.get(path).status_code in (400, 404)
