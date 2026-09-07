Sales tax in the United States is not one rate. It is a state rate with county,
city and special-district rates stacked on top, and the combined figure can differ
between two addresses a mile apart. That is why a national "average" sales tax
number is close to useless for an actual purchase.

## How sales tax is calculated

The arithmetic is simple; the difficulty is entirely in finding the right rate.

```
tax   = price × combined rate
total = price + tax
```

The combined rate is the sum of every layer that applies at the point of sale:

- **State rate** — set by the state, uniform within it.
- **County rate** — added by the county, if it levies one.
- **City rate** — added by the municipality.
- **Special district** — transit authorities, stadium districts and similar bodies
  levy their own, and they do not follow city or county boundaries.

Five states levy no state sales tax at all: Alaska, Delaware, Montana, New
Hampshire and Oregon. Alaska is the interesting one — it has no state rate but
permits local ones, so an Alaskan purchase can still carry sales tax while a
Delaware purchase never does.

Because the rate is set at that granularity, **sales tax by zip code** is the only reliable way to look one up — a state average will be wrong for most addresses inside it.

**Sourcing tax** decides which rate applies. Most states are destination-based:
the rate is the buyer's address, not the seller's. A handful are origin-based for
in-state sales, which is why an online order and an in-store purchase of the same
item can be taxed differently.

## Reverse calculation

Working backwards from a total that already includes tax is a different formula,
and getting it wrong is a common error:

```
price = total ÷ (1 + rate)
tax   = total − price
```

Subtracting the rate from the total does not work. On a $107 total at 7%, the tax
is $7.00 and not $7.49 — the rate applies to the pre-tax price, not to the total.
This is what a **reverse sales tax calculator** is for, and it is the calculation
most often needed when reconciling a receipt.

## What this does not include

- **Exemptions.** Most states treat groceries, prescription drugs and some clothing
  differently, either untaxed or at a reduced rate. This tool applies the general
  rate.
- **Use tax.** Buying untaxed from out of state usually creates a use tax
  obligation at your own rate. It is widely ignored and legally owed.
- **Sales tax holidays.** Several states suspend tax on specific categories for a
  few days a year.
- **Business exemption certificates**, which remove tax on qualifying resale
  purchases entirely.

Where a purchase is large enough for the exemption question to matter, check the
category against the state's own guidance rather than relying on a general rate.

## Who needs this

Anyone reconciling a receipt, pricing a large purchase, or deciding whether an
out-of-state order is genuinely cheaper. The last is the most common real use: a
price difference of a few percent is frequently erased once the destination rate
is applied, and the comparison is not obvious until both numbers are in front of
you.

For anyone comparing two places to live, sales tax belongs in the comparison
alongside income tax. States without an income tax often carry higher consumption
taxes, and looking at one without the other produces the wrong answer — which is
the reason this tool exists next to a cost-of-living comparison rather than on its
own.
