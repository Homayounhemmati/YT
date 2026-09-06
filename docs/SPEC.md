# LifeCalc Pro — Single Reference Specification

> **Status:** This document replaces all three earlier specs. They are kept in `docs/archive/` for history only and are **not authoritative**.
> They contradicted each other in three places (static-first versus SPA, the anti-doorway checklist versus cartesian generation of comparison pages, and a 6-month timeline versus a "wait and validate" phase). This version resolves all three.
>
> **Last revised:** 2026-09-06 · **Version:** 4.7
>
> **Version 4.7:** The whole document set moved to English. The site is English, the data is English, and now the spec is too — one language across the project, and reviewable by anyone. Details in 19-14.
>
> **Version 4.6:** The language boundary became enforceable — every shipping file is English, gated by `check_language.py` in CI. Details in 19-13.
>
> **Version 4.5:** Title/meta/H1 formulas per template, internal anchor text, per-template JSON-LD, robots and OG image — all as data in `data/pages.json` and enforced in CI. Details in 19-12.
>
> **Version 4.2:** Tool depth (tax inside comparison · household size · social contributions) · two new tools · and six SEO gaps, the largest of which was external link building. Details in 19-9.
>
> **Version 4.1:** Numbers moved from prose to reproducible computation (`data/keywords.json` + `scripts/model_revenue.py`); the programmatic architecture gained an entity model, a generation gate, a uniqueness budget and a link graph; section 6 was rewritten around the funnel. Details in 19-8.
>
> **Version 4:** The core identity changed to "the real cost of living in a place — and what you actually keep". The tools are a funnel, not a list; session depth entered the revenue model; the context boundary became explicit and five tools outside it were removed. Details in section 19-7.
>
> **What version 3 added:** Section 4 was reconciled with the engine that was actually built; the tool page template, calculator UX, design tokens, URL rules and the ad placement map were added; plus four strategic sections that were missing entirely: competitive position, measurement, the annual runbook, and risks.

---

## Contents

| # | Section | Status |
|---|---|---|
| 1 | Goal and a realistic revenue model | |
| 2 | Locked decisions | |
| 3 | Architecture and technical stack | |
| 4 | The tax engine — the heart of the project | ✅ built |
| 5 | The data layer and data-validity rules | |
| 6 | Phase 1 page inventory + URL rules | |
| 7 | Content requirements and E-E-A-T | |
| 8 | UI/UX + tokens + tool template + calculator UX | |
| 9 | SEO and indexation | |
| 10 | AdSense + ad placement map | |
| 11 | Timeline and decision gates | |
| 12 | Definition of done | |
| 13 | Tax data — status and verification | ✅ extracted · ⬜ verified |
| 14 | Competitive position | |
| 15 | Measurement and instrumentation | |
| 16 | Annual update runbook | |
| 17 | Risks | |
| 18 | Process for adding a new tool | |
| 19 | Changelog | |

### Related documents

| Document | Role |
|---|---|
| [`keyword-research.md`](keyword-research.md) | Demand validation; the basis for sections 6 and 14 |
| [`data-verification.md`](data-verification.md) | Verification checklist; the basis for section 13 |
| `archive/` | The three original specs — **not authoritative** |

---

## 1. Goal and a realistic revenue model

**Goal:** $500 a month from AdSense.

### 1-1. Working backwards

```
monthly pageviews needed = 500 ÷ RPM × 1000
```

| Page RPM (estimated) | Monthly pageviews needed | Daily pageviews |
|---|---|---|
| $8 (cost-of-living, curiosity traffic, international) | 62,500 | ~2,100 |
| $15 | 33,000 | ~1,100 |
| $25 (tax, US traffic, commercial intent) | 20,000 | ~670 |
| $35 (tax season, high-value keywords) | ~14,300 | ~480 |

**The strategic conclusion:** reaching 20,000 targeted visits is far more plausible than reaching 62,000 general ones. So **our primary lever is RPM, not traffic volume.** The entire document is arranged around that one sentence.

> ⚠️ The RPM figures are estimates and must be replaced with real AdSense dashboard data from month three onward. No decision after month 3 should rest on this table.

> 📊 **Update after keyword validation (2026-08-29):** the self-employment tax cluster alone has a ceiling of roughly **$150–250 a month**. The full model is in [`docs/keyword-research.md`](keyword-research.md), section 6.

### 1-2. Realistic scenarios

| Scenario | Month 3 | Month 6 | Month 12 | Month 18 |
|---|---|---|---|---|
| Pessimistic | $0 (not yet approved) | $10–30 | $80–150 | $200–300 |
| **Base (a reasonable expectation)** | $0–10 | **$50–150** | $250–400 | **~$500** |
| Optimistic | $20–40 | $200–300 | $500–800 | $1,000+ |

**Said plainly:** $500 by month 6 on a new domain, in English, in the finance niche, is a 95th-percentile outcome — not the base case. This document's real target is "$500 at month 12–18, with month 6 as the proof-of-concept point at around $100." If we reach $100 by month 6, the path to $500 is close to assured, because SEO growth compounds.

### 1-3. Cash flow notes

- The AdSense payment threshold is **$100**; a balance below it rolls over to the next month.
- Payment lands around the 21st of the following month.
- Which means **the first real deposit is likely month 8–10**, not the first month that records revenue. Set expectations accordingly.
- The payment account and address must be the offshore company from day one. Changing the address or beneficiary after account approval risks review and suspension — configure it correctly once.

---

### 1-4. The revenue model

> 📊 **The numbers in this section are computed, not written.**
> Source: [`data/keywords.json`](../data/keywords.json) → `scripts/model_revenue.py` → [`revenue-model.md`](revenue-model.md)
> No number here is updated by hand; run the script.

```bash
python3 scripts/model_revenue.py                      # base model
python3 scripts/model_revenue.py --rpm-multiplier 5   # sensitivity analysis
```

#### The cluster

| Metric | Value |
|---|---|
| Monthly cluster volume | **671,720** |
| Weighted average CPC | **$3.51** |
| Tools | 18 |
| Programmatic pages | 81 (30 metros + 51 states) |

#### Model output

| Scenario | Position (hard/medium/easy) | Visits/month | Share | Revenue/month |
|---|---|---|---|---|
| Year 1 — young domain | 25 / 18 / 12 | 9,691 | 0.7% | $132 |
| Year 2 — early authority | 14 / 10 / 6 | 25,207 | 1.7% | $346 |
| **Year 3 — established** | 8 / 6 / 4 | 46,679 | 3.2% | **$640** ✅ |

#### ⚠️ Correcting an optimistic estimate

Earlier versions of this document said "month 18–24". That was a prose estimate. **The computed model says year three** — months 24–36 under the base assumptions.

The gap comes from prose assuming a 3% share without asking **when** that share arrives. The model computes with a real position distribution and an AI Overview penalty, and answers: year three.

#### The two levers that pull that date forward

**1. Session depth — the single largest lever**

| Pages per session | Year 2 revenue | Difference |
|---|---|---|
| 1.1 (no funnel) | $169 | — |
| 1.5 | $233 | +38% |
| **2.2 (base assumption)** | **$346** | **+105%** |
| 3.0 | $475 | +181% |

**The funnel in section 2-2-2 doubles revenue without a single extra visit.** It is the only variable entirely within our control — it depends on neither Google nor competitors. That is why the funnel architecture is the most important product decision, not a UX preference.

**2. The RPM multiplier — the least certain number**

| Multiplier | Year 2 | Year 3 |
|---|---|---|
| ×2 | $173 | $320 |
| ×4 (base) | $346 | $640 |
| ×6 | $519 | $959 |

Migrating to a premium ad network (section 10-5) raises exactly this multiplier. **At year 3, the difference between ×4 and ×6 is the difference between $640 and $959** — on identical traffic.

#### What was deliberately left out

Seven keywords totalling **5,081,500** monthly searches (margin · ebay fee · compound interest · inflation · investment · hours · bmi) were deliberately excluded to keep the context single. The full list with reasons is in `revenue-model.md`.

That figure is written large on purpose: **the "single context" constraint is not free.** But this document puts it ahead of short-term revenue, because diluting topical authority on a young domain kills the core and the periphery alike.

---

## 2. Locked decisions

These are decided. Changing one means rewriting the document, not patching a line.

| Topic | Decision | Why |
|---|---|---|
| **Core identity** | **"The real cost of living in a place — and what you actually keep"** | One single context. A 672k/month cluster, needing a ~3% share. Section 2-2 |
| **Cost of living** | **The core of the project** | The entrance to the funnel. Data from free official sources (BEA · HUD · Eurostat) |
| **Freelancer tools** | **Second cluster, not the core** | Their engine is built, but they do not answer the core sentence |
| **margin · ebay fee · budget · compound interest · investment** | **Removed** | Good volume and CPC, but outside the context — they dilute topical authority |
| **International tax** | Deferred to **phase 3** | High legal risk, not precisely computable, and less SEO value than deepening the US |
| **Stack** | **Next.js with a fully static export** | 160 SPA pages on a new domain risk not being indexed |
| **Data sources** | **Primary public sources only** (IRS, each state's revenue department, BLS, HUD) | Legally sound, differentiating, and the foundation of the Methodology page |
| **Numbeo** | **Not used** | Its terms of service forbid redistribution; and copying a competitor's data carries zero SEO advantage |
| **Comparison pages** | Deferred to phase 2 | State-level search volume is so low that state-vs-state comparison is unjustifiable (section 6-7) |
| **Revenue model** | AdSense only in phase 1 | Tax affiliate offers (accounting software) get evaluated in phase 2 |
| **Final destination** | **A financial calculator hub**, not a general "life" hub | Section 2-2 |
| **Domain** | A single site | — |

### 2-1. What was explicitly removed from the previous spec

- 85 cities and 25 countries of cost-of-living as the **phase 1 core** — the tool itself stays in the catalogue but at the bottom of the priority list
- The international Country Tax Guide
- Automatic generation of comparison pages from pairwise combinations
- `FEDERAL_INCOME_RATE = 14` (an invented flat rate — full reasoning in section 4)
- The `stateRate` field as a guessed "effective rate"
- The currency selector and exchange-rate API (meaningless without international content)
- **43 of the 51 state pages** — after keyword validation, section 6-1

### 2-2. The core identity — one sentence that draws the context boundary

> **"The real cost of living and working in a place — and what actually stays with you."**

Any tool that answers this sentence is in. Any tool that does not is out, **however much volume or CPC it carries**.

#### 2-2-1. Why this sentence, and not just "cost of living"

The second half of the sentence ("what stays with you") is what turns the cluster from a low-value niche into a business. `cost of living calculator` alone carries a CPC of $1.65. But the same user asking "what does it cost there" immediately asks "and how much of my salary is left" — and that question is `take home pay` ($5.69) and `sales tax` ($6.91) and state income tax.

**Result: the cluster's weighted average CPC rises from $1.65 to $3.47, purely by drawing the boundary correctly.**

#### 2-2-2. The tools are a funnel, not a list

```
"What does it cost to live in Austin?"
   ↓ how does that compare to where I am?
"Compare two cities"
   ↓ so what salary do I need?
"Salary conversion"
   ↓ and how much of it do I keep?
"Take-home pay + state tax"
```

The worst economic property of calculator sites is **pages per session ≈ 1.1**: the user takes their number and leaves. This funnel takes it to **2.2–3** — roughly double the revenue on identical traffic and identical RPM.

That lever is larger than almost any other keyword decision, and earlier versions of the revenue model could not see it at all, because they treated every visit as independent.

#### 2-2-3. The boundary — stated explicitly

**In:** cost of living (city and country) · comparison · salary conversion · take-home pay · state income tax · sales tax · country income tax · city pages · the cost of buying a home in a city

**Out — removed:** `profit-margin` · `ebay-fee` · `budget` · compound interest · investment · options profit · inflation · generic amortization

These had good volume and CPC, but they do not answer the core sentence. **They are precisely what dilutes topical authority** — and this project's explicit constraint is not to have that problem.

**Second cluster (not the core):** the freelancer tools — `quarterly-tax` · `1099-deductions` · `self-employment-deductions`. Their engine is built and discarding them would be waste, but they sit outside the core and **are not published until the core's authority is established**.

#### 2-2-4. The moat: why the tax engine was not wasted

| | Numbeo | Bankrate · NerdWallet · Forbes | **costbycity.com** | **realtakehomepay.com** | **Us** |
|---|---|---|---|---|---|
| Cost of living | ✅ | ✅ | ✅ (BEA RPP) | ❌ | ✅ |
| Two-place comparison | ✅ | ✅ | ✅ | ✅ | ✅ |
| Real tax per jurisdiction | ❌ | ❌ | ❌ | ✅ (50 states) | ✅ |
| **Both in one session** | ❌ | ❌ | ❌ | ❌ | **✅** |

> ⚠️ **Correcting a claim of mine.** I previously wrote "nobody offers these together" without having looked at the SERP for these keywords. Checking showed two direct competitors I did not know about:
>
> - **`costbycity.com`** — "Cost of Living Across 387 US Metros. BEA Regional Price Parities and ACS household data". **Exactly the same concept and exactly the same data source we chose.** Position 10 for `cost of living by city`.
> - **`realtakehomepay.com`** — "Compare Job Offers by Take-Home Pay (All 50 States)". It has the tax + comparison angle.
>
> **This is not bad news, but it narrows the claim:** our data choice was independently validated by another site (a good sign), and the fact that both are small sites that rank means this space is penetrable for a niche site. But we are not "the first to do this" — our differentiation is the **intersection** of the two, not either one alone. And neither of them has filled that intersection yet.

### 2-3. Roadmap

Every stage answers the core sentence. The order runs from "what does it cost" to "what do I keep", because that is the user's natural funnel.

| Stage | Content | Role in the funnel |
|---|---|---|
| **1 — Place** | cost-of-living calculator · comparison · 5 sample cities → 25–30 | Funnel entrance, highest volume |
| **2 — Income** | salary converter · salary↔hourly · take-home pay | "What do I need / what do I keep" |
| **3 — Tax by place** | state income tax (51 jurisdictions, engine ready) · sales tax · paycheck · withholding | **The moat** — the cluster's highest CPC |
| **4 — International** | country income tax · country-level European cost of living | An extension of the same funnel |
| **5 — Settling** | house payment · closing cost in a city | The end of the funnel |
| **Second cluster** | Freelancer tools | Only after the core is established |

**Two ordering rules:**

1. **No tool ships before the tools of the stage above it.** The funnel does not work without its early links; a take-home page without a cost-of-living page is just one more calculator.
2. **City pages expand through a gate** — 5 samples, then 25–30. Never all at once.

> **The December deadline was removed.** That deadline came from tax seasonality (up to 46×). The place cluster is close to seasonless, so the project is no longer "December or nothing". Tax season still gives a spike, but the project's failure is no longer tied to it.

---

### 2-4. Cost of living — data and page shapes (now the core, not stage 2.5)

> This cluster went from "rejected" to **the core of the project**. Its path is recorded in sections 19-5 and 19-7.

**I underestimated this cluster three times, and all three were my error:** first I rejected it without measuring; then I measured the wrong keyword (3,600, a long tail); then only the head term (60,500) without the cluster. The real cluster figure is **158,000 searches a month**.

| Keyword | Volume | CPC |
|---|---|---|
| cost of living calculator | 60,500 | $1.65 |
| **cost of living comparison** | **49,500** | $0.97 |
| ~30 major US cities | ~45,000 | $0.89–8.85 |

#### 2-4-1. A structural finding: the demand is in the tool, not in the pair page

| | Volume |
|---|---|
| `cost of living comparison` (the tool itself) | **49,500** |
| `cost of living in austin vs dallas` | 260 |
| `cost of living in san antonio vs dallas` | 40 |

49,500 people want a tool where they pick the two places themselves; only 260 are after one specific pair. This confirms the anti-cartesian rule (section 6-7) and also says what to build instead.

#### 2-4-2. The right shape

| Path | Target | Count |
|---|---|---|
| `/tools/cost-of-living-calculator` | 60,500 | 1 |
| `/tools/cost-of-living-comparison` | **49,500** | 1 |
| `/cost-of-living/{us-city}` | 1,300–3,600 each | **25–30** |
| `/cost-of-living/{eu-country}` | Country level for Europe | Next phase |
| City-pair pages | — | **Zero** |

**Why cities for the US and countries for Europe:** because the official data is published at exactly those levels — BEA at the US metropolitan level, Eurostat at the European country level.

#### 2-4-3. Data — free official sources, better than Numbeo

| Layer | Source |
|---|---|
| US regional price index | **BEA Regional Price Parities** (state and metro) |
| Rent | **HUD Fair Market Rent** (county level) |
| Consumer items | **BLS regional CPI** |
| Europe | **Eurostat comparative price levels** |

The data problem previously marked "unsolved" is in fact solvable with free government sources. The `eurostat`, `censusdata` and `cpi` packages exist on PyPI; `.gov` domains are blocked only inside this sandbox, which is an **environment** limitation, not a project one.

> **This is better than Numbeo, not worse.** Official government data that we link to is the same E-E-A-T story we built for tax — and precisely what Numbeo cannot offer. The `/methodology` page becomes a competitive advantage here too.

#### 2-4-4. Why these pages beat the state tax pages

| | State tax | City cost of living |
|---|---|---|
| Best page | California 210 | Austin 3,600 |
| Median page | ~40 | ~1,500 |
| Ratio | — | **10 to 17 times better** |

**Hard rule:** the same gate discipline. First **5 sample cities**; if they get indexed and take impressions, expand to 25–30. Never all at once.

---

## 3. Architecture and technical stack

### 3-1. The stack

| Layer | Choice | Note |
|---|---|---|
| Framework | **Next.js (App Router)** with `output: "export"` | A complete static HTML file for every page |
| Route generation | `generateStaticParams` | The 51 state pages are built at build time |
| Metadata | `generateMetadata` (server side) | title/description/canonical/OG inside the initial HTML, not after hydration |
| Styling | Tailwind CSS | |
| Components | shadcn/ui + lucide-react (the only icon set) | |
| Calculation | Pure TypeScript, client side | No backend, no API calls |
| Hosting | Cloudflare Pages or Vercel | Both serve a static export for free |
| Testing | Vitest for the tax engine | Section 4-7 is mandatory |

### 3-2. Why this change was critical

The earlier spec said "Static-First" and "React + react-router-dom" at the same time. Those two do not go together: react-router builds a client-side SPA whose initial HTML is effectively empty, with all content constructed after JS runs. Google does render JavaScript, but rendering happens in a separate queue, and for a new domain with no authority and dozens of pages that means slow or partial indexation.

With `output: "export"` every page is a real HTML file carrying all its content, metadata and JSON-LD from the first byte. The calculator becomes interactive after hydration, but **the content never depends on JS**.

**Hard rule:** no indexable text may be produced only after JS runs. If `curl` on a page does not show the content, that page has a bug.

### 3-3. Directory structure

`✅` = exists · `⬜` = not yet

```
scripts/                       ✅ data tooling (Python, outside the bundle)
  extract_tax_data.py          ✅ rebuild the dataset from the source package
  estimated_tax.py             ✅ derive the quarterly schedule from statute
  validate_tax_data.py         ✅ structural validation for CI

src/
  data/tax-year-2026/          ✅
    federal.json               ✅  meta.json  ✅  estimated.json ✅
    states/{slug}.json         ✅ 51 files

  lib/tax/                     ✅ the engine — the only home of tax logic
    money.ts brackets.ts       ✅
    selfEmployment.ts qbi.ts   ✅
    state.ts estimated.ts      ✅
    index.ts                   ✅ orchestrator, the only public entry point
    load.ts                    ✅ JSON loading, kept separate so the engine stays pure
    __tests__/engine.test.ts   ✅ 59 tests

  app/                         ⬜
    layout.tsx  page.tsx
    tools/{tool-slug}/page.tsx
    cost-of-living/page.tsx
    cost-of-living/[place]/page.tsx
    state-taxes/page.tsx
    state-taxes/[state]/page.tsx
    guides/[slug]/page.tsx
    about|methodology|sources|privacy|terms|contact|editorial-policy/
    sitemap.ts  robots.ts
  components/                  ⬜
```

### 3-4. Fixed technical rules

1. **Single source of truth:** no tax calculation is written outside `src/lib/tax/`. Components only take inputs and render outputs.
2. **Data separate from logic:** rates and thresholds live in JSON, not in code. Changing tax year must not require changing logic.
3. **Tax year is a parameter:** every function takes `taxYear`. No year is ever hardcoded.
4. **Everything in integer cents:** internal calculation runs on integer cents so floating-point error cannot accumulate; conversion to dollars happens only at the display layer.
5. **No runtime network dependency:** no fetch in the browser.

---

## 4. The tax engine — the heart of the project

> **Status: built.** `src/lib/tax/` · 59 tests green · typecheck clean.
> This section is no longer design; it describes what exists. If the code and this section disagree, **the code is authoritative** and this section must be corrected.

What separates us from hundreds of low-quality calculators is here and only here.

### 4-1. Why `FEDERAL_INCOME_RATE = 14` was removed

The first spec computed federal tax with an invented flat 14% rate. Three problems: it was wrong at the foundation (federal tax is progressive), it was lethal in a YMYL niche (our user genuinely has to set this money aside), and it was exactly the mistake competitors make. Implementing it properly was one day's work and the data is free — the cheapest competitive advantage available.

### 4-2. Modules

| File | Responsibility |
|---|---|
| `money.ts` | Arithmetic on **integer cents**. Percentages stack six deep in this engine; floating point makes the bracket-by-bracket table disagree with the total it is meant to explain |
| `brackets.ts` | Apply the bracket table + produce per-bracket detail + the marginal rate |
| `selfEmployment.ts` | SE tax per 26 U.S.C. 1401 and 1402 |
| `qbi.ts` | The 199A deduction with phase-in |
| `state.ts` | State engine + surtax |
| `estimated.ts` | Quarterly payments and safe harbor per 6654 |
| `index.ts` | Orchestrator — **the only public entry point** |
| `load.ts` | JSON loading. Deliberately separate so the engine stays pure and runs without a filesystem in the browser and in tests |

### 4-3. Order of calculation

The order matters more than anything else, and it is what most calculators get wrong:

```
1.  netProfit        = businessIncome − businessExpenses
2.  nese             = netProfit × 0.9235            // 1402(a)(12)
3.  if nese < 400    → no SE tax at all               // 1402(b)(2)
4.  socialSecurity   = min(nese, wageBase − w2SsWages) × 12.4%
5.  medicare         = nese × 2.9%                    // no cap
6.  addlMedicare     = max(0, w2Wages + nese − threshold) × 0.9%
7.  seTaxDeduction   = (socialSecurity + medicare) × 50%   // 164(f) — excludes addlMedicare
8.  agi              = netProfit + w2Wages + otherIncome − seTaxDeduction
                       − retirement − seHealthInsurance − hsa
9.  taxableBeforeQbi = max(0, agi − max(standardDeduction, itemized))
10. qbiDeduction     = per 4-5
11. taxableIncome    = max(0, taxableBeforeQbi − qbiDeduction)
12. federalTax       = apply brackets
13. stateTax         = state engine + surtax
14. totalTax         = seTax + addlMedicare + federalTax + stateTax
```

### 4-4. Three details implemented deliberately correctly

Each has a test that goes red if it regresses:

| # | Detail | Why it matters |
|---|---|---|
| 1 | **The Social Security cap is shared with W-2 wages** | An employee with freelance work on the side must not pay twice against one cap. Ignoring this overestimates exactly a large slice of our audience |
| 2 | **Additional Medicare is excluded from the deductible half** | Section 164(f) covers only 1401(a) and (b), not 1401(b)(2) |
| 3 | **The 0.9235 factor and the $400 floor** | SE tax is not on total profit, and below the floor it does not exist at all |

### 4-5. The QBI deduction — where we do not give a definite number

- **Below the threshold:** `min(20% × qbi, 20% × taxableBeforeQbi)` — a definite number
- **Inside the phase-in range:** the W-2 wage limitation enters gradually
- **Above the range:** an SSTB goes to zero; a non-SSTB is limited to 50% of W-2 wages paid — which is zero for a solo freelancer

Above the threshold the engine returns a **range** and sets `deduction` to the conservative end, plus a warning. That overestimates tax — the safe direction for someone trying to learn how much to set aside.

The phase-in range ($50k single / $100k joint) is a statutory constant and, unlike the threshold itself, is not inflation-indexed.

### 4-6. The state engine

It starts from **federal AGI**, subtracts the state standard deduction, applies the bracket table or flat rate, and adds any surtax.

It is deliberately simple. States differ at the starting point — some start from federal taxable income, some disallow the SE tax deduction, most disallow QBI — and the current dataset does not carry those conformity rules. **Rather than modelling them halfway and being quietly wrong, the engine says so explicitly in `notes`.**

### 4-7. Testing — done

59 tests. The main scenario is hand-computed from statute and asserted to the cent ($80k profit, single, no state tax → $16,647.46), with the step-by-step working in a test comment so a human can review it.

Coverage: zero income · a loss · the $400 floor · the wage base cap · the Additional Medicare threshold · all four filing statuses · flat, progressive and no-tax states · the California surtax · phase-in and SSTB · safe harbor selection and the 110% rule · instalment splitting · **and every one of the 51 jurisdictions loads and computes**.

Invariants: the bracket table sums to the federal tax · the components sum to the total · income − tax = take-home · monotonically increasing · tax never exceeds income.

### 4-8. What the engine does **not** model — stated explicitly

Being honest about the edge of accuracy is itself an E-E-A-T signal. A calculator that says "I do not know this part" is more trustworthy than one that always produces a confident number.

| Limitation | Status | Plan |
|---|---|---|
| Employee FICA is not withheld on W-2 wages | ⚠️ warning | **A prerequisite for stage 1.5** — the take-home pay calculator is not built without it |
| State conformity rules | ⚠️ note | Requires 7 new fields in the state dataset |
| Local tax (NYC, Philadelphia, Ohio…) | ⚠️ note in 9 states | Not computed, only warned — a content opportunity competitors lack |
| AMT | Not modelled | Rare for the target audience |
| Capital gains | Not modelled | No input for it; it also affects the QBI cap |
| Loss limitation rules | Not modelled | A warning is emitted |
| Farmers and fishermen (6654(i)) | Not modelled | They have a different quarterly schedule |
| Tax credits (CTC, EITC…) | Not modelled | Outside the scope of a freelancer tool |

**Rule:** every new limitation appears either in `warnings` or in `state.notes`. Never silently.

### 4-9. The cost-of-living engine — stage 2.5

It is a second engine, separate from the tax engine. They share nothing but `money.ts`.

#### 4-9-1. The foundational decision: we publish indices, not invented dollars

The original spec's dataset stored a dollar amount per category per city — and that is exactly where the insurance column got filled with unreal numbers (section 5-3).

Our official sources publish **indices**, not dollar baskets: BEA Regional Price Parities give a number relative to the national average. So the correct model is:

```
input:  the user's own actual costs at the origin
output: those same costs at the destination, scaled by the official index ratio
```

**We invent no dollar amount for any city.** The dollars come from the user's own numbers; we only apply the official ratio. This removes the "fabricated column" problem at the root, is citable, and is more accurate — because every user's spending basket differs.

For a user who does not have their own numbers, a default is shown from HUD FMR (rent) and BLS CPI (the rest), **explicitly labelled "a regional estimate, not your cost"**.

#### 4-9-2. Calculations

```
category scaling:
  targetCost[c] = sourceCost[c] × (targetIndex[c] / sourceIndex[c])

salary equivalence:
  equivalentSalary = currentSalary × (targetAllItems / sourceAllItems)

difference:
  difference = targetTotal − sourceTotal
  percentDiff = (targetTotal / sourceTotal − 1) × 100
```

`c` covers only the categories for which an official source publishes a separate index — BEA separates rent, goods and services. **A category with no official index is not created.**

#### 4-9-3. What this engine does not model

| Limitation | Why |
|---|---|
| ~~Tax is not included in the comparison~~ | **Corrected.** A cross-link is not enough: a comparison that ignores tax is exactly what competitors give. Section 4-9-5 |
| Health insurance | No reliable official index at metro level. **The column is not created** (rule 5-3) |
| Comparing the US with Europe | BEA and Eurostat use different bases; combining them is meaningless. Comparison stays **within a region** |
| Currency conversion | Cross-country European comparison stays in euros |

As with the tax engine, every limitation appears in `warnings`, never silently.

#### 4-9-5. The comparison **must** include tax — this is the moat itself

The first version of this engine left tax out of the comparison and settled for a "cross-link". **That was wrong.** A comparison that sees only cost is what Numbeo gives; the user has to add two numbers from two sites themselves.

```
full comparison output:
  cost difference     = destination cost − origin cost        (BEA index)
  tax difference      = origin net − destination net          (tax engine)
  ─────────────────────────────────────────────
  real annual difference = tax difference − cost difference
```

**Computed with the existing engine** ($95,000, single, 2026): Seattle and Portland have similar cost of living, but their annual net differs by **$7,167** — 7.5% of gross income, from state tax alone. No cost-of-living tool shows this.

It is the only output on the site that is quotable in one sentence and attracts links (section 9-5-2).

#### 4-9-6. Household size

The calculator must be adjustable for a single person, a couple and a family.

**Hard rule:** invented multipliers are forbidden. The first version of the spec had `{single:1, couple:1.6, family:2.2}` with no source behind it. Instead:

- **Rent** comes from HUD FMR by bedroom count — real data, not a multiplier
- **Food and goods** from the BLS Consumer Expenditure household-size tables
- **A category with no household data gets no multiplier** and is labelled "independent of household size" in the UI

#### 4-9-7. Social contributions — a requirement of the international section

For European countries, payroll deductions are not only income tax: social insurance, health and mandatory pension are **larger than income tax itself** in some countries. A calculator showing only tax understates the number badly.

```
Country (new fields)
  socialContributions: [ { name, rate, base, cap, employeeShare } ]
  effectiveDeductionRange: [min, max]
```

**Rule:** as with international tax, we give a **range** here rather than a definite figure, because it depends on residency status and contract type — with an explicit warning.

#### 4-9-4. Testing

The same discipline as section 4-7: a golden scenario with hand calculation · symmetry (`A→B` and `B→A` must be inverses) · identity (`A→A` must change nothing) · every city in the dataset loads and computes.

---

## 5. The data layer and data-validity rules

### 5-1. The source rule

**Every number on this site must have a linkable primary source.** Without exception.

| Data type | Allowed source | Disallowed source |
|---|---|---|
| Federal brackets and thresholds | The annual IRS Revenue Procedure, official forms and instructions | Blogs, secondary summaries |
| SE tax rates and the Social Security cap | IRS Schedule SE + the annual SSA announcement | — |
| Quarterly payment dates | Form 1040-ES and the IRS calendar | — |
| State tax | That state's revenue department | Tax Foundation as a **cross-check**, not as the primary source |
| Rent (phase 2) | HUD Fair Market Rent, public Zillow data | Numbeo |
| Food/goods cost (phase 2) | BLS Consumer Expenditure Survey and CPI | Numbeo |

### 5-2. The data metadata file

`src/data/tax-year-2026/meta.json`:

```jsonc
{
  "taxYear": 2026,
  "lastUpdated": "2026-09-01",
  "nextReviewDue": "2027-01-15",
  "federalSources": [ { "label": "...", "url": "...", "retrieved": "..." } ],
  "changelog": [ { "date": "2026-09-01", "change": "initial version" } ]
}
```

This metadata is displayed directly in three places: the disclaimer box on every page, the `/sources` page, and `dateModified` in the JSON-LD. No date is ever written by hand in the copy.

### 5-3. Data consistency rules (learned from the previous dataset's errors)

The previous spec's city dataset had three structural faults that must not recur:

1. **No derived value is ever stored.** In the old dataset both `index` and the column totals were stored, and they disagreed — Dallas and Nashville both had `index = 105` but their totals were 2,870 and 3,130 (a 9% gap). Any value computable from the others **must be computed at runtime, not stored**.
2. **Every column has one written, consistent definition.** In the old dataset the transport column was 132 for New York (a monthly transit pass) and 250 for Los Angeles (apparently car costs) — two different methodologies in one column. Every field has a precise definition in `/methodology` and every row follows it.
3. **Suspiciously uniform values are a red flag.** The insurance column was between $195 and $215 across all 24 cities. Our audience is US freelancers who buy their own health insurance and know its real cost exactly — an unreal number in that column destroys the credibility of the whole table. **If we do not have real data, we drop the column; we do not invent a substitute number.**

### 5-4. The data validation script

A script that runs in CI and breaks the build if:
- a state has an empty `sources`
- `lastVerified` is older than 12 months
- brackets are unsorted or overlap
- a state with `structure: "progressive"` has fewer than two brackets
- the golden-scenario checksums have changed

### 5-5. The cost-of-living dataset

#### Allowed sources

| Layer | Primary source | Level |
|---|---|---|
| Overall price index | **BEA Regional Price Parities** | US state and metro |
| Rent | **HUD Fair Market Rent** | US county |
| Goods and services | **BLS regional CPI** | US region |
| Europe | **Eurostat comparative price levels** | Country |

**Numbeo remains disallowed** — not only because of its terms, but because non-citable data neutralises the entire E-E-A-T story we built for tax.

#### Data model

```jsonc
// src/data/cost-of-living-{year}/us/{metro-slug}.json
{
  "slug": "austin-tx", "name": "Austin, TX",
  "type": "metro",           // "metro" | "state" | "country"
  "indices": {
    "allItems": 0.0,         // 100 = national average
    "rent": 0.0,
    "goods": 0.0,
    "otherServices": 0.0
  },
  "referenceRent": { "bedrooms1": 0, "bedrooms2": 0 },  // HUD FMR
  "stateSlug": "texas",      // for the cross-link to the tax calculator
  "sources": [ { "label": "...", "url": "...", "retrieved": "..." } ],
  "lastVerified": "", "verification": "pending"
}
```

**The rules in section 5-3 apply without exception:** no derived value is stored · every field has a written definition · **a category with no official index is dropped, not filled with a substitute number**.

`scripts/validate_tax_data.py` needs a cost-of-living equivalent: indices positive, sources non-empty, `lastVerified` under 18 months (BEA publishes annually).

---

## 6. Pages and programmatic architecture

> **Revised 2026-08-29 against real data.** The full list, with each keyword's search volume and the reasoning behind each decision, is in **[`docs/keyword-research.md`](keyword-research.md)**. That document is the basis for this section; where they conflict, it wins, because it has the data.

Phase 1 total: **39 pages** (not the 75 initially estimated). Exact count in section 6-0.

> 📊 **The full data-driven tool catalogue: [`tool-catalogue.md`](tool-catalogue.md)** — 36 tools measured, 3.7 million monthly searches, ranked by "market value = volume × CPC" alongside build cost. That document decides **which tool comes next**; this section only covers phase 1.

### 6-0. Core inventory

| Stage | Pages | Count |
|---|---|---|
| 1 — Place | cost-of-living-calculator · cost-of-living-comparison · city pages | 2 + (5 → 30) |
| 2 — Income | salary-converter · salary-to-hourly · take-home-pay-calculator | 3 |
| 3 — Tax by place | state pages + directory · sales-tax · paycheck-tax · tax-withholding | 3 + (8 → 51) |
| 4 — International | income-tax-calculator · European country pages | 1 + later |
| 5 — Settling | house-payment · closing-cost | 2 |
| Guides | Around the funnel, not freelancer tax | 9 |
| Trust pages | About · Methodology · Sources · Editorial · Privacy · Terms · Contact | 7 |
| Home + tool index | | 2 |
| **First-release total** | | **~42** |
| Behind gates | City pages 5→30 · state pages 8→51 | up to ~110 |

**The guides changed too.** They used to be about freelancer tax (deductions, home office, S-Corp). Now they follow the funnel: "what salary do you need to live in X" · "which states have no income tax" · "how sales tax changes the cost of living" · "what gets left out of a cost-of-living calculation".

### 6-1. Pages by funnel stage

Every page belongs to one of the five funnel stages. A page belonging to no stage **is not built** — that is the simplest test of the context boundary.

#### Stage 1 — Place

| Path | Target keyword | Volume |
|---|---|---|
| `/tools/cost-of-living-calculator` | cost of living calculator | 60,500 |
| `/cost-of-living/{metro}` | "cost of living in X" | 1,300–3,600 each |
| `/cost-of-living` | Directory | — |

#### Stage 2 — Comparison

| Path | Target keyword | Volume |
|---|---|---|
| `/tools/cost-of-living-comparison` | cost of living comparison | 49,500 |

#### Stage 3 — Income

| Path | Target keyword | Volume |
|---|---|---|
| `/tools/salary-to-hourly-calculator` | salary ↔ hourly | 99,000 |
| `/tools/salary-converter` | salary comparison by city | ~8,000 |

#### Stage 4 — What you keep *(the moat)*

| Path | Target keyword | Volume | CPC |
|---|---|---|---|
| `/tools/sales-tax-calculator` | sales tax calculator | 110,000 | **$6.91** |
| `/tools/property-tax-calculator` | property tax calculator | 22,200 | $3.37 |
| `/tools/income-tax-calculator` | income tax calculator | 90,500 | $2.13 |
| `/tools/take-home-pay-calculator` | take home pay calculator | 60,500 | **$5.69** |
| `/tools/paycheck-tax-calculator` | paycheck tax calculator | 18,100 | $4.48 |
| `/tools/tax-withholding-calculator` | tax withholding calculator | 14,800 | **$5.78** |
| `/state-taxes/{state}` · `/state-taxes` | State tax | Low, but it closes the funnel | |

**This stage carries the cluster's highest CPC and its tax engine is already built.** That is why the whole identity revision did not waste the engine.

#### Job offer comparison — a **mode**, not a page

"$120,000 in San Francisco or $95,000 in Austin?" is a valuable question, and it collapses the entire funnel into one answer.

**But `job offer comparison calculator` gets only 30 searches a month.** Under the rule in section 18-1, no page is built for an unproven target — even when the idea is appealing. So it becomes a **second mode inside the comparison tool** (which has 49,500 searches):

| Mode | Input |
|---|---|
| Place comparison | One income, two places |
| **Offer comparison** | Two incomes, two places |

The capability is kept, the trafficless page is not built. This is exactly the discipline the `audit_seo.py` auditor enforces.

#### Stage 5 — Settling

| Path | Target keyword | Volume | CPC |
|---|---|---|---|
| `/tools/closing-cost-calculator` | closing cost calculator | 40,500 | **$6.18** |
| `/tools/house-payment-calculator` | house payment calculator | 33,100 | $2.29 |

### 6-2. Guides (9 pages)

Around the funnel, not around freelancer tax. Each guide deepens one link of the funnel and links to that link's tool:

What salary you need to live in {city} · which states have no income tax (and what replaces it) · how sales tax changes the real cost of living · what gets left out of a cost-of-living calculation · what the BEA indices mean · the real cost of moving between states · net versus gross pay · comparing a job offer between two cities · local tax, the thing most calculators ignore.

### 6-3. Trust pages (7 pages) — **built before the content**

| Page | The critical point |
|---|---|
| `/about` | A **real** introduction with a name and background. A vague About page in a YMYL niche is the most common reason for AdSense rejection |
| `/methodology` | The engines + BEA, HUD and IRS sources, in the user's language |
| `/sources` | The complete list of primary sources with links and retrieval dates |
| `/editorial-policy` | The review process, data updates, and **disclosure of machine assistance** |
| `/privacy` | AdSense cookie disclosure · GDPR/CCPA · "calculations stay client-side" |
| `/terms` | |
| `/contact` | A real, answered contact route |

### 6-4. The second cluster — not published until the core is established

`self-employment-tax-calculator` · `estimated-tax-calculator` · `1099-tax-calculator` · freelancer tax guides.

Their engine is built and tested, but they do not answer the core sentence. **Publication criterion:** after the core clears gate 2 and the stage 4 pages rank — that is, once topical authority for "a place and its tax" is established and adding an adjacent cluster will not dilute it.

### 6-5. Pair comparison pages — zero

`cost of living comparison` has 49,500 searches; the best city pair (`austin vs dallas`) has 260 and most pairs are under 100. **The demand is in the tool, not the pair page.** Our 30 metros produce 435 pairs, and the next phase's 100 metros produce 4,950 — exactly the cartesian trap the first version of this spec fell into.

### 6-6. The goal: being cited in AI Overviews

For this cluster's keywords, the AI Overview sits above the organic results and compresses click-through — the revenue model applies a 30% penalty for it.

But it opens another route: **being cited inside it.** On the tax keyword we checked, the AI Overview cites `taxstra.com` — a small niche site, above TaxAct and QuickBooks. The structure that earns a citation is a step-by-step definition with concrete numbers — exactly what our engines output.

**So on every tool page, the "how it is calculated" section is a design goal, not decoration** (section 8-8).

### 6-7. URL and slug rules

URLs do not change after indexation. One mistake here means a permanent redirect and lost authority.

```
/tools/{tool-slug}                        standalone tool
/state-taxes                              state directory
/state-taxes/{state-slug}                 state page
/guides/{guide-slug}                      guide
/cost-of-living/{metro-slug}              city page (stage 2.5)
/about · /methodology · /sources · ...    trust pages
```

**Hard rules:**

1. **The slug is the target keyword, not a brand name.** `/tools/estimated-tax-calculator`, not `/tools/quarterly`. Slugs come from the validated keyword list.
2. **Never a year in the URL.** `/tools/self-employment-tax-calculator` stays and its content updates annually. A `/2026/` in the path means restarting the page's authority from zero every January.
3. **No extension, no `index.html`, always no trailing slash**, one consistent form site-wide.
4. **Result-sharing parameters never create a new page** — `canonical` always points at the parameter-free version.
5. **State slugs come from the dataset**, not by hand — `california`, `washington-dc`. Single source of truth.
6. **A slug change means a permanent 301** that is never removed, plus a row in `docs/redirects.md`.

### 6-8. Programmatic architecture

~110 pages are generated from **5 templates**. That is the correct definition of programmatic: few templates, many entities, and explicit rules about which entity earns a page.

#### 6-10-1. The entity model

```
Place (the shared abstraction — the funnel entrance)
├── Metro   id: metro-{cbsa}   ← BEA RPP + HUD FMR       ~30 pages
└── Country id: country-{iso2} ← Eurostat CPL             next phase

Jurisdiction (the "what you keep" stage)
└── State   id: state-{abbr}   ← the existing tax dataset  51 pages

relations:
  Metro ──belongsTo──> State        (mandatory, the basis of cross-linking)
  Metro ──similarTo──> Metro[4]     (by index distance, not alphabetically)
  Country ──similarTo──> Country[4]
```

**Rule:** `Place` is a real abstraction in the code, not only in the document. `MetroPage` and `CountryPage` share one template with a data adapter — otherwise adding Europe builds two parallel trees that diverge.

#### 6-10-2. Template inventory

| Template | Path | Entity | Count |
|---|---|---|---|
| `PlacePage` | `/cost-of-living/{slug}` | Metro · Country | 30 → 100+ |
| `StateTaxPage` | `/state-taxes/{state}` | State | 51 |
| `ToolPage` | `/tools/{slug}` | — (manual) | ~12 |
| `DirectoryPage` | `/cost-of-living` · `/state-taxes` | Collection | 2 |
| `GuidePage` | `/guides/{slug}` | — (manual) | 9 |

**5 templates, ~110 pages.** If a sixth template is ever needed, first ask why the new entity does not fit inside `Place`.

#### 6-10-3. The generation gate — which entity earns a page

This is what prevents repeating the 12,720-page mistake. **A page is not auto-generated per entity; the entity has to qualify.**

| Entity | Entry condition |
|---|---|
| **Metro** | Head keyword volume **≥ 500/month** (measured, not guessed) **and** BEA publishes an RPP for it **and** HUD has its rent |
| **State** | All 51 jurisdictions — the dataset is complete and it closes the funnel. The only exception to the volume rule, justified by structural role rather than traffic |
| **Country** | Covered by Eurostat **and** volume **≥ 300/month** |
| **Place pair** | **Never.** The demand is in the tool, not the pair page (section 2-4-1) |

An entity that fails the condition **stays in the dataset and works in the calculator, but gets no dedicated page.** That separation — data versus page — is the lesson learned for states in section 6-5.

#### 6-10-4. The uniqueness budget — a quantitative anti-doorway requirement

Section 7-1 says every page must be unique. Here it gets a number:

| Metric | Minimum |
|---|---|
| Entity-specific unique text | **≥ 40% of body words** |
| Entity-specific facts from a primary source | **≥ 3** |
| FAQ questions with a computed number for that entity | **≥ 3** |
| Boilerplate shared across the template | **≤ 35%** |

> ⚠️ **Calculator output counts as unique but is not sufficient.** A computed number does differentiate, but a page that is only a table and a number is a doorway page. At least one written section specific to that place is required.

The content validation script measures these ratios before the build and breaks the build below threshold — the same pattern as `validate_tax_data.py`.

#### 6-10-5. The internal link graph

Random "related pages" links are worth little. The graph follows the funnel path:

| From | To | Why |
|---|---|---|
| `PlacePage` | `StateTaxPage` for its state | Funnel link: place → what you keep |
| `PlacePage` | The comparison tool prefilled with that place | Funnel link: place → comparison |
| `PlacePage` | 4 places with the **nearest index** | Genuinely related, not alphabetical |
| `StateTaxPage` | The metros in that state | The funnel in reverse |
| `ToolPage` | The next and previous stage's tool | The funnel chain |
| `DirectoryPage` | Every entity in the collection | Discovery and crawl |

**Ceiling: 25 internal links per page.** Beyond that, each link's value is diluted and the page starts to look like a generated link grid.

**The "4 places with the nearest index" rule** is deliberate: a user looking at Austin is interested in cities with a similar cost, not in a city that starts with the same letter. It is both better UX and a genuine topical relevance signal.

#### 6-10-6. Sitemap segmentation — to read indexation per template

```
/sitemap.xml            (index)
├── /sitemaps/tools.xml
├── /sitemaps/places.xml
├── /sitemaps/states.xml
└── /sitemaps/guides.xml
```

**Why segment:** if all 110 pages sit in one sitemap, Search Console only says "60% indexed" and you cannot tell which template failed. Segmented, gate 1 becomes an actionable number: "90% of tools indexed, 20% of city pages" means the problem is in the `PlacePage` template, not in the site.

#### 6-10-7. Scaling gates

| Stage | Pages | Condition to advance |
|---|---|---|
| Sample | 5 major metros | ≥ 4 of 5 indexed + impressions after 3–4 weeks |
| Expansion 1 | Top 30 metros | Median position better than 30 and trending up |
| Expansion 2 | 100+ qualifying metros | The collection's organic traffic rising, with no site-wide decline |

**At no stage is everything published at once.** Batch publication is at most 10 pages a week — a more natural signal, and if something is wrong it surfaces before 100 pages exist.

---

## 7. Content requirements and E-E-A-T

### 7-1. Why this section matters more than every technical section

Google's spam policy has explicitly targeted "scaled content abuse" since 2024: mass-producing pages built mainly to rank, with no independent value. The criterion is **intent and value**, not whether a human or a machine wrote it. Fifty-one pages differing only in a state name and a number are exactly that.

There is one way through: **every page must contain something true only of that state.**

### 7-2. The structure of a state page (900–1,400 words)

| Section | Words | What makes it unique |
|---|---|---|
| 1. Introduction | 100–150 | That state's tax situation in one sentence |
| 2. Calculator | — | With the state preselected |
| 3. Bracket-by-bracket table | — | **Computed output, effectively unique per state** |
| 4. "How state tax works in {state}" | 250–350 | Bracket structure, standard deduction, whether it allows the SE tax deduction |
| 5. "Local tax" | 100–200 | Only for states that have it — a genuine differentiator |
| 6. "Filing and deadlines in {state}" | 150–250 | The state tax authority, state quarterly payments, specific deadlines |
| 7. "Which freelancer this makes sense for" | 200–300 | Real analysis, not filler |
| 8. FAQ (5 questions) | 200–300 | With computed numbers for that state |
| 9. Disclaimer box | — | With an automatic date from `meta.json` |

### 7-2-1. Tool page brief (600–900 words)

Tool pages are shorter than state pages — the user came for a calculator, not an article. But "short" means dense, not thin.

| Section | Words | Note |
|---|---|---|
| Introduction | 80–120 | What question this tool answers |
| **"How it is calculated"** | 200–300 | Step by step with numbers. **The AI Overview citation target** (section 6-8) |
| "What it does not include" | 100–150 | From the engine's `warnings`. Honesty = trust |
| "Who needs this" | 150–200 | A real scenario, not filler |
| FAQ (4–5 questions) | 150–250 | From People Also Ask for that keyword |

### 7-2-2. Guide brief (1,500–2,500 words)

Guides are the backbone of topical authority and the main recipient of external links. Depth matters here.

- **At least one complete worked example** computed by our own engine — not a hypothetical number
- **Links to at least two of our tools** in the body, where the user actually needs them
- **At least three primary-source references** (IRS, statute, a revenue department)
- A table or scannable list — a wall-of-text guide does not get read
- A "common mistake" or "when this rule does not apply" section — the part competitors do not write

### 7-2-3. Cost-of-living city page brief (700–1,000 words)

| Section | Note |
|---|---|
| Introduction | The city's position relative to the national average, with the number |
| Calculator | With the city preselected |
| "What the indices mean" | Interpreting the BEA number in the user's language |
| **"This state's tax"** | A paragraph + a link to the state calculator. **The advantage no competitor has** |
| "Who this suits" | Real analysis |
| Methodology and disclaimer | With BEA and HUD links |

**Rule:** "the index is official" is not an excuse for a thin page. If the page is only an index table, it is the doorway page section 7-1 forbids.

### 7-3. Content production — be realistic

51 pages × ~1,200 words ≈ **61,000 words**, plus 10 guides × ~2,000 ≈ 20,000 words. Roughly **80,000 words of precise tax-domain writing**.

- Written entirely by hand, that is several full-time months. With machine drafting + human review and enrichment, it is feasible.
- **Rule:** no page ships without human review and without adding at least one state-specific fact pulled from a primary source.
- Sections 4, 5 and 6 (tax structure, local tax, deadlines) must be pulled from that state's revenue department site. That work alone turns the page from "a filled-in template" into "a reference".

### 7-4. E-E-A-T signals that are mandatory in a finance niche

- [ ] A named author with a profile page and relevant background
- [ ] Publication date **and** last-reviewed date on every page
- [ ] Outbound links to primary sources (IRS and the states) — linking to authority builds credibility, it does not leak it
- [ ] A consistent disclaimer: "this tool is not a substitute for professional tax advice"
- [ ] A real contact route
- [ ] `Person` and `Organization` in the JSON-LD

### 7-5. Scheduling and updates

Tax changes annually. Fifty-one pages carrying expired data are worse than having no pages.

- Every January: update all brackets and thresholds
- This must be accounted for in the timeline and in time capacity, not come as a surprise
- Until the new year's data is verified, pages must state the reference tax year explicitly

---

### 7-6. Tone and style

~35,000 words of content, likely machine-drafted. Without a tone guide the pages become inconsistent, and inconsistency in a finance niche reads as carelessness.

- **Second person, active voice, simple present.** "you owe", not "one would be liable"
- **The number before the explanation.** Answer first, reasoning second
- **No intensifiers**: "very", "extremely", "incredibly" are cut
- **No certainty we do not have**: "this may", not "this will" — in a YMYL niche that is both legally sound and honest
- **A tax term is defined at first use**, then used freely
- Target readability: around ninth grade. Our audience is not an accountant
- **No "we are the best" claims.** The correct number is the argument
- **Disclosure of machine assistance** in `/editorial-policy`: machine drafting, human review and fact-checking. Hiding it is a trust risk; stating it is not

---

## 8. UI/UX

The previous UI/UX document was the best of the set and most of it is kept verbatim. Changes appear only where it no longer fits the new phase 1 scope.

### 8-1. Golden rules (unchanged)

1. Main navigation is only **2 levels**. The state layer is never in the menu — only search and the directory.
2. **Global search** instead of a megamenu. `GlobalSearch` in the header of every page, with fuzzy matching (typing "califrnia" must find California).
3. **One single template** for all 51 programmatic pages.
4. **The calculator is always above the fold on mobile.**
5. Tables become cards on mobile (`ResponsiveTable`), never horizontal scroll.
6. The directory is always grouped.
7. One consistent colour/typography/icon system. Green = savings, red/orange = cost or high tax, blue = neutral. **These meanings never swap.**
8. Every `AdSlot` has a **fixed min-height**. No layout shift is permitted.
9. Basic accessibility from the start: a real label on every input, an icon alongside colour (red/green colour blindness is common), a touch target of at least 44×44 px.
10. The result must stay visible while typing on mobile — sticky, or a 300–500 ms debounce.

### 8-2. Changes from the previous UI/UX document

| Item | Change |
|---|---|
| Header categories | "Freelancer Tools / Cost of Living / Blog" → becomes "Calculators / Guides / About". Cost of Living does not exist until phase 2 |
| `LocationAccordionGroup` | Continent/country grouping is no longer relevant. Instead: group the 51 states by **tax structure** (no tax / flat / progressive) — more useful, and itself a content angle |
| `CurrencySelector` | Removed (phase 1 is USD only) |
| `CompareRowCard` | Kept, for the 15 state comparison pages |
| `FamilySizeToggle` | Became `FilingStatusSelect` — the four real filing statuses, which unlike the previous spec's guessed `{single:1, couple:1.6}` multipliers have a real, documented mathematical effect on the result |

### 8-3. A new and important component: `TaxBreakdownWaterfall`

A visual account of where every dollar went:

```
gross income  ████████████████████████  $85,000
expenses      ███                       −$12,000
SE tax        ████                      −$10,313
federal tax   ████                      −$8,940
state tax     ██                        −$3,120
─────────────────────────────────────────────
what is left  ███████████████           $50,627
```

This single component does several things at once: it raises time on page, it creates shareable visual content, and it gives a transparency competitors lack.

### 8-4. Vertical layout of a state page

```
1.  Breadcrumb (one line)             Home > Freelance Tax > California
2.  H1 + a one-line description
3.  Calculator  ← no scrolling in the mobile viewport
4.  ResultCard + TaxBreakdownWaterfall
5.  Disclaimer box + data date
6.  AdSlot (after the result, never before it)
7.  Bracket-by-bracket table (ResponsiveTable)
8.  Article content (ContentAccordion on mobile)
9.  FAQ accordion
10. Similar states (horizontal carousel on mobile)
11. Related tools
12. Sidebar AdSlot (desktop only, sticky)
```

### 8-5. `StickyCalculatorCTA` and result sharing

- A floating "Recalculate" button on mobile while scrolling down
- A "copy/share result" button that puts the inputs into query params — real UX value, and it opens a new organic traffic route
- Note: query params must not create duplicate pages. `canonical` always points at the parameter-free version.

### 8-6. Mobile testing before scaling

On a real phone, not just DevTools:
- [ ] Does the calculator fit in the first viewport?
- [ ] Does `ResponsiveTable` convert to cards correctly?
- [ ] Does `AdSlot` cause layout shift? (CLS must stay under 0.1)
- [ ] With the keyboard open, is the result still visible?

---

### 8-7. Design tokens — concrete values, not descriptions

The previous document said "a consistent colour system" without giving numbers, which means every component invents its own colour. The base values:

```css
:root {
  /* semantic — these meanings never swap */
  --positive: #047857;   /* savings, income left, "below threshold" */
  --negative: #b45309;   /* cost, tax, "above threshold" */
  --neutral:  #1d4ed8;   /* informational */
  --warning:  #b91c1c;   /* disclaimer, stale data */

  /* surfaces */
  --bg: #ffffff;  --surface: #f8fafc;  --border: #e2e8f0;
  --text: #0f172a; --text-muted: #475569;

  /* spacing — a 4 px scale, no arbitrary values */
  --space-1: 4px; --space-2: 8px; --space-3: 12px;
  --space-4: 16px; --space-6: 24px; --space-8: 32px;

  --radius: 8px;          /* one radius for every card */
  --radius-sm: 4px;       /* inputs and chips only */

  --font: Inter, system-ui, -apple-system, "Segoe UI", sans-serif;
  --tabular: "Inter", ui-monospace, monospace;  /* numbers only */
}
```

**Rules:**
- **Every money figure uses `font-variant-numeric: tabular-nums`.** Without it, numbers in a table jitter while typing and the page stops looking professional.
- At most **three font weights** (400 / 600 / 700).
- No spacing value outside the scale above.
- An **icon** alongside every semantic colour — red/green colour blindness is common (section 10-3 of the previous UI/UX document).
- Dark mode is not built in phase 1. One correct theme beats two half-finished ones.

### 8-8. The tool page template (`ToolPage`) — the core of the business

Section 8-4 covered the state page layout, but the tool pages — which is where 99% of the demand now sits — had no template.

```
1.  Breadcrumb (one line)
2.  H1 = the target keyword, exactly
3.  One sentence: what this tool does and who for
4.  Calculator          ← no scrolling in the mobile viewport
5.  ResultCard          ← immediately under the inputs, headline number prominent
6.  TaxBreakdownWaterfall
7.  Disclaimer box + data date + tax year
8.  AdSlot (after the result, never before it)
9.  "How it is calculated" ← step by step, with this user's own numbers
10. Bracket-by-bracket table (ResponsiveTable)
11. Article content (ContentAccordion on mobile)
12. FAQ accordion
13. Related tools (3)
14. Sidebar AdSlot (desktop only, sticky)
```

**Section 9 is not incidental.** The SERP showed that the AI Overview for these keywords cites `taxstra.com`, and what earns the citation is a step-by-step definition of the formula with concrete numbers. This section is built precisely for that — and happens to be exactly what our engine produces as `federalBrackets`.

### 8-9. Calculator UX — the defaults are the most important product decision

**A calculator never opens empty.** An empty form means the user must work before seeing any value; exit rate rises and rankings follow. Every tool opens with realistic defaults and **the result is visible from the first moment**.

| Tool | Defaults |
|---|---|
| `self-employment-tax-calculator` | Income 80,000 · expenses 10,000 · single |
| `estimated-tax-calculator` | The same + no prior-year tax (so the safe harbor path is visible) |
| `1099-tax-calculator` | Income 65,000 · expenses 8,000 |
| `freelance-tax-calculator` | All fields, default 80,000 |
| State page | The same defaults + the state preselected |

**Input rules:**
- Numeric inputs use `inputmode="decimal"` — the numeric keyboard on mobile
- Thousands separators while typing, without the caret jumping
- A negative input is not rejected but clamped to zero, with a message
- **300 ms debounce** on calculation (section 10-4 of the previous UI/UX document)
- Advanced fields (retirement, insurance, HSA, itemized deductions) are **collapsed** by default — the initial form has at most 4 fields
- Changing the state **preserves** the user's inputs rather than resetting them

**Displaying the engine's warnings:** every string in `warnings` and `state.notes` must be visible in the UI, not discarded. Their default home is a box under the ResultCard. This is what turns section 4-8 from a list of limitations into a trust signal.

---

## 9. SEO and indexation

### 9-1. Foundations

- A dynamic `sitemap.ts` — generated from the dataset, never by hand
- `robots.ts`
- Google Search Console from **day one**, before any content ships
- An independent, absolute `canonical` on every page
- JSON-LD: `FAQPage` + `BreadcrumbList` + `WebApplication` (for tool pages) + `Organization` + `Person` (author)
- A dynamic OG image per state (`opengraph-image.tsx` in Next.js) — for sharing on Reddit and social networks

### 9-2. Keyword validation **before** writing

The previous document said phase 2 would be data-driven, "not guesswork" — which was an admission that phase 1 was entirely guesswork. The correction:

- [ ] Before writing a single page, check **30 primary keywords** against real volume and difficulty data
- [ ] For each keyword, actually look at the top 10 results: if they are all high-DR domains and major tax brands, that keyword is not reachable in year one — go long-tail
- [ ] The output of this step is a prioritised list that sets the writing order for the 51 states (California and Texas before Wyoming)

### 9-3. Internal linking

Four layers:
1. Directory → state pages
2. State pages ↔ similar states (by tax structure, not alphabetically)
3. State pages ↔ guides (every state links to at least 3 related guides)
4. Guides ↔ tools

### 9-3-1. Internal anchor text

An internal link without an anchor-text rule wastes half its value. Four rules are recorded in `data/pages.json → onPage.anchorText`, in summary:

- Link to an entity page with **the entity's own name** — "Cost of Living in Austin", not "click here".
- Link to a tool with **that tool's primary keyword**, at most once with identical text on any page.
- Anchor text is never the linking page's **own** keyword; it is written with the **destination's** keyword.
- Navigation and footer are exempt from the 25-body-link ceiling but must stay identical across pages.

### 9-3-2. Title, meta and H1 formulas

For 104 programmatic pages these formulas are the most direct lever on click-through from search results and, more importantly, the only thing preventing 87 generated pages from effectively sharing one title. That is why they are not prose; they live in `data/pages.json → onPage.templates` and `scripts/audit_seo.py` enforces them in CI.

| Template | title | H1 |
|---|---|---|
| ToolPage | `{Primary} ({year})` | `{Primary}` |
| PlacePage | `Cost of Living in {Metro} ({year})` | `Cost of Living in {Metro}` |
| StateTaxPage | `{State} Income Tax Calculator ({year})` | `{State} Income Tax Calculator` |
| DirectoryPage | `{Primary} ({year})` | `{Primary}` |
| Home | Fixed — targets no head keyword | "What a place really costs — and what you keep" |

The rules the audit enforces:

- **A 60-character title ceiling.** Measured against the longest possible substitution, not an optimistic sample: `San Francisco-Oakland-Berkeley, CA` takes the title to 59 characters — meaning this ceiling is genuinely closed and adding any word to the PlacePage pattern breaks it.
- **Meta between 110 and 155 characters.** For tools and directories it comes from each page's `metaHook` field, not from `output` — `output` is an internal description whose job is separating pages from each other, not text meant to be seen in a SERP. The audit itself surfaced that distinction the moment it was added (section 9-3-5).
- **The primary keyword must appear in the rendered title and H1**, mandatory for ToolPage and DirectoryPage.
- **Every programmatic template's pattern must carry an entity placeholder** (`{Metro}`, `{State}` or `{Primary}`), otherwise all generated pages share one title.
- **The year goes in the title, never in the URL** (section 6-7) — the title is rewritten annually, the address never.
- **Title casing** is measured exactly as it ships: short prepositions stay lowercase unless they lead ("Cost of Living", not "Cost Of Living").
- The nine no-tax states get a separate meta: a "calculator" title with copy saying there is no state income tax but there is federal — otherwise the page looks empty at first glance.

### 9-3-3. Structured data by template

| Template | JSON-LD |
|---|---|
| ToolPage | `WebApplication` (applicationCategory: FinanceApplication, free offers) + `FAQPage` + `BreadcrumbList` |
| PlacePage | `Place` + `Dataset` (pointing at the BEA/HUD source) + `FAQPage` + `BreadcrumbList` |
| StateTaxPage | `WebApplication` + `FAQPage` + `BreadcrumbList` |
| DirectoryPage | `ItemList` (position and link per row) + `BreadcrumbList` — no FAQPage |
| Global | `Organization` + author `Person` in the layout |

`FAQPage` appears only when those questions are **visible on the page**; structured data without a visible counterpart violates Google's guidelines. `dateModified` updates only on a genuine content change (section 9-4-1).

### 9-3-4. robots.txt and the share image

- `/api/` and internal paths are disallowed.
- **No content page is ever disallowed.** If a page is not worth indexing, it is not generated at all — the gates in section 6-8 do that job.
- `Sitemap:` points at `sitemap.xml`, which itself has four child sitemaps (section 6-8-6).
- No `crawl-delay` — Google ignores it and it only slows other crawlers.
- **A dynamic OG image** per entity (`opengraph-image.tsx`): the place name and its index number on the image. This is not decoration; section 9-5 earns links on Reddit and forums, and a link without an image is effectively invisible there.
- `og:title` may differ from `<title>` — the year is dropped on social networks.

### 9-3-5. The language rule — the whole project is English

The site, the data and the documentation are **all English**. This was not always true: the spec was originally written in Persian, and the boundary between "the Persian document" and "the English site" was only a convention.

That convention broke once. The `output` field in `data/pages.json` held an internal Persian description, and the first time it was wired into the meta formula, 15 pages would have shipped with Persian meta descriptions. The audit caught it, but that proved a remembered convention is not a boundary.

So the boundary became a check, and then the ambiguity was removed entirely by translating everything:

```bash
python3 scripts/check_language.py
```

| Path | Language |
|---|---|
| `data/` · `src/` · `app/` · `public/` · `components/` · `content/` | **English only** — enforced in CI |
| `docs/` · `scripts/` | **English only** — enforced in CI |
| `docs/archive/` | Exempt — the three original documents, kept verbatim as a historical record |

Any non-English character in those paths breaks the build. The archive is the single exception, because rewriting a historical record destroys it.

One detail worth keeping: the checker's own character-class regex is written as escape sequences rather than literals, so the detector does not contain what it detects. Written the obvious way, it flags itself.

### 9-4. Distribution — a section the previous document lacked

The previous document had one line about attracting traffic. For a new domain, **links and brand signals are the bottleneck, not page count.** At least 30% of project time has to go here:

| Channel | The work |
|---|---|
| Reddit | r/freelance, r/tax, r/smallbusiness, r/digitalnomad — **months of genuine answering first, links later.** Dropping links early means a ban |
| Indie Hackers / Hacker News | One "how I built it" post after launch |
| Product Hunt | One planned launch, not a rushed one |
| Accounting forums | A free tool has real value for accountants |
| Quora / specialist forums | Real answers with natural references |
| Seasonal alignment | January to April is peak tax search season. High-value content must be ready in **December**, not March |

**An important timing note:** US tax season is peak traffic and peak CPC. If the site is indexed and settled by December 2026, the January–April 2027 season can produce a revenue jump on its own. The whole timeline is arranged around that window.

### 9-4-1. Technical SEO gaps the audit found

#### Structured data validation

Writing schema is not enough; **valid** schema is required. One syntax error in the JSON-LD means Google ignores the whole block and you never find out.

- An automated CI test: each template renders a sample and its JSON-LD is validated against schema.org
- Required types: `WebApplication` (tools) · `FAQPage` (any page with an FAQ) · `BreadcrumbList` · `Organization` · `Person` (author) · `Dataset` (the methodology page — links to structured data and raises citation odds)
- **`FAQPage` only when the FAQ is genuinely visible on the page.** Schema for hidden content violates the guidelines

#### hreflang and the non-US visitor

Once European country pages arrive, the site has two geographic audiences:

- US pages: `hreflang="en-US"` · country pages: generic `hreflang="en"`
- **A state tax page is meaningless to a European user.** Instead of a redirect (bad UX and a confusing signal), a small bar at the top of the page: "Looking for cost of living outside the US?" with a link
- No automatic IP-based redirect — it misleads Googlebot too

#### Directory pagination

With 100+ metros, the directory cannot stay one page.

- Group by state or region, **not numeric pagination** — semantic grouping is better for the user and produces more indexable pages
- Each group page carries its own unique content (the budget in section 6-8-4 applies here too)
- If numeric pagination ever becomes necessary: `rel="next/prev"` is no longer a signal; each page must stand on its own value or be `noindex`

#### Cannibalisation and canonical — with an automated auditor

> **This section is enforced, not advised.** The map is in [`data/pages.json`](../data/pages.json) · the auditor is `scripts/audit_seo.py` · it runs in CI and breaks the build.

```bash
python3 scripts/audit_seo.py
```

**What is checked:**

| # | Check |
|---|---|
| 1 | Every page has exactly **one** primary target keyword |
| 2 | No keyword is claimed twice |
| 3 | One page's primary keyword is not another page's secondary |
| 4 | Pairs with ≥30% lexical similarity must declare **different primary outputs** |
| 5 | Every target is measured in `data/keywords.json` |
| 6 | Canonical is self on every page and tools strip parameters |
| 7 | Every template in use has a title, H1 and meta formula |
| 8 | Title ≤60, H1 ≤70 and meta between 110 and 155 characters — rendered with the **longest possible substitution**, not an optimistic sample |
| 9 | The primary keyword is present in the rendered title and H1; and every programmatic template's pattern carries an entity placeholder so pages cannot share a title |
| 10 | Anchor-text, OG and robots rules are declared, and every template has defined JSON-LD |

**Current run: 17 pages · 0 errors · 0 warnings** — across all ten checks. All three original warnings were resolved by actual measurement: two keywords were confirmed and recorded (`cost of living by city` 880 · `state income tax rates by state` 3,600) and the third was rejected and its page deleted (`job offer comparison calculator` 30).

##### The most important rule — generic versus entity

The auditor found two pairs at **67%** similarity that are genuine risks:

| | |
|---|---|
| `/tools/income-tax-calculator` | versus `/state-taxes/{state}` |
| `/tools/cost-of-living-calculator` | versus `/cost-of-living/{metro}` |

Both share one pattern: **a generic tool with a location selector, versus the page for one specific place.**

> **A generic tool is never optimised for an entity-qualified query.** `/tools/income-tax-calculator` never carries "California" in its title, H1, meta or H2 — that query belongs to `/state-taxes/california`. And the reverse: a state page is never optimised for the generic keyword.

Without this rule, the generic tool that supports all 51 states unintentionally competes with all 51 state pages — and because the tool is stronger, the state pages never rank.

##### Directory versus tool

A directory **lists**, a tool **calculates**. A directory does not embed a full calculator and a tool does not render the full entity list. If both do both, one has to go.

##### The salary family of four

`income tax` · `take-home pay` · `paycheck tax` · `tax withholding` — four queries with adjacent intent. Their separation **must be visible in the output**, not only in the URL:

| Tool | The ResultCard's headline number |
|---|---|
| income tax | **Annual** tax liability + the bracket table |
| take-home pay | **Annual and monthly** net |
| paycheck tax | **Net per paycheck**, by pay period |
| tax withholding | **What to withhold on the W-4** so the year ends at zero |

The H1, the first sentence and the headline number must show that difference. If all four highlight the same number, they are four duplicate pages however different their URLs.

##### Canonical rules

Seven rules are recorded in `data/pages.json` and checked by the auditor: absolute self-canonical · strip all parameters · no trailing slash · one host (apex or www) · HTTPS mandatory · lowercase · directory group pages carry their own canonical · no page is both canonicalised and noindexed.

**A note on parameters:** the comparison tool accepts `?from=&to=` so it can be prefilled from city pages, but always canonicalises to the parameter-free version. That is deliberate — we do not build city-pair pages (section 6-5), so a parameter must not create an indexable page.

#### Content freshness

`dateModified` in the JSON-LD **updates only when the content genuinely changed.** Bumping the date without changing content is signal manipulation and it gets detected.

The annual data update (section 16) is itself a genuine change and makes `dateModified` legitimate — a structural advantage of a niche whose content is not static.

---

### 9-5. External link building — the critical path, not a side task

**The inconsistency this section fixes:** section 14 says "competitors rank on domain authority and quality alone is not enough" — and then the entire link strategy was one line. If the diagnosis is right, links are the critical path and deserve to be taken as seriously as the tax engine.

#### 9-5-1. Why content alone is not enough

The SERP for the primary keyword: six of the top ten positions are white-label widgets on bank and insurance domains. Their content is weak. **We beat them on quality, but Google sees quality only once somebody has linked to it.** A link is the discovery mechanism for quality, not a substitute for it.

#### 9-5-2. Linkable assets — the things people actually link to

Calculators do not attract links. **Data attracts links.** Three assets built from what we already have:

| Asset | Why it earns links | Cost |
|---|---|---|
| **"Net pay on $95,000 in all 51 jurisdictions"** — a complete table, updated annually | One quotable fact with a number. Journalists and bloggers link to a number, not to a tool | From the existing engine, near zero |
| **"The cheapest and most expensive metros after tax"** | A combination nobody has; Numbeo has no tax | Requires the BEA dataset |
| **Open methodology** — sources, formulas, limitations | Data-driven sites link to a citable source | From section 6-3 |

**Rule:** every asset must be quotable in one sentence. "Seattle and Portland are three hours apart and their annual net pay differs by $7,167" — that earns links. "Our calculator is accurate" does not.

#### 9-5-3. Channels and order

| Phase | Channel | Rule |
|---|---|---|
| Month 1–3 | Reddit (r/personalfinance · r/moving · r/expats) · specialist forums | **Answer only, no links.** An early link means a ban |
| Month 3–6 | The same forums, now with links when it genuinely answers the question | A ratio of at least 10 link-free answers to 1 with a link |
| Month 4+ | Hacker News · Indie Hackers — a "how we built it" post focused on the data | Once, done well |
| Month 6+ | Contact authors of relocation and tax articles, offering data rather than asking for links | We give data and earn links — not the reverse |
| Ongoing | HARO and similar — expert answers using our own data | |

**What is never done:** buying links · link exchanges · low-quality directories · mass guest posting. In a YMYL niche these carry a penalty risk larger than their benefit.

#### 9-5-4. Quantitative target and measurement

| Time | Natural referring domains |
|---|---|
| Month 6 | 5–10 |
| Month 12 | 25–40 |
| Month 18 | 60+ |

**If it is under 5 at month 6, the problem is distribution, not content** — and building more pages will not fix it. This is one of the warning signs in section 17-1.

#### 9-5-5. Share of time

**At least 30% of project time from month 3 onward.** If all the time goes into building pages, we build pages nobody sees — exactly the trap section 14 describes.

---

## 10. AdSense

### 10-1. Approval prerequisites

- [ ] A dedicated domain (not a free subdomain)
- [ ] 30–40 complete, published pages
- [ ] All 7 trust pages (section 6-4) — especially a real About and a Privacy page with cookie disclosure
- [ ] Clean navigation with no broken links
- [ ] No empty or "coming soon" pages
- [ ] Some initial organic traffic (not required, but it helps)

### 10-2. Process expectations

- Review usually takes a few days to a few weeks
- **Being rejected the first time is normal** and not the end; fix the reason and reapply
- A finance (YMYL) niche is scrutinised harder — which is why the trust pages are built before the content, not after
- The timeline allows for **two applications**

### 10-3. Technical implementation

- `AdSlot` with a fixed `min-height` from the first render
- Lazy script loading (`next/script` with `strategy="afterInteractive"`)
- At most 3 slots per page initially; higher density damages both UX and Core Web Vitals
- **Never click your own ads** — even once can lead to a permanent ban
- Auto Ads stay off initially so we keep control of CLS

---

### 10-4. Ad placement map

Ad density affects the $500–700 target directly, but overdoing it damages UX, Core Web Vitals and rankings alike. At most **three slots** in phase 1:

| Slot | Location | Size | `min-height` |
|---|---|---|---|
| `after-result` | Immediately after the ResultCard | responsive | **280px** |
| `in-content` | Between the article section and the FAQ | responsive | **280px** |
| `sidebar` | Sticky, ≥1024px only | 300×600 | **600px** |

**Hard rules:**

1. **No ad above the result.** The user came for the number. An ad before the number raises exit rate and signals "thin content".
2. **`min-height` is reserved from the first render**, before the script loads. CLS must stay under 0.1.
3. **Auto Ads off** — CLS control stays with us.
4. **The sidebar slot does not exist on mobile**, and is not substituted.
5. **Never click your own ads** — even once can lead to a permanent ban.
6. Trust pages (About, Privacy, Terms, Contact) carry **no ads**. AdSense views ad-heavy policy pages poorly.

### 10-5. Migrating to a premium network

AdSense is the starting point, not the destination. At roughly **30,000–50,000 monthly sessions**, premium networks usually raise RPM meaningfully — on the same traffic that can be the difference between $500 and $900.

- Evaluate this at **gate 3**, not earlier
- Network thresholds and terms change and must be verified at that time
- The decision criterion: real AdSense RPM over the past three months versus the new network's estimate, not its marketing claim
- Premium networks run higher ad density; measure the effect on Core Web Vitals before migrating

### 10-6. Cookie consent — a requirement activated by Europe

Before stage 2.5 the target was the US only and this looked like a nice-to-have. **With European country-level cost-of-living pages, it became mandatory.**

**The issue:** our traffic analytics are cookieless (section 15-1), so they are fine — but **AdSense sets cookies**. Google's EU user consent policy requires a certified CMP for European traffic. Without one, Google can stop serving ads to that traffic.

**Decisions:**

1. **A CMP from Google's certified list is installed before ads are enabled.** Not after
2. **Consent Mode** is implemented so measurement still works in the non-consent state
3. US users see no banner — the CMP activates only where it is required
4. A "Do Not Sell or Share" footer link for California
5. `/privacy` must state explicitly that **calculations stay client-side and no financial figure reaches a server** — in a finance niche that is an advantage, not only a requirement

> ⚠️ The details of these requirements change. Before implementing, verify the certified CMP list and current terms — like every other number in this document.

**The fallback if the CMP is late:** keep ads off for European traffic until the CMP is ready. Less revenue, but zero policy risk. **An ad is never served to a European user without consent.**

---

## 11. Timeline and decision gates

The main difference from the previous document: **the validation phase genuinely occupies calendar time**, and after each phase there is a decision gate with a numeric criterion.

> ~~**The project's real deadline is December 2026**~~ — **obsolete as of version 4.** That deadline came from tax seasonality; the place cluster is nearly seasonless. Tax season still gives a jump, but the project's failure is no longer tied to it. The text below is kept for history:
>
> **[obsolete]** Keyword validation showed seasonality up to **46×** (turbotax calculator: 3,600 in July, 165,000 in January). A page published in February has missed the peak and must wait a full year. It is late August today — **we have roughly four months.**

| Month | Work | Output |
|---|---|---|
| **September (week 1)** | ✅ Keyword validation (done) · extract 13 tax data items from primary sources · register the domain · set up GSC | Tax data in JSON |
| **September** | Tax engine + golden tests · 7 trust pages | A tested engine |
| **October** | 5 layer-1 tools · the first 3 guides · 8 state pages | **Gate 1** |
| **November** | 3 W-2 cluster tools · the remaining 6 guides · apply to AdSense | AdSense approved |
| **December** | 🎯 **Everything must be published and indexed** · link push · season preparation | **Gate 2** |
| **January–April** | Tax season: peak traffic · live optimisation from GSC · no large new pages | **Gate 3** (end of April) |
| **May onward** | Per gate 3: expand the states or deepen the W-2 cluster | |

**A note on order:** if time capacity runs short, cut from the end — state pages first, then guides. **The 5 layer-1 tools and the 7 trust pages are never cut**; without them there is neither AdSense approval nor traffic.

### 11-1. Decision gates — numeric criteria, not feelings

**Gate 1 (end of October) — "are we being indexed at all?"**
Three to four weeks after publishing the 8 sample pages:
- ✅ **Continue:** at least 6 of the 8 are indexed and taking impressions
- ⚠️ **Pause and fix:** indexed but zero impressions → the problem is keyword selection, not technical. Review the keywords before building the next 43 pages
- ❌ **Stop and reconsider:** not indexed → a technical or content-quality problem. **Do not scale under any circumstances.** Scaling an indexation problem multiplies it

**Gate 2 (end of December) — "are we ready for the season?"**
- ✅ All layer 1 and 1.5 pages indexed, AdSense approved, monthly organic traffic above 1,000 visits and rising
- ⚠️ Under 500 → stop and focus solely on distribution and links until January, not more pages. Entering the season with unindexed pages is pointless
- Check: are the state pages cannibalising each other? Is there a keyword sitting at position 11–20 that a small push would move to page one?

**Gate 3 (end of April 2027, after tax season) — "is phase 2 justified?"**
- ✅ **Go to phase 2:** season peak above $300/month and an out-of-season base above $100 → expand
- ⚠️ **Go deeper, not wider:** $30–100 → deepen the same tax niche. Adding a second niche on a weak base weakens both
- ❌ **Fundamental review:** under $30 → the core assumption was wrong. Analyse where before investing further

### 11-2. Time capacity — honestly

After the section 6 revision, phase 1 is roughly **35,000 words + an application + a tested calculation engine** (the initial estimate was 80,000 words).

- Full time: comfortably achievable by December
- Part time (~20 hours a week): tight but doable, provided the cut order above is respected
- If capacity is below that, **reduce scope, not quality**. Five excellent tools beat 34 mediocre pages by a wide margin — for Google and for AdSense alike

**That reduction from 80,000 to 35,000 words is the difference between "making tax season 2027" and "missing it".**

---

## 12. Definition of done

No page ships unless all of the following hold:

**Performance budget — a number, not "make it fast"**

| Metric | Ceiling |
|---|---|
| Initial JS per page (compressed) | **90 KB** |
| Total page weight excluding ads | **350 KB** |
| LCP | ≤ 2.0 s |
| INP | ≤ 200 ms |
| CLS | ≤ 0.1 |

**Explicitly forbidden in phase 1:** a charting library (the waterfall is built with CSS/SVG) · a date library (`Intl` suffices) · lodash · any heavy animation. With 36 tools queued, Lighthouse drifts down quietly without a numeric ceiling and nobody notices until it is too late.

**Technical**
- [ ] `curl` on the URL returns the complete content in the HTML (not an empty SPA shell)
- [ ] The performance budget above is met
- [ ] `title`, `description`, `canonical` and JSON-LD are present in the initial HTML
- [ ] Lighthouse: Performance ≥ 90, Accessibility ≥ 95, CLS < 0.1
- [ ] Tested on a real phone
- [ ] Present in `sitemap.xml`

**Data**
- [ ] Every number has a linked primary source
- [ ] `lastVerified` under 12 months
- [ ] Tax engine tests green

**Content**
- [ ] 900–1,400 words
- [ ] At least one state-specific fact from a primary source
- [ ] Human review completed
- [ ] 5 FAQ questions with computed numbers for that state
- [ ] Links to at least 3 related internal pages
- [ ] The disclaimer and data date are displayed

### 12-1. Additionally, for tool pages

Tool pages are the core of the business and carry extra conditions:

- [ ] The calculator opens with realistic defaults and **the result is visible from the first moment** (section 8-9)
- [ ] The initial form has at most 4 fields; the rest are collapsed
- [ ] A "how it is calculated" section using this user's own numbers — the AI Overview entry point (section 8-8)
- [ ] Every `warnings` and `state.notes` string is visible in the UI, not discarded
- [ ] The events in section 15-2 are recorded
- [ ] Every AdSlot's `min-height` is reserved; CLS measured below 0.1
- [ ] Money figures use `tabular-nums` — they do not jitter while typing
- [ ] The H1 is exactly the target keyword from the validated list

### 12-2. Additionally, for cost-of-living pages

- [ ] **No invented dollar amount appears on the page** — dollars come either from the user's input or from HUD/BLS with an explicit "regional estimate" label (section 4-9-1)
- [ ] A category with no official index is not displayed
- [ ] The BEA data year is written on the page — these indices are always published with a lag (section 16-2-1)
- [ ] **The cross-link to that state's tax calculator** is present — the advantage no competitor has
- [ ] `/methodology` lists the BEA and HUD sources with links

**The final smoke test:** put the page next to a competitor's. If you cannot say in one sentence why ours is better, the page is not ready. For this niche that sentence is usually one of: it has real state tax · it shows where the money went · it tells you your next payment date · it says what it does not know.

---

## 13. Tax data — status and verification

**No tax figure is written in this document.** The numbers live only in `src/data/tax-year-{year}/`, alongside their source and date.

### 13-1. Current status (2026-08-29)

| Item | Status |
|---|---|
| Jurisdictions extracted | **51 of 51** (50 states + DC) |
| Structure | 9 no-tax · 15 flat · 27 progressive |
| Federal | Brackets for all 4 statuses + standard deduction + SE tax + Social Security cap + QBI |
| Structural errors | **0** |
| Source class | **Secondary — unverified** |
| Quarterly payment schedule | **Derived algorithmically** from 26 U.S.C. 6654 and 7503 |
| Items not extracted | — |

### 13-2. Tooling

| File | Role |
|---|---|
| `scripts/extract_tax_data.py` | Rebuild the dataset from the source package. Records each state's actual path in its output |
| `scripts/validate_tax_data.py` | Structural validation, for CI. With `--strict` it also fails on warnings |
| `scripts/estimated_tax.py` | Derive the quarterly payment schedule and safe harbor rules from statute |
| `docs/data-verification.md` | A row-by-row checklist with a primary-source link for every item |

### 13-3. Why the data is still "unverified"

The development environment's network cannot reach `irs.gov` or the state revenue departments. The data was extracted from the parameter tree of a maintained open-source tax model, where every parameter carries a reference to a primary source; those references are copied into each file's `provenance.sources`.

The alternative — "extraction from web search" — was tried and rejected: two consecutive searches for the same keyword returned contradictory federal brackets. That is exactly the failure rule number one exists to prevent.

### 13-4. Hard rules

1. **A page does not ship until its corresponding row in `docs/data-verification.md` is ticked.**
2. **The 7 states without 2026 figures** (California, Idaho, Minnesota, Missouri, Oregon, Vermont, Wisconsin) have inflation-indexed brackets and their current values are **2025**. Until the new figures are published, either the page is not built or it is explicitly labelled "based on 2025 figures". Showing a 2025 number under a 2026 heading is the exact mistake this whole project exists to avoid.
3. **Quarterly due dates are computed from statute, not copied from a table.** `scripts/estimated_tax.py` combines the statutory pattern of 26 U.S.C. 6654(c)(2) with the holiday rule of 7503 and produces correct dates for any year. The reason is practical: two web sources gave two different dates for 2026 (June 15 and 16), and the calculation showed June 15 is a Monday, so no shift applies. Years that genuinely do shift (such as April 2028, from a weekend plus DC's Emancipation Day) come out correct automatically.
4. Re-running the extraction script resets every `verification` to `pending`. Commit completed verifications before re-running.

### 13-5. Accuracy details discovered during extraction

These are the things a naive extraction would have got wrong:

| Item | The trap |
|---|---|
| The 0.9235 factor | The source's `net_earnings_exemption` field is **$400** (the minimum earnings threshold), not the factor. The factor must be derived from `1 − (SS rate + Medicare rate) ÷ 2` |
| Georgia | Flat since 2024 (4.99% for 2026), but its repealed progressive table is still in the data |
| Louisiana | Flat since 2025 (3%), the same trap |
| California | The top rate is 12.3%, not 13.3% — the extra percent is a separate mental health services tax above one million dollars |
| New Hampshire | Its interest/dividends tax was repealed in 2025; it now genuinely has no income tax |
| Mississippi | A flat rate with one zero-rate step, not progressive |
| Flat states | Their rate stays fixed for years; "an old date" does not mean "stale". Only an inflation-indexed parameter can go stale |
| Local tax | 9 states have local taxes affecting freelancers, recorded in the `localTaxNote` field |

---

## 14. Competitive position

The SERP analysis (research document, section 3) revealed something that determines the content strategy.

### 14-1. Who the real competitor is

For `self employment tax calculator`, six of the top ten positions are **white-label widgets** on bank and insurance sites: UMB, GuideStone, The Hartford, a Florida credit union, Nationwide, CalcXML.

| | Them | Us |
|---|---|---|
| Calculation source | A licensed widget, identical everywhere | A purpose-built engine with golden tests |
| State tax | None | All 51 jurisdictions |
| Bracket-by-bracket table | None | Yes |
| Quarterly payment calendar | None | With dates derived from statute |
| Limitations | Not declared | Explicit in `warnings` |
| Domain authority | **Very high** | **Zero** |

**The strategic conclusion:** on content quality they are easy to beat. But they rank on domain authority, not on quality — and domain authority is exactly what we lack. **So quality alone is not enough; section 9-4 (links and distribution) is genuinely critical, not a side task.**

### 14-2. An encouraging sign

`sdocpa.com` — a small accounting practice — sits at position 13. And the AI Overview for that same keyword cites **`taxstra.com`**, a small niche site, above TaxAct and QuickBooks. A small site can win in this niche.

### 14-3. The sentence every page must be able to say

> "Put our page next to a competitor's. If you cannot say in one sentence why ours is better, the page is not ready."

For this niche that sentence is usually one of: **it has real state tax** · **it shows exactly where your money went** · **it tells you your next payment date** · **it says what it does not know**.

---

## 15. Measurement and instrumentation

The decision gates in section 11 need data. If we do not measure from day one, there is nothing to decide with by month three.

### 15-1. What goes in from day one

| Tool | When | Why |
|---|---|---|
| Google Search Console | **Before the first page ships** | The only source of impressions and positions. Delay here means irrecoverable lost data |
| Lightweight cookieless analytics | With the first page | Plausible/Umami or similar — light, and no cookie banner |
| The AdSense dashboard | After approval | Real RPM replaces the estimates in section 1 |

### 15-2. Events that are recorded

A calculator without instrumentation is a black box — you cannot tell where the user gives up.

| Event | The question it answers |
|---|---|
| `calc_interact` (first input change) | What share of visitors use the tool at all? |
| `calc_field_changed` (field name) | Which field is confusing? Which is never touched? |
| `calc_advanced_opened` | Are the advanced fields worth it, or just clutter? |
| `result_shared` | Does the share button genuinely open a traffic route? |
| `state_changed` | Which states are actually selected? **A direct input to the decision to build the ninth state page** |
| `warning_shown` (type) | Which limitation hits real users most? That sets the fix priority |

**Rule:** no personal data and no financial value is ever recorded — only the field name and the event. Calculations stay client-side and we say so in `/privacy`; in a finance niche that is itself an advantage.

### 15-3. Monthly review — half an hour, not a project

Every month, just these numbers:

1. **Keywords at positions 11–20** — the nearest win. Strengthening these is cheaper than writing a new page
2. **Pages with high impressions and low CTR** — a title/description problem, not a content problem
3. **Pages with high entries and low `calc_interact`** — the calculator is not being found, or it intimidates
4. **RPM by page** — which cluster actually pays
5. **Is there a keyword that refutes a section 6 assumption?**

---

## 16. Annual update runbook

The project's largest long-term debt. Tax changes every year, and **pages with expired data are worse than no pages** — for the user and for the site's credibility alike.

### 16-1. Calendar

| Time | Work |
|---|---|
| **October–November** | The IRS usually publishes next year's Revenue Procedure. Run `scripts/extract_tax_data.py --year {next}` |
| **November** | The SSA announces next year's Social Security cap |
| **December** | Inflation-indexed states publish their figures — the same 7 states marked stale in section 13 |
| **December** | Verify against `docs/data-verification.md`, then run `--strict` |
| **January** | Switch the site's default year + update page copy + publish |

### 16-2. The runbook

```bash
python3 scripts/extract_tax_data.py --year 2027
python3 scripts/estimated_tax.py     --year 2027
python3 scripts/validate_tax_data.py --year 2027
npm test        # the golden tests must still make sense against the new data
```

Then:
1. Read the `stale for 2027` output — every state listed there either waits or is labelled with the previous year
2. Tick the rows in `docs/data-verification.md`
3. **The previous year is not deleted.** `src/data/tax-year-2026/` stays; a user filling in last year's return needs it. Add a year selector on the tools
4. Update the pages' `dateModified` — a freshness signal for Google

### 16-2-1. The cost-of-living cycle

This cluster's sources also update annually, on a different calendar from tax:

| Source | Publication time |
|---|---|
| BEA Regional Price Parities | Usually late in the year, for the prior year |
| HUD Fair Market Rent | Usually autumn, for the next fiscal year |
| Eurostat comparative price levels | Annually |

**An important note:** unlike tax, whose effective date is definite, these indices are published with a lag — meaning we always display last year's data. **This must be stated explicitly on the page**, not hidden: "BEA indices for {year}, the most recent published data".

### 16-3. The automatic guard

`validate_tax_data.py` **breaks the build** if the dataset is more than 400 days past its generation. This is deliberate: forgetting to update must surface as a CI error, not as quietly wrong pages.

---

## 17. Risks

Stated honestly, each with a specific mitigation. A risk that is not written down has no plan behind it.

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| 1 | **A new domain does not get indexed** | Fatal | Gate 1 with a numeric criterion. No scaling before proof. Static Next.js instead of an SPA |
| 2 | **AI Overviews swallow the organic click** | High, and getting worse | Sections 6-8 and 8-8: a step-by-step structure to earn the citation. Diversify toward tool keywords where the user must interact, not merely read a short answer |
| 3 | **Competitors have far higher domain authority** | High | Section 14. Quality + long-tail + active distribution. Accepting that head keywords do not come in year one |
| 4 | **One wrong number makes 51 pages wrong** | Fatal to credibility | Golden tests · a CI validator · the verify-before-publish rule |
| 5 | **AdSense rejects the site** | Months of delay | Trust pages **before** content. Room for two applications |
| 6 | **Time capacity runs short** | High | An explicit cut order in section 11: states first, then guides; the layer-1 tools never |
| 7 | **A Google algorithm update** | Variable | Focus on one niche, real E-E-A-T, no reliance on a single keyword. If a drop comes: wait four weeks before changing anything — a rushed reaction to an update usually makes it worse |
| 8 | **Seasonality does not deliver the monthly target** | High | Stages 1.5 and 3 (section 2-3), which bring seasonless keywords |
| 9 | **The annual update is forgotten** | High | Section 16 + breaking the build after 400 days |
| 10 | **Project scope drifts toward "life"** | High | Section 2-2: maths and health are explicitly out of scope |

### 17-1. Early warning signs

Watch for these in the monthly review; each appears before the corresponding risk above materialises:

- New pages still not indexed after three weeks ← risk 1
- Impressions rising while clicks stay flat ← risk 2
- `calc_interact` under 20% ← the calculator is not being found; a UX risk
- No page climbing above position 20 despite added content ← risk 3, time to focus on links

---

## 18. Process for adding a new tool

The catalogue has 36 tools and 12 are in phase 1 — meaning **24 iterations** of this process lie ahead. Without a checklist each becomes an ad-hoc decision, and the result is inconsistency.

### 18-1. Gate zero — before writing any code

- [ ] The tool is in [`tool-catalogue.md`](tool-catalogue.md) with its market value recorded
- [ ] **The primary keyword's SERP has been checked.** High market value does not guarantee an easy ranking. If the top ten are all major brands with strong content, go long-tail or skip the tool
- [ ] Does it have an AI Overview? If so, design the "how it is calculated" structure from the start
- [ ] Which category is it in (A / B / tax / mortgage)? If none, **it probably should not be built** — section 2-2

### 18-2. Slug and path

- [ ] Slug = the target keyword, from the validated list (section 6-9)
- [ ] No year, no brand name
- [ ] **The slug is locked after publication** — changing it means a permanent redirect

### 18-3. Logic

- [ ] If it is tax-related: it uses `src/lib/tax/` and **writes no new tax logic** (rule 3-4-1)
- [ ] If it needs data: it has a primary source, in JSON with `sources` and `lastVerified`
- [ ] If it is simple arithmetic: in `src/lib/calc/{name}.ts`, a pure function
- [ ] It has tests — even simple arithmetic. `margin = (price − cost) / price` can be written wrong too
- [ ] Every limitation appears in `warnings`, never silently (section 4-8)

### 18-4. The page

- [ ] The template in section 8-8 · the defaults in section 8-9 · **never an empty form**
- [ ] The content brief in section 7-2-1 (600–900 words)
- [ ] Links to at least 3 internal pages · and is linked from at least 2
- [ ] The events in section 15-2 are recorded
- [ ] It appears in `sitemap.ts` (automatically, from the registry)

### 18-5. Before publishing

- [ ] The definition of done in sections 12 and 12-1 is complete
- [ ] The performance budget in section 12 is met
- [ ] Tested on a real phone
- [ ] The smoke test: "why is ours better?" in one sentence

### 18-6. After publishing

- [ ] Indexation registered in Search Console
- [ ] After 3–4 weeks: is it taking impressions? If not, understand why **before building the next tool**
- [ ] Is `calc_interact` above 20%? If not, the problem is UX, not content

> **The rhythm rule:** never publish more than three tools at once. Bulk publication on a young domain is both a bad signal and makes it impossible to tell which one worked.

---

## 19. Changelog

| # | Fault in the previous document | Correction |
|---|---|---|
| 1 | "static-first" but a React SPA was specified | Next.js with a real static export |
| 2 | `FEDERAL_INCOME_RATE = 14` — an invented flat rate | A complete progressive bracket engine |
| 3 | `stateRate` as a guessed "effective rate" | A real bracket table per state from a primary source |
| 4 | Comparison pages from cartesian combination (12,720 pages) | At most 15 manual, validated pages |
| 5 | The "wait and validate" checklist contradicted the 6-month timeline | Decision gates with numeric criteria, given calendar space |
| 6 | Numbeo as a data source | Public primary sources + a Methodology page |
| 7 | `index` and the column totals were inconsistent | No derived value is stored |
| 8 | The transport column used two different methodologies | Every field has one written, consistent definition |
| 9 | The insurance column carried unreal numbers | If we have no real data, the column is dropped |
| 10 | Distribution strategy in one line | Section 9-4 with channels, timing and a 30% share of project time |
| 11 | Keyword validation deferred to phase 2 | Month zero, before writing any page |
| 12 | No plan for the data going stale annually | A January update cycle + `nextReviewDue` + breaking the build |
| 13 | A $500-by-month-6 target with no computational basis | A revenue model with three scenarios and RPM working-backwards |
| 14 | No testing requirement for the tax logic | Section 4-7, non-negotiable |
| 15 | Guessed household multipliers `{single:1, couple:1.6}` | Four real filing statuses with a documented mathematical effect |

### 19-1. Round two — after keyword validation (2026-08-29)

These were faults in **my own rewrite**, revealed only by real data:

| # | Wrong assumption | Correction | Basis |
|---|---|---|---|
| 16 | The 51 state pages are the core of the project | 8 pages, a secondary layer | California 210/month, Texas 30/month |
| 17 | The tools are the second layer | The tools are the core | estimated tax calculator 27,100/month |
| 18 | The W-2 cluster is out of scope | Moved into phase 1 | 6× the market, the same engine, near-zero marginal cost |
| 19 | 15 state comparison pages | Deferred to phase 2 | State-level volume is far too low |
| 20 | A "six-month" timeline | A hard December 2026 deadline | Seasonality up to 46× |
| 21 | ~80,000 words of content | ~35,000 words | A consequence of the scope reduction |
| 22 | AI Overviews were absent from the document | Made an explicit design target | taxstra.com is cited above TaxAct |
| 23 | "$500 from the tax niche" | The self-employment niche caps at ~$250 | The traffic model, research document section 6 |

### 19-2. Round three — version 3.0

After the engine was built, the document's own gaps became visible:

| # | Gap | Fix |
|---|---|---|
| 24 | Section 4 described a design while the engine was already built | Section 4 rewritten; "the code is authoritative" made explicit |
| 25 | The engine's limitations were recorded nowhere | Section 4-8, eight limitations each with a plan |
| 26 | Tool pages — the core of the business — had no template | Section 8-8 |
| 27 | Calculator UX and defaults were unspecified | Section 8-9 — "it never opens empty" |
| 28 | "A consistent colour system" with no concrete values | Section 8-7 with real tokens |
| 29 | No URL rules — the origin of permanent redirects | Section 6-9, including "never a year in the URL" |
| 30 | Ad placement unspecified, despite being the revenue target directly | Sections 10-4 and 10-5 |
| 31 | The gates needed data but nothing was measured | Section 15 |
| 32 | The SERP finding stayed in the research document, never became strategy | Section 14 |
| 33 | Annual data staleness was called "a problem" with no runbook | Section 16 |
| 34 | No risk was written down | Section 17, with early warning signs |
| 35 | The directory structure did not match reality | Section 3-3 with ✅/⬜ markers |

### 19-3. Round four — version 3.1

One correct piece of pushback, which exposed a hidden assumption.

| # | Item | Outcome |
|---|---|---|
| 36 | The claim "cost of living is worth less" had never been measured | Measured: **3,600 searches a month**. The guess was right, but it was not an argument. Now it is |
| 37 | Cost of living moved from "deferred" to **rejected** | Low volume + an unsolved data source problem |
| 38 | **Hidden assumption:** expanding competes with the tax work for the same scarce resource | Rejected. The scarce resource is "verified tax data" and the simple-arithmetic cluster does not consume it |
| 39 | A 2.4-million "simple maths, high CPC" cluster was discovered | margin ($10.92) · ebay fee ($12.23) · fuel ($8.93) · compound interest (823k) |
| 40 | Splitting categories A and B by "is it the same audience" | Resolves the tension between expansion and topical authority |
| 41 | Layer A added to phase 1, **in parallel rather than after** | 4 tools, 38 pages instead of 34 |
| 42 | The head cluster went from 1.2 to 3.6 million | The share needed for $500 fell from 1.2% to **0.8%** |

### 19-4. Round five — version 3.2

| # | Item | Outcome |
|---|---|---|
| 43 | **My measurement error on cost of living** | Only the long tail had been measured (3,600). The head term is **60,500** — 17× more. The conclusion did not change but the reasoning became correct: the worst value-to-cost **ratio**, not an absence of demand |
| 44 | "Which tool is next?" had no systematic answer | [`tool-catalogue.md`](tool-catalogue.md) — 36 tools ranked by market value alongside build cost |
| 45 | The phase 1 inventory had never been counted | Section 6-0: **39 pages, 12 tools** |
| 46 | `hours calculator` is the catalogue's highest market value and was not on the map | Category A, high priority |

### 19-5. Round six — version 3.3

| # | Item | Outcome |
|---|---|---|
| 47 | **The third and final cost-of-living correction** | The full cluster is **158,000/month**, not 3,600 and not 60,500. The claim "the lowest value in the catalogue" was also wrong — it is mid-pack |
| 48 | The demand is in the **tool**, not the **pair page** | The comparison tool 49,500 · the best city pair 260. One excellent tool instead of thousands of pages |
| 49 | The data problem was not "unsolved" | BEA RPP · HUD FMR · BLS CPI · Eurostat — official, free, citable. **Better than Numbeo** |
| 50 | The city/country structure the user proposed was correct | The official data is published at exactly those levels |
| 51 | City pages are 10–17× better than the state tax pages | Stage 2.5 added to the roadmap |

**The methodological lesson of this round:** when rejecting a cluster, measure the head keyword **and** the cluster around it. Three consecutive underestimates, each from measuring a narrower slice of reality than existed.

### 19-6. Round seven — version 3.4

A document audit found five gaps, the most important of which the previous round had created itself.

| # | Gap | Fix |
|---|---|---|
| 52 | **Cost of living had zero mentions in 6 sections** — the document disagreed with itself | Engine (4-9) · data schema (5-5) · pages (6-8-1) · brief (7-2-3) · budget (12) · runbook (16-2-1) |
| 53 | **Cookie consent** had zero mentions — and Europe made it mandatory | Section 10-6 |
| 54 | No process for adding a tool existed, with 24 iterations ahead | Section 19 |
| 55 | The performance budget had no numbers | Section 12: 90KB of JS, 350KB total, with explicit prohibitions |
| 56 | The content brief covered only state pages — three quarters of the site had none | 7-2-1 tools · 7-2-2 guides · 7-2-3 city |
| 57 | No tone guide, with 35,000 machine-drafted words ahead | Section 7-6, including disclosure of machine assistance |

**The important design decision in 4-9-1:** for cost of living, **no dollar amount is invented for any city.** The official sources publish indices rather than dollar baskets; so the dollars come from the user's own numbers and we only apply the official ratio. This removes the original dataset's "fabricated insurance column" problem at the root.

### 19-7. Round eight — version 4.0 · the identity change

The user asked, with a screenshot of five tools: "these are very related and sit in one context, what do you think?" — and they had seen it correctly.

| # | Item | Outcome |
|---|---|---|
| 58 | The five tools were a **funnel**, not a list | Section 2-2-2: cost of living → comparison → salary → tax |
| 59 | **Session depth was in no model** | The models were `visits × RPM`. With the funnel, pages per session goes from 1.1 to 2.2 — **~2× revenue on the same traffic** |
| 60 | The core identity became one sentence | "The real cost of living in a place — and what you keep" |
| 61 | The context boundary became explicit | margin · ebay fee · budget · compound interest · investment **removed** |
| 62 | Freelancer tools moved from the core to the second cluster | Their engine stays, but they do not answer the core sentence |
| 63 | A 640k/month cluster with a weighted CPC of $3.47 | The share needed for $500: **~3%** (since recomputed to 672k at $3.51) |
| 64 | **The December deadline was removed** | It came from tax seasonality; the place cluster is seasonless |
| 65 | The tax engine went from a side tool to **the moat** | No competitor gives cost of living and tax together |

**Why this decision satisfies all three constraints at once:**

| Constraint | How it was met |
|---|---|
| $500–700 | A 640k cluster needing a 3–4% share — against the 65% the freelancer-tax version required |
| A single context | One sentence draws the boundary; five high-volume tools were removed because of it |
| Topical authority | Every page answers one question from one decision, and the internal links follow the funnel path rather than a random mesh |

**The lesson of this session:** eight rounds of course correction, and almost every one was triggered by the user's pushback rather than my analysis. The pattern that worked: **measure every claim before deciding** — I rejected this one cluster three times without adequate measurement and was wrong all three times.

### 19-8. Round nine — version 4.1 · precision and structure

The goal of this round: numbers from guesswork to computation, and the programmatic structure from description to specification.

| # | Item | Outcome |
|---|---|---|
| 66 | Numbers were scattered through prose and updated by hand | `data/keywords.json` is the single source · `scripts/model_revenue.py` builds the model · `docs/revenue-model.md` is the output |
| 67 | **The "month 18–24" estimate was optimistic** | The model, with a real position distribution and an AI Overview penalty: **year three**. The prose assumed a 3% share without asking when it arrives |
| 68 | The programmatic architecture was undefined | Section 6-8: entity model · 5 templates · generation gate · uniqueness budget · link graph · sitemap segmentation |
| 69 | "Every page must be unique" had no number | The uniqueness budget: ≥40% unique text · ≥3 facts from a primary source · ≤35% boilerplate, with build breaking |
| 70 | No criterion for "which metro earns a page" | The gate: ≥500 searches **and** BEA coverage **and** HUD coverage. A failing entity stays in the dataset but gets no page |
| 71 | A single sitemap, with indistinguishable indexation | Split into tools/places/states/guides — so gate 1 can say which **template** failed |
| 72 | Section 6 still carried the old identity's layers | Rewritten around the five funnel stages |
| 73 | The December deadline and the `/freelance-tax` paths were stale | Marked obsolete and corrected |

**This round's quantitative finding:** the sensitivity analysis showed **session depth is the single largest lever** — from 1.1 to 2.2 means **+105% revenue with no extra visit**. And it is the only variable entirely under our control; it depends on neither Google nor competitors. That promotes the funnel architecture from a UX preference to the most important product decision.

### 19-9. Round ten — version 4.2 · tool depth and SEO

An SEO audit exposed a serious inconsistency, and the user's screenshot exposed two unbacked promises.

**The core inconsistency:** section 14 said "quality alone is not enough, domain authority is the critical path" — and the entire link strategy had **1 mention** in the document. The diagnosis was right and there was no plan behind it.

| # | Item | Fix |
|---|---|---|
| 74 | External link building had 1 mention, despite being the critical path | A complete section 9-5: linkable assets · channels in order · a quantitative target · a 30% share of time |
| 75 | **The comparison did not include tax** | 4-9-5: without tax, the comparison is what Numbeo gives. The moat was disappearing |
| 76 | Household size was not in the engine | 4-9-6, from HUD FMR and BLS — **with no invented multiplier** |
| 77 | Social contributions had zero mentions | 4-9-7 — in Europe often larger than income tax itself |
| 78 | `property-tax-calculator` was missing | 22,200/month · and SmartAsset ranks with per-state pages — **direct evidence that the state programmatic pattern works** |
| 79 | There was no combined tool | `job-offer-comparison` — the whole funnel in one answer, the most linkable asset |
| 80 | Schema validation had zero mentions | 9-4-1 with a CI test and a `Dataset` type for the methodology |
| 81 | hreflang had zero mentions, despite Europe being in scope | 9-4-1, with no IP redirect |
| 82 | Directory pagination had zero mentions with 100+ metros | Semantic grouping instead of numeric pagination |
| 83 | Cannibalisation was treated superficially — and here the risk is real | Four pages chasing one keyword; four separation rules |
| 84 | `dateModified` was superficial | Only on a genuine content change |

**The guiding principle of this round:** for this project, **tool depth is itself the SEO strategy.** Competitors rank on domain authority, not quality; we have no authority and will not gain it quickly. The only route is a tool that earns links and gets cited in AI Overviews — and that tool has to be deeply better, not slightly better.

### 19-10. Round eleven — version 4.3 · the cannibalisation auditor

Cannibalisation moved from advice to an **automated CI check**: `data/pages.json` (the page-to-keyword map) + `scripts/audit_seo.py`.

The first run found **9 errors**. The two important ones shared a pattern:

| Pair | Similarity |
|---|---|
| `/tools/income-tax-calculator` ↔ `/state-taxes/{state}` | 67% |
| `/tools/cost-of-living-calculator` ↔ `/cost-of-living/{metro}` | 67% |

**A generic tool with a location selector, versus a specific place page.** Without a rule, the generic tool supporting all 51 states unintentionally competes with all 51 state pages — and because it is stronger, the state pages never rise. This is the trap almost every programmatic site falls into and it is invisible from the outside.

**Status then: 18 pages · 0 errors · 3 warnings** — three unmeasured keywords that had to be measured before building.

### 19-11. Round twelve — version 4.4 · warnings to zero

The auditor's three warnings were three unmeasured keywords. All three were measured:

| Keyword | Volume | Decision |
|---|---|---|
| `state income tax rates by state` | 3,600 | ✅ Confirmed — the state directory's target |
| `cost of living by city` | 880 | ✅ Confirmed — the city directory's target |
| `job offer comparison calculator` | **30** | ❌ **Page removed** — became a mode inside the comparison tool |

The third case shows the auditor doing its job: an idea I had called "the flagship" a round earlier turned out, on measurement, to have 30 searches a month. The capability is valuable and stays; its dedicated page does not.

**And two direct competitors were found, narrowing the moat claim:**

| Competitor | What it does |
|---|---|
| `costbycity.com` | Cost of living for 387 US metros using **BEA RPP** — our exact concept and our exact data source |
| `realtakehomepay.com` | Job offer comparison by take-home pay, 50 states |

I had previously written "nobody offers these together" without looking at the SERP for these keywords. Corrected. Three consequences: our data choice was independently validated · a small site can rank in this space · but we are not first, and our differentiation is the **intersection** of the two areas, not either alone.

**Status: 17 pages · 0 errors · 0 warnings.**

### 19-12. Round thirteen — version 4.5 · on-page SEO

The audit showed that section 9 had everything about **which** page targets **which** keyword and nothing about what that page **looks like** in search results:

| Topic | Before | Now |
|---|---|---|
| Title formula | 0 mentions | 5 templates, in `pages.json`, enforced |
| Meta description | 0 mentions | 5 templates + an English `metaHook` for 15 pages |
| Internal anchor text | 0 mentions | 4 rules |
| Concrete JSON-LD | 0 mentions | Per template |
| robots.txt | 0 mentions | 4 rules |
| OG image | 1 passing mention | Dynamic per entity, with its reasoning |

The auditor went from 6 checks to **10**, and the moment they were added it found two real defects:

1. **The meta would have been Persian.** I first wired the `output` field in as the meta text; `output` was an internal Persian description whose job is separating pages from each other. The result would have been 15 pages with Persian metas. A separate English `metaHook` was added.
2. **`Cost Of Living`.** Naive capitalisation also capitalised prepositions. The auditor now measures with the same casing rule that ships.

And it made one real constraint visible: with `San Francisco-Oakland-Berkeley, CA`, the PlacePage title reaches **59 of 60** characters. That template's pattern has room for no additional word, and CI now holds that line.

**Status: 17 pages · 10 checks · 0 errors · 0 warnings.**

### 19-13. Round fourteen — version 4.6 · the language boundary

The site was English and the spec Persian; until then that was only a remembered convention, and it had already broken once: the `output` field was an internal Persian description, and wiring it into the meta formula the round before would have produced 15 pages with Persian metas.

- All of `data/pages.json` and `data/keywords.json` were translated to English — 66 strings.
- `scripts/check_language.py` was added and runs in CI: any Persian character in `data/` · `src/` · `app/` · `public/` · `components/` · `content/` breaks the build.
- The boundary was recorded in section 9-3-5.

**Status: 66 shipping files · 0 Persian strings · 17 pages · 10 checks · 0 errors.**

### 19-14. Round fifteen — version 4.7 · one language across the project

The previous round drew a line between an English site and a Persian document. This round removed the line instead of policing it: the whole documentation set was translated to English.

**Why, given that `docs/` never ships and carried no SEO risk:**

- Every identifier the document discusses — field names, slugs, keywords, file paths, statutory citations — was already English. The prose around them was the only thing that was not, which made the document harder to search, harder to quote in a commit message, and harder to hand to anyone else.
- The user had asked for an external agent to review the specification. A reviewer, human or otherwise, reads the project in one language.
- A two-language project has a boundary that must be remembered. A one-language project does not have the boundary at all, and section 9-3-5's failure mode came from exactly that kind of remembered rule.

**What changed:**

- `docs/SPEC.md` (this document), `keyword-research.md`, `data-verification.md`, `tool-catalogue.md`, `revenue-model.md` and `README.md` translated in full.
- `scripts/model_revenue.py`'s output strings translated, so the generated `revenue-model.md` stays English when regenerated.
- `scripts/check_language.py` extended to cover `docs/` and `scripts/`, so the project is now single-language by enforcement rather than by intention.
- **`docs/archive/` is exempt.** Those are the three original specifications as they were written. Translating a historical record destroys it; the archive stays verbatim and is excluded from the check.

Persian numerals were converted to Western ones throughout, so figures in the document now match the figures in the datasets and script output they refer to.

**Status: the whole project in one language · 17 pages · 10 checks · 0 errors · 0 warnings · 59 tests green.**

---

*End of document. Any change to the decisions in section 2 requires revising this document, not a local patch.*
