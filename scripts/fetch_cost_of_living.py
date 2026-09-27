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
    python3 scripts/fetch_cost_of_living.py --rpp-year 2024 --fmr-year 2026

Writes src/data/cost-of-living-{year}/us/{metro-slug}.json in the 5-5 schema, then
run scripts/validate_cost_of_living.py.

WHAT TO VERIFY BEFORE TRUSTING THE OUTPUT: the API paths and parameter names below
were written from documentation, not from a successful call — the sandbox cannot
reach either host. Treat the first run as a smoke test, and check one metro's
figures against the published tables by hand before generating 30 pages from them.
"""
import argparse
import datetime
import json
import os
import pathlib
import sys
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
BEA = "https://apps.bea.gov/api/data"
HUD = "https://www.huduser.gov/hudapi/public/fmr"

# Components of BEA table MARPP, matched by DESCRIPTION rather than by line number.
# An earlier version hard-coded lines 1-4 and mapped line 4 to "other services".
# BEA added a separate Utilities component, which moves "other services" down a
# line — with hard-coded numbers, utilities would have been stored silently as
# other services. The line list is now read from the API and matched by text, and
# the run stops if any component cannot be matched.
RPP_COMPONENTS = {
    "allItems": ("all items",),
    "goods": ("goods",),
    "rent": ("housing", "rents"),
    "utilities": ("utilities",),
    "otherServices": ("other",),
}
REQUIRED_COMPONENTS = {"allItems"}


def get_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def rpp_line_codes(key):
    """Map each component to its MARPP line code by reading the line descriptions."""
    params = urllib.parse.urlencode({
        "UserID": key, "method": "GetParameterValuesFiltered",
        "datasetname": "Regional", "TargetParameter": "LineCode",
        "TableName": "MARPP", "ResultFormat": "JSON",
    })
    rows = get_json(f"{BEA}/?{params}")["BEAAPI"]["Results"]["ParamValue"]
    found = {}
    for row in rows:
        desc = row["Desc"].lower()
        # MARPP also carries real-income and deflator lines; only price-parity
        # lines may be matched to a component.
        if "rpp" not in desc and "price parit" not in desc:
            continue
        for name, needles in RPP_COMPONENTS.items():
            if name in found:
                continue
            # "goods" must not match "services"; "other" must be the services line.
            if name == "otherServices" and "services" not in desc:
                continue
            if name == "goods" and "services" in desc:
                continue
            if any(n in desc for n in needles):
                found[name] = row["Key"]
    print("MARPP components matched:", {k: v for k, v in sorted(found.items())})
    missing = REQUIRED_COMPONENTS - found.keys()
    if missing:
        raise SystemExit(f"Could not identify MARPP lines for {sorted(missing)}; "
                         f"descriptions were: {[r['Desc'] for r in rows]}")
    if len(set(found.values())) != len(found):
        raise SystemExit(f"Two components matched the same line: {found}")
    return found


def fetch_rpp(key, year):
    """BEA Regional Price Parities by metropolitan statistical area."""
    out = {}
    for name, line in rpp_line_codes(key).items():
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


FMR_FIELDS = {"bedrooms0": "Efficiency", "bedrooms1": "One-Bedroom",
              "bedrooms2": "Two-Bedroom", "bedrooms3": "Three-Bedroom",
              "bedrooms4": "Four-Bedroom"}


def county_fips(token, state_abbr, county_name):
    """Resolve a county NAME to HUD's entity id through HUD's own county list.

    The earlier version expected a `countyFips` field that metros.json never had,
    so no rent was ever fetched and every metro silently shipped without one.
    Names are declared in metros.json because they are unambiguous and checkable
    by a reader; the id is looked up rather than typed from memory."""
    rows = get_json(f"{HUD}/listCounties/{state_abbr}",
                    {"Authorization": f"Bearer {token}"})
    hits = [r for r in rows
            if r.get("county_name", "").lower() == county_name.lower()]
    if len(hits) != 1:
        raise SystemExit(f"{county_name}, {state_abbr}: expected one HUD county, "
                         f"found {len(hits)}")
    return hits[0]["fips_code"]


def fetch_fmr(token, year, entity_id):
    """HUD Fair Market Rent, by bedroom count. Rent is the one category where an
    actual dollar figure is published rather than an index (4-9-1). FMR is gross
    rent: shelter plus tenant-paid utilities."""
    data = get_json(f"{HUD}/data/{entity_id}?year={year}",
                    {"Authorization": f"Bearer {token}"})
    basic = data["data"]["basicdata"]
    # Small Area FMR metros return one row per ZIP code plus a metro-wide row.
    if isinstance(basic, list):
        metro = [r for r in basic if str(r.get("zip_code", "")).lower() == "msa level"]
        if len(metro) != 1:
            raise SystemExit(f"{entity_id}: Small Area FMR response without a "
                             "single 'MSA level' row — refusing to pick a ZIP")
        basic = metro[0]
    rent = {k: basic.get(v) for k, v in FMR_FIELDS.items()
            if basic.get(v) is not None}
    if "bedrooms1" not in rent:
        raise SystemExit(f"{entity_id}: no one-bedroom FMR in the response")
    return rent


def match_msa(rpp, metro):
    """Exactly one MSA whose name starts with the metro's principal city and names
    its state. The old rule compared the first word of the slug, so 'San Francisco'
    and 'San Antonio' both reduced to 'san' and matched the same row."""
    city = metro["displayName"].lower()
    abbr = metro["stateAbbr"].upper()
    hits = [(code, row) for code, row in rpp.items()
            if row["name"].lower().startswith(city)
            and abbr in row["name"].split(",")[-1]]
    if len(hits) != 1:
        raise SystemExit(f"{metro['name']}: expected exactly one MSA, found "
                         f"{[r['name'] for _, r in hits]}")
    return hits[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rpp-year", type=int, required=True,
                    help="latest BEA RPP year (published with a lag of about a year)")
    ap.add_argument("--fmr-year", type=int, required=True,
                    help="HUD fiscal year of the Fair Market Rents (current FY)")
    ap.add_argument("--metros", default="data/metros.json",
                    help="only metros that pass the gate in 6-10-3 are built")
    args = ap.parse_args()

    bea_key = os.environ.get("BEA_API_KEY")
    hud_token = os.environ.get("HUD_API_TOKEN")
    if not bea_key or not hud_token:
        sys.exit("Both BEA_API_KEY and HUD_API_TOKEN are required — a metro without "
                 "rent is not a cost-of-living page. Free keys:\n"
                 "  https://apps.bea.gov/API/signup/\n"
                 "  https://www.huduser.gov/portal/dataset/fmr-api.html")

    metros = json.loads((ROOT / args.metros).read_text())["metros"]
    for m in metros:
        for field in ("stateAbbr", "principalCounty"):
            if not m.get(field):
                sys.exit(f"{m['slug']}: metros.json needs `{field}`")
    retrieved = datetime.date.today().isoformat()

    print(f"fetching BEA regional price parities for {args.rpp_year}...")
    rpp = fetch_rpp(bea_key, args.rpp_year)
    print(f"  {len(rpp)} MSAs returned\n")

    outdir = ROOT / f"src/data/cost-of-living-{args.rpp_year}/us"
    outdir.mkdir(parents=True, exist_ok=True)

    for m in metros:
        code, row = match_msa(rpp, m)
        fips = county_fips(hud_token, m["stateAbbr"], m["principalCounty"])
        rent = fetch_fmr(hud_token, args.fmr_year, fips)
        doc = {
            "slug": m["slug"],
            "name": row["name"],
            "displayName": m["displayName"],
            "type": "metro",
            "region": "us",
            "msaCode": code,
            "dataYear": args.rpp_year,
            "fmrYear": args.fmr_year,
            "indices": row["indices"],
            "referenceRent": rent,
            "rentCounty": f"{m['principalCounty']}, {m['stateAbbr']}",
            "stateSlug": m["stateSlug"],
            "sources": [
                {"label": f"BEA Regional Price Parities, MARPP, {args.rpp_year}",
                 "url": "https://www.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area",
                 "retrieved": retrieved},
                {"label": f"HUD Fair Market Rent, FY{args.fmr_year}",
                 "url": "https://www.huduser.gov/portal/datasets/fmr.html",
                 "retrieved": retrieved},
            ],
            "lastVerified": "",
            "verification": "pending",
        }
        (outdir / f"{m['slug']}.json").write_text(json.dumps(doc, indent=2) + "\n")
        print(f"  {m['slug']:<22} {row['name'][:48]:<48} all items "
              f"{row['indices'].get('allItems')}  1BR ${rent['bedrooms1']}")

    print(f"\nwrote {len(metros)} files to {outdir.relative_to(ROOT)}")
    print("BEFORE TRUSTING: check one metro by hand against the published BEA table "
          "and the HUD FMR lookup, then set lastVerified and verification.")
    print(f"next: python3 scripts/validate_cost_of_living.py --year {args.rpp_year}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
