"""Regression tests for the first-session pipeline. Run: python -m pytest -q"""
from decimal import Decimal

from app import calc, facts, store
from app.artifact import structural_errors
from bench import make_gold
from bench.evidence import load_items, resolve_requirement

FY24 = ("2023-10-02", "2024-09-29")


def test_store_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "BLOBS", tmp_path)
    sha1, _, _ = store.put(b"same bytes")
    sha2, _, created = store.put(b"same bytes")
    assert sha1 == sha2 and created is False


def test_income_statement_cells_carry_ixbrl_lineage():
    c = facts.cell("sbux_10k_fy2024", "us-gaap:Revenues", *FY24, heading="CONSOLIDATED STATEMENTS OF EARNINGS")
    assert c["raw_text"] == "36,176.2" and c["scale_hint"] == "millions"
    assert Decimal(c["ixbrl"]["value"]) == Decimal("36176200000")
    assert c["col_header"] == "Sep 29, 2024" and c["printed_page"] == "50"


def test_margin_decomposition_sums_to_margin_change():
    art = make_gold.gold_q07()
    k1 = next(k for k in art["calculations"] if k["id"] == "k1")
    k4 = next(k for k in art["calculations"] if k["id"] == "k4")
    assert abs(Decimal(k1["result"]["value"]) - Decimal(k4["result"]["value"])) < Decimal("1e-12")


def test_ratio_rejects_period_mismatch():
    a = calc.Input("a", Decimal(1), "USD", "2024", "e1", "u1")
    b = calc.Input("b", Decimal(2), "USD", "2023", "e2", "u2")
    try:
        calc.ratio("k", a, b, "x")
    except TypeError:
        return
    raise AssertionError("period mismatch was not rejected")


def test_gold_artifacts_are_structurally_valid():
    for build in (make_gold.gold_q01, make_gold.gold_q04, make_gold.gold_q07):
        assert structural_errors(build()) == []


def test_every_benchmark_requirement_resolves():
    for item in load_items():
        for req in item["expected"].get("required_evidence", []):
            assert resolve_requirement(req), f"{item['id']} has an unresolvable requirement"
