# Tax data verification checklist — tax year 2026

> This document is the output of section 13 of the main specification.

> **The data was produced but is not yet verified.** No page ships until its corresponding row here is ticked.


---

## 1. Current status

| Item | Value |
|---|---|
| Jurisdictions extracted | **51** (50 states + Washington DC) |
| Structure | 9 no-tax · 15 flat · 27 progressive |
| Structural errors | **0** (`scripts/validate_tax_data.py`) |
| Source class | **Secondary** — requires verification |
| Source package | `policyengine-us` version `1.821.4` |
| Generated at | 2026-08-29T16:05:23Z |

### Why "secondary"

The development environment's network cannot reach `irs.gov` or the state revenue department sites. The data was extracted from the parameter tree of a maintained open-source model in which every parameter carries a reference to a primary source (statute, Revenue Procedure, state form); those references are copied into each file's `provenance.sources` field.

**The web-search alternative was deliberately rejected:** two consecutive searches for the same keyword returned contradictory federal brackets (105,700 versus 107,475). The current data agrees with the first and not the second — meaning search summaries are not reliable for this job.


---

## 2. Federal — highest priority

A mistake here makes **every** page wrong at once.


| # | Item | Extracted value | Verified |
|---|---|---|---|
| 1 | Federal brackets (single) | 10% · 12% · 22% · 24% · 32% · 35% · 37% | ⬜ |
| 2 | Thresholds, single | 12,400 · 50,400 · 105,700 · 201,775 · 256,225 · 640,600 | ⬜ |
| 3 | Thresholds, marriedJointly | 24,800 · 100,800 · 211,400 · 403,550 · 512,450 · 768,700 | ⬜ |
| 4 | Thresholds, marriedSeparately | 12,400 · 50,400 · 105,700 · 201,775 · 256,225 · 384,350 | ⬜ |
| 5 | Thresholds, headOfHousehold | 17,700 · 67,450 · 105,700 · 201,750 · 256,200 · 640,600 | ⬜ |
| 6 | Standard deduction | single 16,100 · MFJ 32,200 · HoH 24,150 | ⬜ |
| 7 | SE tax rates | 12.4% + 2.9% = 15.3% | ⬜ |
| 8 | NESE factor | 0.9235 (derived from `1 - (socialSecurityRate + medicareRate) / 2`) | ⬜ |
| 9 | Social Security cap | 184,500 | ⬜ |
| 10 | SE tax minimum threshold | 400 | ⬜ |
| 11 | Additional Medicare | 0.9% above 200,000/250,000/125,000 (not indexed) | ⬜ |
| 12 | QBI | rate 20.0% · phase-out begins: single 201,750 · MFJ 403,500 | ⬜ |
| 13 | Quarterly due dates | Q1 2026-04-15 · Q2 2026-06-15 · Q3 2026-09-15 · Q4 2027-01-15 | ⬜ |
| 14 | Safe harbor percentages | 90% of the current year · 100% of the prior year · 110% if prior-year AGI > $150,000 (MFS: $75,000) | ⬜ |
| 15 | Minimum liability triggering a penalty | $1,000 | ⬜ |

**Primary source for items 1–6:** Rev. Proc. 2025-32 — https://www.irs.gov/pub/irs-drop/rp-25-32.pdf


**Items 13–15 come from a different source.** They were not in the source parameter tree, but unlike the brackets they are statutory constants rather than inflation-indexed figures. Instead of copying a table, `scripts/estimated_tax.py` computes them from the pattern in 26 U.S.C. 6654(c)(2) and the holiday rule in 7503.

> ✅ **This resolved a real contradiction:** two web sources gave two different dates for the second 2026 due date (June 15 and 16). The calculation showed June 15, 2026 is a Monday, so no shift applies. The algorithmic derivation also gets genuinely shifting years right — the first 2028 due date moves to April 18, because April 15 is a Saturday and April 17 is DC's Emancipation Day.

**Verify these three rows** against that year's Form 1040-ES: https://www.irs.gov/pub/irs-pdf/f1040es.pdf


---

## 3. Priority states (the first 8 pages)

| State | Structure | Rate | Stale? | Primary source | Verified |
|---|---|---|---|---|---|
| California | progressive | 9 brackets, top 12.3% | ⚠️ yes | [2021 Form 540 California Resident Income Tax](https://www.ftb.ca.gov/forms/2021/2021-540.pdf) | ⬜ |
| New York | progressive | 9 brackets, top 10.9% | no | [2021 NY Form IT-201 Instructions](https://www.tax.ny.gov/pdf/2021/inc/it201i_2021.pdf#page=51) | ⬜ |
| Texas | none | — | no | — | ⬜ |
| Florida | none | — | no | — | ⬜ |
| Illinois | flat | 4.95% | no | [Income Tax Rates](https://www2.illinois.gov/rev/research/taxrates/Pages/income.aspx) | ⬜ |
| Pennsylvania | flat | 3.07% | no | [PA Form PA-40 Instructions, page 1](https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=1) | ⬜ |
| Washington | none | — | no | — | ⬜ |
| Ohio | progressive | 2 brackets, top 2.75% | no | [Section 5747.02 — Tax rates](https://codes.ohio.gov/ohio-revised-code/section-5747.02) | ⬜ |

---

## 4. The remaining states

| State | Structure | Rate | Stale? | Primary source | Verified |
|---|---|---|---|---|---|
| Alabama | progressive | 3 brackets, top 5% | no | [2024 Alabama Income Tax Instructions](https://www.revenue.alabama.gov/wp-content/uploads/2025/01/24f40bk.pdf#page=25) | ⬜ |
| Alaska | none | — | no | — | ⬜ |
| Arizona | flat | 2.5% | no | [Arizona State Legislature Title 43 - Taxatio](https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01011.htm) | ⬜ |
| Arkansas | progressive | 5 brackets, top 3.7% | no | [2014 Indexed Tax Brackets](https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/TaxBrackets_2014.pdf#page=1) | ⬜ |
| Colorado | flat | 4.4% | no | [Colorado Proposition 121, passed by the elec](https://leg.colorado.gov/sites/default/files/initiative%2520referendum_proposition%20121%20final%20lc%20packet.pdf#page=1) | ⬜ |
| Connecticut | progressive | 7 brackets, top 6.99% | no | [Connecticut General Statutes, Chapter 229, S](https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-700) | ⬜ |
| Delaware | progressive | 7 brackets, top 6.6% | no | [Government of Delaware - Tax Rate Changes](https://revenue.delaware.gov/software-developer/tax-rate-changes/) | ⬜ |
| Georgia | flat | 4.99% | no | [Georgia HB1015 (2023-2024), Section 1 - flat](https://www.legis.ga.gov/legislation/66260) | ⬜ |
| Hawaii | progressive | 12 brackets, top 11% | no | [Tax Rate Schedules For Taxable Years Beginni](https://tax.hawaii.gov/forms/d_18table-on/d_18table-on_p13/) | ⬜ |
| Idaho | flat | 5.3% | ⚠️ yes | [Idaho State Tax Comission - Individual Incom](https://tax.idaho.gov/taxes/income-tax/individual-income/individual-income-tax-rate-schedule/) | ⬜ |
| Indiana | flat | 2.95% | no | [IC 6-3-2-1 Tax rate (a)(3)](https://iga.in.gov/laws/2024/ic/titles/6#6-3-2-1) | ⬜ |
| Iowa | flat | 3.8% | no | [IDR Announces 2023 Interest Rates, Deduction](https://revenue.iowa.gov/taxes/tax-guidance/individual-income-tax/2023-changes-iowa-individual-income-tax) | ⬜ |
| Kansas | progressive | — | no | [2022 Form K-40 instructions](https://www.ksrevenue.gov/pdf/ip22.pdf) | ⬜ |
| Kentucky | flat | 3.5% | no | [2021 Kentucky Individual Income Tax Return R](https://revenue.ky.gov/Forms/Form%20740-2021.pdf#page=1) | ⬜ |
| Louisiana | flat | 3% | no | [Louisiana Revised Statutes, RS 47:32 - Tax o](https://www.legis.la.gov/legis/Law.aspx?d=101946) | ⬜ |
| Maine | progressive | 3 brackets, top 7.15% | no | [§5403. Annual adjustments for inflation 1(A)](https://legislature.maine.gov/statutes/36/title36sec5403.html) | ⬜ |
| Maryland | progressive | 10 brackets, top 6.5% | no | [Maryland 2025 Resident Tax Forms and Instruc](https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=22) | ⬜ |
| Massachusetts | flat | 5% | no | [Section 4: Rates of tax for residents, non-r](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section4) | ⬜ |
| Michigan | flat | 4.25% | no | [Michigan INCOME TAX ACT OF 1967 Chapter 2, 2](http://www.legislature.mi.gov/documents/mcl/pdf/mcl-act-281-of-1967.pdf#page=60) | ⬜ |
| Minnesota | progressive | 4 brackets, top 9.85% | ⚠️ yes | [2023 Minnesota Statutes, 290.06 RATES OF TAX](https://www.revisor.mn.gov/statutes/cite/290.06#stat.290.06.2c) | ⬜ |
| Mississippi | flat | 4% | no | [Mississippi Income Tax Instructions 2022](https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=20) | ⬜ |
| Missouri | progressive | 8 brackets, top 4.7% | ⚠️ yes | [2019 Missouri Income Tax Chart Form MO-1040 ](https://dor.mo.gov/forms/MO-1040%20Instructions_2019.pdf#page=22) | ⬜ |
| Montana | progressive | 2 brackets, top 5.65% | no | [Montana Code Annotated 2021 Title 15, Chapte](https://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0030/0150-0300-0210-0030.html) | ⬜ |
| Nebraska | progressive | 4 brackets, top 4.55% | no | [Legislative Bill 754 (Bill Text)](https://www.nebraskalegislature.gov/FloorDocs/108/PDF/Slip/LB754.pdf#page=3) | ⬜ |
| Nevada | none | — | no | — | ⬜ |
| New Hampshire | none | — | no | — | ⬜ |
| New Jersey | progressive | 7 brackets, top 10.75% | no | [2025 NJ-1040 Instructions - Tax Rate Schedul](https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf#page=65) | ⬜ |
| New Mexico | progressive | 6 brackets, top 5.9% | no | [New Mexico Income Tax, Title 3, Chapter 3, P](https://www.srca.nm.gov/parts/title03/03.003.0007.html) | ⬜ |
| North Carolina | flat | 3.99% | no | [North Carolina Department of Revenue - Tax R](https://www.ncdor.gov/taxes-forms/tax-rate-schedules) | ⬜ |
| North Dakota | progressive | 3 brackets, top 2.5% | no | [2021 North Dakota income tax instructions](https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdf#page=34) | ⬜ |
| Oklahoma | progressive | 4 brackets, top 4.5% | no | [2021 Form 511 instructions](https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf) | ⬜ |
| Oregon | progressive | 4 brackets, top 9.9% | ⚠️ yes | [Chapter 316 - Personal Income Tax](https://www.oregonlegislature.gov/bills_laws/ors/ors316.html) | ⬜ |
| Rhode Island | progressive | 3 brackets, top 5.99% | no | [Rhode Island Division of Taxation Advisory A](https://tax.ri.gov/sites/g/files/xkgbur541/files/2025-11/ADV_2025_22_Inflation_Adjustments.pdf#page=2) | ⬜ |
| South Carolina | progressive | 2 brackets, top 5.21% | no | [SC H.4216 Section 1 - Section 12-6-510(C) (2](https://www.scstatehouse.gov/sess126_2025-2026/bills/4216.htm) | ⬜ |
| South Dakota | none | — | no | — | ⬜ |
| Tennessee | none | — | no | — | ⬜ |
| Utah | flat | 4.45% | no | [Utah Code 59-10-104 (2) (b)](https://le.utah.gov/xcode/historical.html?date=1/1/2014&oc=/xcode/Title59/Chapter10/C59-10-S104_1800010118000101.html) | ⬜ |
| Vermont | progressive | 4 brackets, top 8.75% | ⚠️ yes | [Vermont §5822. Tax on income of individuals,](https://legislature.vermont.gov/statutes/section/32/151/05822) | ⬜ |
| Virginia | progressive | 4 brackets, top 5.75% | no | [Code of Virginia § 58.1-320.](https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/) | ⬜ |
| Washington, D.C. | progressive | 7 brackets, top 10.75% | no | [2021 Form D-40 Booklet](https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=19) | ⬜ |
| West Virginia | progressive | 5 brackets, top 4.58% | no | [West Virginia Senate Bill 392 (2026), §11-21](https://www.wvlegislature.gov/Bill_Text_HTML/2026_SESSIONS/RS/bills/sb392%20sub1%20enr.pdf#page=6) | ⬜ |
| Wisconsin | progressive | 4 brackets, top 7.65% | ⚠️ yes | [State of Wisconsin Department of Revenue](https://www.revenue.wi.gov/Pages/FAQS/pcs-taxrates.aspx) | ⬜ |
| Wyoming | none | — | no | — | ⬜ |

---

## 5. The seven states without 2026 figures

Their brackets are inflation-indexed and the state has not yet published 2026 figures. The current values are **2025**.

- **California** — last value effective from 2025-01-01
- **Idaho** — last value effective from 2025-01-01
- **Minnesota** — last value effective from 2025-01-01
- **Missouri** — last value effective from 2025-01-01
- **Oregon** — last value effective from 2025-01-01
- **Vermont** — last value effective from 2025-01-01
- **Wisconsin** — last value effective from 2025-01-01

**Rule:** until the 2026 figures are published, these pages are either not built or explicitly labelled "based on 2025 figures". Showing a 2025 number under a 2026 heading is the exact mistake this whole project exists to avoid.


---

## 6. How to verify a row

1. Open that row's primary source link (from the JSON file's `provenance.sources`).

2. Compare the number against the JSON file.

3. If they agree: set `verification` to `"verified"` in the file and add `verifiedAt` and `verifiedBy`.

4. If they disagree: **correct the file's number**, not the source. Then add a row to `meta.json`'s `changelog`.

5. After finishing a group: `python3 scripts/validate_tax_data.py --year 2026 --strict`


## 7. Rebuilding the data

```bash
python3 scripts/extract_tax_data.py --year 2026   # rebuild from the source package
python3 scripts/validate_tax_data.py --year 2026  # structural check
```


> Re-running the extraction resets `verification` to `pending`. Commit completed verifications to git before re-running.

