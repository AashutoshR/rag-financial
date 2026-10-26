# Artifact `gold_q04`

**Question:** By how many percentage points did Starbucks' operating margin change from fiscal 2023 to fiscal 2024?

**Principal:** analyst_public · **As of:** none (latest available) · **Snapshot CSN:** 5 · **Outcome:** answer · **Status:** valid

## Answer

Starbucks' GAAP operating margin fell from 16.32% to 14.95%, a change of -1.37 pp (-137 bps). Management describes this as a 130 bps contraction, using rounded margins.

## Claims

| # | Type | Support | Claim | Citations | Calcs |
|---|---|---|---|---|---|
| c1 | calculated | supported | Operating margin was 16.32% in fiscal 2023 and 14.95% in fiscal 2024. | e4, e2, e3, e1 | k1, k2 |
| c2 | calculated | supported | Operating margin changed by -1.37 pp (-137 bps) from fiscal 2023 to fiscal 2024. |  | k3 |
| c3 | management_assertion | supported | Management reports operating margins of 16.3% and 15.0%, a contraction of 130 basis points. | e5 |  |

## Calculations

**k1** `operating_margin_fy2024 = operating_income_fy2024 / revenue_fy2024` → **14.95%**
- operating_income_fy2024 = 5408800000 USD (2023-10-02..2024-09-29) [e3]
- revenue_fy2024 = 36176200000 USD (2023-10-02..2024-09-29) [e1]

**k2** `operating_margin_fy2023 = operating_income_fy2023 / revenue_fy2023` → **16.32%**
- operating_income_fy2023 = 5870800000 USD (2022-10-03..2023-10-01) [e4]
- revenue_fy2023 = 35975600000 USD (2022-10-03..2023-10-01) [e2]

**k3** `operating_margin_change = k1 - k2` → **-1.37 pp (-137 bps)**
- note: inputs are calculations k1 and k2

## Citations

- **e1** `sbux_10k_fy2024:v1:cell:541` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Total net revenues · Sep 29, 2024 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 36,176.2
- **e2** `sbux_10k_fy2024:v1:cell:542` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Total net revenues · Oct 1, 2023 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 35,975.6
- **e3** `sbux_10k_fy2024:v1:cell:571` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Operating income · Sep 29, 2024 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 5,408.8
- **e4** `sbux_10k_fy2024:v1:cell:572` — 10-K · Item 8. Financial Statements and Supplementary Data · CONSOLIDATED STATEMENTS OF EARNINGS · Operating income · Oct 1, 2023 · printed p.50 — published 2024-11-21T02:08:06.000Z
  > 5,870.8
- **e5** `sbux_10k_fy2024:v1:paragraph:335` — 10-K · Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations · Financial Highlights · printed p.36 — published 2024-11-21T02:08:06.000Z
  > • Consolidated operating income decreased to $5.4 billion in fiscal 2024 compared to $5.9 billion in fiscal 2023. Fiscal 2024 operating margin was 15.0% compared to 16.3% in fiscal 2023. Operating margin contraction of 130 basis points was primarily due to investments in store partner wages and bene

## Conflicts

- {"type": "rounding_difference", "fact": "FY2024 operating margin change", "values": {"management (rounded margins)": "-130 bps", "calculated (k3)": "-1.37 pp (-137 bps)"}, "citations": ["e5"], "resolution": "Report the calculated value; note the stated figure."}

## Definition checks

- {"metric": "operating margin", "finding": "GAAP operating income / total net revenues, same basis and 52-week periods in both years", "citations": ["e3"]}

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