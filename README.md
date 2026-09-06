# LifeCalc Pro

The real cost of living and working in a place — and what actually stays with
you. A calculator site for US metros and states, monetised with AdSense.

## Reference document

**[`docs/SPEC.md`](docs/SPEC.md)** is the project's only authority. Read it
before any decision.

The earlier documents in `docs/archive/` are kept for history only and are
**not authoritative** — they contradict each other and the current state in
several places.

## Four hard rules

1. No tax figure enters the code from memory or a secondary source — only a
   primary source with a URL and a date.
2. No tax calculation is written outside `src/lib/tax/`.
3. No page ships without green engine tests and human review.
4. Everything outside `docs/archive/` is English. Enforced in CI.

## Status

| Area | Status |
|---|---|
| Dataset: 51 jurisdictions + federal + quarterly schedule | ✅ Extracted, zero structural errors |
| Tax engine (`src/lib/tax/`) | ✅ 59 tests green, typecheck clean |
| Page and keyword map (`data/`) | ✅ 17 pages, 10 audit checks, zero errors |
| Data verification against primary sources | ⬜ Outstanding — needs `.gov` access |
| Cost-of-living dataset (BEA · HUD · Eurostat) | ⬜ Not started — needs `.gov` access |
| Next.js application | ⬜ Not started |

The specification is well ahead of the code: the tax engine and the datasets
exist, the application does not.

## Commands

```bash
npm test                          # engine tests
npm run typecheck
npm run data:validate             # dataset structural validation
npm run data:extract              # rebuild the dataset

python3 scripts/audit_seo.py      # cannibalisation, canonical and on-page audit
python3 scripts/check_language.py # every shipping file is English
python3 scripts/model_revenue.py  # rebuild docs/revenue-model.md
```

All five run in CI and break the build on failure.

## Next step

Verify the rows in [`docs/data-verification.md`](docs/data-verification.md)
against primary sources. Every dataset value is `verification: pending` until
a human has checked it against IRS or state revenue department publications,
and no page for a jurisdiction ships before its row is ticked.

## Related documents

| Document | Role |
|---|---|
| [`docs/keyword-research.md`](docs/keyword-research.md) | Demand validation — the basis for the page plan |
| [`docs/tool-catalogue.md`](docs/tool-catalogue.md) | 36 tools ranked by market value against build cost |
| [`docs/revenue-model.md`](docs/revenue-model.md) | Generated — do not edit by hand |
| [`docs/data-verification.md`](docs/data-verification.md) | Row-by-row verification checklist |
