# Implementation Checklist

Companion to [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md). Requirement IDs in brackets.
The phase order is fixed. Don't start a phase until the previous phase's exit criteria pass.
**Rule for every phase:** B0 (the baseline) still runs, and each new mechanism has a measured result on the validation set before you keep it.

---

## First working session (do this before anything else) — done 2026-10-22, see [docs/first_session_log.md](docs/first_session_log.md)
- [x] Pick the initial company and its 3 filings (2 × 10-K, 1 × 10-Q); record CIK and accession numbers — Starbucks, plus 2 trap documents
- [x] Write 20 realistic questions covering every type in §4.1 — visual and permission types wait for those corpora
- [x] Hand-write 3 complete gold artifacts (lookup, calculation, explanation vs. evidence), with cell-level citations and calculations
- [x] Create `corpus/manifest.jsonl` with the 3 filings [§6.6]
- [x] Extract and manually inspect 3 financial tables (income statement, segment table, one footnote table)
- [x] Build one BM25 retrieval path and a single-call cited answer (B0)
- [ ] Run B0 on the 20 questions and write down exactly where and why each failure happens — extractive run done and analyzed; **LLM run pending an API key**

---

## P0 — Product contract
- [ ] Repo skeleton per Appendix A; `docker-compose` with Postgres 16 + pgvector + Redis
- [ ] Freeze the artifact JSON schema (§10) as a versioned JSON Schema file plus a validator
- [ ] Write the time-semantics ADR: as-of interpretation, timezone, world vs. system mode [TMP-R1, R2]
- [ ] Write the definitions ADR: margin, growth, pp vs. %, decomposition (Appendix B)
- [ ] Define the personas and ACL groups (§3); seed principals for two tenants
- [ ] Finalize the 10-company list after verifying each property on EDGAR (§6.2)
- [ ] Decide model providers; put embedder, reranker, and generator behind interfaces; record versions in config
- [ ] Set up config hashing so every run records `config_hash`

**Exit:** 20 questions, 3 gold artifacts passing schema validation, company list frozen, ADRs merged.

---

## P1 — Evidence extraction
### Ingestion
- [ ] EDGAR client: submissions + company-facts APIs, `User-Agent` with contact, rate limiting, local cache
- [ ] Content-addressed blob store; identical bytes = no-op [EXT-01]
- [ ] `published_at` from EDGAR `acceptanceDateTime` / press-release time, with basis recorded [EXT-02]
- [ ] Manifest append on every version; rebuild-from-manifest script [§6.6]
- [ ] Store ACL and time metadata on every row now (enforcement comes in P6)
- [ ] Idempotent, retryable RQ jobs with status and error tables [EXT-13]

### Extraction
- [ ] HTML filing parser: Items / sections / heading hierarchy [EXT-03]
- [ ] HTML table extraction with row/column header paths and scale statements [EXT-04]
- [ ] iXBRL linker: concept, context, dimensions, unit, decimals, sign → HTML element [EXT-05]
- [ ] Cross-check iXBRL facts against the company-facts API; report the match rate
- [ ] Digital PDF parser (earnings releases, slides) with page and bounding box [EXT-06]
- [ ] Spreadsheet parser: sheet!cell, formula vs. value, number format [EXT-08]
- [ ] Negative-number and "(loss)" handling with a sign-convention field [EXT-10]
- [ ] Footnote linking [EXT-11]
- [ ] Hidden-text detection (white text, tiny font, comments, metadata) → flag [SEC-04]
- [ ] OCR pipeline for scanned pages with region confidence; low-confidence numbers flagged [EXT-07]
- [ ] Chart extraction via VLM: region, series, confidence, "chart-estimated" label [EXT-09]
- [ ] Parser versioning; re-extraction creates new units, old units retained [EXT-12]
- [ ] Per-document extraction-quality report [EXT-14]

### Data and annotations
- [ ] Expand to all 10 companies (30 × 10-K, 20 × 10-Q, ~20 earnings docs)
- [ ] Synthetic generators (seeded): internal models, contracts, notes, memos (§6.4)
- [ ] Controlled restatement Company R: original + 10-K/A published 2025-08-15
- [ ] Counterfactual company with altered numbers
- [ ] 8+ hostile documents with clean twins (§6.5)
- [ ] Render ≥20 pages to scanned images (noise, skew) so OCR ground truth is exact
- [ ] Annotate ≥20 visual pages and ≥10 digital tables at cell level

**Exit:** idempotent re-ingest; ≥98% cell accuracy on annotated digital tables; OCR and chart accuracy measured and shown with uncertainty; manifest rebuild works.

---

## P2 — Retrieval baseline and evaluation harness
### Benchmark v0
- [ ] Benchmark item schema + validator (§11.2)
- [ ] Annotation tool or spreadsheet workflow with a second-reviewer step
- [ ] Write the 120 dev items first (val and test come later, from the same procedure)
- [ ] Assign groups; split assignment by company × time (§11.4); lock test-company list
- [ ] Mark required evidence units, permitted/forbidden/future sources, expected abstentions

### Baseline B0
- [ ] BM25 over passages and linearized tables [RET-01]
- [ ] B0 answerer: top-k → one LLM call → citations by unit ID
- [ ] Run logging: queries, filters, results, scores, prompts, outputs, tokens, cost, latency [RET-07, OPS-01]
- [ ] Artifact writer (schema-valid, even for B0 — missing parts are explicitly empty)
- [ ] Minimal Streamlit reviewer: answer, claims, click-through to source highlight [ART-02]

### Harness
- [ ] Runner that executes any config on any split under any persona
- [ ] Scorers: recall@k, evidence-set completeness, numerical accuracy (code), citation resolution
- [ ] Citation-support judge; label 150 human pairs; report κ [§11.7]
- [ ] Closed-book probe and counterfactual-company check [§11.4]
- [ ] Report generator: per-split, per company×time cell, per-category failures with artifact links
- [ ] **B0 report** with failure taxonomy

### Retrieval experiments (keep only what wins, §11.8)
- [ ] Dense retrieval (pgvector) [RET-02]
- [ ] Hybrid fusion (RRF) [RET-03]
- [ ] Table-aware retrieval (whole table + cells with header paths) [RET-05]
- [ ] Structured fact retrieval (entity, metric, period) [RET-04]
- [ ] Reranker [RET-03]
- [ ] Metadata filters (form type, section, fiscal period)
- [ ] Paired-bootstrap comparison utility; ADR for each kept or dropped mechanism

**Exit:** reproducible B0 report; ablation table for retrieval mechanisms; recall@20 trend toward ≥90%.

---

## P3 — Entity/metric reconciliation and verified calculations
### Reconciliation
- [ ] Entity registry: CIK/LEI, time-valid aliases (renames), parent/subsidiary/segment links [REC-01, 02]
- [ ] Fiscal-calendar rules per company incl. 52/53-week years; label → date range [REC-03]
- [ ] Scale normalization with original value retained [REC-04]
- [ ] Currency field; FX only with a cited rate; ratio comparison rule [REC-05]
- [ ] Metric-definition catalog: GAAP / non-GAAP / segment / IFRS, with source citations [REC-06]
- [ ] Definition-mismatch detector that runs before any comparison [REC-07]
- [ ] Duration typing: Q / YTD / FY / TTM; reject mixing [REC-08]

### Calculation engine
- [ ] Typed `Quantity` (Decimal value, currency, scale, period, duration, definition, sign)
- [ ] Calc spec DSL (JSON) emitted by the LLM; validator; executor [CALC-01, 02]
- [ ] Inputs must be fact IDs with evidence [CALC-03]
- [ ] Type-check errors → limitations, never coercion [CALC-04]
- [ ] Operations: diff, ratio, margin, growth, pp/bps change, CAGR, share, derived quarter, TTM [§4.2]
- [ ] Undefined-case handling: zero/negative base → "not meaningful" [CALC-06]
- [ ] Margin-change decomposition [CALC-07]
- [ ] Full lineage record and a "re-run from artifact" function [CALC-08, ART-03]
- [ ] Number-grounding check on final prose [CALC-10]
- [ ] Unit tests: property-based tests for arithmetic; fixtures for scale/sign/fiscal traps

### Evaluation
- [ ] Compare B0 (LLM arithmetic) vs. code calculations on numerical accuracy
- [ ] Definition-mismatch case family (§11.5 #2) passes
- [ ] Scale/sign (#8) and fiscal-calendar (#9) families pass

**Exit:** 100% of calculations reproduce from artifacts; numerical accuracy ≥95% on dev; mismatch cases pass.

---

## P4 — Temporal reasoning
- [ ] As-of parser (question text) + API parameter; recorded interpretation [TMP-01]
- [ ] Eligibility filters in retrieval, facts, aliases, definitions [TMP-02]
- [ ] Fact versioning across filings with `supersedes` links; comparative-column recasts [TMP-03, TMP-R4]
- [ ] Latest-eligible selection for "today" and as-of [TMP-04]
- [ ] Partial-amendment handling for 10-K/A and 10-Q/A [TMP-07, UPD-07]
- [ ] "Later restatement exists" note, only when the user can access the later source [TMP-05]
- [ ] Temporal verifier that rejects post-cutoff units and ungrounded values [TMP-06]
- [ ] CSN snapshots: `recorded_from_csn` / `recorded_to_csn` on versions and index rows [UPD-01, 02]
- [ ] Investigation pins a CSN; all reads filter by it; artifact records CSN + version hashes
- [ ] Version becomes visible only after all of its units are indexed [UPD-08]
- [ ] System-as-of replay mode [TMP-R2]
- [ ] Test hooks for injecting commits at chosen investigation steps
- [ ] Restatement family (#1), future-question trap (#10), concurrent correction (#6) pass
- [ ] Measure temporal leakage of B0 vs. temporal mechanisms

**Exit:** 0 temporal leakage on the temporal suite; restatement and concurrent-correction tests pass; snapshot coherence 100%.

---

## P5 — Adaptive investigation
- [ ] Planner: question → evidence requirements (per entity, metric, period, basis) [INV-01]
- [ ] Requirement state machine (open / satisfied / conflicting / incompatible / unavailable / forbidden) [INV-02]
- [ ] Follow-up strategies: reformulation, structured lookup, adjacent filings, earnings releases [INV-03]
- [ ] Budgets: steps, tool calls, tokens, wall-clock, dollars — enforced and recorded [INV-04]
- [ ] Stopping rules incl. "proven unavailable" with logged queries [INV-05]
- [ ] Per-requirement partial answers and abstentions [INV-06]
- [ ] Conflict detection and explicit resolution rules [INV-07]
- [ ] Claim typing and support status [SYN-01, 02]
- [ ] Explanation checker using decomposition; no causal language [SYN-03]
- [ ] Citation-entailment verifier; downgrade/remove unsupported claims [SYN-04, 05]
- [ ] Universe statement for screens [§4.3]
- [ ] Trace stored and shown in the UI [INV-08, ART-04]
- [ ] Unsupported-explanation family (#3) passes
- [ ] Compare single-shot vs. investigation loop on multi-doc, screen, explanation categories with cost and latency

**Exit:** statistically significant gains on the targeted categories within budgets; abstention recall ≥90% on dev.

---

## P6 — Permissions and production behavior
### Authorization
- [ ] Row-level security for tenant isolation [PERM-04]
- [ ] ACL filter inside retrieval queries (pre-scoring) for lexical, dense, and facts [RET-06, PERM-03]
- [ ] ACL intersection on derived data (facts, calculations, artifacts) [PERM-02]
- [ ] Exposure log for every unit retrieved, placed in context, cited, or displayed
- [ ] Release gate: re-check ACL + deletion on all exposed units [PERM-08, UPD-03]
- [ ] Non-disclosure: uniform responses for forbidden vs. non-existent; check timing and counts [PERM-07]
- [ ] Admin separation of duties with audited content grants [PERM-09]
- [ ] Audit log for all access decisions, grants, deletions, exports [PERM-10]

### Cache, conversation, exports
- [ ] Cache keys with principal/equivalence class + `perm_epoch`; dependency sets [PERM-05]
- [ ] Dependency-based invalidation on commit [UPD-06]
- [ ] Conversation-context assembly that redacts turns with revoked exposures [PERM-06]
- [ ] Server-held exports bound to dependencies; revoked or deleted with them [ART-06]

### Updates and lifecycle
- [ ] Correction API → new version → CSN advance → invalidation [UPD-01]
- [ ] Freshness-window enforcement and `superseded` marking [UPD-04]
- [ ] Deletion: logical tombstone on commit, physical purge job within 24 h, purge verifier [UPD-05]
- [ ] Backup/restore that reapplies tombstones [OPS-05]

### Hostile content
- [ ] Delimited evidence prompts; tool calls bound to the principal's policy [SEC-01, 02]
- [ ] Instruction-detection pass at ingestion; flags in the artifact [SEC-03]
- [ ] Output filter: content only from the exposure set; citation-forgery check [SEC-05]
- [ ] Hostile family (#5) passes vs. clean twins [SEC-06]

### Production
- [ ] Complete API endpoints (§9.12) with auth
- [ ] Metrics: queue depth, index lag, cache hit rate, invalidation latency, purge backlog [OPS-02]
- [ ] Retries, backoff, circuit breakers, graceful abstention [OPS-03]
- [ ] Fresh-deploy script + smoke tests [OPS-04]
- [ ] Runbooks: ingest, correct, delete, revoke, restore

### Invariant suites in CI
- [ ] Authorization incl. cross-tenant and existence probes (#11)
- [ ] Permission change (#4)
- [ ] Deletion across all surfaces (#7)
- [ ] Concurrency: 20+ parallel investigations with random commits, revocations, deletions
- [ ] Crash recovery mid-ingestion and mid-investigation
- [ ] Backup/restore with tombstones

**Exit:** all invariant suites pass; fresh deploy → ingest → investigate → inspect → revoke → recover demonstrated.

---

## P7 — Final evaluation and failure analysis
- [ ] Complete val (60) and locked test (120) items; second-reviewer pass; freeze
- [ ] Calibrate targets on dev/val; freeze targets and configuration (record `config_hash`)
- [ ] Single locked-test run; report per split and per company×time cell
- [ ] Full ablation table (leave-one-out) vs. B0
- [ ] Human review of ≥20% of test artifacts
- [ ] Load test: latency p50/p95 and cost per category under concurrency
- [ ] Failure analysis: category, frequency, example artifacts, suspected cause, proposed fix
- [ ] Demo script covering adversarial families #1–#6 with live artifacts
- [ ] Release report and README updated

**Exit:** Definition of Done (§15) satisfied.

---

## Frontier tier (requirements §16) — start each block once that phase's Core exit criteria pass

### P1 Frontier — uncertain evidence
- [ ] Degraded-scan generator: 150/200/300 dpi, skew, blur, JPEG artifacts, with exact ground truth
- [ ] Page-spanning and rotated table fixtures; header-continuation detection
- [ ] Unlabeled bar/line charts; VLM estimates stored as intervals [HX-06]
- [ ] Per-value uncertainty on every extracted number (exact / rounded / approximate / estimated)

### P2 Frontier — retrieval that can't rely on top-k
- [ ] Fact-store screen planner (structured query) + document cross-check [HX-01]
- [ ] Completeness ledger: qualified / not qualified / not evaluable + reason, for 100% of the universe
- [ ] Gold screen answers computed independently from XBRL company facts
- [ ] Counterfactual shadow corpus: seeded perturbation of numbers in real filings, names kept [HX-02]
- [ ] Closed-book run on every split to measure memory temptation
- [ ] Fresh split: filings published after every generator model's release date

### P3 Frontier — changes, explanations, intervals
- [ ] Cross-filing difference miner (same entity, concept, period, dimensions) — start with the 6 real SBUX FY2024 differences
- [ ] Change classifier: restatement / recast / reclassification / sign convention / scale / extraction error; 200 labeled pairs [HX-04]
- [ ] Driver extractor for MD&A explanations; driver-sum check; label set from §16.3 [HX-05]
- [ ] Price/volume/mix decomposition where disclosed (comparable sales: ticket vs. transactions)
- [ ] Interval arithmetic in the calculation engine; rounding bounds from displayed precision [HX-06]
- [ ] Families 12, 13, 14, 16 pass

### P4 Frontier — replay
- [ ] Record/replay store for all model I/O, keyed by prompt hash; content-addressed [HX-03]
- [ ] System-as-of replay reproduces archived artifacts byte-for-byte
- [ ] Replay test after ≥3 corpus commits and 1 parser upgrade
- [ ] Family 30: equal value from an ineligible source is rejected

### P5 Frontier — knowing what it doesn't know
- [ ] Per-claim confidence; calibration plot; ECE; risk–coverage curve vs. B0 [HX-09]
- [ ] False-premise detection and correction (family 15)
- [ ] Missing-link detection in derivations, naming the missing document (family 17)
- [ ] 10-turn conversation suite with coreference and mid-conversation constraint changes [HX-15, family 26]

### P6 Frontier — adversaries and proofs
- [ ] Information-barrier model: wall-crossing, lifting, restriction inheritance on outputs [HX-07]
- [ ] Per-principal query audit; differencing-attack detector; false-block measurement [HX-08]
- [ ] Indistinguishability harness: wording, length, latency, counts; statistical tests [HX-10]
- [ ] Canary seeding and probes across every surface, including vector nearest-neighbour and restored backups [HX-11]
- [ ] Attacker-model red team (white-box), ≥500 attacks; source-authority hierarchy [HX-12]
- [ ] Randomized fault-injection histories + history checker [HX-13]
- [ ] Hash-chained audit log; artifact commitments; tamper verifier [HX-14]
- [ ] Families 18–23, 28 pass

### P7 Frontier — scale and rigor
- [ ] ≥100 companies × 5 years; ≥5M evidence units; blue/green index rebuild [HX-16]
- [ ] Load test at 50 concurrent users; p95 targets
- [ ] Run all suites with Claude Opus 5.5, Sonnet 5.5 and Haiku 5.5; cost–quality Pareto front
- [ ] 900 items, two annotators each, κ ≥0.8, alternative-evidence search; power analysis per category
- [ ] Judge-fooling citation set (family 29); judge rejection ≥95%
- [ ] Frontier definition of done (§16.6)

---

## Progress tracker

| Phase | Status | B0 still runs | Key metric this phase | Result |
|---|---|---|---|---|
| P0 Contract | ☐ | n/a | Gold artifacts valid | |
| P1 Extraction | ☐ | n/a | Cell accuracy | |
| P2 Retrieval + harness | ☐ | ☐ | Recall@20 | |
| P3 Reconcile + calcs | ☐ | ☐ | Numerical accuracy | |
| P4 Temporal | ☐ | ☐ | Temporal leakage | |
| P5 Investigation | ☐ | ☐ | Task completion / abstention | |
| P6 Permissions + prod | ☐ | ☐ | Invariant pass rate | |
| P7 Final eval | ☐ | ☐ | Locked test report | |
