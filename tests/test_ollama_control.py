"""A stalled or cancelled local-model run must stop promptly instead of hanging. Run: python -m pytest -q"""
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from app import baseline
from app.baseline import GenerationStopped, RunControl, generate_ollama
from app.retrieval import default_index


class SilentOllama(BaseHTTPRequestHandler):
    """Accepts the chat request, then sends nothing, like a model stalled on a full GPU."""

    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        time.sleep(30)

    def log_message(self, *args):
        pass


class SlowTokens(BaseHTTPRequestHandler):
    """Streams one token, then stalls between tokens."""

    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")
        self.end_headers()
        self.wfile.write(json.dumps({"message": {"content": "{"}, "done": False}).encode() + b"\n")
        self.wfile.flush()
        time.sleep(30)

    def log_message(self, *args):
        pass


@pytest.fixture
def fake_ollama(monkeypatch):
    servers = []

    def start(handler):
        srv = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        srv.daemon_threads = True
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        servers.append(srv)
        monkeypatch.setattr(baseline, "OLLAMA_URL", f"http://127.0.0.1:{srv.server_address[1]}")
        return srv

    yield start
    for srv in servers:
        srv.shutdown()


HITS, _ = default_index().search("What were Starbucks' net revenues from Japan in fiscal 2024?", k=2)


def test_watchdog_stops_a_run_with_no_first_token(fake_ollama, monkeypatch):
    fake_ollama(SilentOllama)
    monkeypatch.setattr(baseline, "OLLAMA_FIRST_TOKEN_S", 2)
    t0 = time.perf_counter()
    with pytest.raises(GenerationStopped, match="no progress"):
        generate_ollama("q", HITS)
    assert time.perf_counter() - t0 < 10


def test_watchdog_stops_a_run_that_stalls_between_tokens(fake_ollama, monkeypatch):
    fake_ollama(SlowTokens)
    monkeypatch.setattr(baseline, "OLLAMA_TOKEN_GAP_S", 2)
    t0 = time.perf_counter()
    with pytest.raises(GenerationStopped, match="between tokens"):
        generate_ollama("q", HITS)
    assert time.perf_counter() - t0 < 10


def test_cancel_stops_a_running_generation(fake_ollama):
    fake_ollama(SilentOllama)
    control = RunControl()
    result = {}

    def target():
        try:
            generate_ollama("q", HITS, control)
        except GenerationStopped as exc:
            result["stopped"] = str(exc)

    th = threading.Thread(target=target)
    th.start()
    time.sleep(1.0)
    t0 = time.perf_counter()
    control.cancel()
    th.join(timeout=10)
    assert not th.is_alive(), "generation kept running after cancel"
    assert result["stopped"] == "cancelled by the reviewer"
    assert time.perf_counter() - t0 < 5
