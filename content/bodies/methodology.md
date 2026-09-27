Every figure on this site is produced by one of three calculation engines, and none of
them is typed in by hand. This page describes what each engine does, where its inputs
come from, and — as importantly — what it leaves out.

## The tax engine

The tax engine computes federal income tax, state income tax, Social Security and
Medicare from the published rules for the tax year shown on the page. It works in
whole cents from start to finish, so a breakdown always adds up to the total it
explains; floating-point arithmetic drifts by a cent here and there, and a table that
does not sum is a table nobody should trust.

For a salary it applies, in order: pre-tax deductions (with 401(k) deferrals reducing
income-tax wages but not Social Security or Medicare wages, as federal law requires),
the federal standard deduction and brackets, the employee's share of Social Security
up to the annual wage base and of Medicare without a ceiling, and the state's own
schedule — its standard deduction, personal exemption where it has one, and its
brackets or flat rate. For self-employment income it applies self-employment tax
first, because half of it reduces adjusted gross income.

Federal figures come from the Internal Revenue Code and the IRS's annual inflation
adjustments. State figures are drawn from a maintained open model of state tax law
and each state page is published only after its figures have been checked against
that state's own revenue department. A state whose figures for the current year have
not yet been released is not published under the current year.

Each engine is covered by automated tests, and the key cases are worked by hand from
the statute first — a $95,000 salary in Texas, for example, is computed line by line
and the engine must agree with it to the cent.

## The cost-of-living indices

Cost of living is measured with the Bureau of Economic Analysis's Regional Price
Parities, which express the price level of each metro area against a national average
of 100, separately for goods, housing rents, utilities and other services. Rent in
dollars comes from the Department of Housing and Urban Development's Fair Market
Rents, which are gross rents — shelter plus the utilities a tenant pays — set at the
40th percentile of recent movers.

We do not invent a dollar basket for any city. When you compare two places, your own
spending is scaled by the ratio of their official indices, and where a category has
no separate index the overall index is used and the page says so.

## What we deliberately do not model

- Local income taxes, which vary by county, city or school district. Every page that
  quotes a figure in a state with local income tax says the figure is before it.
- State-specific credits and most additions and subtractions to income.
- Tax on investment income, and the treatment of stock compensation.
- Health insurance costs, for which no official index exists at metro level.
- Your employer's withholding, which is an estimate; we compute the liability, and
  the refund or bill at filing is the difference between the two.

## How often this updates

Federal figures change each tax year when the IRS publishes its inflation
adjustments. State figures change when each legislature or revenue department acts,
which happens on different dates. Regional Price Parities are published once a year,
and Fair Market Rents at the start of each federal fiscal year. Every page shows the
year its figures apply to; a page never carries a year its data does not support.
