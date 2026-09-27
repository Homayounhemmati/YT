# Build brief for Base44

This is the construction specification for the site. The SEO values are generated
data rather than suggestions: they live in `data/onpage.generated.json` and every
one is validated in continuous integration.

> **The most important property of this build:** every page's title, meta
> description, H1, canonical, breadcrumb and JSON-LD originate from that file. They
> are imported, never authored in the application and never entered by hand into an
> SEO panel. A value that disagrees with the file is a defect (spec rule 3-7-6).

---

## 0. Build order — read this before starting

**71 of the 78 pages are fully buildable and functional today.** Seven are not:

| Page | Why |
|---|---|
| `/tools/cost-of-living-calculator` | No index data to compute with — a calculator that cannot calculate |
| `/tools/cost-of-living-comparison` | Same |
| `/tools/salary-comparison-by-city` | Same |
| `/cost-of-living` + 4 metro pages | 3 of 5 FAQ answers are placeholders, and a cost-of-living page with no cost data is thin content by definition |

All seven wait on one thing: the BEA/HUD dataset, which is two commands outside the
sandbox (`scripts/fetch_cost_of_living.py`).

### This does **not** block starting

**Build the 71 now.** The ordering problem that would normally exist — launching
without the funnel entrance costs roughly half the projected revenue (spec 21-1) —
does not apply during construction, because **nothing is indexed until the domain
is connected anyway** (section 7 below).

So the sequence is:

1. **Build the 71 functional pages.** Nothing public, nothing indexed.
2. **Fetch the cost-of-living dataset** — two commands, any machine with internet.
3. **Add the remaining 7 pages**, now with real data.
4. **Buy the domain**, set `site.origin`, regenerate, re-import.
5. **Then** remove the index block and launch — with the funnel intact.

### What must not happen

**Do not launch with the 71 alone.** Seven of them link into the place cluster and
become dead ends without it, which means a visitor arriving from search leaves
after one page. The revenue model assumes 2.2 pages per session; without the funnel
entrance it is 1.1, and that is roughly half of year-two revenue.

The 71 are a complete, correct build. They are not a complete site.

## 1. What the site is

A calculator site answering one question in two halves: **what a place costs, and
what you keep there.** Everything is built around that sentence; anything that does
not answer it is out of scope and must not be added.

- **English only.** No other language anywhere in the UI or content.
- **Author:** H.Hemati. Named on `/about` and in the `Person` JSON-LD.
- **Domain:** not yet purchased. See section 7 — this affects what you must NOT do.

---

## 2. Entities — the data behind the generated pages

Two entity collections drive 55 of the 78 pages.

### `states` — 51 rows, data ready

Source: `src/data/tax-year-2026/states/{slug}.json`

| Field | Type | Note |
|---|---|---|
| `slug` | string | The URL segment. Never changes after launch |
| `name` | string | "California" |
| `abbr` | string | "CA" |
| `structure` | enum | `progressive` · `flat` · `none` — **drives which page layout is used** |
| `brackets` | object | Per filing status, each `{from, rate}` |
| `flatRate` | number\|null | |
| `standardDeduction` | object | |
| `localTaxNote` | string\|null | Displayed as its own section when present |
| `personalExemption` | object\|null | Per filing status: `amount`, optional `agiSchedule` (Maryland: the amount steps down above each AGI line) or `maxAgi` (Illinois: none above it). Subtracted after the standard deduction |
| `benefitRecapture` | object\|null | **New York only.** The section 601(d-5) supplemental tax, as the statute's own table. Must be applied — see section 5 |
| `employeeContributions` | array | Payroll contributions withheld from wages that are not income tax — New York Paid Family Leave (0.432%, max $411.91) and disability insurance (0.5%, max $0.60/week), Pennsylvania employee unemployment (0.07%). On **gross** wages; a 401(k) does not reduce them. Show them as their own line on the result card |
| `verification` | enum | Only `"verified"` states are built (the gate in `data/onpage.generated.json` already reflects this) |

### `metros` — 4 rows, data ready (pages wait for their written bodies)

Source: `data/metros.json`. Only four metros exist because the generation gate
requires a **measured** search volume of ≥500/month. Do not add more.

| Field | Note |
|---|---|
| `slug` `name` `displayName` | `displayName` is capped at 20 characters and is what appears in titles |
| `stateSlug` | Links the metro to its state page — **this cross-link is the site's main differentiator** |
| `indices` `referenceRent` | BEA Regional Price Parities 2024 and HUD FY2026 Fair Market Rents — full records in `src/data/cost-of-living-2024/us/{slug}.json`, both checked against the publishers' own files |

---

## 3. Routes

```
/                               home
/tools                          tool index
/tools/{slug}                   13 tool pages
/cost-of-living                 directory
/cost-of-living/{metro}         metro pages — only those in the sitemap (0 today)
/state-taxes                    directory
/tools/paycheck-calculator/{state}   state paycheck pages — only those in the sitemap (8 today)
/about /methodology /sources /editorial-policy /privacy /terms /contact
```

**URL rules — these are not negotiable and cannot be changed after launch:**

- Lowercase, hyphenated, no trailing slash, no file extension.
- **No year in any URL.** The year appears in titles only.
- Query parameters are UI state only. They never create a page and are always
  stripped from the canonical.
- A slug change after launch costs a permanent redirect. Get them right now; they
  are already correct in the generated file.

---

## 4. SEO implementation

### Per page, from `data/onpage.generated.json`

Each entry has: `path` `title` `h1` `metaDescription` `canonical` `breadcrumb`
`h2Outline` `faq` `jsonLd` `internalLinks`.

### The four requirements that decide whether this works

| # | Requirement | Why |
|---|---|---|
| **R1** | Page text is in the HTML the server returns, **before JavaScript runs** | Google's renderer is a second, deferred queue. A new domain cannot afford it |
| **R2** | `title`, `description`, `canonical` in that same initial HTML, **different per row** | A formula that applies after hydration is a formula search engines may never see |
| **R4** | JSON-LD in the initial HTML, per entity | Same reason |
| **R8** | Open Graph tags per entity in the initial response | Social crawlers execute no JavaScript at all |

**Verify these, do not assume them.** After the first two entity pages exist:

| # | What to request | Expected |
|---|---|---|
| 1 | The raw HTML of `/state-taxes/california` | Contains the page text and a `<title>` tag |
| 2 | The raw HTML of `/state-taxes/texas` | A **different** `<title>` from the one above |
| 3 | The same page's `<head>` | Contains an `application/ld+json` block |
| 4 | The page as seen by a social preview service | Per-entity `og:title`, not a site-wide default |
| 5 | The HTTP status of a path that does not exist | **404**, not 200 |

Request the raw server response, not the rendered page in a browser. The two
differ, and only the first is what a search engine reads first.

**Check three different rows, not one.** The failure mode is a page that forgets to
set its metadata; it looks fine and ships a duplicate title, and it will not be the
page you sampled.

### Headings

- Exactly one `<h1>`, and it is the `h1` value from the file.
- `<h2>`s are the `h2Outline` values, in order, unchanged.
- Never skip a level.
- **State pages use a different outline depending on `structure`.** A no-tax state
  must not render "Texas tax brackets" — that outline is already correct in the
  generated file, so use it rather than a single shared template.


### The comparison categories — three, not five

The comparison and cost-of-living tools display **exactly the categories BEA
publishes a separate index for**:

| Displayed | Source |
|---|---|
| Rent | BEA RPP, rent component |
| Goods | BEA RPP, goods component |
| Other services | BEA RPP, services component |

**Food and transport are not separate categories.** BEA does not publish them
individually at metro level — food sits inside goods, transport inside services.

> **Do not add a food row, a transport row, a healthcare row or a utilities row.**
> No official index exists for them at this granularity, and the only way to fill
> such a column is to estimate it.
>
> This is not a hypothetical caution. The project's original dataset had a
> transport column holding 132 for New York (a transit pass) and 250 for Los
> Angeles (car ownership) — two different methodologies in one column, which makes
> every comparison using it wrong. It also had an insurance column sitting between
> $195 and $215 for all 24 cities, which is not what insurance costs anywhere.

A category with no official index is **omitted**, and the page says which
categories it covers. An honest three-column comparison is worth more than a
five-column one where two columns are invented, because the audience for this site
knows what their own costs are and will notice.

### Internal links

`internalLinks` gives every link with its anchor text. Both matter.

- Render real `<a href="/path">` elements. **Not** a click handler on a `div` —
  a crawler follows an anchor and ignores everything else.
- Use the supplied anchor text verbatim. It is written with the destination's
  keyword, never the source's.
- Plus a fixed header (Home · Calculators · Cost of Living · State Taxes) and a
  fixed footer (the seven trust pages) on every page.

### Crawl configuration and sitemap

- Internal and API paths are excluded from crawling. **No content page is ever excluded.**
- One sitemap index with four children: tools, places, states, guides. This is so
  indexation can be read per page type — a single flat sitemap makes that
  impossible.
- **Build exactly the URLs in `data/onpage.generated.json` → `sitemap`.** Pages
  marked `"built": false` are behind the publication gate (no body yet, no data, or
  prior-year figures): they get no route, no link and no sitemap entry until they
  appear in a regenerated file. Links to them have already been resolved away.
- `<lastmod>` only on genuine content change. **If the platform stamps every URL on
  every deploy, omit the field entirely** — a dishonest `lastmod` teaches Google to
  ignore it across the whole site.

---

## 5. The calculators

Every calculator has a tested reference implementation in this repository.

| Engine | Covers | Tests |
|---|---|---|
| `src/lib/tax/` + `payroll.ts` | Income tax, take-home / paycheck (salary, per-period, 401(k) and section 125 rules, state exemptions, New York supplemental tax, state payroll contributions) | 97 |
| `src/lib/col/` | Cost of living, comparison with tax, rent affordability, living wage, household monthly cost | 38 — including real BEA, HUD and BLS data |
| `src/lib/calc/` | House payment (PITI, PMI), home affordability, closing costs, salary↔hourly, sales tax, property tax | 20 |

**New York's supplemental tax.** Above $107,650 of AGI, New York adds a tax that takes
back the benefit of its lower brackets (Tax Law section 601(d-5)). The dataset carries
the statute's table (`benefitRecapture`); `supplementalTax()` in `src/lib/tax/state.ts`
applies it clause by clause. A build that applies only the bracket table is wrong for
every New York salary above that line — the $150,000 and $300,000 New York rows in the
acceptance file exist to catch exactly that.

**If the platform can import these modules, import them — never reimplement.** If it
cannot, the platform's calculators must reproduce **every row of
`docs/calculator-acceptance.md` to the cent** before launch. That file is generated
from the engines; a calculator that disagrees with it is wrong, and it is the
calculator that changes. This is a your-money-or-your-life subject where a wrong
number is the whole risk.

### The cost-of-living calculator — inputs and result card

This is the centre of the funnel: paycheck pages send visitors here, and it sends
them on. Build it to this contract (engine: `cityMonthlyCost`, `grossForNet`,
`suggestedBedrooms` in `src/lib/col`).

**Inputs** — never an empty form; defaults shown on first paint:
1. Metro (select). 2. People in the household, 1 to 5+ (default 1). 3. Bedrooms
(default `suggestedBedrooms(people)`, changeable). 4. Optional: the visitor's own
monthly figure for any line — it replaces that line's estimate. 5. Optional: a salary.

**Result card, in this order:**
1. **What a month costs** this household here — the total, labelled "estimate for a
   typical household of this size" unless every line is the visitor's own.
2. **The salary that covers it after {State} tax** — `grossForNet(annual total)`.
3. **Line by line** — each line with its basis: *HUD Fair Market Rent* · *national
   average at local prices* · *your figure*.
4. **Next steps** (the funnel): compare with where you live now → the comparison;
   what your salary leaves in {State} → that state's paycheck page; can you afford
   the rent → rent affordability.
5. The year of every source, and every warning the engine returns.

The comparison tool leads with `equivalentSalaryAfterTax`: the destination salary
that buys, after that state's tax, what the current salary buys after the current
state's — and shows the price-only answer beside it, so the tax effect is visible.

### Promises the published copy makes — the build must keep them

The trust pages state these as facts. Each is a build requirement, not a nice-to-have:

- **Calculations run in the browser.** No input a visitor types — salary, rent, price —
  is sent to the server, written to the platform's database, or included in an
  analytics event (privacy page, "What stays in your browser").
- **Analytics events carry categories, never values** (`docs/measurement.md` section 1).
- **Footer links:** a consent-settings link for EEA/UK/CH visitors (Google-certified CMP)
  and "Do not sell or share my personal information" for US-state visitors.
- **A contact form** on `/contact` that reaches the author (contact page, first line).
- **State citations beneath each state calculator**, taken from that state's
  `provenance.sources` in the dataset (sources page, "State tax sources").
- **No ad between a calculator and its result** (about page, "How this site makes money").

### Calculator UX

- **Never opens empty.** Realistic defaults, result visible on first paint. An
  empty form makes the user work before seeing value, and they leave.
- At most 4 visible fields; advanced ones collapsed.
- `inputmode="decimal"`, thousands separators, 300 ms debounce.
- Changing the state or metro **preserves** the user's other inputs.
- **Every warning the engine returns must be displayed.** They are in the result
  object. Discarding them turns an honest tool into a confident wrong one.

### Ads

- Three slots maximum: after the result, mid-content, sidebar (desktop only).
- **Never above the result.** The user came for the number.
- Fixed `min-height` reserved from first paint — layout shift must stay under 0.1.
- **No ads on the seven trust pages.**

---

## 6. Performance

| Metric | Ceiling |
|---|---|
| Initial JS, compressed | 90 KB |
| Page weight excluding ads | 350 KB |
| LCP | 2.0 s |
| CLS | 0.1 |

No charting library — the breakdown bar is CSS and inline SVG. No date library;
`Intl` is sufficient.

---

## 7. Before anything is public

**The domain is not bought yet, and that changes the launch sequence.**

> **Nothing may be indexable until the real domain is connected.**

If the site is indexed on a `*.base44.app` subdomain and the domain arrives
afterwards, the authority earned belongs to a domain being abandoned, and both
hosts serving identical content is a duplicate of the entire site.

So, for the whole build period:

- [ ] Crawling fully disabled, **or** platform password protection
- [ ] **No Search Console property yet** — it would collect history for a site that
      will not exist
- [ ] No sitemap submitted
- [ ] No link shared publicly — a link in a forum is a crawl invitation

When the domain is bought: set `site.origin` in `data/pages.json`, re-run
`python3 scripts/generate_onpage.py`, re-import. **One value, every page.** That is
why these are generated rather than typed.

Then, and only then: connect the domain, remove the block, verify with the
section 4 commands, create the Search Console property, submit the sitemaps.

---

## 8. What must not be added

The context boundary is the reason this site can rank at all on a new domain.

**Do not add**, however reasonable they sound: a BMI calculator, compound interest,
investment or loan-amortisation tools, a currency converter, a blog about anything
other than cost of living and tax, or any calculator that does not answer "what a
place costs and what you keep there".

Every one of those was considered and removed deliberately. They carry volume;
they also dilute the topical authority that a new domain has to build before it can
compete for anything.
