# Start here — building LifeCalc Pro

This is the only document to begin from. It says which files to read, in what order,
and which to ignore. Everything the builder needs is in the files listed below;
everything else in the repository is research, history or tooling.

## Read, in this order

1. **`docs/build-spec.md`** — the construction specification: build order, routes,
   SEO implementation, calculators, performance, what must not be added.
2. **`data/onpage.generated.json`** — every page: `path`, `built`, `title`, `h1`,
   `metaDescription`, `canonical`, `breadcrumb`, `h2Outline`, `faq`, `jsonLd`,
   `internalLinks`, and the `sitemap` block. **Build the entries with `built: true`
   and no others.** `docs/onpage-spec.md` is the same data as a readable table.
3. **`content/bodies/{page}.md`** — the written body of each page, rendered under its
   calculator (`home.md` is `/`; `tools__paycheck-calculator.md` is
   `/tools/paycheck-calculator`; `__` stands for `/`).
4. **`docs/base44-cost-of-living-calculator.md`** — the complete brief for the
   cost-of-living calculator.
5. **`docs/calculator-acceptance.md`** — the answers every calculator must give, to
   the cent. A calculator is finished when every row matches.
6. **`docs/measurement.md`** — the analytics events (no amounts, ever).

## The calculators: import, never rewrite

`engine/lifecalc-engine.js` is every calculator on the site as one dependency-free
ES module, bundled from the tested TypeScript in `src/lib/` (included for reference).
Import it; do not reimplement it. Data files are loaded by the app and passed in:

| Data | Path |
|---|---|
| Tax: federal, estimated payments, every state | `src/data/tax-year-2026/` |
| Places: every county, New England town, city; price levels | `src/data/col/` |
| Household spending by size, in current prices | `src/data/ces-2024/baseline.json` |
| The `/cost-of-living` ranked table | `data/col-hub-table.json` |

## Ignore

`docs/SPEC.md` (the decision history — it explains *why*, and parts describe designs
since replaced), `docs/archive/`, `docs/keyword-research.md`, `docs/revenue-model.md`,
`docs/link-building.md`, `docs/copywriting.md`, `docs/data-verification.md`,
`content/drafts/` (not published), `data/tax-primary/`, `data/claims.json`,
`scripts/`, `.github/`. None of them changes what is built.

## Four rules that override anything else

1. Titles, descriptions, H1s, H2s, FAQs and JSON-LD come from
   `data/onpage.generated.json`. Never type them.
2. Numbers come from `engine/lifecalc-engine.js`. Never compute them another way.
3. Only pages with `built: true` exist, and only they are in the sitemap.
4. English only. Nothing on the site is in any other language.
