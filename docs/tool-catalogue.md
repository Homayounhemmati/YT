# Tool catalogue — ranked against data

> Produced from measurements taken in this project. No script generates it — it
> is updated by hand whenever a new measurement is made.

> **Last updated:** 2026-08-31


## How the ranking works

```
market value = monthly volume × CPC
```

This is **not our revenue** — it estimates what the advertising market pays for
that query. It is for prioritising *before* build cost is considered. The "data
dependency" column carries the cost; the final decision comes from combining the
two, not from the rank alone.


⚠️ **A high CPC does not mean an easy ranking.** There is no competition column
here, because advertising competition differs from SEO difficulty; real
difficulty is known only by inspecting each keyword's SERP.


## The table

| # | Tool | Volume/mo | CPC | Market value | Data dependency | Category |
|---|---|---|---|---|---|---|
| 1 | **Hours / timesheet** — a payroll tool, not a “time” tool | 368,000 | $4.58 | **1,685,440** | none | Category A |
| 2 | **Inflation** | 550,000 | $2.97 | **1,633,500** | BLS CPI (free) | Category B |
| 3 | **Compound interest** | 823,000 | $1.74 | **1,432,020** | none | Category B |
| 4 | **Profit margin** — top bid $29.10 | 110,000 | $10.92 | **1,201,200** | none | Category A |
| 5 | **Investment** | 450,000 | $2.00 | **900,000** | none | Category B |
| 6 | **Amortization** | 246,000 | $3.29 | **809,340** | none | Mortgage & property |
| 7 | **Sales tax** | 110,000 | $6.91 | **760,100** | state/local rates | Tax |
| 8 | **Interest** | 165,000 | $3.49 | **575,850** | none | Category B |
| 9 | **eBay fee** | 40,500 | $12.23 | **495,315** | fee schedule | Category A |
| 10 | **Fuel cost** | 40,500 | $8.93 | **361,665** | none | Category B |
| 11 | **Take-home pay** | 60,500 | $5.69 | **344,245** | tax engine | W-2 |
| 12 | **HELOC payment** — HIGH ad competition | 27,100 | $9.92 | **268,832** | none | Mortgage & property |
| 13 | **Tax return** | 40,500 | $6.38 | **258,390** | tax engine | Tax |
| 14 | **Closing cost** | 40,500 | $6.18 | **250,290** | none | Mortgage & property |
| 15 | **Bonus tax** | 22,200 | $9.61 | **213,342** | tax engine | Tax |
| 16 | **Income tax** | 90,500 | $2.13 | **192,765** | tax engine | Tax |
| 17 | **Savings** | 60,500 | $3.16 | **191,180** | none | Category B |
| 18 | **APR** | 33,100 | $5.44 | **180,064** | none | Category B |
| 19 | **Options profit** — a more distant audience | 33,100 | $5.20 | **172,120** | none | Category B |
| 20 | **Salary ↔ hourly** | 99,000 | $1.30 | **128,700** | none | Category A |
| 21 | **Lottery tax** | 22,200 | $5.77 | **128,093** | tax engine | Tax |
| 22 | **Discount** | 40,500 | $3.06 | **123,930** | none | Category A |
| 23 | **Budget** | 22,200 | $5.29 | **117,438** | none | Category A |
| 24 | **Cost of living** — full cluster 158,000 (tool 60,500 + comparison 49,500 + ~30 cities 45,000) | 158,000 | $1.65 | **~300,000** | BEA · HUD · BLS · Eurostat (official, free) | Cost of living |
| 25 | **Tax withholding** | 14,800 | $5.78 | **85,544** | tax engine | W-2 |
| 26 | **Monthly payment** | 27,100 | $3.13 | **84,823** | none | Mortgage & property |
| 27 | **Paycheck tax** | 18,100 | $4.48 | **81,088** | tax engine | W-2 |
| 28 | **House payment** | 33,100 | $2.29 | **75,799** | none | Mortgage & property |
| 29 | **Future value** | 40,500 | $1.72 | **69,660** | none | Category B |
| 30 | **Estimated tax** — January peak 110,000 | 27,100 | $2.22 | **60,162** | engine + calendar | Tax |
| 31 | **Capital gains tax** | 14,800 | $3.96 | **58,608** | tax engine | Tax |
| 32 | **Wage** | 18,100 | $2.89 | **52,309** | none | Category A |
| 33 | **Self-employment tax** — the niche anchor | 9,900 | $5.01 | **49,599** | tax engine | Tax |
| 34 | **Effective tax rate** | 6,600 | $2.87 | **18,942** | tax engine | Tax |
| 35 | **1099 tax** | 1,500 | $5.81 | **8,715** | tax engine | Tax |
| 36 | **SE tax deductions** — top bid $15.20 | 390 | $6.13 | **2,390** | tax engine | Tax |

**Total: 3,767,390 monthly searches · market value 13,171,284**


## Summary by category

| Category | Tools | Volume/mo | Market value | Data dependency |
|---|---|---|---|---|
| Tax — the same engine | 11 | 345,690 | 1,751,107 | tax engine ✅ built |
| W-2 — the same engine | 3 | 93,400 | 510,877 | tax engine ✅ built |
| Category A — same audience, no data | 7 | 698,300 | 3,804,332 | almost none |
| Category B — general finance | 9 | 2,195,700 | 5,516,059 | almost none |
| Mortgage & property | 5 | 373,800 | 1,489,084 | almost none |
| Cost of living | 2 tools + ~30 pages | 158,000 | ~300,000 | free government sources ✅ |
