"""The scorer must accept correct answers and reject plausible wrong ones. Run: python -m pytest -q"""
import json

import pytest

from app.config import ROOT
from bench import make_gold
from bench.checks import answer_failures
from bench.evidence import load_items

ITEMS = {i["id"]: i for i in load_items()}
FIXTURES = json.loads((ROOT / "bench" / "scorer_fixtures.json").read_text(encoding="utf-8"))["fixtures"]


@pytest.mark.parametrize("fx", FIXTURES, ids=[f"{f['item']}-{'pass' if not f['expect'] else 'fail'}-{n}"
                                              for n, f in enumerate(FIXTURES)])
def test_fixture(fx):
    got = answer_failures(ITEMS[fx["item"]], fx["text"], fx["cited_docs"], fx["outcome"])
    assert sorted(got) == sorted(fx["expect"])


@pytest.mark.parametrize("build,item_id", [(make_gold.gold_q01, "q01"), (make_gold.gold_q04, "q04"),
                                           (make_gold.gold_q07, "q07")])
def test_gold_artifacts_pass_every_answer_check(build, item_id):
    art = build()
    text = art["answer_summary"] + " " + " ".join(c["text"] for c in art["claims"])
    cited = sorted({c["document_id"] for c in art["citations"]})
    assert answer_failures(ITEMS[item_id], text, cited, art["outcome"]) == []


def test_every_check_has_a_failing_fixture():
    """A check no fixture ever trips is untested."""
    tripped = {(fx["item"], f.split(":", 1)[1]) for fx in FIXTURES for f in fx["expect"] if f.startswith("check_failed:")}
    for item_id, item in ITEMS.items():
        for c in item["expected"].get("checks", []):
            assert (item_id, c["id"]) in tripped, f"{item_id}: check {c['id']} has no failing fixture"
