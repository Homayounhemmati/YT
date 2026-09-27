# Link building — the operating plan

> Spec section 9-5 sets the strategy. Audit finding 21-3 recorded that it had no
> artifact: nothing a person could execute on a Monday morning. This is that
> artifact. Every asset below is built from an engine or dataset already in the
> repository, and every quotable sentence is registered in `data/claims.json`.

## 1. The three linkable assets

Calculators do not earn links; numbers do. None of the assets is a new page — each
lives on a page that already exists, so no asset competes with a tool for its query.

| # | Asset | Lives on | Built from | Blocked on |
|---|---|---|---|---|
| A1 | **Take-home on a $95,000 salary in every state**, ranked | `/state-taxes` — a column in the existing table | `data/takehome-95k.json` (salary engine) | State data verification (51 pending); 6 prior-year states |
| A2 | **What a salary is worth in each metro after tax *and* prices** | `/cost-of-living` — a column in the directory table | `compareWithTax()` in `src/lib/col` | The BEA/HUD dataset |
| A3 | **Open methodology**: formulas, 115 engine tests with hand-worked golden cases, the claims register | `/methodology` | `src/lib/**/__tests__`, `data/claims.json` | The page body |

### The one sentence each asset must be quotable in

- A1: *"On the same $95,000 salary, where you live changes take-home pay by more than
  $7,500 a year."* (claim `salary-spread`)
- A2: *"$95,000 in Austin against $120,000 in San Francisco: after tax and prices, the
  lower salary can be the larger one."* — publish only once the dataset makes the
  sentence computable; until then it is a hypothesis, not a claim.
- A3: *"Every number on the site traces to a statute, a dataset or a test."*

## 2. Channels, in order

| Months | Channel | What is done | Rule |
|---|---|---|---|
| 1–3 | r/personalfinance, r/SalaryNegotiation, r/moving, r/jobs | Answer relocation and job-offer questions with the computed figure, no link | A link in the first 90 days gets the account banned and the domain flagged |
| 3–6 | The same communities | Link only where the tool answers the question better than a paragraph can | At least 10 link-free answers per answer with a link |
| 2+ | **University career centres** | Ask to be listed on "salary and cost-of-living resources" pages | The single most realistic source of .edu links for this niche; these pages exist to list exactly this kind of tool |
| 4+ | Hacker News, Indie Hackers | One "how we built it" post about the claims register and the test suite | Once, done well |
| 6+ | Authors of relocation, job-offer and "best states for taxes" articles | Offer a figure for their article; do not ask for a link | Give data, earn the link |
| Each January | Local and personal-finance journalists | "What this year's bracket changes mean for a $95,000 paycheck in your state" | Only after the year's data is extracted and verified |

**Never:** bought links, link exchanges, directories, guest-post networks, PBNs. In a
YMYL niche the penalty risk exceeds any benefit.

## 3. Finding targets — the exact searches

| Target | Search |
|---|---|
| Career centre resource pages | `site:.edu "cost of living calculator" career` · `site:.edu "salary calculator" "job offer"` |
| Relocation articles | `"moving to" "cost of living" intitle:{city}` · `"relocating to {city}" salary` |
| Tax-comparison articles | `"states with no income tax" "take-home"` · `"best states" taxes salary 2026` |
| Community threads | `site:reddit.com "job offer" "cost of living" {city}` · `site:reddit.com "moving to {state}" "take home"` |

## 4. Outreach template (to an article author)

> Subject: A figure for your piece on {topic}
>
> Hi {name} — I read your article on {topic}. One number that may be useful to your
> readers: {one registered claim, with its computed figure}. The calculation and its
> sources are open at {methodology URL}. Happy for you to use the figure with or
> without a mention.
>
> {name}, LifeCalc Pro

One follow-up after seven days, never a second. Record every send in the log.

## 5. The log

`docs/link-log.csv` records every outreach and every link earned. A link that is not
in the log did not happen for the purposes of section 6.

## 6. Targets and the warning sign

| Month | Referring domains (natural) |
|---|---|
| 6 | 5–10 |
| 12 | 25–40 |
| 18 | 60+ |

**Fewer than 5 at month 6 means distribution is failing, not content** — building more
pages will not fix it (spec 17-1). At least 30% of project time from month 3 goes here.
