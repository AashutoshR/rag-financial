# B0 baseline report — generator `extractive`

Run `b0_extractive_20261026T023230Z` · 27 dev questions (Starbucks, 5 documents) · BM25 top-8 · no filters

## Metrics (each reported separately)

| Metric | Result |
|---|---|
| Required-evidence recall@8 (what B0 used) | 8/40 (20%) |
| Required-evidence recall@8, value-equivalent units also accepted | 9/40 (22%) |
| Required-evidence recall@20 | 14/40 (35%) |
| Complete evidence set @8 | 7/26 (27%) |
| Complete evidence set @20 | 11/26 (42%) |
| Numerical accuracy (expected values stated correctly) | 5/28 (18%) |
| Direction of change stated correctly | 0/9 (0%) |
| Item-specific checks passed (premise, basis, source, reason…) | 1/18 (6%) |
| Correct outcome on answerable questions | 24/24 (100%) |
| Correct abstention on unanswerable questions | 0/3 (0%) |
| Citations hitting required evidence | 2/26 (8%) |
| Citation resolution (artifact structure valid) | 27/27 (100%) |
| As-of questions exposed to post-cutoff documents | 3/4 (75%) |
| As-of questions citing post-cutoff evidence or stating future values | 1/4 (25%) |
| Latency p50 / max | 3 ms / 193 ms |
| Cost total | $0.0000 |

## Failure categories

| Category | Questions |
|---|---|
| citation_not_supporting | 24 |
| retrieval_miss | 19 |
| check_failed | 17 |
| missing_or_wrong_calculation | 13 |
| wrong_or_missing_value | 10 |
| answered_instead_of_abstaining | 3 |
| temporal_leakage | 1 |

## Per question

| Q | Categories | Outcome | Evidence @8 / @20 | Values | Failures | Answer (truncated) |
|---|---|---|---|---|---|---|
| q01 | fact_lookup | answer | 0/1 · 0/1 | 0/1 | retrieval_miss, citation_not_supporting, wrong_or_missing_value:FY2024 total net revenues | Operating income / Sep 29, 2024: 5,408.8; Oct 1, 2023: 5,870.8; Sep 29, 2024 As a % of Total Net Revenues: 15.0; Oct 1, 2023 As a % of Total Net Revenues: 16.3 |
| q02 | fact_lookup, source_specific | answer | 0/1 · 0/1 | 0/1 | retrieval_miss, citation_not_supporting, wrong_or_missing_value:FY2023 operating income, check_failed:cites_fy2023_10k | Management’s Discussion and Analysis of Financial Condition and Results of Operations (“MD&A”) can be found in the Annual Report on Form 10-K for the fiscal year ended October 1, 2023. |
| q03 | calculation | answer | 0/2 · 0/2 | 0/1 | retrieval_miss, citation_not_supporting, missing_or_wrong_calculation:FY2024 operating margin | Operating margin, as reported (GAAP) / Quarter Ended (1) Mar 30, 2025: 6.9; Quarter Ended (1) Mar 31, 2024: 12.8 |
| q04 | calculation, gold | answer | 0/4 · 0/4 | 0/1 | retrieval_miss, citation_not_supporting, missing_or_wrong_calculation:Operating margin change FY23→FY24 | Fiscal 2024 operating margin was 15.0% compared to 16.3% in fiscal 2023. |
| q05 | calculation | answer | 0/2 · 2/2 | 0/1 | retrieval_miss, citation_not_supporting, missing_or_wrong_calculation:Revenue growth FY23→FY24 | For the two quarters ended March 30, 2025 compared with the two quarters ended March 31, 2024 Product and distribution costs as a percentage of total net revenues decreased 30 basis points for the first two quarters of f |
| q06 | screen, temporal, calculation | answer | 0/2 · 0/2 | 0/2 | retrieval_miss, citation_not_supporting, missing_or_wrong_calculation:Revenue growth, missing_or_wrong_calculation:Operating margin change | For the International segment, revenue declined 2% in fiscal 2024 compared to fiscal 2023, primarily driven by the impact of unfavorable foreign currency translation, a 4% decline in comparable store sales driven by a de |
| q07 | explanation_vs_evidence, gold | answer | 0/2 · 0/2 | 0/1 | retrieval_miss, citation_not_supporting, wrong_or_missing_value:Store operating expenses contribution, check_failed:explanation_partially_supported | Operating Margin North America operating income for fiscal 2025 decr eased 41% to $3.2 billion, compared to $5.4 billion in fiscal 2024. |
| q08 | calculation, decomposition | answer | 0/1 · 0/1 | 0/1 | retrieval_miss, citation_not_supporting, missing_or_wrong_calculation:Store operating expenses contribution | Fiscal 2024 operating margin was 15.0% compared to 16.3% in fiscal 2023. |
| q09 | fact_lookup, quarterly | answer | 0/2 · 2/2 | 1/2 | retrieval_miss, citation_not_supporting, wrong_or_missing_value:Q2 FY25 revenue | Operating income / Quarter Ended Mar 30, 2025: 601.0; Quarter Ended Mar 31, 2024: 1,098.9; Quarter Ended % Change: (45.3); Quarter Ended Mar 30, 2025 As a % of total net revenues: 6.9; Quarter Ended Mar 31, 2024 As a % o |
| q10 | calculation, quarterly | answer | 0/2 · 0/2 | 0/2 | retrieval_miss, citation_not_supporting, missing_or_wrong_calculation:Q2 FY25 operating margin, missing_or_wrong_calculation:Change vs Q2 FY24 | Operating Margin North America operating income for the second quarter of fiscal 2025 decreased 35% to $748 million, compared to $1.1 billion in the second quarter of fiscal 2024. |
| q11 | fact_lookup, duration_trap | answer | 0/1 · 1/1 | 0/1 | retrieval_miss, citation_not_supporting, wrong_or_missing_value:H1 FY25 operating income | Operating Margin Channel Development operating income for the first two quarters of fiscal 2025 decreased 6% to $402 million, compared to $426 million in the first two quarters of fiscal 2024. |
| q12 | fiscal_calendar | answer | 1/1 · 1/1 | 1/1 | check_failed:states_end_date | Fiscal 2025 and 2024 include 52 weeks. |
| q13 | temporal, should_abstain | answer ✗ | 0/0 · 0/0 | 0/0 | answered_instead_of_abstaining, check_failed:abstention_reason_temporal | Company-operated stores / Mar 30, 2025: 1,423.3; Mar 31, 2024: 1,328.1; % Change: 7.2; Mar 30, 2025 As a % of International total net revenues: 76.2; Mar 31, 2024 As a % of International total net revenues: 75.6 |
| q14 | temporal, calculation | answer | 1/1 · 1/1 | 0/1 | citation_not_supporting, missing_or_wrong_calculation:Q2 FY25 operating margin | Operating margin, as reported (GAAP) / Quarter Ended (1) Mar 30, 2025: 6.9; Quarter Ended (1) Mar 31, 2024: 12.8 |
| q15 | multi_document, restatement_check | answer | 0/2 · 0/2 | 0/1 | retrieval_miss, citation_not_supporting, wrong_or_missing_value:FY2024 revenue (both filings), check_failed:states_same | For the two quarters ended March 30, 2025 compared with the two quarters ended March 31, 2024 Revenues Channel Development total net revenues for the first two quarters of fiscal 2025 decreased $21 million, or 2%, primar |
| q16 | definition_mismatch | answer | 0/1 · 0/1 | 0/1 | retrieval_miss, citation_not_supporting, wrong_or_missing_value:GAAP operating margin, check_failed:states_gaap_basis | Operating Margin North America operating income for the second quarter of fiscal 2025 decreased 35% to $748 million, compared to $1.1 billion in the second quarter of fiscal 2024. |
| q17 | should_abstain | answer ✗ | 1/1 · 1/1 | 0/0 | citation_not_supporting, answered_instead_of_abstaining, check_failed:abstention_reason_disclosure | and China consist primarily of revenues from Japan, Canada, and the U.K., which together account for approximately 73 %, 72 %, and 71 % of net revenues from other countries for fiscal years 2025, 2024, and 2023, respecti |
| q18 | fact_lookup, segment, calculation | answer | 1/1 · 1/1 | 1/2 | missing_or_wrong_calculation:North America operating margin | Operating Margin North America operating income for fiscal 2024 decreased 3% to $5.4 billion, compared to $5.5 billion in fiscal 2023. |
| q19 | multi_document | answer | 0/2 · 0/2 | 0/1 | retrieval_miss, citation_not_supporting, wrong_or_missing_value:Q2 FY25 operating income, check_failed:states_match | In this Annual Report on Form 10-K (“10-K” or “Report”) for the fiscal year ended September 28, 2025 (“fiscal 2025”), Starbucks Corporation (together with its subsidiaries) is referred to as “Starbucks,” the “Company,” “ |
| q20 | definition, fact_lookup | answer | 1/1 · 1/1 | 0/1 | citation_not_supporting, wrong_or_missing_value:FY2024 income from equity investees, check_failed:states_inclusion | As of September 29, 2024, and October 1, 2023, there were $ 12.2 million and $ 19.1 million of accounts receivable from equity investees, respectively, on our consolidated balance sheets, primarily related to product sal |
| h01 | false_premise, calculation | answer | 0/2 · 0/2 | 0/1 | retrieval_miss, citation_not_supporting, missing_or_wrong_calculation:Revenue growth FY23→FY24, check_failed:corrects_premise | Revenues International total net revenues for fiscal 2024 decreased $149 million, or 2%, primarily due to unfavorable foreign currency translation impacts ($252 million), as well as a 4% decline in comparable store sales |
| h02 | explanation_vs_evidence, calculation | answer | 1/1 · 1/1 | 0/1 | citation_not_supporting, missing_or_wrong_calculation:Net of stated drivers, check_failed:states_inconsistency | The combination of these changes resulted in an overall decrease in operating margin of 130 basis points in fiscal 2024 when compared to fiscal 2023. |
| h03 | restatement_check, multi_document, sign_convention | answer | 0/2 · 0/2 | 1/1 | retrieval_miss, citation_not_supporting, check_failed:no_restatement, check_failed:explains_sign | During the fiscal year ended September 29, 2024, we repurchased 12.8 million shares of common stock for $1.3 billion on the open market. |
| h04 | approximate_quantity, calculation, partial_disclosure | answer | 1/2 · 1/2 | 0/1 | retrieval_miss, citation_not_supporting, missing_or_wrong_calculation:Combined revenue (approx.) | and China consist primarily of revenues from Japan, Canada, and the U.K., which together account for approximately 73 %, 72 %, and 71 % of net revenues from other countries for fiscal years 2025, 2024, and 2023, respecti |
| h05 | should_abstain, derived_quarter | answer ✗ | 0/1 · 0/1 | 0/0 | retrieval_miss, citation_not_supporting, answered_instead_of_abstaining, check_failed:names_missing_document | During the fourth quarter of fiscal 2024, and for each of the first three quarters of fiscal 2025, we declared a cash dividend of $0.61 per share. |
| h06 | temporal, partial_disclosure | answer | 0/1 · 1/1 | 1/1 | retrieval_miss, temporal_leakage:cited_post_cutoff, citation_not_supporting, check_failed:cites_fy2023_10k, check_failed:not_cites_fy2025_10k | and China consist primarily of revenues from Japan, Canada, and the U.K., which together account for approximately 73 %, 72 %, and 71 % of net revenues from other countries for fiscal years 2025, 2024, and 2023, respecti |
| h07 | definition_mismatch, non_gaap | answer | 1/1 · 1/1 | 0/1 | citation_not_supporting, wrong_or_missing_value:Non-GAAP operating margin, check_failed:states_non_gaap | For the quarter ended March 30, 2025 compared with the quarter ended March 31, 2024 Corporate and Other operating loss increased 12% to $558 million for the second quarter of fiscal 2025 compared to $500 million for the  |