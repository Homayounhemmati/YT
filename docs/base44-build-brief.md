# Build brief for Base44

Hand this to the builder. It says what to construct and, more importantly, what
not to improvise. The SEO values are **generated data, not suggestions** — they are
in `data/onpage.generated.json` and every one of them is validated by CI.

> **The single most important instruction:** every page's title, meta description,
> H1, canonical, breadcrumb and JSON-LD come from that file. Do not write them in
> the app, do not let the builder invent them, do not type them into an SEO panel.
> A value that disagrees with the file is a defect (spec rule 3-7-6).

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

### `metros` — 4 rows, indices pending

Source: `data/metros.json`. Only four metros exist because the generation gate
requires a **measured** search volume of ≥500/month. Do not add more.

| Field | Note |
|---|---|
| `slug` `name` `displayName` | `displayName` is capped at 20 characters and is what appears in titles |
| `stateSlug` | Links the metro to its state page — **this cross-link is the site's main differentiator** |
| `indices` `referenceRent` | `null` until the BEA/HUD dataset is fetched. Build the page; leave these fields empty |

---

## 3. Routes

```
/                               home
/tools                          tool index
/tools/{slug}                   12 tool pages
/cost-of-living                 directory
/cost-of-living/{metro}         4 metro pages
/state-taxes                    directory
/state-taxes/{state}            51 state pages
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

## 4. SEO implementation — the part most likely to go wrong

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

```bash
curl -s  URL/state-taxes/california | grep -o "<title>[^<]*</title>"
curl -s  URL/state-taxes/texas      | grep -o "<title>[^<]*</title>"   # must differ
curl -s  URL/state-taxes/california | grep -c 'application/ld+json'
curl -s -A "facebookexternalhit/1.1" URL/state-taxes/california | grep 'og:title'
curl -sI URL/no-such-page | head -1                                    # must be 404
```

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

### Internal links

`internalLinks` gives every link with its anchor text. Both matter.

- Render real `<a href="/path">` elements. **Not** a click handler on a `div` —
  a crawler follows an anchor and ignores everything else.
- Use the supplied anchor text verbatim. It is written with the destination's
  keyword, never the source's.
- Plus a fixed header (Home · Calculators · Cost of Living · State Taxes) and a
  fixed footer (the seven trust pages) on every page.

### robots.txt and sitemap

- `Disallow: /api/` and internal paths. **No content page is ever disallowed.**
- One sitemap index with four children: tools, places, states, guides. This is so
  indexation can be read per page type — a single flat sitemap makes that
  impossible.
- `<lastmod>` only on genuine content change. **If the platform stamps every URL on
  every deploy, omit the field entirely** — a dishonest `lastmod` teaches Google to
  ignore it across the whole site.

---

## 5. The calculators

Two engines. The tax engine is built and tested; the cost-of-living engine is not.

| Engine | Status |
|---|---|
| Tax — federal + 51 jurisdictions | ✅ `src/lib/tax/`, 59 passing tests |
| Cost of living | ⬜ Blocked on the BEA/HUD dataset |

**Do not reimplement tax logic in the app.** Import the engine. A calculation
rewritten in a component is a calculation nothing tests, and this is a YMYL niche
where a wrong number is the whole risk.

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

- [ ] `robots.txt` disallowing everything, **or** platform password protection
- [ ] **No Search Console property yet** — it would collect history for a site that
      will not exist
- [ ] No sitemap submitted
- [ ] No link shared publicly — a link in a forum is a crawl invitation

When the domain is bought: set `site.origin` in `data/pages.json`, re-run
`python3 scripts/generate_onpage.py`, re-import. **One value, 78 pages.** That is
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
