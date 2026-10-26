"""Download the documents in corpus/sources.json, store them immutably, and append to the manifest.

Re-running is idempotent: a document whose bytes are already in the manifest is skipped [EXT-01].
Usage: python -m app.ingest
"""
import json
from datetime import datetime, timezone

from app import edgar, store
from app.config import MANIFEST, PARSER_VERSION, SOURCES


def load_manifest() -> list[dict]:
    if not MANIFEST.exists():
        return []
    return [json.loads(line) for line in MANIFEST.read_text(encoding="utf-8").splitlines() if line.strip()]


def published_at(meta: dict) -> tuple[str, str]:
    # The submissions API reports acceptanceDateTime with a Z suffix; we treat it as UTC [EXT-02].
    return meta["acceptance_datetime"], "edgar_submissions.acceptanceDateTime (UTC)"


def main() -> None:
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))
    entities = {e["entity_id"]: e for e in sources["entities"]}
    manifest = load_manifest()
    known = {(m["document_id"], m["sha256"]) for m in manifest}

    for doc in sources["documents"]:
        cik = entities[doc["entity_id"]]["cik"]
        url = edgar.document_url(cik, doc["accession"], doc["primary_document"])
        data = edgar.get(url).content
        sha, path, created = store.put(data)
        if (doc["document_id"], sha) in known:
            print(f"unchanged  {doc['document_id']}  {sha[:12]}")
            continue
        meta = edgar.filing_metadata(cik, doc["accession"])
        pub, basis = published_at(meta)
        version_no = 1 + sum(1 for m in manifest if m["document_id"] == doc["document_id"])
        record = {
            "document_id": doc["document_id"],
            "version": version_no,
            "sha256": sha,
            "bytes": len(data),
            "origin_url": url,
            "entity_id": doc["entity_id"],
            "cik": cik,
            "form_type": doc["form_type"],
            "edgar_form": meta["form"],
            "accession": doc["accession"],
            "fiscal_label": doc["fiscal_label"],
            "period_end": doc["period_end"],
            "filing_date": meta["filing_date"],
            "published_at": pub,
            "published_at_basis": basis,
            "ingested_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "acl": doc["acl"],
            "role": doc["role"],
            "license_note": "Public SEC filing; retrieved from EDGAR.",
            "parser_version": PARSER_VERSION,
        }
        with MANIFEST.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        manifest.append(record)
        print(f"ingested   {doc['document_id']}  v{version_no}  {sha[:12]}  published {pub}")


if __name__ == "__main__":
    from app.config import utf8_stdio

    utf8_stdio()
    main()
