# LifeCalc Pro — Single Reference Specification

> **Status:** This document replaces all three earlier specs. They are kept in `docs/archive/` for history only and are **not authoritative**.
> They contradicted each other in three places (static-first versus SPA, the anti-doorway checklist versus cartesian generation of comparison pages, and a 6-month timeline versus a "wait and validate" phase). This version resolves all three.
>
> **Last revised:** 2026-09-12 · **Version:** 5.14
>
> **Version 5.14:** The internal link graph was measured against demand for the first time rather than assumed from the declared rules, and it was badly misallocated — the highest-volume page in the project held 16% of the demand and 5% of the equity. A twentieth check now enforces the ratio. Details in 20-30.
>
> **Version 5.13:** The tool portfolio was rebalanced onto the stated identity. Rent, affordability and living wage did not exist in the spec at all; two overlapping tax tools were removed. The life side went from 20% of tool volume to 48%. Details in 20-29.
>
> **Version 5.12:** Author set (H.Hemati), the build-before-domain rule recorded (19-7), and the Base44 handoff brief written. Details in 20-28.
>
> **Version 5.11:** A ruthless audit, section 21. The headline: the BEA/HUD dataset blocks the funnel entrance, not just 24% of traffic — which puts roughly half of year-2 revenue behind it too. Plus no author identity (an AdSense blocker), and link building still has a section and no artifact.
>
> **Version 5.10:** All twelve tool bodies written — 553,600 searches a month covered, 58% median unique. Details in 20-27.
>
> **Version 5.9:** Four tool bodies written, covering 360,500 searches a month — the group that had zero while the 2,040-search group had four. Keyword check extended to every page with a cluster. Details in 20-26.
>
> **Version 5.8:** The pilot bodies were 46% unique and hit 0 of 5 target keyword variants — uniqueness rules with nothing pushing back. Fixed, enforced, and the trade-off measured. Details in 20-25.
>
> **Version 5.7:** All 51 take-home FAQ answers computed by the engine rather than left pending, and the four metros that pass the measurement gate generated. 78 of 78 buildable pages resolved. Details in 20-24.
>
> **Version 5.6:** The 43% body-uniqueness requirement was tested on four written state pages before committing to 61,000 words — 46% worst case, including two structurally similar states. Details in 20-23.
>
> **Version 5.5:** Thin content measured for the first time — the 51 state pages are ~80% identical furniture on scaffolding alone, and the body-copy requirement is now a number. Details in 20-22.
>
> **Version 5.4:** Platform requirements answered against a live Base44 app — R1, R3, R4, R5 verified; R2 and R8 recorded as inferred; R7 open. The 81-page plan stands. Details in 20-21.
>
> **Version 5.3:** Trust pages added (they were missing entirely), all 74 buildable pages now have generated on-page values, and a completion status per page group in 9-3-10. Details in 20-20.
>
> **Version 5.2:** On-page completed for a platform build — concrete JSON-LD, FAQ formulas, entity-to-field mapping, and a generator that resolves all 51 state pages. Details in 20-19.
>
> **Version 5.1:** Platform is Base44. Section 3 rewritten as nine numbered SEO requirements rather than a framework, with a runnable verification protocol (3-5) and written fallbacks (3-3). Details in 20-18.
>
> **Version 5.0:** On-page SEO closed — heading outlines, breadcrumbs, slug-to-head-term consistency and per-edge anchor text, all enforced. 18 checks. Building can start. Details in 20-17.
>
> **Version 4.9:** The keyword model made explicit and enforced — a page targets an intent cluster represented by a head term, not a single string. Plus the nine guides, previously invisible to every check. Details in 20-16.
>
> **Version 4.8:** The crawl-render-index stage of SEO, enforced — click depth, orphans and funnel cul-de-sacs are now computed from a declared link graph. Plus the five sections that had not caught up with the version 4 identity change, and a deployment/launch/recovery section. Details in 20-15.
>
> **Version 4.7:** The whole document set moved to English. The site is English, the data is English, and now the spec is too — one language across the project, and reviewable by anyone. Details in 20-14.
>
> **Version 4.6:** The language boundary became enforceable — every shipping file is English, gated by `check_language.py` in CI. Details in 20-13.
>
> **Version 4.5:** Title/meta/H1 formulas per template, internal anchor text, per-template JSON-LD, robots and OG image — all as data in `data/pages.json` and enforced in CI. Details in 20-12.
>
> **Version 4.2:** Tool depth (tax inside comparison · household size · social contributions) · two new tools · and six SEO gaps, the largest of which was external link building. Details in 20-9.
>
> **Version 4.1:** Numbers moved from prose to reproducible computation (`data/keywords.json` + `scripts/model_revenue.py`); the programmatic architecture gained an entity model, a generation gate, a uniqueness budget and a link graph; section 6 was rewritten around the funnel. Details in 20-8.
>
> **Version 4:** The core identity changed to "the real cost of living in a place — and what you actually keep". The tools are a funnel, not a list; session depth entered the revenue model; the context boundary became explicit and five tools outside it were removed. Details in section 20-7.
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
| 13 | Data status and verification | Tax ✅ extracted · ⬜ verified · Cost of living ⬜ not acquired |
| 14 | Competitive position | |
| 15 | Measurement and instrumentation | |
| 16 | Annual update runbook | |
| 17 | Risks | |
| 18 | Process for adding a new tool | |
| 19 | Deployment, launch and recovery | |
| 21 | Ruthless audit (2026-09-12) | |
| 20 | Changelog | |

### Related documents

| Document | Role |
|---|---|
| [`keyword-research.md`](keyword-research.md) | Demand validation; the basis for sections 6 and 14 |
| [`data-verification.md`](data-verification.md) | Verification checklist; the basis for section 13 |
| [`onpage-spec.md`](onpage-spec.md) | **Generated** — the resolved on-page values for all 74 buildable pages (9-3-9) |
| [`base44-questions.md`](base44-questions.md) | The platform questions that settle requirements R1–R9 (3-1, 3-5) |
| [`copywriting.md`](copywriting.md) | How to write copy that clears the uniqueness budget — derived from measured pilot pages (7-6) |
| [`base44-build-brief.md`](base44-build-brief.md) | **The handoff document** — what to build, and what not to improvise |
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
| **Platform** | **Base44**, subject to the verification in 3-5 | Chosen by the project owner. The SEO requirements it must satisfy are stated as R1–R9 in 3-1, and are non-negotiable whatever the platform |
| **Data sources** | **Primary public sources only** (IRS, each state's revenue department, BLS, HUD) | Legally sound, differentiating, and the foundation of the Methodology page |
| **Numbeo** | **Not used** | Its terms of service forbid redistribution; and copying a competitor's data carries zero SEO advantage |
| **Comparison pages** | Deferred to phase 2 | State-level search volume is so low that state-vs-state comparison is unjustifiable (section 6-7) |
| **Revenue model** | AdSense only in phase 1 | Tax affiliate offers (accounting software) get evaluated in phase 2 |
| **Final destination** | **A financial calculator hub**, not a general "life" hub | Section 2-2 |
| **Domain** | A single site | — |
| **Exact-match domain** | Neutral. Not a ranking strategy | See below |

#### A note on the exact-match domain

An exact-match domain — one whose name is the target keyword — carried real
ranking weight until Google's 2012 EMD update, which was built specifically to
remove it. Today it is close to neutral as a ranking signal.

**What it still does give**, and these are real:

- A modest click-through advantage in the SERP, because the domain matches what
  the user typed.
- Natural anchor text: when someone links to the site by name, the link carries
  the keyword without anyone engineering it. Section 9-5's link building benefits
  from this at no cost.

**What it does not give:** a shortcut past any of the requirements in this
document. And there is one asymmetry worth stating plainly, because it inverts
the intuition:

> **An exact-match domain makes thin content more dangerous, not safer.** A
> keyword domain over near-duplicate generated pages is the precise pattern the
> EMD update and the 2024 scaled-content-abuse policy were written to catch. The
> domain raises the site's profile against exactly the filter it is least able to
> survive.

The conclusion is not to change the domain. It is that the uniqueness budget in
6-10-4 matters *more* here than it would on a brand domain — which is why it is
now measured rather than asserted.

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
| **1 — Place** | cost-of-living calculator · rent affordability · comparison · 5 sample cities → 25–30 | Funnel entrance, highest volume |
| **2 — Income** | salary comparison by city · salary↔hourly · living wage | "What do I need / what do I keep" |
| **3 — Tax by place** | state income tax (51 jurisdictions, engine ready) · sales tax · property tax · take-home pay | **The moat** — the cluster's highest CPC |
| **4 — International** | country income tax · country-level European cost of living | An extension of the same funnel |
| **5 — Settling** | home affordability · house payment · closing cost in a city | The end of the funnel |
| **Second cluster** | Freelancer tools | Only after the core is established |

**Two ordering rules:**

1. **No tool ships before the tools of the stage above it.** The funnel does not work without its early links; a take-home page without a cost-of-living page is just one more calculator.
2. **City pages expand through a gate** — 5 samples, then 25–30. Never all at once.

> **The December deadline was removed.** That deadline came from tax seasonality (up to 46×). The place cluster is close to seasonless, so the project is no longer "December or nothing". Tax season still gives a spike, but the project's failure is no longer tied to it.

---

### 2-4. Cost of living — data and page shapes (now the core, not stage 2.5)

> This cluster went from "rejected" to **the core of the project**. Its path is recorded in sections 20-5 and 20-7.

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

### 3-1. Requirements first, platform second

The earlier version of this section named a framework. That was a mistake of
altitude: the framework was never the decision, it was one way of satisfying the
decision. **The platform is Base44.** What follows separates what must be true
from what happens to satisfy it, so that a platform change is a change of one
section rather than a rewrite.

#### The non-negotiable requirements

Every one of these is a ranking or indexation requirement, not a preference:

| # | Requirement | Why it cannot be traded away |
|---|---|---|
| R1 | **Indexable content is present in the HTML the server returns**, before any JavaScript runs | The single most consequential SEO property of the whole build. See 3-2 |
| R2 | **Per-page `title`, `meta description` and `canonical` in that same initial HTML** | Formulas in 9-3-2 are worthless if they render after hydration |
| R3 | **Per-entity values for all of the above across ~81 generated pages** | 30 metros and 51 states, each unique. A per-page manual panel does not scale to this |
| R4 | **JSON-LD per template**, in the initial HTML (9-3-3) | Structured data that renders late is structured data Google may never read |
| R5 | **Clean path URLs**, no hash routing, no trailing slash, lowercase (6-7) | Hash fragments are not separate URLs to a crawler |
| R6 | **Controllable `sitemap.xml` and `robots.txt`**, with the segmentation in 6-8-6 | Gate 1 is read per template; one flat sitemap makes it unreadable |
| R7 | **A real HTTP 404** on unknown paths (9-6-5) | Soft 404s at scale poison a whole directory |
| R8 | **Per-entity Open Graph images and tags in the initial response** (9-3-4) | Social crawlers do not execute JavaScript at all |
| R9 | **Custom domain**, not a platform subdomain (10-1) | AdSense approval and authority both depend on it |

#### Requirement status — answered 2026-09-06

The contradiction in the public sources was settled against a **live Base44 app**,
not against documentation. The distinction between what was observed and what was
reasoned is kept, because it decides what still needs testing.

| # | Requirement | Status | Evidence |
|---|---|---|---|
| R1 | Content in the server's HTML | ✅ **Verified** | The live source of a country page was fetched: H1, body copy, stat cards and city cards all present in the HTML. Not an empty shell |
| R2 | Per-entity meta in that HTML | ⚠️ **Inferred** | Reasoned from R1 — "the metadata goes the same way". The `<title>` tag itself was not observed in raw HTML. See below |
| R3 | Values from row data, at scale | ✅ **Verified** | Titles are built from the row (`Cost of living in ${country.name}`). No dashboard entry, no bulk import, no 80 hand-typed pages |
| R4 | Custom JSON-LD per entity | ✅ **Verified** | The `Seo` component takes a `jsonLd` prop and injects a `<script type="application/ld+json">`. Any schema, values per row. An FAQ block already ships on one template |
| R5 | Clean path URLs | ✅ **Verified** | Path routes, no hash |
| R6 | Sitemap and robots | ✅ Per platform | Managed by the platform; segmentation (6-8-6) still to confirm |
| R7 | Real HTTP 404 | ❌ **Unknown** | A 404 page renders visually, but the HTTP **status code** could not be confirmed from inside the app. This is the soft-404 risk in 9-6-5 |
| R8 | Social crawlers get per-entity OG | ⚠️ **Inferred** | Reasoned from the `Seo` component setting `og:*`. Not tested against a social user-agent. See below |
| R9 | Custom domain | ✅ Supported | But whether `*.base44.app` stays publicly indexable afterwards is **unknown** |

**The architecture is sound.** R3 in particular is the answer this project needed:
metadata is derived from the same row as the content, so the annual tax update
(section 16) changes 51 titles by editing one dataset rather than 51 dashboard
fields. That is the programmatic architecture this document specifies, working as
specified.

#### Why R2 and R8 are marked inferred rather than verified

Both answers reason from the same premise: the `Seo` component sets the tags, and
Base44 pre-renders. R1 confirms pre-rendering delivers **body content**. It does
not, by itself, confirm it delivers **`<head>` tags** — those are set in a
`useEffect`, which is a different execution point from the component's render
output, and a pre-renderer can capture one without the other.

For R8 the gap is wider. Social crawlers **never execute JavaScript at all**, so
whether they see per-entity `og:` tags depends entirely on whether the
pre-rendering layer covers their user-agents. That was not tested, and it is
precisely the failure the platform's public feedback board reports.

Neither is a reason to doubt the answer. Both are a reason to spend two minutes
confirming it, because the cost of being wrong is 81 pages sharing one title.

#### The conditional that matters most

The answers carried a caveat worth promoting to a build rule:

> Correct metadata depends on **every** programmatic page calling the `Seo`
> component **with values from its own row**. A page that omits it, or calls it
> with constants, ships duplicate or empty metadata.

**This is not a platform guarantee — it is a per-page obligation**, and it is
exactly the kind of thing that holds on the two pages someone checked and fails
silently on the thirtieth. It is now rule 3-7-7, and section 3-5's protocol exists
to catch it.

### 3-2. Why R1 is the requirement everything else rests on

A client-rendered page returns an effectively empty HTML shell and constructs its
content after JavaScript executes. Google does render JavaScript — but rendering
happens in a **second, separate queue**, after crawling, and it is deferred and
budgeted. For an established domain this costs days. For a new domain with no
authority and ~110 pages, it is the difference between being indexed in weeks and
being indexed partially, slowly, or not at all.

This is not a theoretical concern for this project specifically:

- **Gate 1 (section 11-1) measures indexation of 5 sample pages after 3–4 weeks.**
  If rendering is deferred, that gate reads as failure and the roadmap stalls on a
  platform artifact rather than a content problem.
- **Section 14 concluded that domain authority is our binding constraint.** A
  rendering penalty compounds precisely where we are weakest.
- **Social crawlers never execute JavaScript at all.** Section 9-5 earns links on
  Reddit and forums, and 9-3-4 makes OG images a deliberate part of that. If R8
  fails, the link-building strategy loses its surface.

**The hard rule stands regardless of platform:** if `curl` on a URL does not
return the content, that page has a bug. The rule has not changed since the
first version of this document. Only the thing being tested has.

### 3-3. What is left open, and the fallback for each

After the 2026-09-06 answers, most of this section's original options are moot.
The platform meets the architectural requirements. What remains:

| Open item | If it fails | Cost |
|---|---|---|
| **R7 — 404 returns 200** | Soft 404s across the directory. Mitigate by never linking to a non-existent entity (the generation gate in 6-10-3 already guarantees this) and by returning a `noindex` on the not-found view if the status cannot be fixed | Low, if caught |
| **R9 — `*.base44.app` stays indexable** | The whole site indexed twice, authority split. Mitigate with the absolute self-canonical every page already carries (canonicalRules[0]), which points at the custom domain from both hosts | **Largely already handled** — this is what an absolute canonical is for |
| **R2/R8 unconfirmed** | If `<head>` tags are not pre-rendered, add a pre-render layer for crawler user-agents. The page content is already fine, so this is a narrow fix rather than a re-platform | Medium |
| **Sitemap segmentation (6-8-6)** | One flat sitemap makes gate 1 unreadable per template. Mitigate by reading Search Console's per-directory coverage instead | Low |

**The "split the surface" and "reduce the programmatic surface" fallbacks are
withdrawn.** They existed because R1 and R3 were unknown; both are now verified,
and the 81-page plan stands.

### 3-4. What is platform-independent, and therefore already done

Worth stating plainly, because it is most of the work:

`data/pages.json` · `data/keywords.json` · the keyword clusters · the title, meta
and H1 formulas · the H2 outlines · breadcrumbs · anchor text · the link graph ·
the canonical rules · the JSON-LD shapes · `scripts/audit_seo.py` (18 checks) ·
`src/lib/tax/` (59 tests) · the tax dataset for 51 jurisdictions.

**None of it assumes a framework.** It is a specification of what each page must
contain, which is as valid against Base44 as against anything else. The platform
question is only ever *how* these values reach the HTML.

### 3-5. The three checks still worth running

Most of the protocol this section used to hold has been answered (3-1). Three
things remain, and together they take about two minutes against any live page.

```bash
URL=https://your-app/cost-of-living/germany
OTHER=https://your-app/cost-of-living/japan

# R2 — is the <title> in the raw HTML, and does it differ per row?
curl -s "$URL"   | grep -o "<title>[^<]*</title>"
curl -s "$OTHER" | grep -o "<title>[^<]*</title>"

# R8 — does a social crawler get the per-entity tags? It never runs JavaScript,
# so this is a different question from R2, not the same one.
curl -s -A "facebookexternalhit/1.1" "$URL" | grep -o 'property="og:title"[^>]*'

# R7 — the status code, not the visible page
curl -sI https://your-app/definitely-not-a-real-page | head -1
```

| Result | Meaning |
|---|---|
| Two different `<title>` values | R2 confirmed. The 81-page plan is fully unblocked |
| Same or empty `<title>` | The `useEffect` is not pre-rendered — a crawler pre-render layer is needed for `<head>` only |
| `og:title` shows the entity name | R8 confirmed |
| `og:title` generic or absent | Social previews are app-level. Section 9-5's link building loses its preview surface; fix with the same pre-render layer |
| `HTTP/2 404` | R7 confirmed |
| `HTTP/2 200` | Soft 404. Apply the 3-3 mitigation |

**Then, whatever the result, verify the per-page obligation** from rule 3-7-6:
after building the programmatic pages, check the rendered `<title>` on **three
different rows**, not one. The caveat in 3-1 fails silently on the page nobody
checked, and a single sample cannot detect it.

### 3-6. Repository structure

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

  lib/cost-of-living/          ⬜ the second engine (section 4-9)
    indices.ts                    category scaling from official index ratios
    household.ts                  HUD FMR + BLS household size, no invented multipliers
    compare.ts                    two places, including the tax difference (4-9-5)
    load.ts  __tests__/
  data/cost-of-living-2026/    ⬜ blocked on BEA/HUD access (section 13-6)

```

**The application itself lives in Base44, not here.** This repository is the
source of truth for the two things a platform cannot own:

| Here | Why it stays here |
|---|---|
| **The engines** (`src/lib/`) | Tested to the cent against statute. Rule 3-7-1 says tax logic lives in one place, and that place is version-controlled and covered by 59 tests |
| **The datasets** (`src/data/`) | Every number carries a primary source and a verification state (section 5) |
| **The page specification** (`data/pages.json`) | Keywords, clusters, formulas, link graph, anchor text — 18 CI checks |
| **The auditors** (`scripts/`) | They fail the build. A dashboard cannot |

The page routes described in section 6-7 are built on the platform. **Their
required contents are specified here**, and that separation is deliberate: it is
what makes section 3-3's fallbacks possible without rewriting the project.

### 3-7. Fixed technical rules

1. **Single source of truth:** no tax calculation is written outside `src/lib/tax/`. The UI only takes inputs and renders outputs — and this rule binds harder on a platform that invites logic into the page, because a calculation reimplemented in a component is one nothing tests.
2. **Data separate from logic:** rates and thresholds live in JSON, not in code. Changing tax year must not require changing logic.
3. **Tax year is a parameter:** every function takes `taxYear`. No year is ever hardcoded.
4. **Everything in integer cents:** internal calculation runs on integer cents so floating-point error cannot accumulate; conversion to dollars happens only at the display layer.
5. **No runtime network dependency for a calculation:** a result must never wait on a network round-trip. It is instant, it works offline, and no financial figure the user types leaves the browser — which section 10-6 makes a privacy claim on the `/privacy` page.
6. **Every programmatic page calls the SEO component with values from its own row.** Never omitted, never called with constants. Metadata correctness is a per-page obligation on this platform, not a platform guarantee (3-1), and a page that forgets it looks fine and ships a duplicate title.
7. **The specification in `data/pages.json` is authoritative over anything typed into a platform dashboard.** If a page's title in the dashboard disagrees with the formula here, the formula is right and the dashboard is drift. This is the rule that keeps 18 CI checks meaningful once the pages live somewhere the auditor cannot see.

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

Phase 1 total: **39 pages** (not the 75 initially estimated). Exact count in section 6-0. The keyword-targeted subset of those is mapped in `data/pages.json` — 18 pages, audited in CI.

> 📊 **The full data-driven tool catalogue: [`tool-catalogue.md`](tool-catalogue.md)** — 36 tools measured, 3.7 million monthly searches, ranked by "market value = volume × CPC" alongside build cost. That document decides **which tool comes next**; this section only covers phase 1.

### 6-0. Core inventory

| Stage | Pages | Count |
|---|---|---|
| 1 — Place | cost-of-living-calculator · rent-affordability-calculator · cost-of-living-comparison · city pages | 3 + (5 → 30) |
| 2 — Income | salary-comparison-by-city · salary-to-hourly · living-wage-calculator | 3 |
| 3 — Tax by place | state pages + directory · sales-tax · property-tax · take-home-pay | 4 + (8 → 51) |
| 4 — International | income-tax-calculator · European country pages | 1 + later |
| 5 — Settling | home-affordability · house-payment · closing-cost | 3 |
| Guides | Around the funnel, not freelancer tax | 8 |
| Trust pages | About · Methodology · Sources · Editorial · Privacy · Terms · Contact | 7 |
| Home + tool index | | 2 |
| **First-release total** | | **~43** |
| Behind gates | City pages 5→30 · state pages 8→51 | up to ~110 |

**The guides changed too.** They used to be about freelancer tax (deductions, home office, S-Corp). Now they follow the funnel: "what salary do you need to live in X" · "which states have no income tax" · "how sales tax changes the cost of living" · "what gets left out of a cost-of-living calculation".

### 6-1. Pages by funnel stage

Every page belongs to one of the five funnel stages. A page belonging to no stage **is not built** — that is the simplest test of the context boundary.

#### Stage 1 — Place

| Path | Target keyword | Volume |
|---|---|---|
| `/tools/cost-of-living-calculator` | cost of living calculator | 60,500 |
| `/tools/rent-affordability-calculator` | rent affordability calculator | **90,500** |
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
| `/tools/salary-comparison-by-city` | salary comparison by city | ~8,000 |
| `/tools/living-wage-calculator` | living wage calculator | 12,100 ($6.36 CPC) |

#### Stage 4 — What you keep *(the moat)*

| Path | Target keyword | Volume | CPC |
|---|---|---|---|
| `/tools/sales-tax-calculator` | sales tax calculator | 110,000 | **$6.91** |
| `/tools/property-tax-calculator` | property tax calculator | 22,200 | $3.37 |
| `/tools/income-tax-calculator` | income tax calculator | 90,500 | $2.13 |
| `/tools/take-home-pay-calculator` | take home pay calculator | 60,500 | **$5.69** |
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

#### Country versus country — a mode, not a page

If the site compares two cities and publishes country pages, a user will expect to
compare two countries. That is a real gap and the instinct behind it is right.

**The engine is not the obstacle.** The comparison arithmetic is identical, and
Eurostat publishes comparative price levels at country level exactly as BEA does at
metro level.

Three things are:

1. **Zero measured volume.** Not low volume — unmeasured. Rule 18-1 forbids
   building for an unproven target, and this document has been wrong three times by
   assuming volume it had not checked (section 20-5).
2. **The Eurostat dataset does not exist yet**, and it sits behind the BEA/HUD work
   which is already the critical path.
3. **Within one data region only.** A US metro cannot be compared to a European
   country — BEA and Eurostat use different bases, and running the arithmetic anyway
   produces a confident wrong answer, which is worse than no answer (4-9-3).

There is also an economic asymmetry worth naming: **international traffic carries
materially lower AdSense RPM than US traffic.** A country comparison is therefore
worth less per visit than its search volume implies. That does not make it wrong;
it raises the bar for building it rather than lowering it.

**Decision:** build it as a **third mode of the existing comparison tool**, never
as a page of its own, and only after the head keywords are measured and the
Eurostat dataset exists. Recorded in `data/pages.json → plannedModes`.

**The precedent is job-offer comparison** (6-1). It was an appealing idea, measured
at 30 searches a month, and became a mode rather than a page. A mode costs no URL,
creates no cannibalisation risk and cannot become a thin page — which is why it is
the right shape for any capability whose demand is not yet proven.

#### Stage 5 — Settling

| Path | Target keyword | Volume | CPC |
|---|---|---|---|
| `/tools/home-affordability-calculator` | home affordability calculator | 49,500 | $2.51 |
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

`scripts/validate_content.py` measures these ratios and runs in CI — the same
pattern as `validate_tax_data.py`. A token counts as boilerplate when it appears
on 80% or more of a template's pages.

#### What the measurement actually said

The script was written after an audit found that this section had promised it for
several revisions while nothing enforced it. Its first run, against the generated
scaffolding:

| Template | Pages | Median unique | Worst |
|---|---|---|---|
| TrustPage | 7 | 90% | 90% |
| DirectoryPage | 3 | 67% | 61% |
| ToolPage | 12 | 62% | 56% |
| **StateTaxPage** | **51** | **21%** | **16%** |

**The 51 state pages are about 80% identical furniture**, on the scaffolding
alone. That is the doorway shape this section exists to prevent, and every other
check in the project passed while it was true — cannibalisation, canonical,
titles, anchors, crawl depth, all clean.

The measurement is of scaffolding only, because no body copy exists yet. That is
the useful moment to take it: **it converts "write good unique content" into a
number.**

| Body length | Required uniqueness of the body itself |
|---|---|
| 900 words | **44%** |
| 1,200 words | **43%** |
| 1,400 words | **42%** |

So a state page's body copy must be **at least ~43% words that no other state
page uses**. That is a demanding bar and it is meant to be: it rules out
paraphrasing one article 51 times, and it is met by the material section 7-2
already requires — that state's own bracket structure, its own local tax rules,
its own filing deadlines and authority, pulled from its own revenue department.

**The threshold judges the finished page.** Before body copy exists the script
warns rather than fails; once `--bodies` points at real copy, the same threshold
breaks the build.

#### Uniqueness and keyword targeting pull against each other

The validator checks both, because optimising for one alone breaks the other. That
is not theoretical — it happened:

> **The four pilot bodies scored 46% unique and contained 0 of their 5 cluster
> variants.** Four pages that were genuinely good and did not target their own
> keyword.

The cause was structural. Every uniqueness rule pushes toward varied phrasing, and
nothing pushed back. A writer following them says "Maryland's schedule" and never
writes "Maryland tax brackets" — the phrase people actually search.

So `contentBudget.minVariantsInBody` requires **at least two** cluster variants in
the body, and the cost of that was measured: adding two per page moved uniqueness
from 45%/43% to 44%/42%, roughly half a point per variant, because a phrase on
every page is shared vocabulary by definition.

**Two is where the trade sits.** Five variants per page would cost about two and a
half points and leave the worst page at roughly 40% — on the threshold with
nothing spare. The floor is a guard against forgetting, not a density target.

#### 6-10-4-1. The pilot — the requirement was tested before 61,000 words were written

Writing 51 bodies and then discovering the approach cannot clear 43% would be the
most expensive possible way to learn it. Four were written first and measured.

**Experiment design matters more than the result here.** Measuring a few written
pages against many unwritten ones scores them falsely high — their body words are
trivially absent from pages that have no body. The script therefore has a
`--pilot` mode that compares only pages that have copy, against each other.

| Set | Median unique | Worst |
|---|---|---|
| 3 states, maximally different structures (progressive · flat · none) | 45% | 45% |
| **4 states, adding one structurally similar to an existing one** | **47%** | **46%** |

The second row is the real test. New York and Maryland are both progressive, both
with a local income tax layer, both without a meaningful state standard deduction
— the pair most likely to collapse into paraphrase. **Uniqueness rose rather than
fell**, which says the differentiation is coming from substance rather than from
the accident of picking dissimilar states.

##### What made them different — the transferable pattern

Every one of the four leads with **the structural fact that characterises that
state**, not a generic opening:

| State | The fact the page is built around |
|---|---|
| New York | Nine brackets, but the first four are exhausted in a fortnight; the real question is the city line |
| Pennsylvania | A flat 3.07% that conceals two things — no standard deduction at all, and a local earned income tax nearly everywhere |
| Texas | The absence is structural; the interesting question is what replaces it and for whom that is a good trade |
| Maryland | Ten brackets that behave like one, because 4.75% runs unbroken to $100,000 — and **every** county levies on top |

And each carries **a section that could not exist on another state's page**: the
city line for New York, Philadelphia's Net Profits Tax for Pennsylvania, the
property-versus-income trade for Texas, the word "every" for Maryland.

**That is the rule this pilot produces:** a state page must contain at least one
section that would be factually wrong or meaningless if the state name were
swapped. A page that survives a find-and-replace is the doorway page section 7-1
forbids, whatever its uniqueness score says.

##### The honest limitation

The four bodies run about 550 words each; section 7-2 specifies 900–1,400. The
pilot proves the ratio is achievable, not that it survives being stretched. Length
added without state-specific substance dilutes uniqueness rather than adding to
it, so the remaining words must come from the same source as the first 550 — that
state's own brackets, its own local rules, its own deadlines and authority — and
the CI check is what will say whether they did.



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

**The find-and-replace test**, from the pilot in 6-10-4-1: at least one section of
every state page must be **factually wrong or meaningless if the state name were
swapped**. A page that survives a find-and-replace is a doorway page whatever its
uniqueness score says, and the score is a floor rather than the standard.

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

**These are principles. The working guide is [`docs/copywriting.md`](copywriting.md)**,
which turns them into a section-by-section playbook with measured targets, a list
of constructions that are never used, and the research method for finding an
entity's angle before writing. It is derived from four pages that were written and
then measured, not from general advice.

**One finding from it belongs here, because it changes this section's numbers:**
uniqueness *falls* as length rises. The same four bodies scored 46% worst at ~530
words and 43% worst at ~800. The added material was genuinely entity-specific and
the ratio still slipped, because every paragraph also adds shared vocabulary. So
the target inside 7-2's 900–1,400 range is **the bottom of it**: 900 dense words
beat 1,400 where the last 500 are general.

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
- A dynamic OG image per state, in the initial HTML response (requirement R8) — for sharing on Reddit and social networks

### 9-2. Keyword validation **before** writing

The previous document said phase 2 would be data-driven, "not guesswork" — which was an admission that phase 1 was entirely guesswork. The correction:

- [ ] Before writing a single page, check **30 primary keywords** against real volume and difficulty data
- [ ] For each keyword, actually look at the top 10 results: if they are all high-DR domains and major tax brands, that keyword is not reachable in year one — go long-tail
- [ ] The output of this step is a prioritised list that sets the writing order for the 51 states (California and Texas before Wyoming)

### 9-2-1. One page targets an intent cluster, not one keyword

This is the model, and it had been assumed rather than written down:

> **A page targets a group of phrasings that mean the same thing, represented by
> a head term.** The head is what goes in the title and H1; the group is what the
> page is expected to rank for.

Google matches by intent, not by string. One page routinely ranks for hundreds
of phrasings of one question, and writing a separate page per phrasing is the
fastest way to build a doorway farm. So the unit of planning is the cluster.

**The document had been carrying the wrong model in its data.** Before this was
written down, `data/pages.json` held one `primary` per page and a total of
**three** secondary keywords across eighteen pages — ten pages had none at all.
That is "one page = one string", and it has three costs: the long tail is
unplanned, the content brief cannot know which phrasings to cover naturally, and
the cannibalisation check can only compare head terms.

Each page now declares:

```jsonc
"cluster": {
  "intent":  "From a gross salary, what is my annual and monthly net",
  "variants": ["net pay calculator", "after tax income calculator", …],
  "variantsMeasured": false
}
```

#### The rules, enforced by `scripts/audit_seo.py`

| Rule | Why |
|---|---|
| Every page with a head term declares a cluster, with **≥3 variants** | A head with no expansion means the long tail is unmapped |
| Every cluster states its **intent** in a sentence | Intent is the real axis; the string is a proxy |
| **No two pages state the same intent** | Same intent means one page, whatever the keywords say |
| A term appears in exactly **one** cluster, site-wide | The plain definition of cannibalisation |
| A variant is never another page's **head term** | The worst version of the same thing |
| An entity-qualified variant belongs to the **entity page** | The generic/entity rule (9-4-1): `{state} paycheck calculator` is the state page's, not the paycheck tool's |
| Head in the title and H1; **variants in H2s, FAQ and body only** | A title stuffed with variants ranks for none of them |

#### Intent is a better axis than lexical similarity

The existing check compares head terms by token overlap (≥30% must declare
distinct outputs). That catches `income tax calculator` versus `paycheck tax
calculator`, but it is a proxy and it fails in both directions:

- **Lexically distant, same intent.** "what will my paycheck be" and "take home
  pay calculator" share almost no tokens and are the same question.
- **Lexically close, different intent.** "gross pay vs net pay" and "net pay
  calculator" overlap heavily; one wants a definition, the other a number.

The stated `intent` field is what separates these, and the identical-intent check
is the one that would catch the first case. Lexical similarity is kept as a cheap
first pass, not as the answer.

#### Variants carry no volume, deliberately

**The variants are linguistic expansions of the head term. They are not
measured, and they carry no numbers.** `scripts/model_revenue.py` continues to
compute from measured head terms only.

This is the conservative choice and it is deliberate. The real addressable volume
of a page is its whole cluster, which is larger — often materially — than its
head. Writing an estimated multiplier into the model would raise every projection
in section 1-4 without a single new measurement behind it. This document has
been wrong three times by asserting keyword numbers it had not checked (section
20-5), so the audit **fails the build if any page claims its variants are
measured** while no variant volume exists in `data/keywords.json`.

The practical reading: **the revenue model in 1-4 is a floor, not a forecast.**

### 9-2-2. Pages that do not exist yet are planned, not unplanned

The nine guides in section 6-2 are the main external-link asset (9-5-2) and were
invisible to every check, because they were prose in this document and nothing
else. They are now declared in `data/pages.json → plannedPages` with a proposed
head and a stated intent, exempt from the measured-target rule until promoted,
but **not** exempt from collision checks.

That check found a real collision immediately: the planned guide "states with no
income tax" was **the same query the `/state-taxes` directory already owns**. A
list query, answered by a page that is a list. The guide was retargeted to the
question the directory cannot answer — *do* no-income-tax states cost less, once
sales, property and local tax are counted — which is both non-duplicative and a
better guide, and is one our two engines can answer with computed numbers.

A second overlap was legitimate: `gross pay vs net pay` shares tokens with `net
pay calculator` without sharing intent. For that case a planned page may declare
`overlapsAcknowledged` — but the audit requires a **substantive written reason**
and fails on a one-word one. An overlap can be argued; it cannot be waved away.

**Promotion rule:** a planned page becomes a real page only after its head term
is measured into `data/keywords.json` and its cluster passes every check.

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
- **A dynamic OG image** per entity (requirement R8): the place name and its index number on the image. This is not decoration; section 9-5 earns links on Reddit and forums, and a link without an image is effectively invisible there.
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

### 9-3-6. Heading structure and breadcrumbs

The title and H1 formulas (9-3-2) covered the top of the page and nothing below
it. For 104 generated pages the H2 outline is what makes a page rank for its
whole cluster rather than only its head term, because **the variants live in the
H2s, the FAQ and the body — never in the title**.

Declared per template in `data/pages.json → onPage.templates.h2Outline`:

| Template | Outline |
|---|---|
| ToolPage | How {Primary} is calculated · What this does not include · Who needs this · FAQ |
| PlacePage | What it costs to live in {Metro} · What the indices mean · **{State} income tax on your salary** · Who {Metro} suits · How we calculate this · FAQ |
| StateTaxPage | How {State} income tax works · {State} tax brackets · Local tax in {State} · Filing and deadlines · FAQ |
| DirectoryPage | The full list · How to read these numbers · FAQ |

Enforced:

- **One H1, and it is the head term.** No H2 repeats it — a heading that restates
  the title adds nothing and reads as stuffing.
- **Headings never skip a level**, H1 → H2 → H3.
- **An entity template must name its entity in at least one H2**, or all 30 place
  pages ship an identical outline — which is the doorway pattern in a different
  costume.
- **FAQ heading and FAQPage schema are coupled in both directions.** A template
  declaring the schema without a visible FAQ violates Google's guidelines; a
  visible FAQ with no schema wastes the People Also Ask surface. The audit fails
  on either.

Breadcrumbs are declared per template and must match the URL hierarchy and the
`BreadcrumbList` JSON-LD exactly — a mismatch between the two is a structured-data
error Google reports. The final crumb is the current page and is not a link.

### 9-3-7. Anchor text, enforced per link

Section 9-3-1 stated four anchor rules and nothing checked them. The link graph
now carries anchor text on **every edge**, and the audit enforces:

| Rule | Failure it prevents |
|---|---|
| Written with the **destination's** head term | A link that shares nothing with its target passes no signal |
| **Never contains the source page's own head term** | An outbound link repeating your own target keyword hands the signal to the wrong page |
| No generic anchors — `click here`, `read more`, `learn more`, `here` | The most common wasted internal link on the internet |
| No two links on one page share anchor text | Two identical anchors pointing at different pages is a contradictory signal |
| Entity links carry the entity name | "Cost of Living in Austin", not "this city" — so one template yields a different anchor on every generated page |

Navigation anchors are fixed site-wide and exempt from per-page uniqueness, since
they appear on every page by design.

> **A tooling note worth recording.** The first version of this check reused the
> cannibalisation tokenizer, which deliberately drops `calculator` and `estimator`
> so two tool keywords compare on their meaningful part. With those words dropped,
> `cost of living calculator` reduces to `{cost, living}` and is a subset of nearly
> every cost-of-living phrase — so the check flagged four correct anchors. The
> anchor and slug rules now use their own tokenizer that keeps content words. **A
> check that fires on correct data is worse than no check**, because the fix people
> reach for is to change the data.

### 9-3-8. The slug matches the head term — now enforced

Rule 1 of section 6-7 has always said the slug is the target keyword, not a brand
name. Nothing checked it, and it was already broken:

**`/tools/salary-converter` had the head term `salary comparison by city`.** A
brand-shaped slug, which is the exact case the rule names. Renamed to
`/tools/salary-comparison-by-city` — free to do because nothing is published; after
indexation it costs a permanent redirect and some of the page's authority.

The rule as enforced:

- **ToolPage:** slug tokens equal head-term tokens exactly.
- **Directory and entity pages:** the slug may be *shorter* than the head term —
  `/state-taxes` is a section root and a URL-hierarchy segment, not a keyword — but
  it may never contain a token the head term lacks. Short is fine; different is not.

### 9-3-9. From formula to page — the generated specification

The formulas describe what every page must contain. Somebody still has to put
those values on 81 pages, and on a platform the input is a dashboard field.
**Fifty-one hand-typed titles is fifty-one chances to drift from the formula**,
and drift is invisible until a rankings report shows it.

So the values are produced, not typed:

```bash
python3 scripts/generate_onpage.py
```

| Output | Purpose |
|---|---|
| `data/onpage.generated.json` | Machine-readable, imported into the platform's entity fields (mapping in `data/pages.json → platform`) |
| [`docs/onpage-spec.md`](onpage-spec.md) | Human-readable, for review before import |

For each of the 51 states it resolves: title · H1 · meta description · canonical ·
breadcrumb · H2 outline · five FAQ entries carrying that state's own numbers ·
three JSON-LD blocks with concrete values · internal links with anchor text ·
and the dataset's verification state, so an unverified or 2025-figure state is
visible at import time rather than after publication.

It runs in CI and re-validates every generated value against the same limits the
auditor enforces, so a formula change that breaks one state breaks the build.

#### What generating it found

Three defects that reading the formulas had not surfaced:

1. **Forty-eight of the fifty-one metas were too short.** The auditor renders each
   formula with the *longest* substitution to catch truncation — and never with the
   shortest. With real state names, metas came out at 97–109 characters against a
   110 minimum, while the audit reported clean. **The audit now checks both
   extremes**, and the state and place metas were rewritten to fit at each end.

2. **No single place formula can fit the window.** `San Francisco-Oakland-Berkeley,
   CA` is 34 characters against `Akron`'s 5 — a 37-character swing inside a
   45-character meta budget. This is why formulas use the metro's **display name**,
   capped at 20 characters and required on every metro row, while the full MSA name
   appears once in the body where precision helps and layout does not care.

3. **"Texas tax brackets" was a heading on a state with no income tax.** One
   outline applied to every state produces headings that are wrong on the page —
   thin content of the exact kind section 7-1 forbids, generated at scale. Outlines
   now vary by the dataset's `structure` field: progressive, flat and no-tax states
   get different H2s and different FAQs.

The third is the one worth remembering: **a formula that ignores its entity's
shape scales a mistake as efficiently as it scales a page.**

#### Deliberately left unresolved

Every state's fifth FAQ answer is `PENDING_ENGINE` rather than a number. The tax
engine can compute it, but the take-home figure belongs in the same run as the
cost-of-living comparison, and that dataset does not exist yet (13-6). **Writing a
plausible number now is precisely what rule 5-3 forbids**, and the placeholder is
visible in the generated file so it cannot ship unnoticed.

### 9-3-10. Completion status — what is specified and what is not

The honest answer to "is on-page finished", by page group, so that nothing is
discovered missing during the build:

| Group | Pages | Mapped | Values resolved | Status |
|---|---|---|---|---|
| Home + tool index | 2 | ✅ | ✅ | Complete |
| Tool pages | 12 | ✅ | ✅ | Complete |
| Directories | 2 | ✅ | ✅ | Complete |
| Trust pages | 7 | ✅ | ✅ | Complete |
| State pages | 51 | ✅ | ✅ | **Complete** — the take-home FAQ is now computed, not pending |
| Metro pages | **4** | ✅ | ✅ except 3 FAQ answers | Everything but the BEA/HUD numbers (13-6) |
| Guides | 9 | ⬜ planned | ⬜ | Blocked on keyword measurement |

**78 of 78 buildable pages have generated on-page values.**

##### Why four metro pages and not thirty

Section 6-10-3's gate requires a **measured** head-keyword volume of ≥500/month.
Four metros have one: Austin 3,600 · San Francisco 2,900 · San Antonio 1,900 ·
Houston 1,900. The other 26 in the revenue model are a *modelled* median of 1,500,
and a modelled median is not a measurement.

`data/metros.json` therefore contains four rows, not thirty. That is the gate
working, not a shortfall — and section 6-10-7's sample stage calls for five pages,
so the set is nearly the right size already.

**One caveat is recorded in the file itself:** three of the four are Texas metros.
That reflects which keywords happened to be measured, not that Texas metros are
uniquely valuable, and a fifth outside Texas should be measured before the sample
is treated as geographically representative. The two
outstanding groups are blocked on inputs rather than on specification: metro pages
need BEA and HUD data, guides need their head terms measured. Both have templates,
rules and collision checks already in place, so each becomes generatable the day
its input arrives rather than needing new specification work.

The trust pages were missing entirely until this round, which mattered more than
their count suggests: section 6-3 builds them **before** content, and section 10-1
makes them a precondition for AdSense approval. They are now in the map, in the
footer link graph, and generated.

#### Two more defects the generator surfaced

**"How Sales Tax Calculator is calculated"** — the tool-page outline used the
tool's *name* where it needed the *subject*, producing a clumsy heading on all
twelve tool pages. Every tool now declares a `subject`, and the heading reads "How
sales tax is calculated". Small, and it would have shipped twelve times.

**A seven-character `<title>`** on the trust pages: `Privacy`. Long enough to be
valid, too short to be a useful SERP line, and it reads as an unfinished page. The
trust template now carries the site name — the one place a brand suffix is right,
because the page has no keyword competing for the room — and the audit gained a
title *minimum* alongside its maximum.

Both are the same lesson as the no-tax-state headings: **the formula looked
correct and the output was wrong.** That is the argument for generating and
reading the result rather than trusting the template.

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
| 3 | Intent clusters: every page declares one with ≥3 variants and a stated intent · no term in two clusters · no variant is another page's head · no two pages share an intent · entity-qualified variants belong to the entity page · variants are not claimed as measured |
| 4 | Pairs with ≥30% lexical similarity must declare **different primary outputs** |
| 5 | Every target is measured in `data/keywords.json` |
| 6 | Canonical is self on every page and tools strip parameters |
| 7 | Every template in use has a title, H1 and meta formula |
| 8 | Title ≤60, H1 ≤70 and meta between 110 and 155 characters — rendered with the **longest possible substitution**, not an optimistic sample |
| 9 | The primary keyword is present in the rendered title and H1; and every programmatic template's pattern carries an entity placeholder so pages cannot share a title |
| 10 | Anchor-text, OG and robots rules are declared, and every template has defined JSON-LD |
| 11 | Every declared internal link resolves to a real page, and no page exceeds the 25-body-link ceiling |
| 12 | Every page is within 3 clicks of the home page |
| 13 | No page is an orphan — every page has at least one inbound link |
| 14 | No page's links stay entirely inside its own funnel stage |
| 15 | Planned pages (section 9-2-2) declare a head and an intent, do not collide with an existing page, and argue any overlap in writing |
| 16 | Every slug matches its head term — exactly for tools, as a subset for section roots (9-3-8) |
| 17 | Every template has an H2 outline: no H2 repeats the H1, entity templates name their entity, FAQ heading and FAQPage schema are coupled both ways (9-3-6) |
| 18 | Every link edge carries anchor text: destination's head term, never the source's own, never generic, never duplicated on a page (9-3-7) |
| 19 | Meta formulas fit at **both** extremes — the longest entity name must not truncate, the shortest must not fall under the minimum (9-3-9) |
| 20 | Titles clear a minimum length as well as a maximum, and a template may declare per-page outlines instead of one shared outline (9-3-10) |

**Current run: 25 pages · 0 errors · 0 warnings** — across all twenty checks, plus **74 pages** with fully generated on-page values validated by `scripts/generate_onpage.py`. All three original warnings were resolved by actual measurement: two keywords were confirmed and recorded (`cost of living by city` 880 · `state income tax rates by state` 3,600) and the third was rejected and its page deleted (`job offer comparison calculator` 30).

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

##### The salary family — reduced from four to two

`income tax` · `take-home pay` · `paycheck tax` · `tax withholding` were four queries with adjacent intent, held apart only by a rule that their outputs must differ. Version 5.13 stopped defending that separation and collapsed it: `paycheck tax` (18,100) and `tax withholding` (14,800) were **removed**, and their intent folded into `take-home pay`, whose output now carries the per-paycheck breakdown.

The reasoning is recorded in 20-29. A separation that needs a rule to survive is a separation Google is unlikely to honour, and two pages defended by a rule are worth less than one page that owns the intent outright.

| Tool | The ResultCard's headline number |
|---|---|
| income tax | **Annual** tax liability + the bracket table |
| take-home pay | **Annual, monthly and per-paycheck** net |

**The same test now applies to the two affordability tools**, which are genuinely distinct and must stay that way:

| Tool | The ResultCard's headline number |
|---|---|
| home affordability | **A maximum price** — what income and debts support |
| house payment | **A monthly payment** — what a given price costs |
| rent affordability | **A rent ceiling** — and the metro's actual rent beside it |

The H1, the first sentence and the headline number must show that difference. If two pages highlight the same number, they are duplicates however different their URLs.

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

### 9-6. Crawl, render, index — the three steps before ranking

A page ranks only after Google has crawled it, rendered it, and indexed it.
Sections 9-1 to 9-5 are about what happens after that. An audit found thirteen
topics in this earlier stage with zero mentions in this document, and the ones
that genuinely bite a 110-page programmatic site are below. Where a topic does
not apply to us, that is said rather than padded.

#### 9-6-1. Click depth and orphan pages — enforced

A page reachable only from page four of a paginated directory is crawled late
and valued low, and on a programmatic site that is how generated pages quietly
die. So the link graph in section 6-10-5 is declared as data in
`data/pages.json → crawl` and `pages` `links`, and the auditor computes rather
than assumes:

| Rule | Limit |
|---|---|
| Click depth from the home page | **≤ 3** |
| Pages with zero inbound links | **0** |
| Body links per page | ≤ 25 (navigation exempt) |
| Every declared link resolves to a real page | required |
| No page's links stay entirely inside its own funnel stage | required |

Writing this check found two real defects the prose had hidden:

1. **Four tools were unreachable from the home page.** Section 6-0 counted a
   "tool index" page, but the page map never had one, so `sales-tax`,
   `property-tax`, `closing-cost` and `house-payment` had no crawl path at all,
   and `sales-tax-calculator` — 110,000 searches a month at $6.91, the highest
   market value on the site — was a complete orphan. `/tools` now exists.
2. **The four salary-family tax tools were a closed loop.** They linked only to
   each other, so a visitor arriving from search on the highest-CPC pages we
   have would leave after one page. Each now leads back out of stage 4.

Neither was visible by reading. Both are the kind of thing that costs months
before anyone notices, which is why this is a check and not a paragraph.

**`/tools` deliberately targets no keyword**, exactly like the home page: every
tool keyword already belongs to a tool page, and a hub competing with its own
children is the worst cannibalisation available. It exists for crawling and for
people.

#### 9-6-2. Crawl budget — does not apply, and here is why

Crawl budget becomes a real constraint somewhere in the tens of thousands of
URLs, or where a server is slow enough that Googlebot throttles itself. We have
~110 static HTML files on a CDN. **Neither condition is near.**

This is written down so that nobody later spends a week on log-file analysis and
crawl-rate tuning for a site where the entire problem is "are we linked to".
The gate in 9-6-1 is the crawl work that matters at our size.

What replaces log-file analysis: **Search Console's Crawl Stats report**. Static
hosting on a free tier gives no server logs, so that report is the only crawl
telemetry we will have — and at 110 pages it is enough.

#### 9-6-3. Mobile-first indexing — and one myth not to repeat

Google indexes the **mobile** rendering. Anything absent from the mobile HTML
effectively does not exist. Serving one HTML document to both satisfies this by
construction; a platform that varies its output by device does not, and that is
worth confirming during the 3-5 protocol. Two rules follow either way:

- **The `ContentAccordion` on mobile (sections 8-4 and 8-8) must be CSS-collapsed
  with its full content present in the HTML.** Content behind an accordion is
  indexed and fully weighted; content *fetched on click* is not reliably indexed
  at all. The difference is not the accordion, it is whether the text is in the
  first byte — which is already the hard rule in section 3-2.
- **No mobile-only truncation.** "Read more" that ships half the article to
  mobile ships half the article to the index.

> The myth worth not repeating: "hidden content is downranked." It was true
> before mobile-first indexing and has been false since. Collapsing long content
> on a small screen is good UX and costs nothing in ranking. Only the fetch-on-click
> variant is dangerous.

#### 9-6-4. `lastmod` — accurate or absent, never automatic

Google uses `<lastmod>` in a sitemap only while it stays consistently honest. A
build that stamps every URL with the current timestamp — the default behaviour
of almost every static generator — teaches Google to ignore the field entirely,
across the whole site.

**Rule:** `lastmod` comes from the same source as `dateModified` (section 9-4-1):
a genuine content or data change, never the build time. A page whose content did
not change keeps its previous `lastmod` across deploys. If that cannot be
guaranteed, the field is **omitted** — an absent `lastmod` costs nothing, a
dishonest one costs the signal site-wide.

The annual data update (section 16) is a genuine change and legitimately moves
both fields on every affected page at once.

#### 9-6-5. Redirects and 404s

- **Never a redirect chain.** A slug change adds a 301 to the *current* final
  destination; when a second change happens, the first redirect is repointed, not
  stacked. `docs/redirects.md` records both hops so the repointing is possible.
- **The 404 page must return HTTP 404**, not 200 with an apology on it. Static
  hosts differ here and it is silent when wrong: a 200 on a missing URL becomes a
  soft 404, and enough of them make Google distrust the whole directory. This is
  verified once at deploy (section 20-2) and after any host change.
- **A removed entity 410s or 301s, and never 200s onto an empty template.** The
  generation gate in section 6-10-3 means a page only exists if its entity has
  data; if data is later withdrawn, the page goes with it.
- **Our soft-404 risk is not missing pages, it is thin ones.** A place page whose
  dataset row is sparse would render a valid-looking shell. The uniqueness budget
  in 6-10-4 is what prevents that, and it breaks the build rather than shipping it.

#### 9-6-6. Images and alt text

**The site is close to imageless by design** — section 12 forbids charting
libraries, so `TaxBreakdownWaterfall` is CSS and inline SVG rather than a
rendered image. That removes most image SEO surface. What remains:

- Inline SVG that conveys information carries `role="img"` and a `<title>`
  element — it is not reached by `alt`, which is the mistake this replaces.
- The author photo on `/about` carries real `alt`; it is an E-E-A-T signal
  (section 7-4), not decoration.
- Dynamic OG images (section 9-3-4) are never in-page content and need no `alt`.
- Any decorative image gets `alt=""`, not a keyword.

#### 9-6-7. Submission and transport

- **IndexNow** is worth wiring up on a static site because it costs one file and
  one ping — but be precise about what it buys: **Bing and Yandex support it,
  Google does not.** It is a small Bing win, not a Google indexation lever, and
  it must not be presented in a status report as one.
- Google discovery is the sitemaps in section 6-8-6 plus internal links, and at
  our size that is sufficient.
- **HSTS** is set so the browser never makes the http→https hop. HTTPS itself is
  a very light ranking signal; the real reason is that a redirect hop on every
  cold visit is a measurable LCP cost against the 2.0 s budget.

#### 9-6-8. SERP features we can actually win

| Feature | Our route | Realistic? |
|---|---|---|
| AI Overview citation | Step-by-step formula with concrete numbers (sections 6-6, 8-8) | **Yes** — `taxstra.com` proves a small site can |
| People Also Ask | The FAQ blocks, written from the actual PAA questions for that keyword (section 7-2-1) | Yes, and it is cheap |
| Featured snippet | A direct definition or a table in the first screen of the answer section | Sometimes; not designed for specifically |
| Sitelinks | Earned, not requested — follows from a clean, shallow architecture (9-6-1) | Later, if the brand query exists |

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
| **1** | ✅ Keyword validation · ✅ tax engine · ✅ datasets and auditors · register the domain · GSC before anything ships · **run the 3-5 verification protocol** · app skeleton · 7 trust pages | An indexable shell |
| **1–2** | **Acquire and verify the cost-of-living dataset** (BEA RPP · HUD FMR · BLS CPI) — the blocking dependency for everything downstream | A verified place dataset |
| **2** | **Stage 1 — place:** cost-of-living calculator · `/cost-of-living` directory · **5 sample metros** | **Gate 1** |
| **3** | **Stages 2–3 — comparison and income:** comparison tool · salary converter · salary↔hourly · apply to AdSense | AdSense approved |
| **4** | **Stage 4 — what you keep:** the six tax tools (engine already built) · `/state-taxes` · 8 state pages · first 3 guides | **Gate 2** |
| **5** | Per gate 1: expand metros 5 → 30 · remaining guides · link building begins in earnest | 30 place pages |
| **6+** | **Stage 5 — settling:** house payment · closing cost · expand states per gate 2 | Full phase 1 |
| **Tax season (Jan–Apr)** | Live optimisation from GSC · no large new pages · the stage 4 pages take their seasonal peak | **Gate 3** |

**The order changed in version 4 and this table had not caught up.** It used to
schedule the freelancer tax tools first, which contradicts rule 1 of section
2-3: no tool ships before the tools of the stage above it. A take-home page
without a cost-of-living page is just one more calculator — it has no funnel to
sit in, and the funnel is worth +105% revenue (section 1-4).

The tax engine being finished does not change the order. It changes the *cost*
of stage 4, not its position.

**The one hard dependency:** stage 1 cannot start until the cost-of-living
dataset exists. That is currently the project's critical path and the only item
here that is genuinely blocked (section 13-6).

**A note on order:** if time capacity runs short, cut from the end — stage 5 first, then the extra state pages, then guides. **Stage 1, stage 4 and the 7 trust pages are never cut**: stage 1 is the funnel entrance, stage 4 is the moat and the revenue, and without the trust pages there is no AdSense approval at all.

### 11-1. Decision gates — numeric criteria, not feelings

**Gate 1 — "are we being indexed at all?"**
Three to four weeks after the 5 sample metro pages ship (section 6-10-7):
- ✅ **Continue:** at least 4 of the 5 are indexed and taking impressions → expand to 30 metros
- ⚠️ **Pause and fix:** indexed but zero impressions → the problem is keyword selection, not technical. Review before building the next 25
- ❌ **Stop and reconsider:** not indexed → a technical or content-quality problem. **Do not scale under any circumstances.** Scaling an indexation problem multiplies it

Read this per sitemap, not site-wide (section 6-8-6): "90% of tools indexed,
20% of place pages" means the `PlacePage` template is at fault, not the site.

**Gate 2 — "is the funnel actually working?"**
- ✅ Stage 1 to 4 pages indexed, AdSense approved, monthly organic traffic above 1,000 and rising
- ⚠️ Under 500 → stop building and focus solely on distribution and links (section 9-5). More pages do not fix a distribution problem
- **The funnel check, which is unique to this gate:** pages per session above **1.5** and rising toward 2.2. This is the assumption the entire revenue model rests on (section 1-4), and gate 2 is the first point at which it can be measured rather than assumed. If it is stuck at 1.1, the internal links are not doing their job and no amount of traffic compensates
- Check: are any two pages cannibalising? Is a keyword sitting at position 11–20 that a small push would move to page one?

**Gate 3 (end of April, after tax season) — "is phase 2 justified?"**
- ✅ **Go to phase 2:** season peak above $300/month and an out-of-season base above $100 → expand metros to 100+, evaluate country-level
- ⚠️ **Go deeper, not wider:** $30–100 → deepen the existing cluster. Adding a second niche on a weak base weakens both
- ❌ **Fundamental review:** under $30 → the core assumption was wrong. Analyse where before investing further
- Also evaluate here, and not before: migrating to a premium ad network (section 10-5)

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
- [ ] **`curl` on the URL returns the complete content in the HTML** (not an empty shell). On a client-rendered platform this is requirement R1 and the single most important check in this list — it is verified per template at least once, and re-verified after any platform change
- [ ] `curl` as Googlebot and as `facebookexternalhit` returns the same content and the correct per-entity metadata (R3, R8) — prerendering is frequently user-agent gated, so testing as a browser proves nothing
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

## 13. Data status and verification

**No figure is written in this document.** The numbers live only in
`src/data/`, alongside their source and date.

Sections 13-1 to 13-5 cover the tax dataset, which exists and is unverified.
Section 13-6 covers the cost-of-living dataset, which does not exist yet and is
the project's critical path.

### 13-1. Tax data — current status (2026-08-29)

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

### 13-6. The cost-of-living dataset — not yet acquired, and on the critical path

Everything above concerns tax. The project has a second dataset, and it does not
exist yet.

| Item | Status |
|---|---|
| BEA Regional Price Parities (state + metro) | ⬜ Not acquired |
| HUD Fair Market Rent (county, by bedroom count) | ⬜ Not acquired |
| BLS regional CPI | ⬜ Not acquired |
| Eurostat comparative price levels | ⬜ Next phase (section 2-4-2) |
| `scripts/extract_cost_of_living.py` | ⬜ Not written |
| Cost-of-living equivalent of `validate_tax_data.py` | ⬜ Not written (required by section 5-5) |

**Why it is blocked here and not in reality:** `.gov` domains are unreachable
from this development sandbox — the same limitation that made the tax data
secondary rather than primary (13-3). All three US sources publish free,
machine-readable, licence-clean data. This is an environment constraint, not a
project one, and it is the first thing to resolve outside the sandbox.

**Alternative routes were tested, not assumed.** PyPI is reachable and `.gov` is
not, so packages install but fetch from blocked hosts at runtime. The `cpi` package
does ship a 62 MB bundled database — but it holds **CPI, which measures inflation
over time, not price level between places**. CPI cannot compare Austin with San
Francisco; that is exactly what Regional Price Parities do and CPI does not. It is
useful for the annual update in section 16 and useless for the comparison this
project is built on.

**So the blocker became one command instead of a research task:**

```bash
export BEA_API_KEY=...      # free, apps.bea.gov/API/signup
export HUD_API_TOKEN=...    # free, huduser.gov FMR API
python3 scripts/fetch_cost_of_living.py --year 2024
python3 scripts/validate_cost_of_living.py --year 2024
```

`fetch_cost_of_living.py` builds only the metros that pass the 6-10-3 gate, in the
5-5 schema, with sources and a `pending` verification state.
`validate_cost_of_living.py` is the equivalent of `validate_tax_data.py` that 5-5
required and that did not exist — it enforces the three rules the original city
dataset broke: no derived value stored, one definition per column across every row,
and a category with no official index omitted rather than substituted. It runs in
CI and no-ops until the dataset exists.

> ⚠️ **The API paths in the fetcher were written from documentation, not from a
> successful call** — the sandbox cannot reach either host. Treat the first run as a
> smoke test and check one metro against the published tables by hand before
> generating 30 pages from it.

**Why it matters more than the tax verification backlog:** the tax dataset
exists and is merely unverified. This one does not exist at all, and stage 1 of
the roadmap cannot start without it (section 11). It is the project's critical
path, and risk 11 in section 17 is about it.

**The rules it must satisfy on arrival** are already written and are not
negotiable on the grounds of convenience:

- No derived value stored (5-3, rule 1)
- One written definition per column (5-3, rule 2)
- **A category with no official index is dropped, not filled with a substitute
  number** (5-3 rule 3, 4-9-1) — this is the rule that the original dataset's
  fabricated insurance column broke
- Indices carry their vintage year, and it is displayed (16-2-1)
- `lastVerified` under 18 months, since BEA publishes annually (5-5)

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

### 14-4. The place cluster — the SERP that has not been analysed

Sections 14-1 to 14-3 analyse the SERP for `self employment tax calculator`.
That was the core keyword when they were written. **It no longer is.** Stage 1
is the place cluster, and its SERP has never had the same treatment.

What is actually known, and no more than this:

| Fact | Source |
|---|---|
| `costbycity.com` ranks position 10 for `cost of living by city`, on BEA RPP — our exact concept and data source | Live check, section 2-2-4 |
| `realtakehomepay.com` compares job offers by take-home pay across 50 states | Live check, section 2-2-4 |
| `cost of living calculator` is 60,500/month at $1.65; `cost of living comparison` is 49,500 at $0.97 | `data/keywords.json` |

**What is not known**, and must be before stage 1 ships:

- Who holds the top ten for `cost of living calculator` and `cost of living
  comparison`. NerdWallet and Bankrate almost certainly appear, but "almost
  certainly" is the kind of claim this document has been wrong with three times
  on this exact cluster (section 20-5)
- Whether an AI Overview fires on those keywords, which sets the traffic model's
  penalty for the largest part of the funnel
- What the top-ranking city pages actually contain, which determines whether the
  uniqueness budget in 6-10-4 is sufficient or generous

**This is gate zero for stage 1** (section 18-1 applies the same rule to every
new tool): the SERP is checked before the pages are built, not after. It is
listed here as an open item rather than filled with a plausible-looking table,
because a fabricated competitive analysis is worse than an absent one — it gets
believed.

**The one structural read that does hold:** both known competitors are small
sites, and both rank. That is the same signal as `sdocpa.com` and `taxstra.com`
in the tax SERP, and it is the strongest evidence the project has that a niche
site can win here. It also means we are not first, and our claim is the
intersection rather than either half.


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
| `place_changed` (metro) | Which metros are actually selected — including ones we have no page for. **The gate in 6-10-3 asks whether a metro deserves a page; this answers it with our own users rather than an external volume estimate** |
| `comparison_run` (mode) | Is the job-offer mode used enough to justify the extra inputs (section 6-1)? |
| `funnel_step` (from → to) | Which link in the funnel actually gets clicked, and which one breaks the chain |
| `warning_shown` (type) | Which limitation hits real users most? That sets the fix priority |

**Rule:** no personal data and no financial value is ever recorded — only the field name and the event. Calculations stay client-side and we say so in `/privacy`; in a finance niche that is itself an advantage.

### 15-3. Monthly review — half an hour, not a project

Every month, just these numbers:

1. **Keywords at positions 11–20** — the nearest win. Strengthening these is cheaper than writing a new page
2. **Pages with high impressions and low CTR** — a title/description problem, not a content problem
3. **Pages with high entries and low `calc_interact`** — the calculator is not being found, or it intimidates
4. **RPM by page** — which cluster actually pays
5. **Pages per session, and which funnel link produced it** — from `funnel_step`. This is the number the revenue model is most sensitive to (section 1-4), so it is reviewed monthly rather than at gates only
6. **Top `place_changed` metros with no page yet** — the cheapest page decisions available, because the demand is already measured on our own site
7. **Is there a keyword that refutes a section 6 assumption?**

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
| 1 | **A new domain does not get indexed** | Fatal | Gate 1 with a numeric criterion. No scaling before proof. **R1 verified against a live app on 2026-09-06** (3-1): content is in the server's HTML, so the rendering-queue penalty does not apply |
| 2 | **AI Overviews swallow the organic click** | High, and getting worse | Sections 6-8 and 8-8: a step-by-step structure to earn the citation. Diversify toward tool keywords where the user must interact, not merely read a short answer |
| 3 | **Competitors have far higher domain authority** | High | Section 14. Quality + long-tail + active distribution. Accepting that head keywords do not come in year one |
| 4 | **One wrong number makes 51 pages wrong** | Fatal to credibility | Golden tests · a CI validator · the verify-before-publish rule |
| 5 | **AdSense rejects the site** | Months of delay | Trust pages **before** content. Room for two applications |
| 6 | **Time capacity runs short** | High | An explicit cut order in section 11: states first, then guides; the layer-1 tools never |
| 7 | **A Google algorithm update** | Variable | Focus on one niche, real E-E-A-T, no reliance on a single keyword. If a drop comes: wait four weeks before changing anything — a rushed reaction to an update usually makes it worse |
| 8 | **Seasonality does not deliver the monthly target** | High | Stages 1.5 and 3 (section 2-3), which bring seasonless keywords |
| 9 | **The annual update is forgotten** | High | Section 16 + breaking the build after 400 days |
| 10 | **Project scope drifts toward "life"** | High | Section 2-2: maths and health are explicitly out of scope |
| 11 | **The cost-of-living dataset cannot be acquired or is unusable** | **Fatal — it is the critical path** | It is stage 1 and everything downstream depends on it (section 11). BEA, HUD and BLS all publish free, machine-readable, licence-clean data, so the risk is effort and shape, not availability. Mitigation: build it against 5 metros first and only then commit to 30. If it genuinely fails, the fallback is a tax-first site — which section 1-4 shows caps around $250/month, so this risk is the difference between the target and half of it |
| 12 | **BEA or HUD changes its methodology or release cadence** | Medium | Section 16-2-1 already expects a publication lag. The indices are stored with their vintage year and displayed with it, so a methodology change is visible rather than silent |
| 14 | **A programmatic page ships without its SEO component**, or with constant values | Medium, and silent | Rule 3-7-6. It fails on the page nobody checked, so 3-5 samples three rows rather than one |
| 13 | **A competitor with authority copies the tax-plus-cost intersection** | Medium | `costbycity.com` and `realtakehomepay.com` each hold one half already (section 2-2-4). The defence is not secrecy — it is being first to depth and earning the links (section 9-5) while the intersection is still empty |

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
- [ ] If it is place-related: it uses `src/lib/cost-of-living/` and **invents no dollar amount for any place** (rule 4-9-1)
- [ ] If it needs data: it has a primary source, in JSON with `sources` and `lastVerified`
- [ ] If it is simple arithmetic: in `src/lib/calc/{name}.ts`, a pure function
- [ ] It has tests — even simple arithmetic. `margin = (price − cost) / price` can be written wrong too
- [ ] Every limitation appears in `warnings`, never silently (section 4-8)

### 18-4. The page

- [ ] The template in section 8-8 · the defaults in section 8-9 · **never an empty form**
- [ ] The content brief in section 7-2-1 (600–900 words)
- [ ] Links to at least 3 internal pages · and is linked from at least 2
- [ ] **It is added to `data/pages.json` with its funnel stage and its links**, and `audit_seo.py` passes — otherwise it is an orphan on the day it ships (section 9-6-1)
- [ ] It links to at least one page outside its own funnel stage
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

## 19. Deployment, launch and recovery

Written after an audit found this had zero coverage: the document specified what
to build and how it should rank, and nothing about putting it on the internet.
Most of what follows has a direct SEO consequence, which is why it is here
rather than in a README.

### 19-1. Hosting

**Base44 hosts the application**, on a custom domain (requirement R9). That
removes most of the choices this section used to make and replaces them with
verifications, because a hosted platform decides these for you and does not always
tell you what it decided.

| What must be true | How it is confirmed |
|---|---|
| A real HTTP 404 on unknown paths | `curl -I` in 19-2. Silent when wrong, and poisons a directory (9-6-5) |
| HSTS and sane cache headers on HTML | Inspect response headers. If they cannot be set, HTML must at least not be cached hard — an annual data update behind a month-long cache is last year's brackets under this year's heading |
| One host only, apex **or** www | Both resolving means the site is indexed twice and its authority split |
| A custom domain, not `*.base44.app` | AdSense (10-1) and authority both require it |
| Preview or draft URLs are not public | See the staging warning below — on a hosted platform you often do not choose whether these exist |

**Where the platform cannot satisfy one of these, section 3-3's fallbacks apply**
— most likely fallback 3, putting a CDN in front for the content surface. Decide
that from the 3-5 results, before launch, not after.

### 19-2. Pre-launch verification — run against the live domain

Every one of these has been an SEO incident on somebody's site. They are cheap
to check once and expensive to discover from a traffic graph.

```bash
curl -sI https://DOMAIN/nonexistent-page   | head -1   # must be 404, not 200
curl -sI https://DOMAIN/                   | head -1   # must be 200
curl -sI http://DOMAIN/                    | head -1   # must be 301 to https
curl -sI https://DOMAIN/tools/             | head -1   # must be 301 to no-slash
curl -sI https://DOMAIN/TOOLS              | head -1   # must be 301 to lowercase
curl -s  https://DOMAIN/robots.txt                     # must not disallow content
curl -s  https://DOMAIN/sitemap.xml        | head -20  # must list the child sitemaps
curl -s  https://DOMAIN/state-taxes/california | grep -c "California"   # content in HTML
```

| Check | Failure mode if skipped |
|---|---|
| 404 returns 404 | Soft 404s across the whole directory; Google stops trusting it |
| One host only (apex **or** www) | The entire site indexed twice, authority split |
| HTTP → HTTPS 301 | A redirect hop on every cold visit, measurable in LCP |
| Trailing slash canonicalised | Every URL indexable in two forms |
| `robots.txt` does not block content | The single most common catastrophic launch bug |
| Content present in `curl` output | The SPA failure mode section 3-2 exists to prevent |
| **Staging is not indexable** | See below — this one is the worst |

> ⚠️ **The staging trap.** A preview deployment on a public URL, with content
> identical to production, is a duplicate of the entire site. Most hosted
> platforms create preview or draft URLs by default, and Base44 apps are reachable
> at a platform subdomain as well as the custom domain. **Both cases must be
> resolved before launch**: the preview password-protected, and the platform
> subdomain either disabled or 301-redirected to the custom domain. `noindex`
> alone is not enough — it still permits crawling and linking, and it is one
> misconfiguration away from being indexed instead of production.
>
> Check it directly: `curl -sI https://YOUR-APP.base44.app` should redirect to the
> custom domain, not serve a copy of the site.

### 19-3. Headers

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Cache-Control: public, max-age=0, must-revalidate      # HTML
Cache-Control: public, max-age=31536000, immutable     # hashed assets
```

HTML must not be cached hard: an annual data update (section 16) that sits
behind a month-long cache is a page showing last year's tax brackets under this
year's heading — the exact failure section 13-4 exists to prevent.

### 19-4. Launch sequence

Order matters, and two of these cannot be done late.

1. **Search Console verified before the first content page is public.** Position
   and impression history cannot be backfilled; every day without it is data
   permanently lost (section 15-1).
2. Trust pages live (section 6-3) — before content, because AdSense review looks
   for them and because a site of calculators with no About page is a YMYL red flag.
3. Stage 1 pages ship, and the pre-launch checks in 19-2 run against the live domain.
4. Sitemaps submitted, one per template, so gate 1 can be read per template.
5. **Wait three to four weeks.** Gate 1 is a measurement, and there is nothing to
   measure before Google has had time to crawl. Building the next 25 metros during
   this window is exactly what section 6-10-7 forbids.
6. AdSense application only after 30–40 complete pages exist (section 10-1).
7. Batch publication thereafter: **at most 10 pages a week**, per section 6-10-7.

### 19-5. Monitoring

At this size, monitoring is four things, not a platform:

| Signal | Why | Cadence |
|---|---|---|
| Uptime and status code on the home page and one place page | A site returning 5xx during a crawl gets pages dropped from the index, and recovery is slow | Continuous, any free checker |
| GSC **Page indexing** report | The first place a template-wide failure appears | Weekly to gate 2, then monthly |
| GSC **Crawl stats** | Our only crawl telemetry — static hosting gives no logs (section 9-6-2) | Monthly |
| Core Web Vitals field data | The budget in section 12 is a lab number; this is the real one | Monthly |

### 19-6. Recovery

**A bad deploy.** Both hosts keep previous deployments and can roll back to one
in about a minute. That is the response — diagnose afterwards, not first. A
static site has no partial-failure state: the previous build is known good.

**Wrong data shipped.** Roll back the deployment, then fix the dataset, then
re-run `validate_tax_data.py --strict` before redeploying. Do not hot-fix a
number in a JSON file on a branch that has not passed the validator; that is how
a second wrong number ships behind the first.

**Accidental deindexation** (a `robots.txt` or `noindex` mistake): fix, redeploy,
then request validation in Search Console rather than waiting. Recovery is
typically days to weeks, and the cost is real — which is why 19-2 checks
`robots.txt` on every launch and after any host configuration change.

**AdSense suspension.** Ads stop; the site does not. Do not react by changing
ad density or placement (section 10-4) before reading the stated reason —
guessing at a policy violation usually adds a second one. The traffic and the
rankings are unaffected, which is the argument for never letting ad revenue
drive a structural decision.

**What has no recovery path**, and therefore gets the care up front: a changed
URL after indexation (section 6-7), a lost Search Console history, and a
dishonest `lastmod` (section 9-6-4) — Google's distrust of that field is
site-wide and not quickly undone.

### 19-7. Building before the domain is bought

The build order is: construct the site on the platform, then buy the domain. That
is a reasonable sequence and it carries exactly one risk, which is avoidable but
not recoverable.

**The risk:** if the site is indexed on a `*.base44.app` subdomain and the custom
domain arrives afterwards, every signal earned in the meantime belongs to a domain
that is being abandoned. A 301 carries much of it across, but not all, and the
transition costs weeks of ranking volatility at precisely the moment a new site can
least afford it. Worse, the two hosts serving identical content is the duplicate
described in 19-2.

**The rule, therefore:**

> **Nothing is indexable until the real domain is connected.** Build freely on the
> platform subdomain; keep it out of the index until the domain exists.

Concretely, for the whole pre-domain period:

| Action | When |
|---|---|
| `robots.txt` disallowing everything, or the platform's password protection | From the first deploy |
| Search Console property | **Only after** the custom domain is connected — a property on the subdomain collects history for a site that will not exist |
| Sitemap submission | After the domain, never before |
| Any link shared publicly | After the domain. A link posted to a forum is a crawl invitation |

The cost of this discipline is nothing, because nothing of value happens in the
index during construction anyway. The cost of skipping it is a migration.

**One exception worth knowing:** section 15-1 says Search Console history cannot be
backfilled, and that is still true — but it starts from the domain, not from the
build. Connecting the domain the week before launch loses nothing.

#### The one value that encodes this

`data/pages.json → site.origin` is `https://example.com` until the domain is
bought. Every canonical, JSON-LD URL and OG tag is generated from it, so the
domain is changed **in one place and regenerated**, not edited across 78 pages.

That is the whole reason the on-page values are generated rather than typed
(9-3-9), and buying the domain late is the case it was designed for.

---

## 20. Changelog

| # | Fault in the previous document | Correction |
|---|---|---|
| 1 | "static-first" but a React SPA was specified | Resolved as requirements R1–R9 (section 3-1) rather than a framework name, so the platform can change without the specification changing |
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

### 20-1. Round two — after keyword validation (2026-08-29)

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

### 20-2. Round three — version 3.0

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

### 20-3. Round four — version 3.1

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

### 20-4. Round five — version 3.2

| # | Item | Outcome |
|---|---|---|
| 43 | **My measurement error on cost of living** | Only the long tail had been measured (3,600). The head term is **60,500** — 17× more. The conclusion did not change but the reasoning became correct: the worst value-to-cost **ratio**, not an absence of demand |
| 44 | "Which tool is next?" had no systematic answer | [`tool-catalogue.md`](tool-catalogue.md) — 36 tools ranked by market value alongside build cost |
| 45 | The phase 1 inventory had never been counted | Section 6-0: **39 pages, 12 tools** |
| 46 | `hours calculator` is the catalogue's highest market value and was not on the map | Category A, high priority |

### 20-5. Round six — version 3.3

| # | Item | Outcome |
|---|---|---|
| 47 | **The third and final cost-of-living correction** | The full cluster is **158,000/month**, not 3,600 and not 60,500. The claim "the lowest value in the catalogue" was also wrong — it is mid-pack |
| 48 | The demand is in the **tool**, not the **pair page** | The comparison tool 49,500 · the best city pair 260. One excellent tool instead of thousands of pages |
| 49 | The data problem was not "unsolved" | BEA RPP · HUD FMR · BLS CPI · Eurostat — official, free, citable. **Better than Numbeo** |
| 50 | The city/country structure the user proposed was correct | The official data is published at exactly those levels |
| 51 | City pages are 10–17× better than the state tax pages | Stage 2.5 added to the roadmap |

**The methodological lesson of this round:** when rejecting a cluster, measure the head keyword **and** the cluster around it. Three consecutive underestimates, each from measuring a narrower slice of reality than existed.

### 20-6. Round seven — version 3.4

A document audit found five gaps, the most important of which the previous round had created itself.

| # | Gap | Fix |
|---|---|---|
| 52 | **Cost of living had zero mentions in 6 sections** — the document disagreed with itself | Engine (4-9) · data schema (5-5) · pages (6-8-1) · brief (7-2-3) · budget (12) · runbook (16-2-1) |
| 53 | **Cookie consent** had zero mentions — and Europe made it mandatory | Section 10-6 |
| 54 | No process for adding a tool existed, with 24 iterations ahead | Section 18 |
| 55 | The performance budget had no numbers | Section 12: 90KB of JS, 350KB total, with explicit prohibitions |
| 56 | The content brief covered only state pages — three quarters of the site had none | 7-2-1 tools · 7-2-2 guides · 7-2-3 city |
| 57 | No tone guide, with 35,000 machine-drafted words ahead | Section 7-6, including disclosure of machine assistance |

**The important design decision in 4-9-1:** for cost of living, **no dollar amount is invented for any city.** The official sources publish indices rather than dollar baskets; so the dollars come from the user's own numbers and we only apply the official ratio. This removes the original dataset's "fabricated insurance column" problem at the root.

### 20-7. Round eight — version 4.0 · the identity change

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

### 20-8. Round nine — version 4.1 · precision and structure

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

### 20-9. Round ten — version 4.2 · tool depth and SEO

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

### 20-10. Round eleven — version 4.3 · the cannibalisation auditor

Cannibalisation moved from advice to an **automated CI check**: `data/pages.json` (the page-to-keyword map) + `scripts/audit_seo.py`.

The first run found **9 errors**. The two important ones shared a pattern:

| Pair | Similarity |
|---|---|
| `/tools/income-tax-calculator` ↔ `/state-taxes/{state}` | 67% |
| `/tools/cost-of-living-calculator` ↔ `/cost-of-living/{metro}` | 67% |

**A generic tool with a location selector, versus a specific place page.** Without a rule, the generic tool supporting all 51 states unintentionally competes with all 51 state pages — and because it is stronger, the state pages never rise. This is the trap almost every programmatic site falls into and it is invisible from the outside.

**Status then: 18 pages · 0 errors · 3 warnings** — three unmeasured keywords that had to be measured before building.

### 20-11. Round twelve — version 4.4 · warnings to zero

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

### 20-12. Round thirteen — version 4.5 · on-page SEO

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

### 20-13. Round fourteen — version 4.6 · the language boundary

The site was English and the spec Persian; until then that was only a remembered convention, and it had already broken once: the `output` field was an internal Persian description, and wiring it into the meta formula the round before would have produced 15 pages with Persian metas.

- All of `data/pages.json` and `data/keywords.json` were translated to English — 66 strings.
- `scripts/check_language.py` was added and runs in CI: any Persian character in `data/` · `src/` · `app/` · `public/` · `components/` · `content/` breaks the build.
- The boundary was recorded in section 9-3-5.

**Status: 66 shipping files · 0 Persian strings · 17 pages · 10 checks · 0 errors.**

### 20-14. Round fifteen — version 4.7 · one language across the project

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

### 20-15. Round sixteen — version 4.8 · crawl architecture and the stale sections

Three separate audits drove this round, each measuring rather than asserting.

**1. Thirteen technical SEO topics had zero mentions.** Everything in sections
9-1 to 9-5 concerns what happens after a page is indexed; the crawl-render-index
stage before it was missing entirely. Section 9-6 covers it, and the two
computable parts became checks rather than prose. The auditor went from 10 to
**14 checks**: link resolution, click depth, orphans, the body-link ceiling, and
funnel cul-de-sacs.

That found two defects reading had not:

| Defect | Consequence |
|---|---|
| **`/tools` did not exist** although section 6-0 counted it | Four tools unreachable from home; `sales-tax-calculator` — 110,000/month at $6.91, the site's highest market value — a complete orphan |
| **The four salary-family tools linked only to each other** | A closed loop on our highest-CPC pages: search visitors leave after one page, against a model that assumes 2.2 |

**2. Five sections had not caught up with the version 4 identity change.** The
worst was section 11: its timeline still scheduled the freelancer tax tools
first, which directly contradicts rule 1 of section 2-3. Rewritten around the
funnel stages, with the cost-of-living dataset named as the critical path.

| Section | Was | Now |
|---|---|---|
| 3-3 | The tree had no cost-of-living engine, though 4-9 specifies one | Added, marked blocked |
| 11 | A tax-first schedule and October/December gates | Funnel-ordered, with a pages-per-session check at gate 2 |
| 13 | "Tax data" only — the second dataset unmentioned | Retitled; 13-6 gives the cost-of-living dataset its own status |
| 14 | Only the tax SERP analysed | 14-4 states what is known about the place SERP and, explicitly, what is not |
| 15 | No place events | `place_changed`, `comparison_run`, `funnel_step` — the last measures the assumption the revenue model rests on |
| 17 | No risk for the blocking dependency | Risks 11–13, the first of which is fatal and on the critical path |
| 18 | Assumed every new tool is a tax tool | Covers the place engine, and requires the new page to enter `pages.json` and pass the audit |

**3. Deployment, launch and recovery had zero coverage** — the document said
what to build and how it should rank, and nothing about putting it online.
Section 19 covers hosting, a pre-launch verification script, headers, the launch
order, monitoring and recovery. Most of it is SEO: a 404 returning 200, a second
indexable host, a `robots.txt` mistake, and an indexable staging deployment are
all silent and all expensive.

Two points of precision worth keeping:

- **9-6-3 refuses a common myth.** Accordion-hidden content is indexed and fully
  weighted under mobile-first indexing; the dangerous variant is content fetched
  on click, which is a different failure and already covered by 3-2.
- **9-6-2 says crawl budget does not apply to us**, at ~110 static pages, so that
  nobody later spends a week on log-file analysis for a site whose entire crawl
  problem is "is it linked to".
- **14-4 leaves the place SERP table empty on purpose.** A fabricated competitive
  analysis is worse than an absent one, because it gets believed — and this
  document has been wrong about this exact cluster three times.

**Status: 18 pages · 14 checks · 0 errors · 0 warnings · 59 tests green.**

### 20-16. Round seventeen — version 4.9 · the keyword model itself

The user asked whether the model is "one page per keyword group, where a head
term represents the group". It is — and the document had been carrying that
model in prose while carrying a different one in its data.

**What the data actually said:** one `primary` per page and **three** secondary
keywords across eighteen pages. Ten pages had none. That is one page per keyword
*string*, and it costs three things: the long tail goes unplanned, the content
brief cannot know which phrasings to cover, and the cannibalisation check can
only ever compare head terms.

Section 9-2-1 writes the model down and `data/pages.json` now carries it: an
`intent` sentence and ≥3 variants per page, with six rules enforced in CI
(checks 3 and 15, taking the auditor to **15 checks**).

**The addition that matters most is `intent`.** Lexical similarity was the only
axis before, and it fails in both directions: "what will my paycheck be" and
"take home pay calculator" share almost no tokens and are one question, while
"gross pay vs net pay" and "net pay calculator" overlap heavily and are two.
Two pages may now not state the same intent, whatever their keywords look like.

**The nine guides were invisible to every check** — prose in section 6-2 and
nothing else — despite being the main external-link asset. They are now in
`plannedPages`, and the collision check found one immediately: the planned guide
`states with no income tax` was **the same query `/state-taxes` already owns**.
A list query, aimed at a page that is a list. Retargeted to what the directory
cannot answer — whether no-income-tax states actually cost less once sales,
property and local tax are counted. Non-duplicative, a better guide, and one our
own two engines can answer with computed numbers.

A second overlap was legitimate rather than wrong, so the check grew an escape
hatch that cannot be abused: a planned page may declare `overlapsAcknowledged`,
and the audit **fails on a reason shorter than 40 characters**. An overlap can be
argued in writing; it cannot be waved away.

**One thing deliberately not done.** The variants carry no volumes. The true
addressable volume of a page is its whole cluster, which is materially larger
than its head, and adding an estimated multiplier would raise every projection in
section 1-4 without one new measurement behind it. The audit fails the build if
any page claims measured variants while no variant volume exists in
`data/keywords.json`. The revenue model stays a floor, not a forecast — this
document has been wrong three times by asserting keyword numbers it had not
checked (section 20-5), and the fix for that is not a fourth estimate.

**Status: 18 pages · 15 checks · 0 errors · 0 warnings · 59 tests green.**

### 20-17. Round eighteen — version 5.0 · on-page SEO closed

The goal of this round was to finish on-page SEO so that building can start and
internal linking has a complete specification to build against. The auditor went
from 15 checks to **18**, and closing it surfaced two defects in the data and one
in the tooling.

**The slug rule had never been checked, and was already broken.**
`/tools/salary-converter` carried the head term `salary comparison by city` — a
brand-shaped slug, which is the exact case rule 6-7-1 names and forbids. Renamed
to `/tools/salary-comparison-by-city`. Free now; after indexation it costs a
permanent redirect and part of the page's authority. The rule as enforced
distinguishes tools (slug equals the head term) from section roots like
`/state-taxes` (the slug may be shorter than the head, never different).

**Heading structure did not exist below the H1.** Sections 9-3-2 covered the top
of the page and nothing under it, which matters because the cluster variants from
9-2-1 live in the H2s, the FAQ and the body — never in the title. Each template
now declares an H2 outline, and the audit enforces that no H2 repeats the H1,
that entity templates name their entity (or 30 place pages ship one identical
outline), and that **FAQ heading and FAQPage schema are coupled in both
directions** — schema without a visible FAQ violates the guidelines, a visible
FAQ without schema wastes the People Also Ask surface.

**Anchor text was four written rules that nothing checked.** Every one of the 66
link edges now carries anchor text, enforced: written with the destination's head
term, never containing the source page's own head term, never generic, never
duplicated within a page.

**The tooling defect is the one worth remembering.** The first version of the
anchor check reused the cannibalisation tokenizer, which deliberately drops
`calculator` and `estimator` so two tool keywords compare on their meaningful
part. With those dropped, `cost of living calculator` reduces to `{cost, living}`
and is a subset of nearly every cost-of-living phrase — so the check flagged four
perfectly correct anchors. A check that fires on correct data is worse than no
check, because the fix people reach for is to change the data. The anchor and slug
rules now use their own tokenizer that keeps content words.

Both new rule sets were verified by planting violations — a generic anchor, a
self-referencing anchor, a duplicate anchor, an anchor unrelated to its
destination, a brand-shaped slug, and an H2 repeating its H1 — and confirming
each failed.

**On-page SEO is now closed.** What is specified and enforced: title, meta, H1,
H2 outline, breadcrumbs, slug, canonical, intent clusters, structured data per
template, robots, OG images, anchor text, click depth, orphans, and funnel
cul-de-sacs. The next work is building, and internal linking now has a complete
graph with anchor text to build from rather than a paragraph of advice.

**Status: 18 pages · 18 checks · 0 errors · 0 warnings · 59 tests green.**

### 20-18. Round nineteen — version 5.1 · the platform decision

The project owner chose **Base44** as the build platform. This document had a
framework named in three places and its reasoning built around one, so the
correction is structural rather than a find-and-replace.

**Section 3 now separates requirements from implementation.** Naming a framework
was a mistake of altitude: the framework was never the decision, it was one way
of satisfying it. The decision is nine numbered requirements — R1 to R9 — each of
which is a ranking or indexation constraint rather than a preference. A platform
change is now a change to one section instead of a rewrite.

**On the decisive question, this document does not guess.** Base44's own
documentation says crawlers receive fully rendered content including meta tags
and structured data. Its public feedback board carries long-standing,
heavily-upvoted requests stating the opposite — that meta tags are applied
client-side and social crawlers see only generic app-level tags. Both can be true
at different times, and the disagreement lands precisely on R1, R3, R4 and R8:
the requirements that decide whether 81 programmatic pages rank or sit invisible.

This is section 13-3 again, where two web sources gave contradictory federal tax
brackets. The response then was to stop reading and start deriving. The response
now is **section 3-5: a runnable verification protocol**, one throwaway app and
about a day, testing each requirement as Googlebot and as a social crawler
specifically — because prerendering is frequently user-agent gated, and testing
as a browser proves nothing. It ends at Search Console's URL Inspection, which is
Google's own answer and outranks every other source.

Section 3-3 writes the fallbacks down now, while they are cheap: configure it ·
put a prerender layer in front · split the surface so content is static HTML and
the calculators are embedded · or reduce the programmatic surface and revise the
revenue model honestly. **The last is a real outcome, not a threat** — 81
near-identical pages without per-entity metadata are the doorway pattern section
7-1 forbids, and that is why the protocol runs before the build rather than after.

**Section 3-4 states what does not change, which is most of the work.**
`data/pages.json`, the clusters, every formula, the H2 outlines, breadcrumbs,
anchor text, the link graph, the canonical rules, the JSON-LD shapes, the 18 CI
checks, both engines, and the 51-jurisdiction dataset assume no framework. They
specify what each page must contain. The platform question is only ever how those
values reach the HTML.

One rule was added to 3-7 for exactly this move: **the specification in
`data/pages.json` is authoritative over anything typed into a platform
dashboard.** Where a dashboard title disagrees with the formula, the formula is
right and the dashboard is drift. Without that rule, 18 CI checks quietly stop
meaning anything once the pages live somewhere the auditor cannot see.

Also updated: hosting (19-1) is now the platform's, so the section became
verifications rather than choices; the staging warning now covers the platform
subdomain, which must redirect to the custom domain rather than serve a second
copy of the site; and the `curl` item in the definition of done is now marked as
what it has become — the single most important check in that list.

**Status: 18 pages · 18 checks · 0 errors · 0 warnings · 59 tests green.**

### 20-19. Round twenty — version 5.2 · the generated on-page specification

Completing on-page SEO for a platform build means answering a question a
framework build never asks: **who types these values, and onto what?** On Base44
the answer is a dashboard field per page, and fifty-one hand-typed titles is
fifty-one chances to drift from the formula.

Four things were missing and are now present:

| Gap | Now |
|---|---|
| **Zero concrete JSON-LD** — only type names | Full payloads per template in `data/pages.json → onPage.jsonLd`, resolved per entity |
| **No FAQ formulas**, though 7-2 requires five per page with that entity's numbers | Question and answer templates per template *and per tax structure* |
| **No entity → platform field mapping** | `data/pages.json → platform`, with the rule that the specification wins over the dashboard (3-7-6) |
| **Nothing produced the actual values** | `scripts/generate_onpage.py` → `data/onpage.generated.json` + `docs/onpage-spec.md`, in CI |

All 51 states now resolve completely: title, H1, meta, canonical, breadcrumb, H2
outline, five FAQ entries with their own numbers, three JSON-LD blocks, internal
links with anchor text, and the dataset's verification state — so an unverified or
2025-figure state is visible at import rather than after publication.

**Generating them found three defects that reading the formulas had not.**

**1. Forty-eight of fifty-one metas were too short.** The auditor renders each
formula with the *longest* substitution to catch truncation, and never with the
shortest. Real state names produced 97–109 characters against a 110 minimum while
the audit reported clean. The audit now checks **both** extremes — check 19 — and
the affected formulas were rewritten to fit at each end.

**2. No single place formula can fit the window.**
`San Francisco-Oakland-Berkeley, CA` is 34 characters against `Akron`'s 5: a
37-character swing inside a 45-character meta budget. Hence the rule that formulas
use a **display name capped at 20 characters**, required on every metro row, with
the full MSA name appearing once in the body where precision helps and layout does
not care.

**3. "Texas tax brackets" was a heading on a state with no income tax.** One
outline applied to fifty-one states produces headings that are wrong on the page.
That is thin content of exactly the kind section 7-1 forbids, generated at scale
and looking tidy while being wrong. Outlines and FAQs now vary by the dataset's
`structure` field.

The third is the one to remember: **a formula that ignores its entity's shape
scales a mistake as efficiently as it scales a page.** It is also the argument for
generating rather than templating blindly — the defect was invisible in the
formula and obvious in the output.

**One thing deliberately left unresolved.** Every state's fifth FAQ answer is
`PENDING_ENGINE`, not a number. The engine can compute it, but that figure belongs
in the same run as the cost-of-living comparison and that dataset does not exist
(13-6). Writing a plausible number now is what rule 5-3 forbids, and the
placeholder is visible in the generated file so it cannot ship unnoticed.

**Status: 18 mapped pages · 19 checks · 51 generated state pages · 0 errors ·
0 warnings · 59 tests green.**

### 20-20. Round twenty-one — version 5.3 · the gaps a page count exposed

The question was whether on-page is finished. Counting rather than asserting gave
the answer: **no**, in three specific places.

| Group | Was | Now |
|---|---|---|
| **Trust pages** | Absent from `data/pages.json` entirely | 7 pages mapped, footer-linked, generated |
| **16 non-entity pages** | Formulas but no resolved values — hand-typed into a dashboard | Generated |
| **Guides** | Planned only | Template, rules and structured data added; still blocked on measurement |

The trust pages mattered more than seven suggests: section 6-3 builds them
**before** content and section 10-1 makes them a precondition for AdSense
approval. They had a paragraph in section 6-3 and nothing anywhere else — no
title, no meta, no breadcrumb, and no inbound link. A `globalFooter` was added to
the crawl graph, which is what keeps policy pages out of orphan status without
putting them in the main navigation.

**The generator now resolves 74 pages**, not 51, and two more defects surfaced the
moment they were rendered:

- **"How Sales Tax Calculator is calculated."** The tool outline used the tool's
  name where it needed the subject. Twelve pages, each with a clumsy heading in the
  position most likely to be quoted by an AI Overview (6-6). Tools now declare a
  `subject`.
- **A seven-character `<title>`** — `Privacy`. Valid, useless as a SERP line, and
  reads as an unfinished page. The trust template carries the site name now, and
  the audit gained a title minimum to sit beside its maximum (check 20).

Both are the same lesson as the no-tax-state headings one round earlier: **the
formula looked correct and the output was wrong.** Templates are not reviewable;
their output is. Three rounds running, the defect was invisible in the formula and
obvious in the generated page.

One structural addition: a template may now declare `h2OutlinePerPage`. An About
page and a Privacy page share no structure, and forcing one outline across both
produces headings that are wrong on at least one — the identical failure to
"Texas tax brackets" on a state with no income tax.

**What remains is blocked on inputs, not on specification.** Metro pages need the
BEA and HUD dataset; guides need their head terms measured. Both already have
templates, rules and collision checks, so each becomes generatable the day its
input arrives.

**Status: 25 mapped pages · 20 checks · 74 generated pages · 0 errors · 0 warnings
· 59 tests green.**

### 20-21. Round twenty-two — version 5.4 · the platform questions answered

The requirement questions from 3-1 were put to a live Base44 project and answered
on 2026-09-06. **The architecture is sound and the 81-page plan stands.**

| Verified | Inferred | Unknown |
|---|---|---|
| R1 content in HTML · R3 metadata from row data · R4 custom JSON-LD · R5 clean URLs · real `<a href>` links | R2 per-entity `<title>` · R8 social crawler tags | R7 404 status code · whether `*.base44.app` stays indexable |

**R3 is the answer that mattered most.** Titles are built from the row
(`Cost of living in ${country.name}`), not typed into a panel. That means the
annual tax update changes 51 titles by editing one dataset — the programmatic
architecture this document specifies, working as specified. The "reduce the
programmatic surface" fallback is withdrawn.

**Two answers are recorded as inferred rather than verified, deliberately.** Both
reason from the same premise: the SEO component sets the tags and the platform
pre-renders. R1 confirms pre-rendering delivers **body content**. It does not by
itself confirm it delivers **`<head>` tags**, which are set in a `useEffect` — a
different execution point, and a pre-renderer can capture one without the other.
For R8 the gap is wider: social crawlers never execute JavaScript at all, so the
question is entirely whether pre-rendering covers their user-agents. That was not
tested, and it is exactly the failure the platform's public feedback board reports.

This is not doubt about the answer. It is the same rule applied to the platform
that section 5-1 applies to every tax figure: **an inference is recorded as an
inference.** Section 3-5 is now three commands and about two minutes, rather than
the full protocol it held before.

**The most actionable thing in the answers was a caveat, not an answer.** Correct
metadata depends on every programmatic page calling the SEO component *with its
own row's values*. A page that omits it, or passes constants, ships a duplicate
title and looks completely fine. That is a **per-page obligation, not a platform
guarantee** — promoted to rule 3-7-6, added as risk 14, and the reason 3-5 now
says to sample **three** rows rather than one. It is the classic failure that holds
on the two pages someone checked and breaks on the thirtieth.

**Status: 25 mapped pages · 20 checks · 74 generated pages · 0 errors · 59 tests
green.**

### 20-22. Round twenty-three — version 5.5 · the thin-content measurement

Three standards were named as the ones that decide whether this site ranks: no
cannibalisation, sound programmatic structure, no thin content. Checking which
were actually enforced gave an uncomfortable answer — the first two were, and
**the third had been promised by section 6-10-4 for several revisions while
nothing measured it.**

`scripts/validate_content.py` now does. Its first run:

| Template | Pages | Median unique | Worst |
|---|---|---|---|
| TrustPage | 7 | 90% | 90% |
| DirectoryPage | 3 | 67% | 61% |
| ToolPage | 12 | 62% | 56% |
| **StateTaxPage** | **51** | **21%** | **16%** |

**The 51 state pages are roughly 80% identical furniture.** Every other check in
the project passed while that was true: cannibalisation, canonical, titles,
anchor text, crawl depth, orphans, clusters — all clean, on 51 pages that share
four fifths of their words.

That is the whole argument for measuring rather than asserting, in one table. The
project has been thorough about *which page targets what* and had no instrument at
all for *whether the page is worth having*.

**The measurement converts an instruction into a number.** With a 174-word
scaffolding at 21% unique, a 1,200-word body must itself be **43% unique** for the
finished page to clear the 40% threshold. "Write good unique content" is
unfalsifiable; "43% of this page's words must appear on no other state page" is
not, and it is met by exactly the material 7-2 already requires — that state's own
brackets, its own local tax rules, its own deadlines and authority.

Two corrections to the check itself, both the same class of error as previous
rounds:

- **The numeric-token rule fired on tool and directory pages**, which legitimately
  have no numbers in their copy — a calculator's numbers arrive at runtime. Scoped
  to entity templates.
- **The threshold judges a finished page**, so failing on scaffolding alone would
  fail on the absence of work not yet due. It warns before body copy exists and
  fails once `--bodies` points at real copy.

Also recorded, in section 2: **an exact-match domain does not change any of this.**
It is close to neutral as a ranking signal since 2012, gives a modest click-through
and natural-anchor-text benefit, and carries one asymmetry worth stating — a
keyword domain over near-duplicate generated pages is the precise pattern the EMD
update and the 2024 scaled-content-abuse policy were written to catch. It raises
the site's profile against the filter it is least able to survive. The conclusion
is not to change the domain; it is that 6-10-4 matters more here, not less.

**Status: 25 mapped pages · 20 checks · 74 generated pages · 5 CI validators ·
0 errors · 59 tests green.**

### 20-23. Round twenty-four — version 5.6 · the pilot

The previous round produced a number: a state page's body must be about 43% words
that appear on no other state page. Writing 51 bodies and *then* finding out the
approach cannot reach it would be the most expensive possible way to learn it.

Four were written first and measured. New York, Pennsylvania, Texas, Maryland.

**The experiment design mattered more than the result.** Measuring a few written
pages against many unwritten ones scores them falsely high — their body words are
trivially absent from pages that have no body at all. The script gained a
`--pilot` mode that compares only pages with copy, against each other.

| Set | Median unique | Worst |
|---|---|---|
| 3 states, maximally different (progressive · flat · none) | 45% | 45% |
| **4 states, adding one structurally similar to an existing one** | **47%** | **46%** |

The second row is the test that counts. New York and Maryland are both
progressive, both with a local income tax layer, both without a meaningful state
standard deduction — the pair most likely to collapse into paraphrase. Uniqueness
**rose**, which says the differentiation comes from substance rather than from
having picked dissimilar states for the first attempt.

**The pattern that produced it** is now a rule in 7-2, and it is stricter than the
number: every state page must contain at least one section that would be
**factually wrong or meaningless if the state name were swapped**. The city line
for New York. Philadelphia's Net Profits Tax for Pennsylvania. The
property-versus-income trade for Texas. The word "every" for Maryland — every
county levies, without exception, which is a different situation from a state
where a local levy is a caveat.

A page that survives a find-and-replace is a doorway page whatever its uniqueness
score says. The score is a floor, not the standard.

**Stated limitation:** the four bodies run about 550 words against the 900–1,400
that section 7-2 specifies. The pilot proves the ratio is achievable, not that it
survives being stretched — and length added without state-specific substance
dilutes uniqueness rather than adding to it. The CI check now runs against
`content/bodies` in pilot mode, so **the test gets harder automatically as bodies
are added**, which is the property worth having.

**Status: 25 mapped pages · 20 checks · 74 generated · 4 bodies written at 46%+ ·
6 CI validators · 0 errors · 59 tests green.**

### 20-24. Round twenty-five — version 5.7 · every page the data allows

"Complete every part of the document, every page." Measuring what was actually
missing separated two very different kinds of gap: work not done, and work waiting
on an input.

**Fifty-one placeholders were work not done.** Every state page's take-home FAQ
read `PENDING_ENGINE`. The reasoning for that had been sound — writing a plausible
number is what rule 5-3 forbids — but it quietly ignored that **the engine exists
and is tested to the cent**. The honest fix was to run it.

`scripts/compute_takehome.ts` computes a $95,000 single-filer scenario in all 51
jurisdictions. Oregon keeps $66,993 at an effective 29.5%, $7,167 of it state tax;
Texas keeps $74,160 at 21.9% with no state layer. Fifty-one answers, each carrying
its own arithmetic, none estimated.

**The $7,167 spread is the linkable asset section 9-5-2 specifies** — "net pay on
$95,000 in all 51 jurisdictions". Section 4-9-5 quoted that figure before anything
had produced it. The number was right and is now sourced, which is a better state
for it to be in.

**Metro pages were the other kind of gap, and the gate answered it.** Section
6-10-3 requires a *measured* head-keyword volume of ≥500/month. Four metros have
one — Austin 3,600, San Francisco 2,900, San Antonio 1,900, Houston 1,900. The
other 26 in the revenue model are a modelled median of 1,500, and **a modelled
median is not a measurement**.

So `data/metros.json` has four rows rather than thirty, and all four are generated
with title, meta, H1, breadcrumb, outline, JSON-LD, internal links and the tax FAQ
answer already computed. Only the three index and rent answers wait on BEA and
HUD. That is the gate working rather than a shortfall — and 6-10-7's sample stage
wants five pages, so the set is nearly the right size already.

**A caveat is recorded in the data file itself:** three of the four are Texas
metros, which reflects which keywords happened to be measured rather than any
property of Texas. A fifth outside Texas should be measured before the sample is
treated as geographically representative.

**Where completeness now stands: 78 of 78 buildable pages have generated on-page
values.** What is left is genuinely blocked on inputs — BEA/HUD figures for three
metro FAQ answers, and keyword measurement before any of the nine guides may be
promoted out of `plannedPages`.

**Status: 78 generated pages · 20 checks · 7 CI validators · 4 bodies at 46%+ ·
0 errors · 59 tests green.**

### 20-25. Round twenty-six — version 5.8 · the rule the guide was missing

The question was whether the SEO, content and copywriting documents are complete
enough that keyword targeting will not be lost. Checking rather than agreeing found
that it already had been.

**The four pilot bodies scored 46% unique and contained 0 of their 5 cluster
variants.** Not one of them used the phrase people actually search. The head
keyword was absent from all four.

**The cause was structural, not carelessness.** Every rule in the copywriting guide
pushes toward varied phrasing — vary the sentence shape, do not repeat, find the
angle nobody else has — and nothing pushed the other way. A writer following those
instructions exactly writes "Maryland's schedule" and "the Maryland tax estimate",
and never once writes "Maryland tax brackets".

This is the sharpest example yet of a pattern this project keeps hitting: **an
instruction that is correct in isolation produces a wrong result when it is the
only instruction.** The uniqueness work was right. It was also, on its own,
capable of producing four pages that rank for nothing.

Three fixes:

- `contentBudget.minVariantsInBody` requires **at least two** cluster variants in
  the body, enforced by `validate_content.py`.
- Section 3-a of the copywriting guide covers where variants go and what a natural
  placement looks like — the test being whether you would have written the phrase
  if nobody had told you it was a keyword.
- The four bodies were fixed with natural placements only. Texas now reads "There
  is no Texas income tax rate to quote and there are no Texas tax brackets", which
  is both a keyword placement and the most accurate sentence on the page.

**The trade-off was measured rather than assumed.** Adding two variants per page
moved uniqueness from 45%/43% to 44%/42% — about half a point per variant, because
a phrase repeated on every page becomes shared vocabulary by definition.

That is why the floor is two and not five. Five per page would cost roughly two and
a half points and leave the worst page at about 40%, on the threshold with nothing
spare. **Uniqueness and keyword coverage pull against each other, and two is where
the trade sits.**

**Status: 78 generated pages · 20 checks · 7 CI validators · 4 bodies at 42% unique
with variants hit · 0 errors · 59 tests green.**

### 20-26. Round twenty-seven — version 5.9 · where the words should have gone

Asked what the right next move is, the honest answer was that the last two rounds
had been optimising the wrong thing. Counting bodies against search volume:

| Template | Pages | Bodies written | Searches/month |
|---|---|---|---|
| **ToolPage** | 12 | **0** | **553,600** |
| StateTaxPage | 51 | 4 | 2,040 |

Four bodies had been written for the 2,040-search group and none for the
553,600-search group. **A 271× misallocation**, and it looked like diligence the
whole time.

**A correction to an earlier claim in this document.** Round 20-24 framed the
cost-of-living dataset as blocking a cluster "77× the entire state set". That
compared the wrong things. The precise split:

| | Searches/month | Share |
|---|---|---|
| Blocked on the BEA/HUD dataset | 159,400 | 24% |
| **Buildable today** | **512,320** | **76%** |

The two cost-of-living *tools* (110,000 searches) are blocked because a calculator
with no index data cannot function — that part of the earlier claim holds. But the
tax, payroll and mortgage tools carry 510,280 searches and are buildable now, on an
engine that already exists and passes 59 tests. **Three quarters of the cluster was
never blocked on anything.**

Four tool bodies were written, highest volume first — sales tax, salary-to-hourly,
income tax, take-home pay — covering 360,500 searches a month. They measure at
**56% median unique, 55% worst**, comfortably above the 40% threshold and better
than the state pages, because a sales tax page and a mortgage page have less shared
vocabulary than fifty-one state pages ever will.

**And the keyword check had the same blind spot as the writing.** It was scoped to
entity templates, so the first four tool bodies hit 1 of 5 variants and nothing
complained. The check now covers **any page with a declared cluster** — which,
again, means it now covers the group carrying 553,600 searches rather than only the
group carrying 2,040.

The pattern is worth naming, because it has now appeared three rounds running:
**the instrument is scoped to where the last problem was found, not to where the
value is.** Uniqueness was measured before keyword coverage. Entity pages were
checked before tool pages. State bodies were written before tool bodies. Each was a
reasonable next step from the previous one, and the sequence drifted away from what
matters.

**Status: 78 generated pages · 20 checks · 8 CI validators · 8 bodies written
(4 tool at 55%, 4 state at 42%) · 0 errors · 59 tests green.**

### 20-27. Round twenty-eight — version 5.10 · the tool bodies

All twelve tool page bodies are written. **553,600 searches a month now have copy**,
against zero at the start of the round.

| Template | Pages | Bodies | Median unique | Worst |
|---|---|---|---|---|
| ToolPage | 12 | **12** | **58%** | **55%** |
| StateTaxPage | 51 | 4 | 44% | 42% |

Tool pages measure substantially better than state pages, and the reason is
structural rather than a matter of effort: a sales tax page and a mortgage page
share far less vocabulary than fifty-one state pages ever can. **The 40% threshold
is much harder to clear on entity templates**, which is worth knowing before
writing the remaining 47 state bodies.

Two defects surfaced while writing.

**The keyword check could not see across a line break.** Markdown wraps, so
"cost of living comparison\ncalculator" is one phrase on the page and two strings
in the file. The check reported a missing keyword that was plainly present, which
is the failure mode most likely to make someone edit correct copy to satisfy a
broken instrument. It now collapses whitespace and strips emphasis before matching.

**Three of the first four tool bodies hit 1 of 5 variants** and nothing complained,
because the check was still scoped to entity templates. Fixed in the previous
round; this round confirmed the fix catches real cases — `tax-withholding` was
caught and corrected on the way in rather than after the fact.

**One shortfall, stated rather than hidden.** Section 7-2-1 specifies 600–900 words
for a tool page. These run 448–600. They are complete in structure — every section
of the brief is present — but they sit at or below the floor of the range.

The headroom exists to grow them: at 58% unique they are well clear of the 40%
threshold, unlike the state pages at 44%. But the length finding in 6-10-4-1 applies
— words added without substance dilute rather than add — so growing them means
finding more that is genuinely specific to each tool, not padding to a count.

**Status: 78 generated pages · 20 checks · 8 CI validators · 16 bodies (12 tool at
55%, 4 state at 42%) · 553,600 searches covered · 0 errors · 59 tests green.**

---

## 21. Ruthless audit — 2026-09-12

Six findings, measured rather than asserted, ordered by what they cost against the
$500–700 goal. Two of them change the plan; the rest are work not yet done.

### 21-1. The dataset blocks the funnel, not just 24% of the traffic

This is the finding that reframes everything else.

| Funnel stage (2-2-2) | Pages available |
|---|---|
| **1 — place** | **0 of 3** |
| **2 — compare** | **0 of 1** |
| 3 — income | 1 of 2 |
| 4 — keep | 8 of 8 |
| 5 — settle | 2 of 2 |

**Stages 1 and 2 are entirely blocked**, and they are the funnel *entrance*. Round
20-26 recorded the BEA/HUD dataset as blocking 24% of search volume. That
understated it, because the revenue model's largest single lever — session depth at
2.2 pages, worth +105% — is built on a funnel that starts at stage 1.

| Pages per session | Year 2 revenue |
|---|---|
| 1.1 — no funnel | $169 |
| **2.2 — the model's base case** | **$346** |

Launching with stage 4 alone is a site of tax calculators that link to each other.
**That is roughly $177 a month at year two, about half the projection** — on top of
the 24% of traffic already counted.

**The dataset is therefore worth 24% of traffic plus roughly half the revenue on
the other 76%.** It is not one of several priorities. It is the precondition for
the business model, and `scripts/fetch_cost_of_living.py` is two commands away from
resolving it.

### 21-2. There is no author, and that is an AdSense blocker

`data/pages.json` still carries `{AUTHOR_NAME}` unresolved and `site.origin` as
`https://example.com`.

Section 7-4 requires a named author with a profile page and relevant background,
and section 6-3 names a vague About page as **the most common reason for AdSense
rejection in a YMYL niche**. Section 10-1 makes the trust pages a precondition for
approval.

No amount of content fixes this. It needs a real person's name, a real background,
and a real contact route — and it needs deciding before the trust pages are
written, because they are written around it.

**Everything downstream of AdSense approval depends on a decision nobody has
made.**

### 21-3. Link building has a section and no artifact

| Concern | What exists |
|---|---|
| Tax engine | 59 tests, a validator, CI |
| On-page SEO | 20 checks, 78 generated pages, CI |
| Content uniqueness | A validator, a measured pilot, CI |
| **External links** | **A prose section** |

Section 14 concludes that **domain authority is the binding constraint** and
section 9-5 allocates **30% of project time** to it. Neither produced a target
list, an outreach record, or a way to tell whether the month-6 goal of 5–10
referring domains is being met.

The project instrumented everything it could measure and left the thing it
identified as the critical path entirely unmeasured. That asymmetry is not an
oversight in one section; it is the shape of the whole project.

### 21-4. 94,400 searches a month have no recorded decision

Section 18-1 requires a decision for every tool in the catalogue. Absence of a page
is a legitimate outcome; absence of a decision is not.

| Tool | Volume | CPC | Status |
|---|---|---|---|
| bonus tax calculator | 22,200 | **$9.61** | No page, no deferral, no rejection |
| heloc payment calculator | 27,100 | **$9.92** | " |
| lottery tax calculator | 22,200 | $5.77 | " |
| capital gains tax calculator | 14,800 | $3.96 | " |
| effective tax rate calculator | 6,600 | $2.87 | " |
| 1099 tax calculator | 1,500 | $5.81 | " |

Two of them carry the **highest CPCs in the entire catalogue**. They may well
belong outside the context boundary — that is a defensible answer — but nobody has
given it, and the catalogue exists precisely so that this question gets answered
rather than drifted past.

### 21-5. The guides are the link asset, and they do not exist

Nine pages. Section 9-5-2 calls guides the main recipient of external links, which
makes them the intended solution to the constraint in 21-3.

**Zero have measured keywords, so none can be promoted out of `plannedPages`, so
none can be written.** The blocker is one keyword research pass.

### 21-6. The ratio of specification to artifact

| | |
|---|---|
| Specification | 3,836 lines |
| Body copy | 9,238 words |
| Engine tests | 59 passing |
| **Pages built** | **0** |

This has been flagged repeatedly and remains true. The specification is now
considerably more complete than anything that could be built from it in a week,
and every additional round of specification widens the gap rather than closing it.

### 21-7. What this audit does not find

Stated so the list above is read in proportion. The keyword targeting is sound and
enforced. Cannibalisation is measured across 20 checks. Thin content has a
validator and a measured pilot. The tax engine is tested to the cent against
statute. The on-page specification is complete for all 78 buildable pages.

**The work that was done is solid. The finding is that it was not always the work
that mattered most** — 21-1 and 21-3 are both cases of the project going deep where
it could measure rather than where the value was.

---

### 20-28. Round twenty-nine — version 5.12 · the handoff

Two decisions from the audit in section 21 are now made, and the specification is
packaged for handoff.

**Author: H.Hemati.** Recorded in `data/pages.json → site.author` and resolved
through every generated `Person` and `Organization` block —
`{AUTHOR_NAME}` no longer appears anywhere in the output. What is deliberately
**not** done: the background paragraph on `/about`. Inventing a biography is the one
thing that would make a YMYL trust page worse than leaving it blank, so the name is
set and the substance is a human's to write.

**Domain: deferred by choice**, built first and bought later. That sequence is fine
and carries exactly one risk, now recorded as section 19-7:

> If the site is indexed on a platform subdomain and the custom domain arrives
> afterwards, the authority earned belongs to a domain being abandoned — and both
> hosts serving identical content is a duplicate of the whole site.

The rule that removes it costs nothing: **nothing is indexable until the real
domain is connected.** No Search Console property, no sitemap, no public link
during the build. Section 15-1 still holds — Search Console history cannot be
backfilled — but it starts from the domain, not from the build, so connecting the
week before launch loses nothing.

This is also the case the generated on-page values were designed for. `site.origin`
is one value; the domain arrives, it is set, `generate_onpage.py` runs, and 78
pages update. Had these been typed into a dashboard, buying the domain late would
mean editing 78 canonicals by hand.

**[`docs/base44-build-brief.md`](base44-build-brief.md) is the handoff document.**
It states what to build and, more usefully, what not to improvise — the SEO values
are generated data rather than suggestions, the tax engine is imported rather than
reimplemented, and the context boundary is a list of things that must not be added
however reasonable they sound.

**Verification at handoff:** 20 checks · 0 errors · 0 warnings · thin content
measured at 58% (tools) and 44% (states) against a 40% floor · 78 pages generated ·
73 link edges all carrying anchor text · 59 engine tests green.

**Status: 78 generated pages · 20 checks · 8 CI validators · 16 bodies · author
set · 0 errors.**

---

### 20-29. Round thirty — version 5.13 · the portfolio did not match the identity

**What was found.** Section 2-2 states the identity as *"the real cost of living in a
place — and what you actually keep"*. The tool portfolio built to serve it was 12 tools,
of which **6 were tax tools**. Measured by search volume the split was:

| Side | Tools | Volume | Share |
|---|---|---|---|
| Cost of living (stages 1, 2, 5) | 4 | 110,000 + 73,600 | **20%** |
| Tax (stage 4) | 6 | 316,100 | **57%** |

The funnel entrance — the half of the identity sentence that comes first — had one tool.
The moat had six.

**What was missing.** A live keyword pull found that the spec contained no entry at all
for the largest life-side terms. `rent`, `afford` and `living wage` each appeared **zero
times** in `data/keywords.json`:

| Term | Volume | CPC |
|---|---|---|
| rent affordability calculator | 90,500 | $0.69 |
| rent calculator | 60,500 | $1.02 |
| home affordability calculator | 49,500 | $2.51 |
| living wage calculator | 12,100 | **$6.36** |

**Rent is not an adjacent topic — it is the largest component of the thing this site
measures.** BEA's Regional Price Parity is built from rent, goods and services, and
section 2-4 already committed to HUD Fair Market Rent at county level as the rent
source. These tools therefore needed **no new dataset**: they run on data the project
had already decided to fetch.

**What changed.**

| Action | Page | Volume |
|---|---|---|
| Added | `/tools/rent-affordability-calculator` (stage 1) | 90,500 |
| Added | `/tools/home-affordability-calculator` (stage 5) | 49,500 |
| Added | `/tools/living-wage-calculator` (stage 3) | 12,100 |
| Removed | `/tools/paycheck-tax-calculator` | 18,100 |
| Removed | `/tools/tax-withholding-calculator` | 14,800 |

Net **+119,200** searches a month, and the life side moved from 20% to **48%** of tool
volume. `sales-tax` and `property-tax` were kept: both are genuinely part of what a
place costs, which is the test section 6-1 applies. `paycheck-tax` and `tax-withholding`
failed that test — they are payroll mechanics, and their intent was already inside
`take-home-pay`, whose output now carries the per-paycheck breakdown that justified them.

**Three second-order corrections this forced:**

1. **A planned guide had to go.** `/guides/salary-needed-to-live-in-city` was declared
   with the intent *"given one place, what absolute income clears its cost of living"* —
   which is precisely the living wage tool's intent. Per the rule in `plannedPages`, a
   guide duplicating a tool's intent is cannibalisation that ships. The tool's head term
   is measured and the guide's was not, so the guide was removed. Guides: 9 → 8.

2. **The auditor rejected an overclaim of mine.** The three new clusters were written
   with `variantsMeasured: true` when only their head terms had been measured. Check 11
   refused all three. Corrected to `false`, and the two variants that *were* measured
   (`how much house can i afford calculator` 33,100, `how much rent can i afford
   calculator` 4,400) went into `keywords.json` as real data. This is the check earning
   its place: the overclaim was invisible in the prose and fatal in the data.

3. **`moving cost calculator` was rejected despite a $13.80 CPC** — the highest in the
   project. There is no free authoritative dataset for mover rates, so the tool would
   have to invent multipliers, which section 2 forbids and which is how thin content
   gets built. It is recorded here as a deliberate rejection rather than an oversight.

**The pattern, again.** The six tax tools entered the spec because they had high CPC.
That is the same failure mode section 21 named: *the instrument gets scoped to where the
last problem was found, not to where the value is.* Here it had a second edge — optimising
for CPC selected for **dead-end pages**. Someone searching `sales tax calculator` takes a
number and leaves; someone searching `rent calculator` is mid-decision about where to
live, which is the entire funnel. Section 2-2-2 makes session depth the only revenue
variable fully under our control, and the portfolio had been built against it.

**Status: 79 generated pages · 20 checks · 0 audit errors · 17 bodies (13 tool at 59%
median unique) · life side 48% of tool volume.**

---

### 20-30. Round thirty-one — version 5.14 · the link graph was never measured

Section 9-3 had rules for anchor text, click depth and orphans, and every one of
them passed. None of them asks the question that decides whether a page ranks:
**does the page receiving the internal links have the demand that justifies them?**

**The instrument was wrong first.** A first pass treated each declared row in
`data/pages.json` as one node. But `/cost-of-living/{metro}` is 30 URLs and
`/state-taxes/{state}` is 51: **26 declared rows are 105 real URLs**, and the two
programmatic sets are 77% of them. Collapsing them understated the equity the
programmatic pages pass by roughly two orders of magnitude and produced a
different, wrong answer. `scripts/analyze_link_equity.py` expands the templates
before running PageRank.

**What the corrected measurement found.**

| Page | Demand | Equity | Support |
|---|---|---|---|
| `/tools/sales-tax-calculator` | 16.5% | 5.2% | **0.32x** |
| `/tools/rent-affordability-calculator` | 13.6% | 6.2% | **0.46x** |
| `/tools/salary-comparison-by-city` | 0.7% | 7.1% | **10.8x** |

The highest-volume page in the project had **one** inbound link, from the tool
index. The 4,400-search page had four. And the 81 programmatic pages — the site's
entire equity reservoir — linked to **neither** of the two largest tools.

**The cause is structural, not an oversight.** Links were written when each page
was written, so every page links to what its author had in mind at the time.
Nothing ever looked at the resulting distribution. That is how a site ends up
routing its authority to its smallest pages while its largest ones starve.

**What changed.** Nineteen body links were added, every one of them justified by
subject rather than by the metric:

- **The 30 metro pages** now link to rent affordability and sales tax. Rent is the
  largest line in any metro's cost and sales tax is what makes its goods cost what
  they do — these were missing links about the page's own subject.
- **The 51 state pages** now link to sales tax: the other half of what a state takes.
- **The home page linked to 3 of 13 tools**, all three already over-supplied. It now
  carries the highest-demand tools as well. A home page that promotes a site's
  smallest pages is an on-page defect in its own right.
- Sales tax had two outbound links and no route back into the funnel; it now
  returns to the cost-of-living directory.

**Result: every keyword page moved into the 0.76x–1.27x band; zero under-linked.**
The two remaining over-linked pages (`living-wage` 5.8x, `salary-comparison-by-city`
7.0x) are small pages whose inbound links are all topically correct. Removing a
relevant link to flatten a ratio would be gaming the instrument, which is the
failure this section exists to prevent.

**A keyword correction, found while checking the new tools.** `living wage
calculator` was recorded at 12,100 @ $6.36. That figure belongs to **`mit living
wage calculator`** — a branded navigational query for `livingwage.mit.edu` that
cannot be targeted at all. Verified against the live SERP: the real head term is
**5,400 @ $9.06**. The page stays, on the highest CPC in the project, but the
justification in 20-29 was overstated and is corrected here.

**A rejection, measured rather than assumed.** A programmatic rent set
(`/rent/{metro}`) was considered and rejected: `average rent in {city}` measures
1,000–1,300 per city, and the metro pages already carry rent as a section. It
would have been 30 thin pages competing with 30 existing ones.

**What the SERP says about the living wage page.** At positions 3 and 4 for
`living wage calculator` sit NerdWallet's and Bankrate's **cost-of-living**
calculators. Google is blending the two intents, which means this page carries a
real cannibalisation risk against our own `/tools/cost-of-living-calculator`. The
differentiation rule applies with more force here than anywhere else on the site:
one solves for cost given a place, the other solves for salary given a place, and
the headline number must make that unmistakable.

**Status: 79 generated pages · 21 checks · 9 CI validators · 0 under-linked pages.**

---

*End of document. Any change to the decisions in section 2 requires revising this document, not a local patch.*
