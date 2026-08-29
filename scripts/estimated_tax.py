#!/usr/bin/env python3
"""
Derive the federal estimated-tax payment schedule and safe-harbor rules.

These are NOT in the upstream parameter tree used by extract_tax_data.py — that
model computes annual liability, not payment timing. They are also different in
kind from the bracket data: the installment schedule and the safe-harbor
percentages are statutory constants in 26 U.S.C. 6654, not figures the IRS
re-inflates every year. So rather than hardcoding dates copied from a web page,
this derives them from the statutory rule for any year:

  26 U.S.C. 6654(c)(2): installments are due on the 15th day of the 4th, 6th and
  9th months of the taxable year, and the 1st month of the following year.
  26 U.S.C. 7503: when that day is a Saturday, Sunday, or a legal holiday in the
  District of Columbia, the deadline moves to the next business day.

Deriving the dates also means a search result claiming "June 16" can be checked
rather than believed: the script reports which installments actually shifted and
why.

Usage:
    python3 scripts/estimated_tax.py --year 2026
"""
import argparse, datetime, json, pathlib

# Statutory installment pattern: (month offset from start of tax year, day).
# The fourth installment falls in January of the following year.
INSTALLMENTS = [
    {"period": "Q1", "month": 4, "day": 15, "yearOffset": 0,
     "covers": "January 1 - March 31"},
    {"period": "Q2", "month": 6, "day": 15, "yearOffset": 0,
     "covers": "April 1 - May 31"},
    {"period": "Q3", "month": 9, "day": 15, "yearOffset": 0,
     "covers": "June 1 - August 31"},
    {"period": "Q4", "month": 1, "day": 15, "yearOffset": 1,
     "covers": "September 1 - December 31"},
]


def nth_weekday(year, month, weekday, n):
    """Date of the nth given weekday in a month (weekday: Monday=0)."""
    d = datetime.date(year, month, 1)
    d += datetime.timedelta(days=(weekday - d.weekday()) % 7)
    return d + datetime.timedelta(weeks=n - 1)


def last_weekday(year, month, weekday):
    d = datetime.date(year, month, 28)
    while (d + datetime.timedelta(days=7)).month == month:
        d += datetime.timedelta(days=7)
    return d - datetime.timedelta(days=(d.weekday() - weekday) % 7)


def observed(d):
    """A holiday on Saturday is observed Friday; on Sunday, Monday (5 U.S.C. 6103)."""
    if d.weekday() == 5:
        return d - datetime.timedelta(days=1)
    if d.weekday() == 6:
        return d + datetime.timedelta(days=1)
    return d


def dc_holidays(year):
    """Legal holidays in the District of Columbia that can move a tax deadline.

    Federal holidays under 5 U.S.C. 6103 plus Emancipation Day (April 16), which
    is a DC holiday and therefore counts for section 7503 even though it is not
    a federal holiday.
    """
    h = {
        observed(datetime.date(year, 1, 1)): "New Year's Day",
        nth_weekday(year, 1, 0, 3): "Birthday of Martin Luther King, Jr.",
        nth_weekday(year, 2, 0, 3): "Washington's Birthday",
        observed(datetime.date(year, 4, 16)): "Emancipation Day (DC)",
        last_weekday(year, 5, 0): "Memorial Day",
        observed(datetime.date(year, 6, 19)): "Juneteenth National Independence Day",
        observed(datetime.date(year, 7, 4)): "Independence Day",
        nth_weekday(year, 9, 0, 1): "Labor Day",
        nth_weekday(year, 10, 0, 2): "Columbus Day",
        observed(datetime.date(year, 11, 11)): "Veterans Day",
        nth_weekday(year, 11, 3, 4): "Thanksgiving Day",
        observed(datetime.date(year, 12, 25)): "Christmas Day",
    }
    return h


def next_business_day(d, holidays):
    """Section 7503: roll forward past weekends and DC legal holidays."""
    reasons = []
    while True:
        if d.weekday() == 5:
            reasons.append("Saturday")
        elif d.weekday() == 6:
            reasons.append("Sunday")
        elif d in holidays:
            reasons.append(holidays[d])
        else:
            return d, reasons
        d += datetime.timedelta(days=1)


def build(year):
    rows = []
    for spec in INSTALLMENTS:
        y = year + spec["yearOffset"]
        statutory = datetime.date(y, spec["month"], spec["day"])
        holidays = dc_holidays(y)
        due, reasons = next_business_day(statutory, holidays)
        rows.append({
            "period": spec["period"],
            "covers": spec["covers"],
            "statutoryDate": statutory.isoformat(),
            "dueDate": due.isoformat(),
            "dueDayOfWeek": due.strftime("%A"),
            "shifted": due != statutory,
            "shiftReason": " then ".join(reasons) if reasons else None,
            "shareOfRequiredAnnualPayment": 25.0,
        })

    return {
        "taxYear": year,
        "installments": rows,
        "safeHarbor": {
            "description": (
                "No underpayment penalty if total withholding plus estimated "
                "payments meets the lesser of the two tests below."),
            "currentYearPercent": 90.0,
            "priorYearPercent": 100.0,
            "priorYearPercentHighIncome": 110.0,
            "highIncomeAgiThreshold": {
                "single": 150000, "marriedJointly": 150000,
                "headOfHousehold": 150000, "marriedSeparately": 75000,
            },
            "thresholdInflationIndexed": False,
            "minimumTaxDueForPenalty": 1000,
            "notes": [
                "The prior-year test requires that a return covering 12 months "
                "was filed for the prior year.",
                "Withholding counts as paid evenly across the year regardless of "
                "when it was actually withheld, which is why increasing "
                "withholding late in the year can still cure an underpayment.",
                "Farmers and fishermen follow a different schedule under "
                "section 6654(i).",
            ],
        },
        "provenance": {
            "derivedBy": "scripts/estimated_tax.py",
            "method": (
                "Dates computed from the statutory pattern in 26 U.S.C. "
                "6654(c)(2) and the weekend/holiday rule in 26 U.S.C. 7503, not "
                "copied from a secondary source."),
            "sources": [
                {"title": "26 U.S. Code 6654 - Failure by individual to pay estimated income tax",
                 "url": "https://www.law.cornell.edu/uscode/text/26/6654"},
                {"title": "26 U.S. Code 7503 - Time for performance of acts where last day falls on Saturday, Sunday, or legal holiday",
                 "url": "https://www.law.cornell.edu/uscode/text/26/7503"},
                {"title": "5 U.S. Code 6103 - Holidays",
                 "url": "https://www.law.cornell.edu/uscode/text/5/6103"},
                {"title": "IRS Form 1040-ES (Estimated Tax for Individuals)",
                 "url": "https://www.irs.gov/pub/irs-pdf/f1040es.pdf"},
            ],
        },
        "verification": "pending",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=2026)
    ap.add_argument("--out", default="src/data")
    args = ap.parse_args()

    data = build(args.year)
    outdir = pathlib.Path(args.out) / ("tax-year-%d" % args.year)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "estimated.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    print("estimated tax schedule for %d" % args.year)
    for r in data["installments"]:
        flag = ("  <- shifted from %s (%s)" % (r["statutoryDate"], r["shiftReason"])
                if r["shifted"] else "")
        print("  %s  %s  %-9s  covers %s%s"
              % (r["period"], r["dueDate"], r["dueDayOfWeek"], r["covers"], flag))
    sh = data["safeHarbor"]
    print("safe harbor: lesser of %g%% current year or %g%% prior year "
          "(%g%% if prior-year AGI > $%s, $%s if MFS)"
          % (sh["currentYearPercent"], sh["priorYearPercent"],
             sh["priorYearPercentHighIncome"],
             format(sh["highIncomeAgiThreshold"]["single"], ","),
             format(sh["highIncomeAgiThreshold"]["marriedSeparately"], ",")))


if __name__ == "__main__":
    main()
