# Artifact `gold_q07`

**Question:** What reasons did management give for Starbucks' fiscal 2024 operating margin decline, and do the reported cost lines support those reasons?

**Principal:** analyst_public · **As of:** none (latest available) · **Snapshot CSN:** 5 · **Outcome:** answer · **Status:** valid

## Answer

Operating margin fell 1.37 pp (137 bps) (16.32% → 14.95%). Management cites wage and benefit investments, deleverage and promotions, partly offset by pricing and efficiencies, but its quantified drivers net to only -60 bps. The income statement shows store operating expenses as the largest drag (-1.338 pp). The non-recurrence of a fiscal 2023 asset-sale gain (-0.254 pp) goes unmentioned. Wages and benefits barely moved as a share of revenue (+0.13 pp (+13 bps)). The explanation is therefore only partially supported.

## Claims

| # | Type | Support | Claim | Citations | Calcs |
|---|---|---|---|---|---|
| c1 | management_assertion | supported | Management attributes the 130 bps operating-margin contraction primarily to investments in store partner wages and benefits (~140 bps), deleverage (~130 bps) and increased promotional activity (~100 bps), partially offset by pricing (~180 bps) and in-store operational efficiencies (~130 bps). | e21 |  |
| c2 | calculated | supported | Operating margin fell 1.37 pp (137 bps), from 16.32% to 14.95%. | e20, e19, e2, e1 | k2, k3, k4 |
| c3 | calculated | supported | Management's quantified drivers net to -60 bps, so about 70 bps of the stated 130 bps contraction is not accounted for by the listed items. | e21 | k5 |
| c4 | calculated | supported | Store operating expenses rose from 40.92% to 42.26% of total net revenues, lowering margin by 1.338 pp — the largest single contributor. Product and distribution costs fell as a share of revenue, raising margin by 0.807 pp. | e5, e6, e3, e4 | k1 |
| c5 | calculated | supported | Fiscal 2023 included a $91.3 million gain from sale of assets with no fiscal 2024 equivalent; its absence lowered the margin comparison by 0.254 pp. Management's driver list does not mention it. | e18, e21 | k1 |
| c6 | system_inference | partially_supported | Management's explanation is only partially supported. Its direction — store-level cost pressure — is consistent with the rise in store operating expenses. But the size of individual drivers can't be verified from reported line items: total wages and benefits moved only +0.13 pp (+13 bps) as a share of revenue, against a stated ~140 bps impact. The attribution is likely measured before the offsetting efficiencies, on a basis the filing does not disclose. The filing can't establish that these factors caused the whole decline. | e21, e22, e23 | k1, k5, k8 |

## Calculations

**k1** `Δmargin = Σ sign_i × (line_i,new / revenue_new − line_i,old / revenue_old); sign = −1 for expenses, +1 for income items` → **-1.37 pp**
- revenue_fy2024 = 36176200000 USD (2023-10-02..2024-09-29) [e1]
- revenue_fy2023 = 35975600000 USD (2022-10-03..2023-10-01) [e2]
- Product and distribution costs FY2024 = 11180600000 USD (2023-10-02..2024-09-29) [e3]
- Product and distribution costs FY2023 = 11409100000 USD (2022-10-03..2023-10-01) [e4]
- Store operating expenses FY2024 = 15286500000 USD (2023-10-02..2024-09-29) [e5]
- Store operating expenses FY2023 = 14720300000 USD (2022-10-03..2023-10-01) [e6]
- Other operating expenses FY2024 = 565600000 USD (2023-10-02..2024-09-29) [e7]
- Other operating expenses FY2023 = 539400000 USD (2022-10-03..2023-10-01) [e8]
- Depreciation and amortization expenses FY2024 = 1512600000 USD (2023-10-02..2024-09-29) [e9]
- Depreciation and amortization expenses FY2023 = 1362600000 USD (2022-10-03..2023-10-01) [e10]
- General and administrative expenses FY2024 = 2523300000 USD (2023-10-02..2024-09-29) [e11]
- General and administrative expenses FY2023 = 2441300000 USD (2022-10-03..2023-10-01) [e12]
- Restructuring and impairments FY2024 = 0 USD (2023-10-02..2024-09-29) [e13]
- Restructuring and impairments FY2023 = 21800000 USD (2022-10-03..2023-10-01) [e14]
- Income from equity investees FY2024 = 301200000 USD (2023-10-02..2024-09-29) [e15]
- Income from equity investees FY2023 = 298400000 USD (2022-10-03..2023-10-01) [e16]
- Gain from sale of assets FY2024 = 0 USD (2023-10-02..2024-09-29) [e17]
- Gain from sale of assets FY2023 = 91300000 USD (2022-10-03..2023-10-01) [e18]

| Line | Share FY-new | Share FY-old | Contribution (pp) |
|---|---|---|---|
| Product and distribution costs | 30.9060% | 31.7134% | 0.807 |
| Store operating expenses | 42.2557% | 40.9175% | -1.338 |
| Other operating expenses | 1.5635% | 1.4993% | -0.064 |
| Depreciation and amortization expenses | 4.1812% | 3.7876% | -0.394 |
| General and administrative expenses | 6.9750% | 6.7860% | -0.189 |
| Restructuring and impairments | 0.0000% | 0.0606% | 0.061 |
| Income from equity investees | 0.8326% | 0.8295% | 0.003 |
| Gain from sale of assets | 0.0000% | 0.2538% | -0.254 |

**k2** `operating_margin_fy2024 = operating_income_fy2024 / revenue_fy2024` → **14.95%**
- operating_income_fy2024 = 5408800000 USD (2023-10-02..2024-09-29) [e19]
- revenue_fy2024 = 36176200000 USD (2023-10-02..2024-09-29) [e1]

**k3** `operating_margin_fy2023 = operating_income_fy2023 / revenue_fy2023` → **16.32%**
- operating_income_fy2023 = 5870800000 USD (2022-10-03..2023-10-01) [e20]
- revenue_fy2023 = 35975600000 USD (2022-10-03..2023-10-01) [e2]

**k4** `operating_margin_change = k2 - k3` → **-1.37 pp (-137 bps)**
- note: inputs are calculations k2 and k3

**k5** `sum of management-stated driver impacts (bps)` → **-60 bps**
- wages and benefits investment = -140 bps (FY2024 vs FY2023) [e21]
- deleverage = -130 bps (FY2024 vs FY2023) [e21]
- promotional activity = -100 bps (FY2024 vs FY2023) [e21]
- pricing = 180 bps (FY2024 vs FY2023) [e21]
- in-store operational efficiencies = 130 bps (FY2024 vs FY2023) [e21]
- note: Driver values are management estimates ('approximately'); methodology not disclosed.

**k6** `wages_benefits_share_fy2024 = wages_and_benefits_fy2024 / revenue_fy2024` → **24.40%**
- wages_and_benefits_fy2024 = 8828600000 USD (2023-10-02..2024-09-29) [e22]
- revenue_fy2024 = 36176200000 USD (2023-10-02..2024-09-29) [e1]

**k7** `wages_benefits_share_fy2023 = wages_and_benefits_fy2023 / revenue_fy2023` → **24.28%**
- wages_and_benefits_fy2023 = 8733400000 USD (2022-10-03..2023-10-01) [e23]
- revenue_fy2023 = 35975600000 USD (2022-10-03..2023-10-01) [e2]

**k8** `wages_benefits_share_change = k6 - k7` → **+0.13 pp (+13 bps)**
- note: inputs are calculations k6 and k7

## Citations

- **e1** `sbux_10k_fy2024:v1:cell:541` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Total net revenues · Sep 29, 2024 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 36,176.2
- **e2** `sbux_10k_fy2024:v1:cell:542` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Total net revenues · Oct 1, 2023 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 35,975.6
- **e3** `sbux_10k_fy2024:v1:cell:544` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Product and distribution costs · Sep 29, 2024 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 11,180.6
- **e4** `sbux_10k_fy2024:v1:cell:545` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Product and distribution costs · Oct 1, 2023 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 11,409.1
- **e5** `sbux_10k_fy2024:v1:cell:547` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Store operating expenses · Sep 29, 2024 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 15,286.5
- **e6** `sbux_10k_fy2024:v1:cell:548` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Store operating expenses · Oct 1, 2023 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 14,720.3
- **e7** `sbux_10k_fy2024:v1:cell:550` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Other operating expenses · Sep 29, 2024 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 565.6
- **e8** `sbux_10k_fy2024:v1:cell:551` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Other operating expenses · Oct 1, 2023 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 539.4
- **e9** `sbux_10k_fy2024:v1:cell:553` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Depreciation and amortization expenses · Sep 29, 2024 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 1,512.6
- **e10** `sbux_10k_fy2024:v1:cell:554` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Depreciation and amortization expenses · Oct 1, 2023 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 1,362.6
- **e11** `sbux_10k_fy2024:v1:cell:556` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · General and administrative expenses · Sep 29, 2024 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 2,523.3
- **e12** `sbux_10k_fy2024:v1:cell:557` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · General and administrative expenses · Oct 1, 2023 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 2,441.3
- **e13** `sbux_10k_fy2024:v1:cell:559` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Restructuring and impairments · Sep 29, 2024 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > —
- **e14** `sbux_10k_fy2024:v1:cell:560` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Restructuring and impairments · Oct 1, 2023 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 21.8
- **e15** `sbux_10k_fy2024:v1:cell:565` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Income from equity investees · Sep 29, 2024 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 301.2
- **e16** `sbux_10k_fy2024:v1:cell:566` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Income from equity investees · Oct 1, 2023 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 298.4
- **e17** `sbux_10k_fy2024:v1:cell:568` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Gain from sale of assets · Sep 29, 2024 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > —
- **e18** `sbux_10k_fy2024:v1:cell:569` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Gain from sale of assets · Oct 1, 2023 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 91.3
- **e19** `sbux_10k_fy2024:v1:cell:571` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Operating income · Sep 29, 2024 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 5,408.8
- **e20** `sbux_10k_fy2024:v1:cell:572` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Operating income · Oct 1, 2023 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 5,870.8
- **e21** `sbux_10k_fy2024:v1:paragraph:335` — 10-K · Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations · Financial Highlights · printed p.36 — published 2024-11-21T02:08:06.000Z
  > • Consolidated operating income decreased to $5.4 billion in fiscal 2024 compared to $5.9 billion in fiscal 2023. Fiscal 2024 operating margin was 15.0% compared to 16.3% in fiscal 2023. Operating margin contraction of 130 basis points was primarily due to investments in store partner wages and bene
- **e22** `sbux_10k_fy2024:v1:cell:1476` — 10-K · Item 8. Financial Statements and Supplementary Data · Note 7: Supplemental Balance Sheet and Statement of Earnings Information (in millions) · Wages and benefits · Year Ended Sep 29, 2024 · printed p.74 — published 2024-11-21T02:08:06.000Z
  > 8,828.6
- **e23** `sbux_10k_fy2024:v1:cell:1477` — 10-K · Item 8. Financial Statements and Supplementary Data · Note 7: Supplemental Balance Sheet and Statement of Earnings Information (in millions) · Wages and benefits · Year Ended Oct 1, 2023 · printed p.74 — published 2024-11-21T02:08:06.000Z
  > 8,733.4

## Conflicts

- {"type": "internal_inconsistency", "fact": "FY2024 operating margin drivers", "values": {"stated total": "-130 bps", "sum of stated drivers (k5)": "-60 bps", "calculated change (k4)": "-1.37 pp (-137 bps)"}, "citations": ["e21"], "resolution": "Not resolvable from the filing; reported as a limitation."}

## Definition checks

- {"metric": "operating income", "finding": "Starbucks' GAAP operating income includes income from equity investees and gains from asset sales; both are included in the decomposition as income items.", "citations": ["e15"]}

## Limitations

- Driver impacts are management estimates with an undisclosed methodology; they can't be reconciled to line items.
- 'Wages and benefits' in Note 7 covers store operating expenses only; labor in other lines is not broken out.
- Segment-level drivers (North America, International) are not analyzed in this artifact.

## Trace and versions

```json
{
  "trace": {
    "author": "hand-written gold",
    "steps": null,
    "tokens": 0,
    "cost_usd": 0
  },
  "versions": {
    "calc_engine": "calc@0.1.0",
    "parser": "ixbrl-html@0.1.0"
  }
}
```