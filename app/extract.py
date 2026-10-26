"""Evidence extraction for EDGAR inline-XBRL HTML filings [EXT-03..05, EXT-10, EXT-14, SEC-04].

Produces addressable evidence units:
  paragraph   one block of text, the citation target for prose
  passage     a chunk of consecutive paragraphs under one heading, the retrieval unit for prose
  table       a whole table, linearized for retrieval
  cell        one numeric table cell with row/column headers, scale, sign and its iXBRL fact

Usage: python -m app.extract          (extracts every manifest version not yet extracted)
"""
import json
import re
from collections import deque
from decimal import Decimal, InvalidOperation

from bs4 import BeautifulSoup, NavigableString, Tag

from app import store
from app.config import EXTRACTED, MANIFEST, PARSER_VERSION

ITEM_RE = re.compile(r"^(PART\s+[IV]+\b|Item\s+\d+[A-C]?\.)", re.I)
NOTE_RE = re.compile(r"^Note\s+\d+\s*:", re.I)
SCALE_RE = re.compile(r"\bin\s+(thousands|millions|billions)\b", re.I)
NUM_RE = re.compile(r"^\(?\$?\s*-?[\d,]+(\.\d+)?\s*%?\)?$")
PASSAGE_WORDS = 180


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def style_of(el: Tag) -> str:
    return (el.get("style") or "").replace(" ", "").lower()


def is_hidden(el: Tag) -> bool:
    return "display:none" in style_of(el)


def is_bold(el: Tag) -> bool:
    spans = [s for s in el.find_all("span") if norm(s.get_text())]
    return bool(spans) and all("font-weight:700" in style_of(s) or "font-weight:bold" in style_of(s) for s in spans)


def parse_contexts(soup: BeautifulSoup) -> dict:
    contexts = {}
    for ctx in soup.find_all("xbrli:context"):
        period = ctx.find("xbrli:period")
        start, end, instant = (period.find(t) for t in ("xbrli:startdate", "xbrli:enddate", "xbrli:instant"))
        dims = {m.get("dimension"): norm(m.get_text()) for m in ctx.find_all("xbrldi:explicitmember")}
        dims.update({m.get("dimension"): norm(m.get_text()) for m in ctx.find_all("xbrldi:typedmember")})
        contexts[ctx.get("id")] = {
            "start": norm(start.get_text()) if start else None,
            "end": norm(end.get_text()) if end else None,
            "instant": norm(instant.get_text()) if instant else None,
            "dims": dims,
        }
    return contexts


def to_decimal(text: str) -> Decimal | None:
    t = text.replace(",", "").replace("$", "").replace("%", "").replace("(", "").replace(")", "").strip()
    if t in ("—", "–", "-", ""):
        return None
    try:
        return Decimal(t)
    except InvalidOperation:
        return None


class Extractor:
    def __init__(self, record: dict):
        self.rec = record
        self.prefix = f"{record['document_id']}:v{record['version']}"
        self.units: list[dict] = []
        self.counter = {"paragraph": 0, "passage": 0, "table": 0, "cell": 0}
        self.page = 1
        self.printed_pages: dict[int, str] = {}
        self.section = None
        self.heading = None
        self.recent_text: deque[str] = deque(maxlen=6)
        self.pending: list[dict] = []  # paragraphs waiting to be chunked into a passage
        self.hidden_texts: list[str] = []
        self.contexts: dict = {}
        self.anchors: dict[int, str] = {}  # id(element) -> DOM anchor, see anchor_ids()

    def new_id(self, kind: str) -> str:
        self.counter[kind] += 1
        return f"{self.prefix}:{kind}:{self.counter[kind]}"

    def base(self, kind: str) -> dict:
        return {
            "unit_id": self.new_id(kind),
            "kind": kind,
            "document_id": self.rec["document_id"],
            "version": self.rec["version"],
            "sha256": self.rec["sha256"],
            "section": self.section,
            "heading": self.heading,
            "html_page": self.page,
        }

    # ---- prose -------------------------------------------------------------------------
    def flush_passage(self) -> None:
        if not self.pending:
            return
        unit = self.base("passage")
        unit["section"], unit["heading"] = self.pending[0]["section"], self.pending[0]["heading"]
        unit["html_page"] = self.pending[0]["html_page"]
        unit["html_page_end"] = self.pending[-1]["html_page"]
        unit["paragraph_ids"] = [p["unit_id"] for p in self.pending]
        unit["dom_anchor"] = self.pending[0].get("dom_anchor")
        unit["text"] = " ".join(p["text"] for p in self.pending)
        self.units.append(unit)
        self.pending = []

    def paragraph(self, el: Tag) -> None:
        text = norm(el.get_text(" "))
        if not text:
            return
        if re.fullmatch(r"\d{1,3}", text):  # printed page number footer
            self.printed_pages[self.page] = text
            return
        if ITEM_RE.match(text) and len(text) < 160:
            self.flush_passage()
            self.section = text
            self.heading = None
            self.recent_text.append(text)
            return
        if text.lower() == "table of contents":  # page-header navigation link, not content
            return
        if (is_bold(el) or NOTE_RE.match(text)) and len(text) < 140:
            self.flush_passage()
            self.heading = text
            self.recent_text.append(text)
            return
        unit = self.base("paragraph")
        unit["text"] = text
        unit["element_id"] = el.get("id")
        unit["dom_anchor"] = self.anchors.get(id(el))
        self.units.append(unit)
        self.recent_text.append(text)
        self.pending.append(unit)
        if sum(len(p["text"].split()) for p in self.pending) >= PASSAGE_WORDS:
            self.flush_passage()

    # ---- tables ------------------------------------------------------------------------
    def table(self, el: Tag) -> None:
        self.flush_passage()
        grid_rows = []
        for tr in el.find_all("tr"):
            col, cells = 0, []
            for td in tr.find_all(["td", "th"], recursive=False):
                span = int(td.get("colspan", 1) or 1)
                cells.append({"td": td, "col": col, "span": span, "text": norm(td.get_text(" "))})
                col += span
            grid_rows.append(cells)

        def has_value(row):
            return any(c["td"].find("ix:nonfraction") or (NUM_RE.match(c["text"]) and c["text"] not in ("$", "%"))
                       for c in row if c["text"])

        first_data = next((i for i, r in enumerate(grid_rows) if has_value(r)), None)
        if first_data is None:  # text-only table (e.g. table of contents): keep as a paragraph
            text = " | ".join(" ".join(c["text"] for c in r if c["text"]) for r in grid_rows if any(c["text"] for c in r))
            if text:
                unit = self.base("paragraph")
                unit.update({"text": text, "element_id": el.get("id"), "from_table": True,
                             "dom_anchor": self.anchors.get(id(el))})
                self.units.append(unit)
                self.pending.append(unit)
                self.flush_passage()
            return

        col_headers: dict[int, list[str]] = {}
        for row in grid_rows[:first_data]:
            for c in row:
                if c["text"] and c["col"] > 0:
                    for k in range(c["col"], c["col"] + c["span"]):
                        col_headers.setdefault(k, []).append(c["text"])
        context_text = " ".join(self.recent_text)
        scale_match = SCALE_RE.search(context_text) or SCALE_RE.search(
            " ".join(c["text"] for r in grid_rows[:first_data] for c in r))
        caption = next((t for t in reversed(self.recent_text)
                        if len(t) < 140 and not (t.startswith("(") and SCALE_RE.search(t))), None)
        if self.heading and caption != self.heading and self.heading not in (caption or ""):
            caption = f"{self.heading} — {caption}" if caption else self.heading

        table = self.base("table")
        table.update({"caption": caption, "scale_hint": scale_match.group(1).lower() if scale_match else None,
                      "element_id": el.get("id"), "dom_anchor": self.anchors.get(id(el)), "cell_ids": []})
        lines, parent = [], None
        for row in grid_rows[first_data:]:
            label_cell = next((c for c in row if re.search(r"[A-Za-z]", c["text"])), None)
            label = label_cell["text"] if label_cell else ""
            values = [c for c in row if c is not label_cell and c["text"] and c["text"] not in ("$", "%", ")", "%)")
                      and (c["td"].find("ix:nonfraction") or NUM_RE.match(c["text"]) or c["text"] in ("—", "–"))]
            if not values:
                if label:
                    parent = label
                continue
            row_path = [p for p in (parent, label) if p]
            line_parts = []
            for c in values:
                cell = self.cell(c, row, row_path, col_headers, table)
                line_parts.append(f"{cell['col_header'] or '?'}: {c['text']}")
            lines.append(" > ".join(row_path) + " | " + "; ".join(line_parts))
            if label.lower().startswith("total"):
                parent = None
        table["text"] = " ".join(filter(None, [caption, f"(in {table['scale_hint']})" if table["scale_hint"] else None])) \
            + "\n" + "\n".join(lines)
        self.units.append(table)

    def cell(self, c: dict, row: list, row_path: list, col_headers: dict, table: dict) -> dict:
        header = None
        for k in list(range(c["col"], c["col"] + c["span"])) + [c["col"] - 1, c["col"] - 2, c["col"] + c["span"]]:
            if k in col_headers:
                header = " ".join(dict.fromkeys(col_headers[k]))
                break
        idx = row.index(c)
        nxt = row[idx + 1]["text"] if idx + 1 < len(row) else ""
        negative_display = c["text"].startswith("(") or nxt.startswith(")")
        percent = c["text"].endswith("%") or nxt.startswith("%")
        unit = self.base("cell")
        unit.update({
            "table_id": table["unit_id"],
            "dom_anchor": table["dom_anchor"],
            "row_path": row_path,
            "col_header": header,
            "raw_text": c["text"],
            "display_value": str(v) if (v := to_decimal(c["text"])) is not None else None,
            "negative_display": negative_display,
            "percent": percent,
            "scale_hint": None if percent else table["scale_hint"],
        })
        fact = c["td"].find("ix:nonfraction")
        if fact is not None:
            ctx = self.contexts.get(fact.get("contextref"), {})
            scale = int(fact.get("scale", 0) or 0)
            shown = to_decimal(norm(fact.get_text()))
            if shown is None and "zero" in (fact.get("format") or ""):
                shown = Decimal(0)
            value = None
            if shown is not None:
                value = shown.scaleb(scale) * (-1 if fact.get("sign") == "-" else 1)
            unit["ixbrl"] = {
                "concept": fact.get("name"),
                "context_id": fact.get("contextref"),
                "period": {k: ctx.get(k) for k in ("start", "end", "instant")},
                "dims": ctx.get("dims", {}),
                "unit": fact.get("unitref"),
                "decimals": fact.get("decimals"),
                "scale": scale,
                "sign": fact.get("sign"),
                "element_id": fact.get("id"),
                "value": format(value, "f") if value is not None else None,
            }
        unit["text"] = f"{' > '.join(row_path)} | {header}: {c['text']}"
        table["cell_ids"].append(unit["unit_id"])
        self.units.append(unit)
        return unit

    # ---- walk --------------------------------------------------------------------------
    def walk(self, el: Tag) -> None:
        for child in el.children:
            if isinstance(child, NavigableString) or not isinstance(child, Tag):
                continue
            if is_hidden(child):
                text = norm(child.get_text(" "))
                if text and not child.find("ix:header"):
                    self.hidden_texts.append(text[:200])
                continue
            if child.name == "table":
                self.table(child)
            elif child.name in ("div", "p") and not child.find(["div", "p", "table"]):
                self.paragraph(child)
            else:
                self.walk(child)
            if "page-break-after:always" in style_of(child) or "break-after:page" in style_of(child):
                self.page += 1

    def run(self) -> tuple[list[dict], dict]:
        html = store.path_for(self.rec["sha256"]).read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")
        self.contexts = parse_contexts(soup)
        self.anchors = {id(el): a for el, a in anchor_ids(soup)}
        ix_total = len(soup.find_all("ix:nonfraction"))
        for header in soup.find_all("ix:header"):
            header.decompose()
        self.walk(soup.body)
        self.flush_passage()
        for u in self.units:
            u["printed_page"] = self.printed_pages.get(u["html_page"])
        cells = [u for u in self.units if u["kind"] == "cell"]
        report = {
            "document_id": self.rec["document_id"],
            "version": self.rec["version"],
            "parser_version": PARSER_VERSION,
            "units": dict(self.counter),
            "ixbrl_numeric_facts_in_document": ix_total,
            "ixbrl_facts_linked_to_cells": sum(1 for c in cells if "ixbrl" in c),
            "cells_without_ixbrl": sum(1 for c in cells if "ixbrl" not in c),
            "cells_without_col_header": sum(1 for c in cells if not c["col_header"]),
            "tables_without_scale_hint": sum(1 for u in self.units if u["kind"] == "table" and not u["scale_hint"]),
            "html_pages": self.page,
            "hidden_text_blocks": len(self.hidden_texts),
            "hidden_text_samples": self.hidden_texts[:5],
        }
        return self.units, report


def anchor_ids(soup: BeautifulSoup):
    """Stable positional anchors for block elements, computed on the unmodified document.

    The source viewer (app/server.py) assigns the same ids when it serves a filing, so a unit's dom_anchor
    lets the reviewer jump to the exact block even when the filing gives it no id of its own.
    """
    for i, el in enumerate(soup.find_all(["div", "p"])):
        yield el, f"u-b-{i}"
    for i, el in enumerate(soup.find_all("table")):
        yield el, f"u-t-{i}"


def out_dir(record: dict):
    return EXTRACTED / record["document_id"] / f"v{record['version']}"


def load_units(record: dict) -> list[dict]:
    path = out_dir(record) / "units.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def main() -> None:
    records = [json.loads(line) for line in MANIFEST.read_text(encoding="utf-8").splitlines() if line.strip()]
    for rec in records:
        d = out_dir(rec)
        report_path = d / "report.json"
        if report_path.exists() and json.loads(report_path.read_text(encoding="utf-8"))["parser_version"] == PARSER_VERSION:
            print(f"skip       {rec['document_id']} v{rec['version']} (already extracted with {PARSER_VERSION})")
            continue
        units, report = Extractor(rec).run()
        d.mkdir(parents=True, exist_ok=True)
        with (d / "units.jsonl").open("w", encoding="utf-8") as f:
            for u in units:
                f.write(json.dumps(u) + "\n")
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"extracted  {rec['document_id']} v{rec['version']}  {report['units']}  "
              f"ix linked {report['ixbrl_facts_linked_to_cells']}/{report['ixbrl_numeric_facts_in_document']}")


if __name__ == "__main__":
    from app.config import utf8_stdio

    utf8_stdio()
    main()
