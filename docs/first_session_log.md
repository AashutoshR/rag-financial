# First working session — log and failure analysis

Date: 2026-10-22 · Corpus CSN 5 · Parser `ixbrl-html@0.1.2` · Calc engine `calc@0.1.0`

## 1. What was done

| Checklist step | Result | Where |
|---|---|---|
| Pick company and filings | Starbucks (CIK 0000829224): FY2023 10-K, FY2024 10-K, Q2 FY2025 10-Q (core) + Q2 FY2025 earnings release and FY2025 10-K (traps) | [corpus/sources.json](../corpus/sources.json) |
| 20 realistic questions | 20 dev items across 16 category tags, with expected values, evidence specs, outcomes, traps | [bench/items/dev_first20.json](../bench/items/dev_first20.json) |
| 3 gold artifacts | q01 (lookup), q04 (margin change), q07 (explanation vs. evidence); all pass structural validation | [bench/gold/](../bench/gold/) |
| Immutable manifest | 5 versions, SHA-256 content-addressed, `published_at` from EDGAR acceptance time; re-ingest is a no-op | [corpus/manifest.jsonl](../corpus/manifest.jsonl) |
| Extract and inspect tables | 3 tables inspected by hand; 2,140 iXBRL-tagged cells cross-checked against the SEC API with 0 mismatches | [table_inspection.md](table_inspection.md) |
| BM25 + cited-answer baseline | B0 with `extractive` generator run; `llm` generator written, not yet run (no API key on this machine) | [app/baseline.py](../app/baseline.py) |
| Record where it fails | This document + [bench/reports/b0_extractive.md](../bench/reports/b0_extractive.md) | |

### Why Starbucks
- FY2024 revenue rose 0.56% while operating margin fell 1.37 pp, so it fits the representative question.
- 52/53-week fiscal year ending the Sunday closest to September 30, so "fiscal 2024" ≠ calendar 2024.
- The FY2025 10-K was published 2025-11-14, after the 2025-06-30 cutoff, and repeats FY2024 figures. It is a natural future-leakage trap.
- The earnings release reports GAAP (6.9%) and non-GAAP (8.2%) operating margin side by side, giving a definition trap.
- Starbucks' GAAP operating income includes income from equity investees and asset-sale gains. Comparisons with other companies need a definition check.
- A real 10-Q/A exists (filed 2024-02-16, Q1 FY2024). It isn't ingested yet and is a candidate for the amendment tests.

## 2. Findings from the real data (useful for the benchmark)

**The "unsupported explanation" case exists in the FY2024 10-K** (gold q07):
- Management says the 130 bps contraction was "primarily due to" wages and benefits (~140 bps), deleverage (~130), promotions (~100), partly offset by pricing (~180) and efficiencies (~130). **Those drivers net to −60 bps, not −130.**
- The unrounded change is −137 bps. The 130 bps comes from rounded margins (16.3% → 15.0%).
- On the income statement, store operating expenses are the largest drag (−1.34 pp). The absence of FY2023's $91.3M asset-sale gain costs −0.25 pp, and management doesn't mention it.
- Wages and benefits (Note 7) rose only +0.13 pp as a share of revenue, against a stated ~140 bps impact. The attribution can't be verified from reported line items.

**Partial-disclosure trap for abstention**: Japan revenue is not disclosed (q17). But the 10-K says Japan, Canada and the U.K. together make up ~72% of "other countries" revenue. A system can easily turn that into a fabricated Japan figure.

## 3. Extraction defects found by inspection

| # | Defect | Effect | Status |
|---|---|---|---|
| X1 | Table caption picked "(in millions, except per share data)" | Income statement not findable by name | Fixed (0.1.1) |
| X2 | "Table of Contents" page-header links became headings and captions | Wrong captions on Note 17 tables | Fixed (0.1.1) |
| X3 | iXBRL values serialized in scientific notation (`2.97659E+10`) | Ugly, risky for string comparison | Fixed (0.1.1) |
| X4 | Fix X1 regressed Note 7 captions to a stale heading ("Other Investments") | Found by the inspection script's NOT FOUND check | Fixed (0.1.2), "Note N:" lines now headings |
| X5 | Row hierarchy lost in multi-block tables (Note 17: "Fiscal 2023 >" applies to one row only) | Row labels ambiguous without the iXBRL period | Open; iXBRL context still gives the right period |
| X6 | MD&A segment tables lack the segment name ("Results of operations by segment") | North America / International tables indistinguishable by caption | Open |
| X7 | Scale missing for 51 of 72 tables in the FY2024 10-K (e.g. Note 15 EPS, Note 17) | Untagged numbers have no scale | Open; tagged cells are safe because iXBRL carries `scale` |
| X8 | Earnings release (not iXBRL) segment paragraphs have no segment name; "Operating margin of 11.6%" appears twice for different segments | Can't attribute segment figures | Open; needs layout-aware heading detection |
| X9 | ~40 cells per filing use company-specific `sbux:` concepts that the SEC company-facts API omits | Those cells can't be cross-checked automatically | Open; check against the filing's own XBRL instance instead |
| X10 | Untagged MD&A tables repeat iXBRL figures | Strict evidence matching under-counts correct retrieval | Mitigated in the scorer (value-equivalent recall) |

## 4. B0 results (extractive generator)

Corpus: 5 documents · 1,032 passages + 285 tables · BM25 top-8 · no filters.

| Metric | Result |
|---|---|
| Required-evidence recall@8 | 17% (20% accepting value-equivalent units) |
| Required-evidence recall@20 | 33% |
| Complete evidence set @8 / @20 | 26% / 42% |
| Numerical accuracy | 14% (3/22) |
| Correct abstention | 0/2 |
| Citations hitting required evidence | 11% |
| Citation resolution | 100% |
| As-of questions exposed to post-cutoff documents | 2/3 |
| As-of questions citing post-cutoff evidence | 0/3 (by luck: see F5) |
| Latency p50 | 12 ms · cost $0 |

The extractive generator is a lower bound: it can't calculate or abstain. The numbers that matter for the next phase are the **retrieval** numbers, which don't depend on the generator.

## 5. Failure analysis — where and why B0 fails

| # | Failure | Evidence | Root cause | Fix to test (phase) |
|---|---|---|---|---|
| F1 | **Calculation inputs are not retrievable by the question's words** | For "operating margin" questions (q03, q04, q06, q08) the income statement ranks 155–344 | The metric name ("margin") never appears next to its inputs ("operating income", "total net revenues") | Metric → input decomposition before retrieval, plus structured fact lookup [RET-04] (P2–P3) |
| F2 | **Period blindness** | q07 answered with FY2025 text; q10/q16 with segment, not consolidated, figures | Tables say "Sep 29, 2024", questions say "fiscal 2024"; BM25 treats 2024/2025 as near-equal tokens | Add fiscal-period labels to table/cell text at extraction; period filter from the question (P2, P4) |
| F3 | **No document scoping** | Top-8 spread across all 5 documents; the earnings release answers annual questions | No metadata filters (form type, fiscal period) | Metadata filters [RET-08] (P2) |
| F4 | **Long linearized tables dominate or vanish** | Earnings-release tables up to 5.9k chars rank #1 for unrelated questions; the 382-token income statement loses to short MD&A passages | BM25 length normalization over flattened tables | Index rows/cells as well as whole tables [RET-05] (P2) |
| F5 | **Temporal exposure** | 2/3 as-of questions put FY2025 10-K content in front of the generator | No `published_at` filter. With an LLM this will likely become cited leakage | As-of filter inside the query [TMP-02] (P4); the LLM run will show the real leak rate |
| F6 | **Never abstains** | q13 (future period) and q17 (undisclosed Japan) both answered | B0 has no evidence-sufficiency check | Requirement tracking + abstention (P5) |
| F7 | **Wrong source version** | q02 asks for the FY2023 10-K figure; B0 cites another filing | No source-version awareness | Source/version constraints in the plan (P4) |
| F8 | **Definition not stated** | q16 answer doesn't mention GAAP vs non-GAAP | No definition catalog | Metric definitions [REC-06/07] (P3) |
| F9 | **Segment vs consolidated confusion** | q10/q16 answered with North America figures | Segment passages match "operating margin" more strongly than the consolidated table | Entity/segment resolution [REC-02] (P3) |

## 6. Problems found in the benchmark itself (fix before scaling to 300 items)
1. **Missing valid alternative evidence.** q12 was scored as unsupported although its answer came from a 10-Q sentence that correctly states the fact. Annotation needs a step to search for alternative supporting units.
2. **Strict iXBRL-only evidence under-counts.** Untagged MD&A tables with the same value count as misses unless value-equivalence is accepted. Report both numbers.
3. **Number tolerance must follow stated precision.** "$5.4 billion" for 5,355.3 is correct rounding; a flat 5% tolerance was too loose.
4. **Partial value checks.** q12 checks "52 weeks" but not the end date. Several items need date and text expectations as well as numbers.
5. **Sign isn't scored.** The scorer matches magnitudes, so "declined 1.37 pp" and "−1.37 pp" both pass, and so would "+1.37 pp". Add a direction check before the LLM run.

## 7. Not done yet / honest limits
- **LLM B0 has not been run.** No `ANTHROPIC_API_KEY` is set here. The code path (`--generator llm`, Claude Opus 5.5, structured JSON output, server-side refusal fallback) is written but untested against the API.
- 20 items are too few for statistics. These results show where B0 fails, not how well it performs.
- No dense retrieval, no Postgres, no permissions, no OCR/chart pages yet. These are later phases by design.
- `published_at` uses EDGAR's UTC acceptance time against a New York-time cutoff. That's fine for this corpus, but should be converted properly in P4.

## 8. Next session, in order
1. Set `ANTHROPIC_API_KEY`, run `python -m bench.run_b0 --generator llm`, and compare it with the extractive run (expect the temporal leak rate to appear).
2. Fix the scorer sign check and add date/text expectations (§6).
3. Retrieval experiments against B0, one at a time: fiscal-period labels on tables (F2), row-level table units (F4), metadata filters (F3), dense retrieval, hybrid. Keep each only if recall@8 improves on the dev set.
4. Add the remaining 9 companies' filings incrementally, starting with one non-September fiscal year and one IFRS filer.

## 9. Frontier upgrade (requirements v2.0, §16)

The project now has a Frontier tier: 16 levers (HX-01…HX-16), 19 more adversarial families (#12–#30), a 900-item evaluation plan and a separate definition of done. Mining the ingested filings for real hard cases produced:

| Finding | Detail | Benchmark item |
|---|---|---|
| XBRL sign drift without a visible change | Share repurchases display as (1,259.1) in both 10-Ks, but are tagged −1,259.1M (FY2024 10-K) and +1,259.1M (FY2025 10-K). 5 of the 6 differing FY2024 facts are sign-only. | h03 |
| Tag meaning contradicts the table | "Other countries" revenue (US and China listed separately) is tagged `us-gaap:NonUsMember` | h04 evidence |
| Bundled approximate disclosure | Japan + Canada + U.K. ≈ 72% (FY2024), 71% (FY2023) of other-countries revenue → combined ≈ $4,619–4,684M | h04, h06 |
| Missing link | Q4 FY2024 operating income needs the Q3 FY2024 10-Q, absent from the corpus; FY − H1 (2,824.5) is the tempting wrong answer | h05 |
| Equal value, ineligible source | **B0 actually did this:** for h06 it stated the correct 71% but cited the FY2025 10-K, published after the cutoff. A value-only scorer would count it correct. | h06 |

B0 (extractive) on all 27 items: recall@8 20%, numerical accuracy 18%, abstention 0/3, and 1 of 4 as-of questions citing post-cutoff evidence. It fails all 7 Frontier items.

**Scorer gaps:** closed in §10.

## 10. Scorer v2 — answer-level checks

Answer scoring moved to [bench/checks.py](../bench/checks.py), and each item now declares what a good answer must do instead of the scorer guessing from categories:

| Gap (§6, §9) | Now scored by |
|---|---|
| Sign of a change not checked | `direction` on signed values: explicit sign, or the direction word nearest the number in its clause |
| Approximate results presented as exact (h04) | `approximate`: a hedge word before the number, or a stated range that contains the value |
| Premise correction (h01), inconsistency (h02), no-restatement + sign explanation (h03), non-GAAP basis (h07), GAAP basis (q16), missing document named (h05), abstention reasons (q13, q17), end date (q12) | `mentions` / `not_mentions` checks |
| Right source cited (q02, h06) | `cites_doc` / `not_cites_doc` |
| Comparison answered (q15, q19), inclusion stated (q20) | `mentions_near_value`: the wording must sit in the sentence that states the number |

**The scorer is tested on both sides.** [scorer_fixtures.json](../bench/scorer_fixtures.json) has 46 hand-written answers (21 correct, 25 plausible but wrong). Correct ones must pass, and each plausible wrong answer must produce exactly its listed failures. The 3 gold artifacts must pass every check, and every check must have a fixture that trips it. 56 tests pass.

**Bugs this caught in the scorer itself:**
1. "1.37 percentage points" was parsed as "1.37 percent", because `percent` came before `percentage points` in the unit pattern. Every pp answer written in words would have been scored wrong.
2. "Direction stated correctly: 9/9" was reported while the baseline stated none of those values: an unchecked direction counted as correct.
3. Two false passes on real B0 output: a dividend sentence ("first three quarters of fiscal 2025") satisfied "names the missing Q3 document", and boilerplate containing "same" satisfied "says the figures match". Both outputs are now regression fixtures.

B0 (extractive) under scorer v2: numerical accuracy 18% (all 5 credited values audited as genuine), direction 0/9, item checks 1/18 (the one pass is a legitimate "must not mention"), abstention 0/3.

**Still not automatable with patterns**, and left to the LLM judge plus human review: whether causal language is asserted (q07), whether an explanation label is the right one, and whether a premise correction is actually backed by evidence.

## 11. Web console and local model (Ollama)

- **Generator `ollama`**: local `gemma4:e4b` (7.5B, Q4_K_M) through Ollama's chat API, with the same prompt and JSON schema as the Claude generator, temperature 0, seed 0, and thinking off. On this machine the model runs mostly on CPU: a cold load took 4.5 minutes, and a warm 7.4K-token prompt takes about 68 seconds. Evidence blocks are capped at 1,800 characters for this generator; the cap is recorded in each artifact's `versions`.
- **First Ollama result (q01, "total net revenues for fiscal 2024")**: gemma answered **$7,338.9M**, the International segment's revenue, not the consolidated $36,176.2M. BM25 put the International segment table in the top 8, and the model took its "Total net revenues" row. This is failure F9 (segment vs. consolidated) in a real model, and the scorer flagged it (`wrong_or_missing_value`). In the console's inspector, the cited table's columns read "As a % of International Total Net Revenues", so a reviewer sees the cause immediately.
- **Console**: FastAPI ([app/server.py](../app/server.py)) plus a no-build front end ([web/](../web/)). Investigations run in a single-worker queue. Every citation opens the exact cell or passage and the stored filing scrolled to it. To make that possible, extraction (parser 0.1.3) now records a positional DOM anchor for every unit; unit IDs and text are unchanged from 0.1.2.
- **Safety**: filings are untrusted. They're served with `Content-Security-Policy: default-src 'none'; sandbox` inside a sandboxed iframe, highlight IDs are allow-listed, and the front end inserts all document text with `textContent`. 8 server tests cover these properties, the job flow and input validation (64 tests in total).

## 12. Local-model stall: diagnosis and fixes

**Symptom:** an Ollama run in the console showed "Generating" for 700+ seconds.

**Diagnosis (from Ollama's log, nvidia-smi and controlled experiments):**
1. GPU offload stalled. Ollama had put part of the model on the 8 GB laptop GPU, which other apps had filled to 6.6 GB. GPU utilization was 0%, the model process used about 0.7 CPU cores, and Ollama logged "GPU discovery watchdog timed out" just before the run. The run took 777 s; the same prompt takes about 40 s on the CPU alone.
2. Ollama 0.40.6 wedges after a client disconnects mid-answer. llama-server cancels the task and goes idle, but Ollama never forwards the next request (reproduced twice: requests waited until the client gave up). Unloading the model (`keep_alive: 0`) clears it; the next run reloads the model (199 s cold) and succeeds.
3. On Windows, closing a socket from another thread does not wake a blocked read (all three methods tested waited the full 15 s), so the first cancel implementation couldn't work.

**Fixes:**
- CPU-only by default (`OLLAMA_NUM_GPU=0`, configurable).
- Streaming over a `select()`-polled socket (HTTP/1.0), checking for stop requests every 0.5 s: Cancel takes effect in under a second, verified against real Ollama (0.05 s).
- Stall watchdog: stops a run with an explanation if there's no first token within 420 s or a gap of more than 60 s between tokens.
- Automatic model reset after any cancel or stall, so the next run isn't blocked by the wedge.
- The console shows the phase (reading evidence vs. writing answer) with a token count, a Cancel button, a slow-run warning, and clears the previous answer when a new run starts.
- 3 tests with a fake Ollama that never answers or stalls mid-answer: both watchdog paths and Cancel finish within seconds.
- Scorer false negative fixed: q17's abstention check now accepts "not provided"; gemma's real answer is a regression fixture.

**Result:** the same q17 run through the console now completes in 29 s with a correct abstention, scored Checks 1/1, outcome correct. 68 tests pass.
