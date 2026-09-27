#!/usr/bin/env python3
"""National household spending by category and household size, from the BLS
Consumer Expenditure Survey.

This is the "national average" half of the cost-of-living calculator's household
estimate; BEA Regional Price Parities price it locally. Housing and utilities are
deliberately absent: rent comes from HUD Fair Market Rent, which already includes
tenant-paid utilities, and fetching them here would count them twice.

    python3 scripts/fetch_ces.py --year 2024            # BLS series via FRED, no key
    BLS_API_KEY=... python3 scripts/fetch_ces.py --year 2024 --via bls

FRED (Federal Reserve Bank of St. Louis) republishes these BLS series under the same
IDs; the keyless BLS API is capped at a small daily quota per network, which a
shared egress address exhausts quickly, so FRED is the default.

Writes src/data/ces-{year}/baseline.json in the SpendingBaseline shape
(src/lib/col/types.ts).

Series IDs were confirmed on 2026-09-27 against the series titles FRED publishes
(e.g. CXUFOODHOMELB0502M = "Expenditures: Food at Home by Size of Consumer Unit:
One Person Consumer Unit") and one value cross-checked against the BLS API (3,395
for 2024). Demographic table LB05 is size of consumer unit; LB04 is age. The script
stops on any series that comes back missing rather than writing a zero.
"""
import argparse
import datetime
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
API = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# key -> (label, CE item codes summed into it, BEA price-parity component)
CATEGORIES = {
    "food_home":     ("Groceries",                ["FOODHOME"],             "goods"),
    "food_away":     ("Eating out",               ["FOODAWAY"],             "otherServices"),
    # Transportation less the two other parts of it. The gasoline series itself
    # (GASOIL) ends in 2023 on FRED; the CE hierarchy is exact (2022, one person:
    # 2,103 + 1,590 + 2,233 + 553 = 6,479 = TRANS), so nothing is estimated.
    "vehicles_fuel": ("Car purchase and fuel",    ["TRANS", "-VEHOTHXP", "-PUBTRANS"], "goods"),
    "vehicle_other": ("Car insurance and upkeep", ["VEHOTHXP"],             "otherServices"),
    "public_transit":("Public transportation",    ["PUBTRANS"],             "otherServices"),
    "health":        ("Health care",              ["HEALTH"],               "otherServices"),
    "apparel":       ("Clothing",                 ["APPAREL"],              "goods"),
    # Telephone services (cell + landline). Not in HUD gross rent, so no double count;
    # internet access is a separate CE line and is not included here.
    "phone":         ("Phone service",            ["PHONE"],                "otherServices"),
    "entertainment": ("Entertainment",            ["ENTRTAIN"],             "allItems"),
    "personal_care": ("Personal care",            ["PERSCARE"],             "allItems"),
    "education":     ("Education",                ["EDUCATN"],              "otherServices"),
}
# Table LB05, size of consumer unit: 02 one person, 03 two or more (unused),
# 04 two, 05 three, 06 four, 07 five or more.
SIZE_CODES = {"1": "02", "2": "04", "3": "05", "4": "06", "5": "07"}


def series_id(item, size_code):
    return f"CXU{item}LB05{size_code}M"


def fetch(ids, year, key):
    body = {"seriesid": ids, "startyear": str(year), "endyear": str(year)}
    if key:
        body["registrationkey"] = key
    req = urllib.request.Request(API, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def fetch_fred(ids, year):
    """{series_id: annual dollars} from FRED's keyless CSV download. Uses curl:
    Python's own client stalls on FRED from some networks while curl does not."""
    import csv, io, subprocess
    out = {}
    for n, sid in enumerate(ids, 1):
        if n % 10 == 0:
            print(f"  {n}/{len(ids)} series", file=sys.stderr, flush=True)
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
        p = subprocess.run(["curl", "-sS", "--fail", "--max-time", "30", "--retry", "4",
                            "--retry-all-errors", url], capture_output=True, text=True)
        if p.returncode != 0:
            print(f"  {sid}: {p.stderr.strip() or 'no response'}", file=sys.stderr)
            continue                      # reported as missing by build()
        for row in list(csv.reader(io.StringIO(p.stdout)))[1:]:
            if row and row[0].startswith(f"{year}-") and row[1] not in ("", "."):
                out[sid] = float(row[1])
        time.sleep(0.3)
    return out


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
            signed = [(-1 if i.startswith("-") else 1, series_id(i.lstrip("-"), code)) for i in items]
            gaps = [sid for _, sid in signed if sid not in values]
            if gaps:
                missing += gaps
                continue
            table[size][key] = round(sum(s * values[sid] for s, sid in signed), 2)
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
    ap.add_argument("--via", choices=["fred", "bls"], default="fred")
    args = ap.parse_args()
    ids = sorted({series_id(i.lstrip("-"), c) for c in SIZE_CODES.values()
                  for _, items, _ in CATEGORIES.values() for i in items})
    values = {}
    if args.via == "fred":
        values = fetch_fred(ids, args.year)
    else:
        for i in range(0, len(ids), 50):      # the API takes 50 series per request
            values.update(parse(fetch(ids[i:i + 50], args.year, os.environ.get("BLS_API_KEY")), args.year))
    out = build(values, args.year)
    if args.via == "fred":
        out["source"]["label"] += " (series retrieved through FRED, Federal Reserve Bank of St. Louis)"
        out["source"]["mirror"] = "https://fred.stlouisfed.org/"
    dest = ROOT / f"src/data/ces-{args.year}"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "baseline.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {dest.relative_to(ROOT)}/baseline.json — {len(CATEGORIES)} categories x "
          f"{len(SIZE_CODES)} household sizes. Check one figure against the published table.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
