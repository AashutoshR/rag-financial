"""Paths and settings shared by every module."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
BLOBS = DATA / "blobs"
EXTRACTED = DATA / "extracted"
RUNS = DATA / "runs"
CORPUS = ROOT / "corpus"
MANIFEST = CORPUS / "manifest.jsonl"
SOURCES = CORPUS / "sources.json"

# SEC asks for a descriptive User-Agent with contact details. Set SEC_USER_AGENT to your own.
SEC_USER_AGENT = os.environ.get(
    "SEC_USER_AGENT", "rag-financial-capstone research project admin@example.com"
)
SEC_MAX_RPS = 5  # below the SEC's 10 requests/second limit

PARSER_VERSION = "ixbrl-html@0.1.3"
