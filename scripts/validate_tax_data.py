#!/usr/bin/env python3
"""
Structural validation of the generated tax dataset. Intended to run in CI and
fail the build, per SPEC.md section 5-4.

This checks that the data is internally coherent and carries provenance. It
CANNOT check that the numbers are right — that is what the human verification
pass in docs/data-verification.md is for.

Usage:
    python3 scripts/validate_tax_data.py --year 2026
"""
import argparse, datetime, json, pathlib, sys

FILING_STATUSES = ["single", "marriedJointly", "marriedSeparately", "headOfHousehold"]
MAX_SOURCE_AGE_DAYS = 400  # roughly one filing season plus a month


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def error(self, where, msg):
        self.errors.append("%s: %s" % (where, msg))

    def warn(self, where, msg):
        self.warnings.append("%s: %s" % (where, msg))


def check_brackets(rep, where, rows):
    if not rows:
        return
    if rows[0]["from"] != 0:
        rep.error(where, "first bracket must start at 0, starts at %s" % rows[0]["from"])
    prev = None
    for i, r in enumerate(rows):
        if r["rate"] < 0 or r["rate"] > 100:
            rep.error(where, "bracket %d rate out of range: %s" % (i, r["rate"]))
        if prev is not None:
            if r["from"] <= prev["from"]:
                rep.error(where, "bracket %d threshold %s not above previous %s"
                          % (i, r["from"], prev["from"]))
            if r["rate"] < prev["rate"]:
                rep.error(where, "bracket %d rate %s decreases from %s"
                          % (i, r["rate"], prev["rate"]))
        prev = r


def check_federal(rep, fed, year):
    w = "federal"
    if fed.get("taxYear") != year:
        rep.error(w, "taxYear is %s, expected %d" % (fed.get("taxYear"), year))

    for st in FILING_STATUSES:
        rows = fed.get("brackets", {}).get(st)
        if not rows:
            rep.error(w, "missing brackets for %s" % st)
            continue
        check_brackets(rep, "%s/%s" % (w, st), rows)
        if rows[-1].get("to") is not None:
            rep.error(w, "%s: top bracket must be open-ended" % st)
        if len(rows) != 7:
            rep.warn(w, "%s has %d brackets, expected 7" % (st, len(rows)))
        if not fed.get("standardDeduction", {}).get(st):
            rep.error(w, "missing standard deduction for %s" % st)

    se = fed.get("selfEmployment", {})
    nese = se.get("neseFactor")
    ss, med = se.get("socialSecurityRate"), se.get("medicareRate")
    if None in (nese, ss, med):
        rep.error(w, "self-employment rates incomplete")
    else:
        expected = round(1 - (ss + med) / 200, 6)
        if abs(nese - expected) > 1e-9:
            rep.error(w, "neseFactor %s does not equal 1-(%s+%s)/2 = %s"
                      % (nese, ss, med, expected))
        if abs((ss + med) - 15.3) > 1e-9:
            rep.warn(w, "combined SE rate is %s, expected 15.3" % (ss + med))
    if not se.get("socialSecurityWageBase"):
        rep.error(w, "missing Social Security wage base")
    if se.get("deductiblePortion") != 50.0:
        rep.error(w, "deductiblePortion must be 50 (half of SE tax)")
    addl = se.get("additionalMedicare", {})
    if addl.get("inflationIndexed") is not False:
        rep.error(w, "additional Medicare thresholds are statutory, not indexed")

    if not fed.get("provenance", {}).get("sources"):
        rep.error(w, "no source links")


def check_state(rep, d, year):
    w = "states/%s" % d.get("slug", "?")
    for field in ("slug", "name", "abbr", "structure", "taxYear"):
        if not d.get(field):
            rep.error(w, "missing %s" % field)
    if d.get("taxYear") != year:
        rep.error(w, "taxYear is %s, expected %d" % (d.get("taxYear"), year))

    structure = d.get("structure")
    if structure == "unknown":
        rep.error(w, "structure could not be determined; needs manual entry")
        return
    if structure == "none":
        if d.get("brackets") or d.get("flatRate"):
            rep.error(w, "marked no-income-tax but carries rates")
        if not d.get("notes"):
            rep.error(w, "no-tax state must explain that federal and SE tax still apply")
        return

    brackets = d.get("brackets") or {}
    if structure == "flat":
        if d.get("flatRate") in (None, 0):
            rep.error(w, "flat state has no flatRate")
    elif structure == "progressive":
        if not brackets:
            rep.error(w, "progressive state has no brackets")
        for st, rows in brackets.items():
            if len(rows) < 2:
                rep.error(w, "%s: progressive state needs 2+ brackets, has %d"
                          % (st, len(rows)))
    for st, rows in brackets.items():
        check_brackets(rep, "%s/%s" % (w, st), rows)

    prov = d.get("provenance", {})
    if not prov.get("sources"):
        rep.error(w, "no source links")
    if not prov.get("resolvedPaths"):
        rep.error(w, "no resolved source paths recorded")
    if d.get("verification") not in ("pending", "verified"):
        rep.error(w, "bad verification status: %s" % d.get("verification"))
    if d.get("verification") == "pending":
        rep.warn(w, "values not yet checked against a primary source")
    if d.get("staleForTargetYear"):
        rep.warn(w, "indexed figures predate tax year %d" % year)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=2026)
    ap.add_argument("--data", default="src/data")
    ap.add_argument("--strict", action="store_true",
                    help="treat warnings as failures (use once verification is done)")
    args = ap.parse_args()

    root = pathlib.Path(args.data) / ("tax-year-%d" % args.year)
    rep = Report()

    if not root.exists():
        print("no dataset at %s — run scripts/extract_tax_data.py" % root)
        return 1

    check_federal(rep, json.loads((root / "federal.json").read_text()), args.year)

    files = sorted((root / "states").glob("*.json"))
    if len(files) != 51:
        rep.error("states", "expected 51 jurisdictions, found %d" % len(files))
    slugs = set()
    for f in files:
        d = json.loads(f.read_text())
        if d.get("slug") in slugs:
            rep.error("states", "duplicate slug %s" % d.get("slug"))
        slugs.add(d.get("slug"))
        if d.get("slug") != f.stem:
            rep.error(str(f), "slug %s does not match filename" % d.get("slug"))
        check_state(rep, d, args.year)

    meta = json.loads((root / "meta.json").read_text())
    if meta.get("taxYear") != args.year:
        rep.error("meta", "taxYear mismatch")
    try:
        gen = datetime.datetime.strptime(meta["generatedAt"], "%Y-%m-%dT%H:%M:%SZ")
        age = (datetime.datetime.utcnow() - gen).days
        if age > MAX_SOURCE_AGE_DAYS:
            rep.error("meta", "dataset is %d days old; re-extract and re-verify" % age)
    except (KeyError, ValueError):
        rep.error("meta", "generatedAt missing or malformed")

    for e in rep.errors:
        print("ERROR  %s" % e)
    shown = rep.warnings[:12]
    for x in shown:
        print("warn   %s" % x)
    if len(rep.warnings) > len(shown):
        print("warn   ... and %d more" % (len(rep.warnings) - len(shown)))

    print("\n%d errors, %d warnings across %d jurisdictions"
          % (len(rep.errors), len(rep.warnings), len(files)))
    if rep.errors:
        return 1
    if args.strict and rep.warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
