# Tax data verification — tax year 2026

> Rule 13-4-1: no state page ships until every figure it relies on has been checked
> against the primary source that sets it. The page gate in
> `scripts/generate_onpage.py` enforces this: a state is built only when its dataset
> says `"verification": "verified"`.

## 1. How verification works

The dataset is **extracted** from a secondary source (`policyengine-us` 2.15.9,
`scripts/extract_tax_data.py`), then **checked** against primary sources recorded in
`data/tax-primary/2026.json`. For each jurisdiction the register holds:

- `sources` — the primary documents opened (IRS Revenue Procedure, statute, the
  state's own 2026 withholding guide or bulletin), with the retrieval date;
- `set` — any value a primary source corrects, with `why`;
- `computed` — values derived from a statute's own formula where the agency has not
  yet published the figure (each one says so);
- `expect` — every value a page relies on.

`scripts/apply_primary_sources.py` applies `set`, checks every `expect` value, and
marks the jurisdiction verified only when all match. `extract_tax_data.py` runs it
after every extraction, so a regeneration cannot silently undo a correction: a
changed upstream value fails the build instead of reaching a page.

**To verify another state:** open its 2026 primary source (withholding guide,
statute or revenue-department page — not a search summary), add an entry to the
register, run the script. **Never** mark a state verified by editing its JSON.

## 2. Status — 8 of 51 jurisdictions verified, plus federal

### Federal — ✅ verified 2026-09-27

Brackets and standard deduction for all four filing statuses (Rev. Proc. 2025-32,
sections 4.01 and 4.14), QBI thresholds (4.26), Social Security wage base $184,500,
92.35%, due dates and safe-harbor rules (2026 Form 1040-ES), FICA and
self-employment rates, the 0.9% Additional Medicare Tax thresholds and the $400
filing threshold (26 U.S.C. 1401, 3101, 6017). Every extracted value matched.

### What the check found in the launch states

| State | Finding | Effect on a $95,000 single salary |
|---|---|---|
| Illinois | Exemption was 2025's $2,850; the 2026 amount is **$2,925** (Bulletin FY 2026-15, IL-700-T) | state tax $4,561 → **$4,558** |
| Maryland | Standard deduction was 2025's $3,350; the Comptroller's 2026 figure is **$3,400**. Joint / head of household **$6,850** is computed from Tax-General 10-217(c) (not yet published; recheck against the 2026 resident booklet). HB 411 (2026, $4,100) died in committee | state tax $4,149 → **$4,147** |
| New York | Brackets correct, but the **section 601(d-5) supplemental tax** above $107,650 of AGI was missing. Now modelled from the statute's own table | none at $95,000; **+$480** at $150,000, +$2,614 at $300,000 |
| New York (payroll) | Paid Family Leave (0.432%, max $411.91) and disability insurance (0.5%, max $0.60 a week) were not deducted | take-home $71,098 → **$70,656** |
| Pennsylvania (payroll) | Employee unemployment contribution (0.07% of all wages, 2026) was not deducted | take-home $72,746 → **$72,680** |
| Georgia | 4.99% and $15,000 / $30,000 confirmed (HB 463, retroactive to January 1, 2026; employers withheld 5.19% until May 11, 2026) | — |
| Texas, Florida, Pennsylvania, North Carolina | Confirmed as extracted | — |

Twelve states withhold employee paid-leave, disability or long-term-care contributions
that are not yet entered (California, Colorado, Connecticut, Delaware, Hawaii, Maine,
Massachusetts, Minnesota, New Jersey, Oregon, Rhode Island, Washington); each is
flagged `payrollContributions: "not-modelled"` and held behind the gate.

Connecticut also recaptures its lower brackets at higher incomes; the engine does not
apply that yet, so Connecticut is flagged and held behind the gate even once verified.

### Every jurisdiction

| Jurisdiction | Structure | Rate | Status | Model gap |
|---|---|---|---|---|
| Alaska | none | — | ⬜ pending |  |
| Alabama | progressive | 3 brackets | ⬜ pending | exemption not extracted |
| Arkansas | progressive | 5 brackets | ⬜ pending | exemption not extracted |
| Arizona | flat | 2.5% | ⬜ pending | exemption not extracted |
| California | progressive | 9 brackets | ⚠️ 2025 figures — held | exemption not extracted |
| Colorado | flat | 4.4% | ⬜ pending | exemption not extracted |
| Connecticut | progressive | 7 brackets | ⬜ pending | exemption not extracted, recapture not modelled |
| Washington, D.C. | progressive | 7 brackets | ⬜ pending | exemption not extracted |
| Delaware | progressive | 7 brackets | ⬜ pending | exemption not extracted |
| Florida | none | — | ✅ verified |  |
| Georgia | flat | 4.99% | ✅ verified |  |
| Hawaii | progressive | 12 brackets | ⬜ pending | exemption not extracted |
| Iowa | flat | 3.8% | ⬜ pending | exemption not extracted |
| Idaho | flat | 5.3% | ⚠️ 2025 figures — held | exemption not extracted |
| Illinois | flat | 4.95% | ✅ verified (corrected) |  |
| Indiana | flat | 2.95% | ⬜ pending | exemption not extracted |
| Kansas | progressive | 0 brackets | ⬜ pending | exemption not extracted |
| Kentucky | flat | 3.5% | ⬜ pending | exemption not extracted |
| Louisiana | flat | 3.0% | ⬜ pending | exemption not extracted |
| Massachusetts | flat | 5.0% | ⬜ pending | exemption not extracted |
| Maryland | progressive | 10 brackets | ✅ verified (corrected) |  |
| Maine | progressive | 3 brackets | ⬜ pending | exemption not extracted |
| Michigan | flat | 4.25% | ⬜ pending | exemption not extracted |
| Minnesota | progressive | 4 brackets | ⚠️ 2025 figures — held | exemption not extracted |
| Missouri | progressive | 8 brackets | ⚠️ 2025 figures — held | exemption not extracted |
| Mississippi | flat | 4.0% | ⬜ pending | exemption not extracted |
| Montana | progressive | 2 brackets | ⬜ pending | exemption not extracted |
| North Carolina | flat | 3.99% | ✅ verified |  |
| North Dakota | progressive | 3 brackets | ⬜ pending | exemption not extracted |
| Nebraska | progressive | 4 brackets | ⬜ pending | exemption not extracted |
| New Hampshire | none | — | ⬜ pending |  |
| New Jersey | progressive | 7 brackets | ⬜ pending | exemption not extracted |
| New Mexico | progressive | 6 brackets | ⬜ pending | exemption not extracted |
| Nevada | none | — | ⬜ pending |  |
| New York | progressive | 9 brackets | ✅ verified (corrected) |  |
| Ohio | progressive | 2 brackets | ⬜ pending | exemption not extracted |
| Oklahoma | progressive | 4 brackets | ⬜ pending | exemption not extracted |
| Oregon | progressive | 4 brackets | ⚠️ 2025 figures — held | exemption not extracted |
| Pennsylvania | flat | 3.07% | ✅ verified |  |
| Rhode Island | progressive | 3 brackets | ⬜ pending | exemption not extracted |
| South Carolina | progressive | 2 brackets | ⬜ pending | exemption not extracted |
| South Dakota | none | — | ⬜ pending |  |
| Tennessee | none | — | ⬜ pending |  |
| Texas | none | — | ✅ verified |  |
| Utah | flat | 4.45% | ⬜ pending | exemption not extracted |
| Virginia | progressive | 4 brackets | ⬜ pending | exemption not extracted |
| Vermont | progressive | 4 brackets | ⚠️ 2025 figures — held |  |
| Washington | none | — | ⬜ pending |  |
| Wisconsin | progressive | 4 brackets | ⬜ pending | exemption not extracted |
| West Virginia | progressive | 5 brackets | ⬜ pending | exemption not extracted |
| Wyoming | none | — | ⬜ pending |  |

## 3. Rebuilding

```bash
python3 scripts/extract_tax_data.py --year 2026     # extract, then re-apply the register
python3 scripts/validate_tax_data.py --year 2026    # structural check
npx tsx scripts/compute_takehome.ts && python3 scripts/generate_onpage.py
```
