#!/usr/bin/env python3
"""National household spending by category and household size, from the BLS
Consumer Expenditure Survey. Run OUTSIDE the sandbox (api.bls.gov is blocked here).

This is the "national average" half of the cost-of-living calculator's household
estimate; BEA Regional Price Parities price it locally. Housing and utilities are
deliberately absent: rent comes from HUD Fair Market Rent, which already includes
tenant-paid utilities, and fetching them here would count them twice.

    export BLS_API_KEY=...      # free: https://data.bls.gov/registrationEngine/
    python3 scripts/fetch_ces.py --year 2024

Writes src/data/ces-{year}/baseline.json in the SpendingBaseline shape
(src/lib/col/types.ts).

VERIFY BEFORE TRUSTING: the series-ID pattern and item codes below were written
from BLS documentation, not from a successful call. The script stops on any series
that comes back missing rather than writing a zero, and prints the IDs it asked for;
fix CATEGORIES or SIZE_CODES against the BLS series finder if the first run stops.
"""
import argparse
import datetime
import json
import os
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
API = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# key -> (label, CE item codes summed into it, BEA price-parity component)
CATEGORIES = {
    "food_home":     ("Groceries",                ["FOODHOME"],             "goods"),
    "food_away":     ("Eating out",               ["FOODAWAY"],             "otherServices"),
    "vehicles_fuel": ("Car purchase and fuel",    ["VEHPURCH", "GASOLINE"], "goods"),
    "vehicle_other": ("Car insurance and upkeep", ["VEHOTHXP"],             "otherServices"),
    "public_transit":("Public transportation",    ["PUBTRANS"],             "otherServices"),
    "health":        ("Health care",              ["HEALTH"],               "otherServices"),
    "apparel":       ("Clothing",                 ["APPAREL"],              "goods"),
    "phone":         ("Phone and internet",       ["TELEPHON"],             "otherServices"),
    "entertainment": ("Entertainment",            ["ENTRTAIN"],             "allItems"),
    "personal_care": ("Personal care",            ["PERSCARE"],             "allItems"),
    "education":     ("Education",                ["EDUCATN"],              "otherServices"),
}
# Size of consumer unit: one person ... five or more.
SIZE_CODES = {"1": "02", "2": "03", "3": "04", "4": "05", "5": "06"}


def series_id(item, size_code):
    return f"CXU{item}LB04{size_code}M"


def fetch(ids, year, key):
    body = {"seriesid": ids, "startyear": str(year), "endyear": str(year)}
    if key:
        body["registrationkey"] = key
    req = urllib.request.Request(API, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def parse(payload, year):
    """{series_id: annual dollars} for the requested year; missing series omitted."""
    if payload.get("status") != "REQUEST_SUCCEEDED":
        raise SystemExit(f"BLS: {payload.get('status')} {payload.get('message')}")
    out = {}
    for s in payload["Results"]["series"]:
        for d in s.get("data", []):
            if str(d.get("year")) == str(year):
                try:
                    out[s["seriesID"]] = float(d["value"].replace(",", ""))
                except (ValueError, KeyError):
                    pass
    return out


def build(values, year):
    missing, table = [], {size: {} for size in SIZE_CODES}
    for size, code in SIZE_CODES.items():
        for key, (_, items, _) in CATEGORIES.items():
            ids = [series_id(i, code) for i in items]
            gaps = [i for i in ids if i not in values]
            if gaps:
                missing += gaps
                continue
            table[size][key] = round(sum(values[i] for i in ids), 2)
    if missing:
        raise SystemExit("Missing series (no zero was written): " + ", ".join(sorted(missing)))
    return {
        "year": year,
        "source": {"label": f"BLS Consumer Expenditure Survey, {year}, by size of consumer unit",
                   "url": "https://www.bls.gov/cex/",
                   "retrieved": datetime.date.today().isoformat()},
        "categories": {k: {"label": v[0], "index": v[2]} for k, v in CATEGORIES.items()},
        "annualByHouseholdSize": table,
        "verification": "pending",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, required=True)
    args = ap.parse_args()
    ids = [series_id(i, c) for c in SIZE_CODES.values()
           for _, items, _ in CATEGORIES.values() for i in items]
    values = {}
    for i in range(0, len(ids), 50):          # the API takes 50 series per request
        values.update(parse(fetch(ids[i:i + 50], args.year, os.environ.get("BLS_API_KEY")), args.year))
    out = build(values, args.year)
    dest = ROOT / f"src/data/ces-{args.year}"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "baseline.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {dest.relative_to(ROOT)}/baseline.json — {len(CATEGORIES)} categories x "
          f"{len(SIZE_CODES)} household sizes. Check one figure against the published table.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
