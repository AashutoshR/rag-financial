# Table inspection — first working session

Automatic check: every extracted cell with a non-dimensional iXBRL fact is compared with the value the SEC company-facts API reports for the same concept, accession and period.

| Document | Cells checked | Match | Mismatch | Not in API |
|---|---|---|---|---|
| sbux_10k_fy2023 | 613 | 573 | 0 | 40 |
| sbux_10k_fy2024 | 600 | 564 | 0 | 36 |
| sbux_10q_q2fy2025 | 463 | 425 | 0 | 38 |
| sbux_er_q2fy2025 | 0 | 0 | 0 | 0 |
| sbux_10k_fy2025 | 620 | 578 | 0 | 42 |

## Tables inspected by hand

### sbux_10k_fy2024 — CONSOLIDATED STATEMENTS OF EARNINGS
`sbux_10k_fy2024:v1:table:20` · Item 8. Financial Statements and Supplementary Data · HTML page 53 (printed 50) · scale hint: millions

| Row | Column | Raw | Scale | Neg. shown | iXBRL concept | Period | Dims | Value |
|---|---|---|---|---|---|---|---|---|
| Company-operated stores | Sep 29, 2024 | 29,765.9 | millions |  | us-gaap:Revenues | 2023-10-02→2024-09-29 | CompanyOperatedStoresMember | 29765900000 |
| Company-operated stores | Oct 1, 2023 | 29,462.3 | millions |  | us-gaap:Revenues | 2022-10-03→2023-10-01 | CompanyOperatedStoresMember | 29462300000 |
| Company-operated stores | Oct 2, 2022 | 26,576.1 | millions |  | us-gaap:Revenues | 2021-10-04→2022-10-02 | CompanyOperatedStoresMember | 26576100000 |
| Licensed stores | Sep 29, 2024 | 4,505.1 | millions |  | us-gaap:Revenues | 2023-10-02→2024-09-29 | LicensedStoresMember | 4505100000 |
| Licensed stores | Oct 1, 2023 | 4,512.7 | millions |  | us-gaap:Revenues | 2022-10-03→2023-10-01 | LicensedStoresMember | 4512700000 |
| Licensed stores | Oct 2, 2022 | 3,655.5 | millions |  | us-gaap:Revenues | 2021-10-04→2022-10-02 | LicensedStoresMember | 3655500000 |
| Other | Sep 29, 2024 | 1,905.2 | millions |  | us-gaap:Revenues | 2023-10-02→2024-09-29 | ProductAndServiceOtherMember | 1905200000 |
| Other | Oct 1, 2023 | 2,000.6 | millions |  | us-gaap:Revenues | 2022-10-03→2023-10-01 | ProductAndServiceOtherMember | 2000600000 |
| Other | Oct 2, 2022 | 2,018.7 | millions |  | us-gaap:Revenues | 2021-10-04→2022-10-02 | ProductAndServiceOtherMember | 2018700000 |
| Total net revenues | Sep 29, 2024 | 36,176.2 | millions |  | us-gaap:Revenues | 2023-10-02→2024-09-29 |  | 36176200000 |
| Total net revenues | Oct 1, 2023 | 35,975.6 | millions |  | us-gaap:Revenues | 2022-10-03→2023-10-01 |  | 35975600000 |
| Total net revenues | Oct 2, 2022 | 32,250.3 | millions |  | us-gaap:Revenues | 2021-10-04→2022-10-02 |  | 32250300000 |
| Product and distribution costs | Sep 29, 2024 | 11,180.6 | millions |  | us-gaap:ProductionAndDistributionCosts | 2023-10-02→2024-09-29 |  | 11180600000 |
| Product and distribution costs | Oct 1, 2023 | 11,409.1 | millions |  | us-gaap:ProductionAndDistributionCosts | 2022-10-03→2023-10-01 |  | 11409100000 |
| Product and distribution costs | Oct 2, 2022 | 10,317.4 | millions |  | us-gaap:ProductionAndDistributionCosts | 2021-10-04→2022-10-02 |  | 10317400000 |
| Store operating expenses | Sep 29, 2024 | 15,286.5 | millions |  | sbux:StoreOperatingExpenses | 2023-10-02→2024-09-29 |  | 15286500000 |
| Store operating expenses | Oct 1, 2023 | 14,720.3 | millions |  | sbux:StoreOperatingExpenses | 2022-10-03→2023-10-01 |  | 14720300000 |
| Store operating expenses | Oct 2, 2022 | 13,561.8 | millions |  | sbux:StoreOperatingExpenses | 2021-10-04→2022-10-02 |  | 13561800000 |
| Other operating expenses | Sep 29, 2024 | 565.6 | millions |  | us-gaap:OtherCostAndExpenseOperating | 2023-10-02→2024-09-29 |  | 565600000 |
| Other operating expenses | Oct 1, 2023 | 539.4 | millions |  | us-gaap:OtherCostAndExpenseOperating | 2022-10-03→2023-10-01 |  | 539400000 |
| Other operating expenses | Oct 2, 2022 | 461.5 | millions |  | us-gaap:OtherCostAndExpenseOperating | 2021-10-04→2022-10-02 |  | 461500000 |
| Depreciation and amortization expenses | Sep 29, 2024 | 1,512.6 | millions |  | us-gaap:DepreciationAndAmortization | 2023-10-02→2024-09-29 |  | 1512600000 |
| Depreciation and amortization expenses | Oct 1, 2023 | 1,362.6 | millions |  | us-gaap:DepreciationAndAmortization | 2022-10-03→2023-10-01 |  | 1362600000 |
| Depreciation and amortization expenses | Oct 2, 2022 | 1,447.9 | millions |  | us-gaap:DepreciationAndAmortization | 2021-10-04→2022-10-02 |  | 1447900000 |
| General and administrative expenses | Sep 29, 2024 | 2,523.3 | millions |  | us-gaap:GeneralAndAdministrativeExpense | 2023-10-02→2024-09-29 |  | 2523300000 |
| General and administrative expenses | Oct 1, 2023 | 2,441.3 | millions |  | us-gaap:GeneralAndAdministrativeExpense | 2022-10-03→2023-10-01 |  | 2441300000 |
| General and administrative expenses | Oct 2, 2022 | 2,032.0 | millions |  | us-gaap:GeneralAndAdministrativeExpense | 2021-10-04→2022-10-02 |  | 2032000000 |
| Restructuring and impairments | Sep 29, 2024 | — | millions |  | us-gaap:RestructuringSettlementAndImpairmentProvisions | 2023-10-02→2024-09-29 |  | 0 |
| Restructuring and impairments | Oct 1, 2023 | 21.8 | millions |  | us-gaap:RestructuringSettlementAndImpairmentProvisions | 2022-10-03→2023-10-01 |  | 21800000 |
| Restructuring and impairments | Oct 2, 2022 | 46.0 | millions |  | us-gaap:RestructuringSettlementAndImpairmentProvisions | 2021-10-04→2022-10-02 |  | 46000000 |
| Total operating expenses | Sep 29, 2024 | 31,068.6 | millions |  | us-gaap:CostsAndExpenses | 2023-10-02→2024-09-29 |  | 31068600000 |
| Total operating expenses | Oct 1, 2023 | 30,494.5 | millions |  | us-gaap:CostsAndExpenses | 2022-10-03→2023-10-01 |  | 30494500000 |
| Total operating expenses | Oct 2, 2022 | 27,866.6 | millions |  | us-gaap:CostsAndExpenses | 2021-10-04→2022-10-02 |  | 27866600000 |
| Income from equity investees | Sep 29, 2024 | 301.2 | millions |  | us-gaap:IncomeLossFromEquityMethodInvestments | 2023-10-02→2024-09-29 |  | 301200000 |
| Income from equity investees | Oct 1, 2023 | 298.4 | millions |  | us-gaap:IncomeLossFromEquityMethodInvestments | 2022-10-03→2023-10-01 |  | 298400000 |
| Income from equity investees | Oct 2, 2022 | 234.1 | millions |  | us-gaap:IncomeLossFromEquityMethodInvestments | 2021-10-04→2022-10-02 |  | 234100000 |
| Gain from sale of assets | Sep 29, 2024 | — | millions |  | us-gaap:GainLossOnDispositionOfAssets1 | 2023-10-02→2024-09-29 |  | 0 |
| Gain from sale of assets | Oct 1, 2023 | 91.3 | millions |  | us-gaap:GainLossOnDispositionOfAssets1 | 2022-10-03→2023-10-01 |  | 91300000 |
| Gain from sale of assets | Oct 2, 2022 | — | millions |  | us-gaap:GainLossOnDispositionOfAssets1 | 2021-10-04→2022-10-02 |  | 0 |
| Operating income | Sep 29, 2024 | 5,408.8 | millions |  | us-gaap:OperatingIncomeLoss | 2023-10-02→2024-09-29 |  | 5408800000 |

…35 more cells

### sbux_10k_fy2024 — Note 17: Segment Reporting
`sbux_10k_fy2024:v1:table:63` · Item 8. Financial Statements and Supplementary Data · HTML page 88 (printed 85) · scale hint: None

| Row | Column | Raw | Scale | Neg. shown | iXBRL concept | Period | Dims | Value |
|---|---|---|---|---|---|---|---|---|
| Beverage (1) | Sep 29, 2024 | 21,883.9 | None |  | us-gaap:Revenues | 2023-10-02→2024-09-29 | BeverageMember | 21883900000 |
| Beverage (1) | Sep 29, 2024 | 60 | None |  | us-gaap:ConcentrationRiskPercentage1 | 2023-10-02→2024-09-29 | ProductTypeMember, BeverageMember, SalesRevenueNetMember | 0.60 |
| Beverage (1) | Oct 1, 2023 | 21,684.8 | None |  | us-gaap:Revenues | 2022-10-03→2023-10-01 | BeverageMember | 21684800000 |
| Beverage (1) | Oct 1, 2023 | 60 | None |  | us-gaap:ConcentrationRiskPercentage1 | 2022-10-03→2023-10-01 | ProductTypeMember, BeverageMember, SalesRevenueNetMember | 0.60 |
| Beverage (1) | Oct 2, 2022 | 19,555.3 | None |  | us-gaap:Revenues | 2021-10-04→2022-10-02 | BeverageMember | 19555300000 |
| Beverage (1) | Oct 2, 2022 | 61 | None |  | us-gaap:ConcentrationRiskPercentage1 | 2021-10-04→2022-10-02 | ProductTypeMember, BeverageMember, SalesRevenueNetMember | 0.61 |
| Food (2) | Sep 29, 2024 | 6,749.2 | None |  | us-gaap:Revenues | 2023-10-02→2024-09-29 | FoodMember | 6749200000 |
| Food (2) | Sep 29, 2024 | 19 | None |  | us-gaap:ConcentrationRiskPercentage1 | 2023-10-02→2024-09-29 | ProductTypeMember, FoodMember, SalesRevenueNetMember | 0.19 |
| Food (2) | Oct 1, 2023 | 6,585.1 | None |  | us-gaap:Revenues | 2022-10-03→2023-10-01 | FoodMember | 6585100000 |
| Food (2) | Oct 1, 2023 | 18 | None |  | us-gaap:ConcentrationRiskPercentage1 | 2022-10-03→2023-10-01 | ProductTypeMember, FoodMember, SalesRevenueNetMember | 0.18 |
| Food (2) | Oct 2, 2022 | 5,804.2 | None |  | us-gaap:Revenues | 2021-10-04→2022-10-02 | FoodMember | 5804200000 |
| Food (2) | Oct 2, 2022 | 18 | None |  | us-gaap:ConcentrationRiskPercentage1 | 2021-10-04→2022-10-02 | ProductTypeMember, FoodMember, SalesRevenueNetMember | 0.18 |
| Other (3) | Sep 29, 2024 | 7,543.1 | None |  | us-gaap:Revenues | 2023-10-02→2024-09-29 | OtherProductsMember | 7543100000 |
| Other (3) | Sep 29, 2024 | 21 | None |  | us-gaap:ConcentrationRiskPercentage1 | 2023-10-02→2024-09-29 | ProductTypeMember, OtherProductsMember, SalesRevenueNetMember | 0.21 |
| Other (3) | Oct 1, 2023 | 7,705.7 | None |  | us-gaap:Revenues | 2022-10-03→2023-10-01 | OtherProductsMember | 7705700000 |
| Other (3) | Oct 1, 2023 | 22 | None |  | us-gaap:ConcentrationRiskPercentage1 | 2022-10-03→2023-10-01 | ProductTypeMember, OtherProductsMember, SalesRevenueNetMember | 0.22 |
| Other (3) | Oct 2, 2022 | 6,890.8 | None |  | us-gaap:Revenues | 2021-10-04→2022-10-02 | OtherProductsMember | 6890800000 |
| Other (3) | Oct 2, 2022 | 21 | None |  | us-gaap:ConcentrationRiskPercentage1 | 2021-10-04→2022-10-02 | ProductTypeMember, OtherProductsMember, SalesRevenueNetMember | 0.21 |
| Total | Sep 29, 2024 | 36,176.2 | None |  | us-gaap:Revenues | 2023-10-02→2024-09-29 |  | 36176200000 |
| Total | Sep 29, 2024 | 100 | None |  | us-gaap:ConcentrationRiskPercentage1 | 2023-10-02→2024-09-29 | ProductTypeMember, SalesRevenueNetMember | 1.00 |
| Total | Oct 1, 2023 | 35,975.6 | None |  | us-gaap:Revenues | 2022-10-03→2023-10-01 |  | 35975600000 |
| Total | Oct 1, 2023 | 100 | None |  | us-gaap:ConcentrationRiskPercentage1 | 2022-10-03→2023-10-01 | ProductTypeMember, SalesRevenueNetMember | 1.00 |
| Total | Oct 2, 2022 | 32,250.3 | None |  | us-gaap:Revenues | 2021-10-04→2022-10-02 |  | 32250300000 |
| Total | Oct 2, 2022 | 100 | None |  | us-gaap:ConcentrationRiskPercentage1 | 2021-10-04→2022-10-02 | ProductTypeMember, SalesRevenueNetMember | 1.00 |

### sbux_10k_fy2024 — Note 7: Supplemental Balance Sheet and Statement of Earnings Information (in millions)
`sbux_10k_fy2024:v1:table:36` · Item 8. Financial Statements and Supplementary Data · HTML page 77 (printed 74) · scale hint: millions

| Row | Column | Raw | Scale | Neg. shown | iXBRL concept | Period | Dims | Value |
|---|---|---|---|---|---|---|---|---|
| Land | Sep 29, 2024 | 56.9 | millions |  | us-gaap:PropertyPlantAndEquipmentGross | →2024-09-29 | LandMember | 56900000 |
| Land | Oct 1, 2023 | 46.1 | millions |  | us-gaap:PropertyPlantAndEquipmentGross | →2023-10-01 | LandMember | 46100000 |
| Buildings | Sep 29, 2024 | 684.8 | millions |  | us-gaap:PropertyPlantAndEquipmentGross | →2024-09-29 | BuildingMember | 684800000 |
| Buildings | Oct 1, 2023 | 666.5 | millions |  | us-gaap:PropertyPlantAndEquipmentGross | →2023-10-01 | BuildingMember | 666500000 |
| Leasehold improvements | Sep 29, 2024 | 11,453.9 | millions |  | us-gaap:PropertyPlantAndEquipmentGross | →2024-09-29 | LeaseholdImprovementsMember | 11453900000 |
| Leasehold improvements | Oct 1, 2023 | 10,133.7 | millions |  | us-gaap:PropertyPlantAndEquipmentGross | →2023-10-01 | LeaseholdImprovementsMember | 10133700000 |
| Store equipment | Sep 29, 2024 | 3,803.6 | millions |  | us-gaap:PropertyPlantAndEquipmentGross | →2024-09-29 | StoreEquipmentMember | 3803600000 |
| Store equipment | Oct 1, 2023 | 3,332.5 | millions |  | us-gaap:PropertyPlantAndEquipmentGross | →2023-10-01 | StoreEquipmentMember | 3332500000 |
| Roasting equipment | Sep 29, 2024 | 865.7 | millions |  | us-gaap:PropertyPlantAndEquipmentGross | →2024-09-29 | RoastingEquipmentMember | 865700000 |
| Roasting equipment | Oct 1, 2023 | 859.4 | millions |  | us-gaap:PropertyPlantAndEquipmentGross | →2023-10-01 | RoastingEquipmentMember | 859400000 |
| Capitalized software | Sep 29, 2024 | 1,049.7 | millions |  | us-gaap:PropertyPlantAndEquipmentGross | →2024-09-29 | SoftwareAndSoftwareDevelopmentCostsMember | 1049700000 |
| Capitalized software | Oct 1, 2023 | 897.2 | millions |  | us-gaap:PropertyPlantAndEquipmentGross | →2023-10-01 | SoftwareAndSoftwareDevelopmentCostsMember | 897200000 |
| Furniture, fixtures and other | Sep 29, 2024 | 775.5 | millions |  | us-gaap:PropertyPlantAndEquipmentGross | →2024-09-29 | FurnitureAndFixturesMember | 775500000 |
| Furniture, fixtures and other | Oct 1, 2023 | 767.3 | millions |  | us-gaap:PropertyPlantAndEquipmentGross | →2023-10-01 | FurnitureAndFixturesMember | 767300000 |
| Work in progress | Sep 29, 2024 | 750.9 | millions |  | us-gaap:PropertyPlantAndEquipmentGross | →2024-09-29 | ConstructionInProgressMember | 750900000 |
| Work in progress | Oct 1, 2023 | 607.5 | millions |  | us-gaap:PropertyPlantAndEquipmentGross | →2023-10-01 | ConstructionInProgressMember | 607500000 |
| Property, plant and equipment, gross | Sep 29, 2024 | 19,441.0 | millions |  | us-gaap:PropertyPlantAndEquipmentGross | →2024-09-29 |  | 19441000000 |
| Property, plant and equipment, gross | Oct 1, 2023 | 17,310.2 | millions |  | us-gaap:PropertyPlantAndEquipmentGross | →2023-10-01 |  | 17310200000 |
| Accumulated depreciation | Sep 29, 2024 | ( 10,775.5 ) | millions | yes | us-gaap:AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment | →2024-09-29 |  | 10775500000 |
| Accumulated depreciation | Oct 1, 2023 | ( 9,923.1 ) | millions | yes | us-gaap:AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment | →2023-10-01 |  | 9923100000 |
| Property, plant and equipment, net | Sep 29, 2024 | 8,665.5 | millions |  | us-gaap:PropertyPlantAndEquipmentNet | →2024-09-29 |  | 8665500000 |
| Property, plant and equipment, net | Oct 1, 2023 | 7,387.1 | millions |  | us-gaap:PropertyPlantAndEquipmentNet | →2023-10-01 |  | 7387100000 |

### sbux_10q_q2fy2025 — CONSOLIDATED STATEMENTS OF EARNINGS
`sbux_10q_q2fy2025:v1:table:3` · Item 1. Financial Statements · HTML page 3 (printed 3) · scale hint: millions

| Row | Column | Raw | Scale | Neg. shown | iXBRL concept | Period | Dims | Value |
|---|---|---|---|---|---|---|---|---|
| Company-operated stores | Quarter Ended Mar 30, 2025 | 7,285.0 | millions |  | us-gaap:Revenues | 2024-12-30→2025-03-30 | EntityOperatedUnitsMember | 7285000000 |
| Company-operated stores | Quarter Ended Mar 31, 2024 | 7,052.6 | millions |  | us-gaap:Revenues | 2024-01-01→2024-03-31 | EntityOperatedUnitsMember | 7052600000 |
| Company-operated stores | Two Quarters Ended Mar 30, 2025 | 15,070.3 | millions |  | us-gaap:Revenues | 2024-09-30→2025-03-30 | EntityOperatedUnitsMember | 15070300000 |
| Company-operated stores | Two Quarters Ended Mar 31, 2024 | 14,807.9 | millions |  | us-gaap:Revenues | 2023-10-02→2024-03-31 | EntityOperatedUnitsMember | 14807900000 |
| Licensed stores | Quarter Ended Mar 30, 2025 | 1,016.0 | millions |  | us-gaap:Revenues | 2024-12-30→2025-03-30 | FranchisedUnitsMember | 1016000000 |
| Licensed stores | Quarter Ended Mar 31, 2024 | 1,054.5 | millions |  | us-gaap:Revenues | 2024-01-01→2024-03-31 | FranchisedUnitsMember | 1054500000 |
| Licensed stores | Two Quarters Ended Mar 30, 2025 | 2,151.7 | millions |  | us-gaap:Revenues | 2024-09-30→2025-03-30 | FranchisedUnitsMember | 2151700000 |
| Licensed stores | Two Quarters Ended Mar 31, 2024 | 2,246.6 | millions |  | us-gaap:Revenues | 2023-10-02→2024-03-31 | FranchisedUnitsMember | 2246600000 |
| Other | Quarter Ended Mar 30, 2025 | 460.6 | millions |  | us-gaap:Revenues | 2024-12-30→2025-03-30 | ProductAndServiceOtherMember | 460600000 |
| Other | Quarter Ended Mar 31, 2024 | 455.9 | millions |  | us-gaap:Revenues | 2024-01-01→2024-03-31 | ProductAndServiceOtherMember | 455900000 |
| Other | Two Quarters Ended Mar 30, 2025 | 937.4 | millions |  | us-gaap:Revenues | 2024-09-30→2025-03-30 | ProductAndServiceOtherMember | 937400000 |
| Other | Two Quarters Ended Mar 31, 2024 | 933.8 | millions |  | us-gaap:Revenues | 2023-10-02→2024-03-31 | ProductAndServiceOtherMember | 933800000 |
| Total net revenues | Quarter Ended Mar 30, 2025 | 8,761.6 | millions |  | us-gaap:Revenues | 2024-12-30→2025-03-30 |  | 8761600000 |
| Total net revenues | Quarter Ended Mar 31, 2024 | 8,563.0 | millions |  | us-gaap:Revenues | 2024-01-01→2024-03-31 |  | 8563000000 |
| Total net revenues | Two Quarters Ended Mar 30, 2025 | 18,159.4 | millions |  | us-gaap:Revenues | 2024-09-30→2025-03-30 |  | 18159400000 |
| Total net revenues | Two Quarters Ended Mar 31, 2024 | 17,988.3 | millions |  | us-gaap:Revenues | 2023-10-02→2024-03-31 |  | 17988300000 |
| Product and distribution costs | Quarter Ended Mar 30, 2025 | 2,737.6 | millions |  | us-gaap:ProductionAndDistributionCosts | 2024-12-30→2025-03-30 |  | 2737600000 |
| Product and distribution costs | Quarter Ended Mar 31, 2024 | 2,648.7 | millions |  | us-gaap:ProductionAndDistributionCosts | 2024-01-01→2024-03-31 |  | 2648700000 |
| Product and distribution costs | Two Quarters Ended Mar 30, 2025 | 5,631.3 | millions |  | us-gaap:ProductionAndDistributionCosts | 2024-09-30→2025-03-30 |  | 5631300000 |
| Product and distribution costs | Two Quarters Ended Mar 31, 2024 | 5,629.2 | millions |  | us-gaap:ProductionAndDistributionCosts | 2023-10-02→2024-03-31 |  | 5629200000 |
| Store operating expenses | Quarter Ended Mar 30, 2025 | 4,176.0 | millions |  | sbux:StoreOperatingExpenses | 2024-12-30→2025-03-30 |  | 4176000000 |
| Store operating expenses | Quarter Ended Mar 31, 2024 | 3,724.1 | millions |  | sbux:StoreOperatingExpenses | 2024-01-01→2024-03-31 |  | 3724100000 |
| Store operating expenses | Two Quarters Ended Mar 30, 2025 | 8,379.1 | millions |  | sbux:StoreOperatingExpenses | 2024-09-30→2025-03-30 |  | 8379100000 |
| Store operating expenses | Two Quarters Ended Mar 31, 2024 | 7,575.6 | millions |  | sbux:StoreOperatingExpenses | 2023-10-02→2024-03-31 |  | 7575600000 |
| Other operating expenses | Quarter Ended Mar 30, 2025 | 138.7 | millions |  | us-gaap:OtherCostAndExpenseOperating | 2024-12-30→2025-03-30 |  | 138700000 |
| Other operating expenses | Quarter Ended Mar 31, 2024 | 132.8 | millions |  | us-gaap:OtherCostAndExpenseOperating | 2024-01-01→2024-03-31 |  | 132800000 |
| Other operating expenses | Two Quarters Ended Mar 30, 2025 | 291.3 | millions |  | us-gaap:OtherCostAndExpenseOperating | 2024-09-30→2025-03-30 |  | 291300000 |
| Other operating expenses | Two Quarters Ended Mar 31, 2024 | 283.2 | millions |  | us-gaap:OtherCostAndExpenseOperating | 2023-10-02→2024-03-31 |  | 283200000 |
| Depreciation and amortization expenses | Quarter Ended Mar 30, 2025 | 418.9 | millions |  | us-gaap:DepreciationAndAmortization | 2024-12-30→2025-03-30 |  | 418900000 |
| Depreciation and amortization expenses | Quarter Ended Mar 31, 2024 | 371.9 | millions |  | us-gaap:DepreciationAndAmortization | 2024-01-01→2024-03-31 |  | 371900000 |
| Depreciation and amortization expenses | Two Quarters Ended Mar 30, 2025 | 826.2 | millions |  | us-gaap:DepreciationAndAmortization | 2024-09-30→2025-03-30 |  | 826200000 |
| Depreciation and amortization expenses | Two Quarters Ended Mar 31, 2024 | 737.2 | millions |  | us-gaap:DepreciationAndAmortization | 2023-10-02→2024-03-31 |  | 737200000 |
| General and administrative expenses | Quarter Ended Mar 30, 2025 | 632.3 | millions |  | us-gaap:GeneralAndAdministrativeExpense | 2024-12-30→2025-03-30 |  | 632300000 |
| General and administrative expenses | Quarter Ended Mar 31, 2024 | 654.6 | millions |  | us-gaap:GeneralAndAdministrativeExpense | 2024-01-01→2024-03-31 |  | 654600000 |
| General and administrative expenses | Two Quarters Ended Mar 30, 2025 | 1,298.0 | millions |  | us-gaap:GeneralAndAdministrativeExpense | 2024-09-30→2025-03-30 |  | 1298000000 |
| General and administrative expenses | Two Quarters Ended Mar 31, 2024 | 1,302.6 | millions |  | us-gaap:GeneralAndAdministrativeExpense | 2023-10-02→2024-03-31 |  | 1302600000 |
| Restructuring | Quarter Ended Mar 30, 2025 | 116.2 | millions |  | us-gaap:RestructuringSettlementAndImpairmentProvisions | 2024-12-30→2025-03-30 |  | 116200000 |
| Restructuring | Quarter Ended Mar 31, 2024 | — | millions |  | us-gaap:RestructuringSettlementAndImpairmentProvisions | 2024-01-01→2024-03-31 |  | 0 |
| Restructuring | Two Quarters Ended Mar 30, 2025 | 116.2 | millions |  | us-gaap:RestructuringSettlementAndImpairmentProvisions | 2024-09-30→2025-03-30 |  | 116200000 |
| Restructuring | Two Quarters Ended Mar 31, 2024 | — | millions |  | us-gaap:RestructuringSettlementAndImpairmentProvisions | 2023-10-02→2024-03-31 |  | 0 |

…56 more cells
