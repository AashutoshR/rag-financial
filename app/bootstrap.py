"""Prepare a fresh checkout: verify the stored filings, extract evidence, build gold answers, run the baseline.

The filings themselves are committed (data/blobs) so results are reproducible without network access; everything
else under data/ is derived and rebuilt here. Usage: python -m app.bootstrap
"""
import hashlib
import json
import os
import subprocess
import sys

from app.config import MANIFEST
from app import store


def verify_blobs() -> None:
    records = [json.loads(line) for line in MANIFEST.read_text(encoding="utf-8").splitlines() if line.strip()]
    for rec in records:
        path = store.path_for(rec["sha256"])
        if not path.exists():
            sys.exit(f"missing source file for {rec['document_id']} ({path}); run: python -m app.ingest")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != rec["sha256"]:
            sys.exit(f"{rec['document_id']}: stored file hash {actual[:12]} does not match manifest {rec['sha256'][:12]}")
    print(f"verified   {len(records)} source files against the manifest", flush=True)


def step(module: str, *args: str) -> None:
    print(f"running    python -m {module} {' '.join(args)}".rstrip(), flush=True)
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    subprocess.run([sys.executable, "-W", "ignore", "-m", module, *args], check=True, env=env)


def main() -> None:
    verify_blobs()
    step("app.extract")
    step("bench.make_gold")
    step("bench.run_b0", "--generator", "extractive")
    print("ready      start the console: python -m uvicorn app.server:app --port 8000")


if __name__ == "__main__":
    from app.config import utf8_stdio

    utf8_stdio()
    main()
