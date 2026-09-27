# Measurement — proving the funnel, not assuming it

> The revenue model assumes 2.2 pages per session. That number drives roughly half of
> modelled revenue and has never been measured. This is how it is measured, and what
> is done when it comes back lower.

## 1. Events (GA4)

| Event | When | Parameters |
|---|---|---|
| `calculate` | A calculator produces a result | `tool` (slug), `input_mode` (salary / hourly), `pay_frequency`, `has_state` |
| `funnel_click` | A click on an internal link to another tool or entity page | `from`, `to`, `from_stage`, `to_stage`, `placement` (result_card / body / related / nav) |
| `source_click` | A click to a cited primary source (IRS, BEA, HUD, a state revenue site) | `source_domain` |
| `faq_open` | An FAQ answer is expanded | `tool`, `question_index` |

No input values are sent — salaries and rents are personal financial data. Only the
categories above.

## 2. The four numbers that matter

| Metric | Definition | Target by month 3 | If below |
|---|---|---|---|
| Pages per session | GA4 views / sessions | 2.2 (the model's assumption) | Below 1.6: the funnel is not working — revise the model before anything else |
| Continuation rate | Sessions with `funnel_click` after `calculate` / sessions with `calculate` | 35% | Move the next-step link into the ResultCard, directly under the number |
| Entry-to-stage-2 | Sessions entering at stage 1 that reach a stage-2 or later page | 25% | Check the stage-1 pages' next-step anchors against the funnel map |
| Calculate rate | Sessions with `calculate` / sessions on a tool page | 60% | The calculator sits too low, or the form asks for too much |

## 3. Search Console

- **Coverage per sitemap segment** — the reason the sitemap is segmented. A template
  indexing below 70% while others index above 90% is a template problem.
- **Cannibalisation watch** — any query with impressions on two of our URLs in the same
  week. Resolve by intent, never by adding a canonical to hide it.
- **CTR by template** — titles are generated; a template-wide CTR problem is fixed once
  in the formula, not page by page.

## 4. AdSense

- RPM by template, not site-wide: the tax pages and the cost-of-living pages earn at
  very different CPCs, and a blended RPM hides which one is working.
- Never an ad between the form and the ResultCard (spec 10-4).

## 5. Consent — required before the first ad serves

- **EEA, UK and Switzerland:** AdSense requires a Google-certified consent management
  platform. Without one, ads to those visitors are limited.
- **US state privacy laws** (California and the states that followed): a "Do not sell or
  share my personal information" link, and AdSense restricted data processing for those
  visitors.
- GA4 Consent Mode, so that analytics respects the same choice.

These are launch items, listed in `scripts/launch_readiness.py`.
