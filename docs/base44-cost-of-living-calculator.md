# Base44 brief — Cost of Living Calculator

> Hand this file to the builder as it is. It is complete: what to build, the data
> to load, the one function to call, what to show, and the table the finished
> calculator is checked against. **Build nothing that is not in here, and compute
> nothing yourself** — every number the page shows comes from the engine.

Page: `/tools/cost-of-living-calculator` · Template: ToolPage · Stage 1 of the funnel.

---

## 1. What the calculator does

The visitor chooses a place — a US city, county, or New England town — and says
who lives with them. The calculator shows:

1. **What a month costs** that household there, line by line, each line labelled with
   where it comes from.
2. **The salary that covers it** after federal income tax, Social Security, Medicare and
   that state's income tax and payroll contributions — including the child tax credit.
3. Optionally, **the comparison with where they live now**: the same household's month
   there, and the salary here that keeps their spending power after both states' taxes.

Coverage: all 3,077 counties HUD prices by county, all 1,603 New England towns HUD
prices by town, and 19,308 cities (every incorporated place in the Census Bureau's
estimates, plus Urban Honolulu) — the 50 states and DC. An unincorporated community is
reached through its county.

---

## 2. Files to import

Copy these from the repository into the app unchanged. They are generated from the
publishers' own files and validated in CI; never edit them by hand.

| File | Size | Load when |
|---|---|---|
| `src/data/col/meta.json` | 1 KB | page load — source names and years |
| `src/data/col/price-areas.json` | 105 KB | page load — BEA price levels for 485 areas |
| `src/data/ces-2024/baseline.json` | 6 KB | page load — BLS spending by household size, with the CPI factors that carry it to current prices |
| `src/data/tax-year-2026/federal.json`, `estimated.json` | 10 KB | page load |
| `src/data/col/search-index.json` | 554 KB (144 KB gzipped) | **when the place box first gets focus**, not on first paint |
| `src/data/col/places/{st}.json` | up to 118 KB each | when a place in that state is chosen |
| `src/data/tax-year-2026/states/{state-slug}.json` | 1–13 KB each | when a place in that state is chosen |

Engine code (TypeScript, no dependencies): `src/lib/tax/` and `src/lib/col/`.
**Import these modules; do not reimplement them.** If the platform truly cannot import
them, reimplement from the code and prove the result against section 8 to the cent.

---

## 3. The one call

```ts
import { computeCostOfLiving, resolvePlace, searchEntries } from "src/lib/col";

const place = resolvePlace(stateFile, priceAreas, key, countyId);   // key from the search index
const result = computeCostOfLiving({
  taxYear: 2026,
  place,
  tax: { federal, estimated, state: stateTaxData },   // state file for place.stateSlug
  baseline,                                           // ces-2024/baseline.json
  years: { priceLevels: meta.years.priceLevels, rent: meta.years.rent },
  adults: 1,            // 1 | 2
  children: 0,          // 0 … 6; children under 17
  bedrooms: undefined,  // default: result.household.suggestedBedrooms
  filingStatus: undefined,   // default: 2 adults → joint; 1 adult + children → head of household; else single
  own: { food_home: 350 },   // optional: the visitor's own monthly figure per line key
  rentOverride: undefined,   // optional: the visitor's own rent
  compare: undefined,        // optional: { place, tax, salary } — where they live now
});
```

`result` holds everything the card shows: `lines[]` (key, label, monthly, basis),
`monthlyTotal`, `annualTotal`, `salary` (gross, hourly, breakdown, `stateDataStatus`,
notes), `comparison`, `sources`, `warnings`, and `household` (the defaults actually
used). Recalculate on every input change; it runs in about half a millisecond
(measured) once the files are loaded.

**Cities that span counties.** A city entry may carry `alsoIn` (other counties it
spans where the rent or price level differs). When it does, show a small select —
"Which part of Raleigh?" — listing the main county first; pass the choice as
`countyId` to `resolvePlace`.

---

## 4. Inputs

Never an empty form: on first paint, run the calculation for **Austin, TX**, one adult,
no children. If the URL carries `?place=<key>&st=<ST>` (paycheck pages link this way),
start from that place instead.

| Input | Control | Default | Notes |
|---|---|---|---|
| Place | Search box over `search-index.json`, then the state file | Austin, TX | Match anywhere in the label, case-insensitive; rank by population. Below the box: "Can't find it? Choose a state" → state select → search that state's file (it has every city, however small). |
| Adults | Two-option toggle: 1 · 2 | 1 | |
| Children under 17 | Stepper 0–6 | 0 | |
| Bedrooms | Select Studio · 1 · 2 · 3 · 4 | `suggestedBedrooms` | Label the default "(suggested)". |
| Filing status | Select, inside "Tax details" (collapsed) | from the engine | Single · Married filing jointly · Head of household |
| Your own figures | "Use my own numbers" (collapsed): one currency field per line, placeholder = the estimate | empty | A filled field replaces that line. The rent field sets `rentOverride`. |
| Compare with where I live now | Collapsed section: a second place search + "Your salary there" | empty | Both needed before the comparison shows. |

---

## 5. The result card, in this order

1. **"What a month costs"** — `monthlyTotal`, large. Under it, the household in words
   ("1 adult, 1-bedroom home in Austin, TX") and, unless `allOwnFigures`, the label
   *"Estimate for a typical household of this size — replace any line with your own."*
2. **"The salary that covers it"** — `salary.gross` a year and `salary.hourlyAt2080`
   an hour. One line beneath: "after federal tax, Social Security, Medicare and
   {State} tax" (for a state with no income tax: "… Medicare; {State} has no income tax").
   - If `salary.stateDataStatus === "unverified"`: an amber note directly under the
     number, **"{State}'s 2026 tax figures are still being checked"**, expandable to
     `salary.notes`. Never hide the number; never show the note for verified states.
   - A "Tax breakdown" disclosure: federal tax (negative = refund from the child tax
     credit, show as "credit"), Social Security and Medicare, state tax, state payroll
     contributions, take-home.
3. **Line by line** — a table: label · basis chip · monthly. Basis chips:
   *HUD Fair Market Rent* · *National average at local prices* · *Your figure*.
4. **Comparison** (only when given): the same household's month in the other place,
   the difference (green when cheaper here), then "To keep your spending power after
   tax you'd need **{equivalentSalary}** here" and, smaller, "On prices alone:
   {priceOnlyEquivalent}". The gap between those two is the point — do not drop either.
5. **Next steps** (the funnel; each is a `funnel_click`):
   - "What does {State} take from a paycheck?" → `/tools/paycheck-calculator/{stateSlug}`
     when that page is built (see `data/onpage.generated.json`), otherwise `/tools/paycheck-calculator`
   - "Compare two cities side by side" → `/tools/cost-of-living-comparison`
   - "Can you afford the rent on your income?" → `/tools/rent-affordability-calculator`
6. **Sources** — the four strings in `result.sources`, each linking to its publisher,
   and every string in `result.warnings` as a plain list. Never trim these: they are
   what makes the estimate honest.

### Number formatting

Show whole dollars on the card (`$3,687`), rounded half-up from the engine's value.
The engine's values are exact to the cent; rounding is display-only. Hourly figures
keep cents (`$25.17`). Negative amounts: `-$1,381`. Never compute a total from the
rounded lines — show `monthlyTotal`.

### States

- **Loading a state file:** keep the previous result visible and dim it; no spinner
  replacing the card.
- **A file fails to load:** "We couldn't load {State}'s data. Try again." with a retry
  button; the rest of the page stays usable.
- **Own rent of 0 or a blank field:** treat blank as "use the estimate"; 0 is a valid
  figure (someone living rent-free).

---

## 6. SEO — generated, never typed

Title, meta description, H1, canonical, breadcrumb, H2 outline, FAQ and JSON-LD for
this page are in `data/onpage.generated.json` (path `/tools/cost-of-living-calculator`).
The body copy is `content/bodies/tools__cost-of-living-calculator.md`, rendered under
the calculator. The calculator sits **above the fold**, directly under the H1; the
body follows the result card. The content must be in the server-rendered HTML
(section 4 of `docs/build-spec.md`).

---

## 7. Analytics (GA4) — no amounts, ever

| Event | When | Parameters |
|---|---|---|
| `calculate` | first result, and each change after a 1-second pause | `tool`=`cost-of-living-calculator`, `state`, `place_kind` (city / county / town — from the key: `city:` is a city, otherwise the entry's `kind`), `adults`, `children`, `bedrooms`, `has_own_figures`, `has_compare`, `state_data` (verified / unverified) |
| `funnel_click` | a next-step link | as in `docs/measurement.md` |
| `source_click` | a source link | `source_domain` |

No place name, salary, rent or any other amount is sent: they are personal financial
data, and the page promises not to send them.

---

## 8. Acceptance — the build is done when these match

`docs/calculator-acceptance.md`, sections **"Cost of living calculator"**, **"every line
for one person in Austin"** and **"comparison"**. Enter each row's inputs; every value
must match the table to the cent (compare the engine values, before display rounding).
The Boston row must show the amber "still being checked" note; the others must not.

The table is regenerated from the engine whenever the data is rebuilt, and CI fails if
the committed copy is stale — so the table in the repository is always the answer.

---

## 9. Do not

- Invent a place, a price level or a spending line. A place missing from the files is
  a data bug to report, not a gap to fill.
- Hide the "unverified" note, the sources, or the warnings.
- Default to "married" because there are two people: filing status follows *adults*.
- Add an "overall cost-of-living score". There is none in the data, deliberately.
- Show the family salary without the child tax credit — pass `children`.
- Send any amount to analytics, a URL, or a third party.

---

## 10. Keeping it current

| Data | Publisher | Updated | Rebuild |
|---|---|---|---|
| Price levels | BEA Regional Price Parities | each December | `python3 scripts/build_col_places.py` |
| Rent | HUD Fair Market Rents | each fiscal year (Oct) | same |
| Places | Census delineation and population estimates | yearly | same |
| Spending and CPI factors | BLS Consumer Expenditure (Sept) and CPI (monthly) | quarterly is enough | `python3 scripts/fetch_ces.py --year 2024` |
| Tax | IRS and each state | yearly, and when a state changes law | `data/tax-primary` + `scripts/apply_primary_sources.py` |

After any rebuild: `npx tsx scripts/acceptance_cases.ts`, commit, and re-run section 8.
