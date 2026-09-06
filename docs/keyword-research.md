# Keyword validation — month zero

> **Run date:** 2026-08-29 · **Market:** United States / English
> **Source:** search index data (volume, CPC, 12-month trend) + live SERPs
>
> This document is the output of step 9-2 of the main specification and **sets the order in which pages are built**.

---

## ⚠️ Two warnings before reading the numbers

1. **`competition` in this data is Google Ads competition, not SEO difficulty.** Almost every tax keyword shows as "LOW" because few advertisers bid on them — that has nothing to do with how hard it is to rank. Read real difficulty from the SERP analysis (section 3), not from that column.
2. **Volumes are estimates** (confidence around 0.7) and are 12-month averages. In this niche the average is misleading — read section 4.

---

## 1. The main finding: the 51-state-page plan is not supported by the data

This is the most important result of this research and it **refutes the core assumption of both versions of the specification** — the first, which made 51 states the core, and my rewrite, which kept it.

| Keyword | Monthly volume |
|---|---|
| self employment tax calculator **california** | 210 |
| self employment tax calculator **texas** | 30 |
| self employment tax **by state** | 10 |
| self-employment tax calculator **federal and state** | 110 |

California is the most populous state in the US and its entire demand for this topic is **210 searches a month**. Texas is 30.

**Estimate for all 51 states:** roughly 1,000–2,000 searches a month combined. If we took position one on all 51 keywords — which will not happen in year one — that is roughly 300–600 visits a month.

**The cost:** 51 pages × 1,200 words = **61,000 words**, plus extracting bracket tables and rules from 51 revenue departments.

**Conclusion:** the worst return-to-effort ratio in the whole plan. The state pages drop from "the core of the project" to "a secondary layer, at most 8–10 large states".

---

## 2. Where the real demand is

Almost all the volume sits in a handful of generic tool pages, not in geographic segmentation:

| Keyword | Monthly volume | CPC | Estimated value |
|---|---|---|---|
| take home pay calculator | 60,500 | $5.69 | Very high |
| tax return calculator | 40,500 | $6.38 | Very high |
| **estimated tax calculator** | **27,100** | $2.22 | **High — and an explosive January peak** |
| irs estimated tax payment | 33,100 | $7.28 | High |
| estimated tax payments | 22,200 | $6.77 | High |
| paycheck tax calculator | 18,100 | $4.48 | High |
| tax withholding calculator | 14,800 | $5.78 | High |
| **self employment tax calculator** | **9,900** | **$5.01** | **Our niche anchor** |
| self-employment tax brackets | 4,400 | $3.09 | Medium |
| how to calculate self-employment tax | 1,900 | $6.08 | Medium |
| 1099 tax calculator with deductions | 720 | $5.81 | Low volume, high value |
| self employment tax deductions calculator | 390 | $6.13 (top $15.20) | Low volume, high value |

**One excellent page on "estimated tax calculator" is worth more than all 51 state pages.**

### 2-1. An important discovery: the same engine, six times the market

The engine defined in section 4 of the specification (federal + state brackets + FICA) also computes W-2 employees with very little extra work. And that side of the market is **much larger**:

- take home pay calculator — 60,500
- income tax calculator — 90,500
- paycheck tax calculator — 18,100
- after tax income calculator — 18,100

The W-2 cluster totals roughly **187,000 a month** against roughly **30,000** for the self-employment cluster.

It is harder to compete in, but **its marginal build cost is near zero** because the engine is the same. This belongs in phase 1.5, not phase 2.

---

## 3. SERP analysis — can we compete at all?

A live check of `self employment tax calculator` (2026-08-29):

| Position | Domain | Type |
|---|---|---|
| 1 | taxact.com | Tax software |
| 2 | apps.irs.gov | The IRS itself |
| 3 | irs.gov | The IRS itself |
| 4 | jacksonhewitt.com | Tax software |
| 5 | **umb.com** | A bank |
| 6 | **guidestone.org** | A retirement institution |
| 7 | **thehartford.com** | An insurance company |
| 8 | play.google.com | An Android app |
| 9 | **midflorida.com** | A local credit union |
| 10 | **nationwide.com** | An insurance company |
| 11 | calcxml.com | A calculator widget |
| 13 | **sdocpa.com** | A small accounting practice |

### Interpretation

**The good news:** six of the top ten positions are white-label widgets on bank and insurance sites. They have no depth of content, no state support, no quarterly payment calendar, and no bracket-by-bracket table. **On content quality they are easy to beat.**

**The bad news:** they rank on domain authority, not quality. And domain authority is exactly what we lack. This confirms that **content quality alone is not enough** — section 9-4 of the specification (links and distribution) is genuinely critical, not a side task.

**The encouraging news:** `sdocpa.com` — a small accounting practice — sits at position 13. And more importantly, the AI Overview for this keyword cites **`taxstra.com`**, a small niche site, above TaxAct and QuickBooks. A small site can win in this niche.

### 3-1. AI Overviews — a new reality the specification did not have

On the primary keyword, **an AI Overview is displayed above all organic results** (the first organic result is effectively in absolute position 2). This heavily compresses organic click-through and our traffic model has to become more conservative.

But it opens another route: **being cited inside the AI Overview.** `taxstra.com` did exactly that. The structure that earns the citation — a step-by-step definition of the formula with concrete numbers — is exactly what our engine produces. This should become an explicit goal in the specification, not an accident.

---

## 4. Seasonality — more extreme than the specification assumed

The real 12-month trend, not the average:

| Keyword | Trough (summer) | Peak (January) | Multiple |
|---|---|---|---|
| turbotax calculator | 3,600 | 165,000 | **46×** |
| tax return calculator | 6,600 | 201,000 | **30×** |
| estimated tax calculator | 6,600 | 110,000 | **17×** |
| tax withholding calculator | 8,100 | 33,100 | 4× |
| self employment tax calculator | 6,600 | 18,100 | 2.7× |
| take home pay calculator | 49,500 | 60,500 | 1.2× (nearly flat) |

**Two operational consequences:**

1. **The project's real deadline is December 2026, not "six months".** A page published in February has missed the peak and must wait a year. It is late August — roughly four months.
2. **`take home pay calculator` is nearly seasonless.** That means steady income in the months outside tax season. For monthly revenue to be even — and our goal is "$500 a month", not "$6,000 a year" — the W-2 cluster is the stabiliser.

> **Superseded in version 4 of the specification.** The December deadline came from tax seasonality. Once the core identity moved to the place cluster, which is nearly seasonless, the deadline no longer binds. Tax season still gives a jump; the project's failure is no longer tied to it.

---

## 5. Revised page plan

From **~75 pages** to **~37 pages**. Fewer, but every one on proven demand.

### Layer 1 — the core tools (built first; these are the business)

| # | Path | Target keyword | Volume |
|---|---|---|---|
| 1 | `/tools/self-employment-tax-calculator` | self employment tax calculator | 9,900 |
| 2 | `/tools/estimated-tax-calculator` | estimated tax calculator + estimated tax payments | 27,100 + 22,200 |
| 3 | `/tools/1099-tax-calculator` | the 1099 cluster | ~1,500 |
| 4 | `/tools/freelance-tax-calculator` | the complete calculator, an umbrella page | ~1,000 |
| 5 | `/tools/self-employment-tax-deductions-calculator` | low volume but CPC up to $15.20 | 390 |

### Layer 1.5 — the W-2 cluster (same engine, six times the market)

| # | Path | Target keyword | Volume |
|---|---|---|---|
| 6 | `/tools/take-home-pay-calculator` | take home pay calculator | 60,500 |
| 7 | `/tools/paycheck-tax-calculator` | paycheck tax calculator | 18,100 |
| 8 | `/tools/tax-withholding-calculator` | tax withholding calculator | 14,800 |

> More competitive, and probably will not rank well in year one — but because the engine is shared, the marginal cost of each is one page of content. Worth building even if the return arrives later.

### Layer 2 — guides with proven demand (9 pages)

| Path | Volume |
|---|---|
| `/guides/self-employment-tax-brackets` | 4,400 |
| `/guides/how-to-calculate-self-employment-tax` | 1,900 |
| `/guides/self-employment-tax-vs-income-tax` | 710 (two keywords) |
| `/guides/how-to-avoid-self-employment-tax` (the S-Corp angle) | 260 |
| `/guides/is-self-employment-tax-deductible` | 210 |
| `/guides/estimated-tax-due-dates` | from the estimated cluster |
| `/guides/safe-harbor-and-underpayment-penalty` | from the estimated cluster |
| `/guides/freelance-tax-deductions` | the deductions cluster |
| `/guides/home-office-deduction` | the deductions cluster |

### Layer 3 — state pages: 8 states, not 51

California, New York, Texas, Florida, Illinois, Pennsylvania, Washington, Ohio

**No ninth state is built until gate 1's outcome is known.** If these 8 take impressions and rank, expand to the next 15–20. If not, stop — the remaining 43 pages are not worth it.

### Layer 4 — trust pages (7 pages, unchanged)

About · Methodology · Sources · Editorial Policy · Privacy · Terms · Contact

**Total: 5 + 3 + 9 + 8 + 7 = 32 pages** (plus home and directory = 34). That meets AdSense's 30–40 page threshold.

**Content volume: from 80,000 words to about 35,000.** That is the difference between "achievable by December" and "not achievable".

---

## 6. Revised traffic model

Total addressable demand for the plan above (excluding the W-2 cluster): roughly **55,000 searches a month**. With the W-2 cluster: roughly **140,000**.

| Stage | Realistic share | Monthly visits | Revenue at $20 RPM |
|---|---|---|---|
| Month 6 (position 15–30) | ~3% | ~1,700 | ~$35 |
| Month 12 (position 8–15) | ~8% | ~4,500 | ~$90 |
| Month 18 (position 4–10) | ~15% | ~8,500 | ~$170 |
| + the January peak | — | 3–5× in that month | — |

### The honest finding from this model

**The self-employment tax cluster alone does not reach $500 a month** — even with good execution. Its ceiling is roughly $150–250 a month, with seasonal spikes.

The path to $500 has three components and all three are required:
1. Dominating the self-employment cluster (this plan) — a ~$150 base
2. **The W-2 cluster on the same engine** — the largest lever, ~$200+
3. The January-to-April peak — which alone can push several months above target

That is why layer 1.5 moved from "phase 2" into phase 1. Without it the numeric goal is not met.

---

## 6-5. Second measurement round — the financial cluster beyond tax (2026-08-29)

The question: is restricting to freelancer tax correct? To answer it, the broader financial cluster was measured.

### Cost of living — now measured, not assumed

| Keyword | Volume | CPC | Market value |
|---|---|---|---|
| **cost of living calculator** | **60,500** | $1.65 | 99,825 |
| cost of living comparison calculator | 3,600 | $2.03 | 7,308 |

> ⛔ **This table was wrong twice and both errors were mine.**
>
> **First:** in the initial review I said "cost of living is worth less" without measuring.
> **Second:** I measured, but the **wrong keyword** — only `cost of living comparison calculator`, a long tail (3,600) — and rejected the whole cluster on that basis. The head term `cost of living calculator` is **60,500**, seventeen times what I reported.
>
> The methodological lesson: when rejecting a cluster, you must have measured the **head keyword**, not the first thing that appeared in the expansion.

### The third correction — the full cluster, finally

Both corrections above were still incomplete: I counted only the head keyword, not the cluster.

| Keyword | Volume | CPC |
|---|---|---|
| cost of living calculator | 60,500 | $1.65 |
| **cost of living comparison** | **49,500** | $0.97 |
| cost of living in austin | 3,600 | $2.71 |
| cost of living in san francisco | 2,900 | $0.89 |
| cost of living in san antonio | 1,900 | **$8.85** |
| houston cost of living | 1,900 | $4.05 |
| cost of living in houston | 1,300 | $3.37 |

**Cluster total with ~30 large cities: roughly 158,000 searches a month.**

> ⛔ **Three times, and underestimated every time.** First without measuring. Second on the wrong keyword (3,600). Third on the head keyword only (60,500) without the cluster. The real figure is **158,000**.
>
> The claim "the lowest market value in the whole catalogue" was also wrong. With the full cluster its market value is around **300,000** — mid-pack, above budget, discount and future value.

### The structural finding — more important than the numbers themselves

City-pair comparisons were measured separately:

| Keyword | Volume |
|---|---|
| **cost of living comparison** (the tool itself) | **49,500** |
| cost of living in austin vs dallas | 260 |
| cost of living in austin vs houston | 170 |
| cost of living in san antonio vs houston | 70 |
| cost of living in san antonio vs dallas | 40 |
| dallas vs houston vs austin cost of living | 10 |

**The demand is in the "tool", not in the "pair page".** 49,500 people want a tool where they choose the two places themselves; only 260 are after a specific "Austin versus Dallas".

This confirms the specification's anti-cartesian rule and also says what to build instead: **one excellent comparison tool**, plus single-city pages for the large cities — and no pair pages at all.

### Compared with the state tax pages

| | State tax | City cost of living |
|---|---|---|
| Best page | California 210 | Austin 3,600 |
| Median page | ~40 | ~1,500 |
| Ratio | — | **~10 to 17 times better** |

Per page, the cost-of-living city pages are **far** better than the state tax pages — which were themselves cut to 8 pages in the specification.

### The data problem — solvable with free official sources

| Layer | Source | Status |
|---|---|---|
| US regional price index | **BEA Regional Price Parities** — state and metro level | Official, free, citable |
| US rent | **HUD Fair Market Rent** — county level | Official, free, machine-readable |
| US consumer items | **BLS regional CPI** | Official, free |
| **Europe — country level** | **Eurostat comparative price levels** | Official, free |

The `eurostat`, `censusdata` and `cpi` packages exist on PyPI. `.gov` domains are blocked in this sandbox so they cannot be pulled here, but that is an **environment** limitation, not a project one.

> **This is better than Numbeo, not worse.** Official government data we can link to is exactly the E-E-A-T story the specification built for tax — and something Numbeo cannot offer.

**Final conclusion:** cost of living enters the roadmap. Its structure is exactly what the user proposed: **cities for the US, countries for Europe** — because the available official data is published at precisely those levels.

### The cluster that genuinely should be added

| Keyword | Volume | CPC | Data dependency |
|---|---|---|---|
| **margin calculator** | 110,000 | **$10.92** (top $29.10) | none |
| **ebay fee calculator** | 40,500 | **$12.23** | a fixed fee table |
| **fuel cost calculator** | 40,500 | **$8.93** | none |
| apr calculator | 33,100 | $5.44 | none |
| budget calculator | 22,200 | $5.29 | none |
| options profit calculator | 33,100 | $5.20 | none |
| compound interest calculator | **823,000** | $1.74 | none |
| inflation calculator | **550,000** | $2.97 | **BLS CPI — public and free** |
| investment calculator | 450,000 | $2.00 | none |
| interest calculator | 165,000 | $3.49 | none |
| savings calculator | 60,500 | $3.16 | none |
| salary ↔ hourly | 99,000 | $0.88–1.72 | none |
| future value calculator | 40,500 | $1.72 | none |
| monthly payment calculator | 27,100 | $3.13 | none |

**Approximate total: 2.4 million monthly searches.**

### Why this discovery matters more than its volume

The hidden assumption that was wrong: "expanding competes with the tax work for the same scarce resource."

This project's scarce resource is **verified tax data and YMYL content**. But the last column above shows these calculators do not consume it:

| | The tax cluster | This cluster |
|---|---|---|
| Dataset required | 51 jurisdictions + federal + quarterly | almost none |
| Annual verification | Mandatory | None |
| E-E-A-T burden | Heavy YMYL | Light |
| Cost per page | Hours of data + 1,200 words | A few dozen lines of arithmetic |
| Seasonality | Up to 46× | Nearly flat |

**So this cluster does not threaten the December deadline** — unlike cost of living, which is a complete data project in itself. It can run in parallel and hold the revenue floor in the months outside tax season.

**Warning:** a high CPC does not mean an easy ranking. `margin calculator` and `ebay fee calculator` have entrenched competitors. Their advantage is that they carry a lighter YMYL burden, so the domain-authority barrier is lower.

> **Superseded in version 4 of the specification.** This entire cluster was later removed from scope: it has good volume and CPC but does not answer the core sentence, and it dilutes topical authority. See specification section 2-2-3. It is recorded here because the reasoning that produced it — the scarce-resource analysis — remains correct; only its conclusion was overridden by the context constraint.

---

## 7. Decisions arising from this research

| # | Decision | Basis |
|---|---|---|
| 1 | 51 state pages → 8 pages | California 210/month, Texas 30/month |
| 2 | Tools promoted from the second layer to the core of the project | 99% of demand is there |
| 3 | The W-2 cluster moved from phase 2 to phase 1.5 | 6× the market, near-zero marginal cost |
| 4 | `estimated-tax-calculator` is the highest build priority | 27,100 + a January peak of 110,000 |
| 5 | Project deadline: **December 2026** | Seasonality up to 46× |
| 6 | Being cited in AI Overviews became an explicit goal | taxstra.com proved a small site can |
| 7 | Revenue model: the tax cluster alone does not reach the target | Section 6 above |
| 8 | Cost of living deferred — this time with measurement | 3,600/month, section 6-5 |
| 9 | The "simple maths, high CPC" cluster is added | 2.4 million/month with no data dependency, section 6-5 |

> **Decisions 1, 5, 8 and 9 were later overturned**, and the corrections are recorded in this document above and in specification section 20. Decision 8 in particular was wrong three times over: the cluster is 158,000/month, not 3,600, and it became the core of the project. The table is kept as written because the record of a wrong decision is more useful than a quietly corrected one.

---

*This document is the result of one research run. After three months of Search Console data it should be replaced with our own real data, not by repeating this research.*
