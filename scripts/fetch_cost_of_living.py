#!/usr/bin/env python3
"""Build the cost-of-living dataset from BEA and HUD. Run this OUTSIDE the sandbox.

This is the project's critical path (spec 13-6). The place cluster is 158,000
searches a month against roughly 1,880 for all 51 state pages combined, and none of
it can be built until this dataset exists.

It cannot run in the development sandbox, where `.gov` is unreachable — that is an
environment limitation, not a project one (13-3). Everything else is ready: the
schema is specified in 5-5, the page templates are generated, and the audit checks
are in place. This script is the missing step.

    export BEA_API_KEY=...      # free: https://apps.bea.gov/API/signup/
    export HUD_API_TOKEN=...    # free: https://www.huduser.gov/portal/dataset/fmr-api.html
    python3 scripts/fetch_cost_of_living.py --year 2024

Writes src/data/cost-of-living-{year}/us/{metro-slug}.json in the 5-5 schema, then
run scripts/validate_cost_of_living.py.

WHAT TO VERIFY BEFORE TRUSTING THE OUTPUT: the API paths and parameter names below
were written from documentation, not from a successful call — the sandbox cannot
reach either host. Treat the first run as a smoke test, and check one metro's
figures against the published tables by hand before generating 30 pages from them.
"""
import argparse
import json
import os
import pathlib
import sys
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
BEA = "https://apps.bea.gov/api/data"
HUD = "https://www.huduser.gov/hudapi/public/fmr"

# RPP line codes in BEA table MARPP. Line 1 is the all-items index; the component
# lines are what section 4-9-2 scales by category.
RPP_LINES = {"allItems": "1", "goods": "2", "rent": "3", "otherServices": "4"}


def get_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def fetch_rpp(key, year):
    """BEA Regional Price Parities by metropolitan statistical area."""
    out = {}
    for name, line in RPP_LINES.items():
        params = urllib.parse.urlencode({
            "UserID": key, "method": "GetData", "datasetname": "Regional",
            "TableName": "MARPP", "LineCode": line, "GeoFips": "MSA",
            "Year": str(year), "ResultFormat": "JSON",
        })
        data = get_json(f"{BEA}/?{params}")
        results = data["BEAAPI"]["Results"]
        if "Error" in results:
            raise SystemExit(f"BEA error on line {line}: {results['Error']}")
        for row in results["Data"]:
            code = row["GeoFips"]
            entry = out.setdefault(code, {"name": row["GeoName"], "indices": {}})
            try:
                entry["indices"][name] = float(row["DataValue"])
            except (ValueError, KeyError):
                pass  # suppressed or unavailable; validator will catch the gap
    return out


def fetch_fmr(token, year, county_fips):
    """HUD Fair Market Rent, by bedroom count. Rent is the one category where an
    actual dollar figure is published rather than an index (4-9-1)."""
    url = f"{HUD}/data/{county_fips}?year={year}"
    data = get_json(url, {"Authorization": f"Bearer {token}"})
    d = data["data"]["basicdata"]
    return {"bedrooms1": d.get("One-Bedroom"), "bedrooms2": d.get("Two-Bedroom")}


def slugify(geo_name):
    base = geo_name.split(" (")[0]
    return (base.lower().replace(", ", "-").replace(" ", "-")
                .replace("--", "-").replace(".", "").replace("'", ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, required=True,
                    help="BEA publishes with a lag; use the most recent available "
                         "year and record it on the page (16-2-1)")
    ap.add_argument("--metros", default="data/metros.json",
                    help="only metros that pass the gate in 6-10-3 are built")
    args = ap.parse_args()

    bea_key = os.environ.get("BEA_API_KEY")
    hud_token = os.environ.get("HUD_API_TOKEN")
    if not bea_key:
        sys.exit("BEA_API_KEY is not set. Free key: https://apps.bea.gov/API/signup/")

    gate = json.loads((ROOT / args.metros).read_text())["metros"]
    wanted = {m["slug"]: m for m in gate}
    print(f"building {len(wanted)} metros that pass the 6-10-3 gate\n")

    print("fetching BEA regional price parities...")
    rpp = fetch_rpp(bea_key, args.year)
    print(f"  {len(rpp)} MSAs returned")

    outdir = ROOT / f"src/data/cost-of-living-{args.year}/us"
    outdir.mkdir(parents=True, exist_ok=True)

    written, missed = 0, []
    for code, row in rpp.items():
        slug = slugify(row["name"])
        match = next((m for s, m in wanted.items()
                      if s.split("-")[0] in slug), None)
        if not match:
            continue
        rent = None
        if hud_token and match.get("countyFips"):
            try:
                rent = fetch_fmr(hud_token, args.year, match["countyFips"])
            except Exception as e:
                missed.append(f"{slug}: HUD {type(e).__name__}")

        doc = {
            "slug": match["slug"],
            "name": row["name"],
            "displayName": match["displayName"],
            "type": "metro",
            "msaCode": code,
            "indices": row["indices"],
            "referenceRent": rent,
            "stateSlug": match["stateSlug"],
            "dataYear": args.year,
            "sources": [
                {"label": f"BEA Regional Price Parities, MARPP, {args.year}",
                 "url": "https://www.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area",
                 "retrieved": ""},
                {"label": f"HUD Fair Market Rent {args.year}",
                 "url": "https://www.huduser.gov/portal/datasets/fmr.html",
                 "retrieved": ""},
            ],
            "lastVerified": "",
            "verification": "pending",
        }
        (outdir / f"{match['slug']}.json").write_text(
            json.dumps(doc, indent=2) + "\n")
        written += 1

    print(f"\nwrote {written} files to {outdir.relative_to(ROOT)}")
    for m in missed:
        print(f"  warn: {m}")
    if written < len(wanted):
        print(f"\n{len(wanted) - written} metros not matched in the BEA response — "
              "check the GeoName-to-slug matching before relying on this")
    print("\nnext: python3 scripts/validate_cost_of_living.py --year", args.year)
    return 0


if __name__ == "__main__":
    sys.exit(main())
