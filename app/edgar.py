"""Minimal EDGAR client: polite rate limiting, descriptive User-Agent."""
import time

import requests

from app.config import SEC_MAX_RPS, SEC_USER_AGENT

_last_request = 0.0


def get(url: str) -> requests.Response:
    global _last_request
    wait = 1.0 / SEC_MAX_RPS - (time.monotonic() - _last_request)
    if wait > 0:
        time.sleep(wait)
    resp = requests.get(url, headers={"User-Agent": SEC_USER_AGENT}, timeout=60)
    _last_request = time.monotonic()
    resp.raise_for_status()
    return resp


def submissions(cik: str) -> dict:
    return get(f"https://data.sec.gov/submissions/CIK{cik}.json").json()


def filing_metadata(cik: str, accession: str) -> dict:
    """Return form, filing date and acceptance time for one accession from the submissions API."""
    recent = submissions(cik)["filings"]["recent"]
    i = recent["accessionNumber"].index(accession)
    return {
        "form": recent["form"][i],
        "filing_date": recent["filingDate"][i],
        "acceptance_datetime": recent["acceptanceDateTime"][i],
        "report_date": recent["reportDate"][i],
    }


def document_url(cik: str, accession: str, filename: str) -> str:
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}/{filename}"
