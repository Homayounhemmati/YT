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


BULK = "https://apps.bea.gov/regional/zip/MARPP.zip"


def load_bulk():
    """BEA's own bulk file for table MARPP — no API key, straight from the source.
    Returns ({msa_code: {"name", "indices": {component: value}}}, year, released)."""
    import csv, io, zipfile
    req = urllib.request.Request(BULK, headers={"User-Agent": "LifeCalc data import"})
    with urllib.request.urlopen(req, timeout=120) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
    name = next(n for n in z.namelist() if n.startswith("MARPP_MSA") and n.endswith(".csv"))
    released = z.getinfo(name).date_time
    rows = list(csv.DictReader(io.TextIOWrapper(z.open(name), encoding="latin-1")))
    years = [c for c in rows[0] if c.strip().isdigit()]
    year = max(years)
    # Components are matched by description, never by line number (utilities is
    # line 4 and "other" line 5 — a hard-coded 4 would store utilities as other).
    comp = {}
    for r in rows:
        desc = (r.get("Description") or "").strip().lower()
        for key, needles in RPP_COMPONENTS.items():
            if "rpp" in desc and any(n in desc for n in needles):
                if key == "otherServices" and "services" not in desc:
                    continue
                if key == "goods" and "services" in desc:
                    continue
                comp.setdefault(r["LineCode"], key)
    out = {}
    for r in rows:
        key = comp.get(r.get("LineCode"))
        if not key:
            continue
        code = r["GeoFIPS"].strip().strip('"')
        v = (r.get(year) or "").strip()
        try:
            val = float(v)
        except ValueError:
            continue   # "(NA)" or suppressed: the category is omitted, never filled
        e = out.setdefault(code, {"name": r["GeoName"].strip().strip('"'), "indices": {}})
        e["indices"][key] = val
    return out, int(year), "%04d-%02d-%02d" % released[:3], sorted(set(comp.values()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fmr-year", type=int, required=True,
                    help="HUD fiscal year of the Fair Market Rents (current FY)")
    ap.add_argument("--metros", default="data/metros.json",
                    help="only metros that pass the gate in 6-10-3 are built")
    args = ap.parse_args()

    # Rent comes from HUD's county file, imported locally by
    # scripts/import_hud_fmr.py; each metro names its principal county's FIPS code.
    fmr_path = ROOT / f"src/data/rent-fy{args.fmr_year}/fmr-counties.json"
    if not fmr_path.exists():
        sys.exit(f"{fmr_path.relative_to(ROOT)} is missing: run scripts/import_hud_fmr.py "
                 f"--year {args.fmr_year} first")
    fmr = json.loads(fmr_path.read_text())

    metros_doc = json.loads((ROOT / args.metros).read_text())
    metros = metros_doc["metros"]
    for m in metros:
        for field in ("stateAbbr", "principalCounty", "principalCountyFips"):
            if not m.get(field):
                sys.exit(f"{m['slug']}: metros.json needs `{field}`")
    retrieved = datetime.date.today().isoformat()

    print("fetching BEA Regional Price Parities (bulk file MARPP)...")
    rpp, year, released, components = load_bulk()
    print(f"  {len(rpp)} areas · latest year {year} · file dated {released} · components {components}\n")
    if "allItems" not in components:
        sys.exit("the all-items line was not identified — stopping rather than guessing")

    outdir = ROOT / f"src/data/cost-of-living-{year}/us"
    outdir.mkdir(parents=True, exist_ok=True)

    for m in metros:
        code, row = match_msa(rpp, m)
        county = fmr["counties"].get(m["principalCountyFips"])
        if not county or not county.get("rent"):
            sys.exit(f"{m['slug']}: no single HUD FMR for county {m['principalCountyFips']}")
        rent = county["rent"]
        doc = {
            "slug": m["slug"],
            "name": row["name"],
            "displayName": m["displayName"],
            "type": "metro",
            "region": "us",
            "msaCode": code,
            "dataYear": year,
            "fmrYear": args.fmr_year,
            "indices": row["indices"],
            "referenceRent": rent,
            "rentCounty": f"{m['principalCounty']}, {m['stateAbbr']}",
            "stateSlug": m["stateSlug"],
            "sources": [
                {"label": f"BEA Regional Price Parities, MARPP, {year} (released {released})",
                 "url": "https://www.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area",
                 "retrieved": retrieved},
                {"label": fmr["source"]["label"], "url": fmr["source"]["url"],
                 "retrieved": fmr["source"]["retrieved"]},
            ],
            "lastVerified": "",
            "verification": "pending",
        }
        (outdir / f"{m['slug']}.json").write_text(json.dumps(doc, indent=2) + "\n")
        m["indices"] = row["indices"]
        m["dataYear"] = year
        m["msaCode"] = code
        m["dataStatus"] = "indices-and-rent-ready"
        print(f"  {m['slug']:<18} {row['name'][:46]:<46} all items "
              f"{row['indices'].get('allItems')}  1BR ${rent['bedrooms1']:,.0f}")

    (ROOT / args.metros).write_text(json.dumps(metros_doc, indent=2, ensure_ascii=False) + "\n")
    print(f"\nwrote {len(metros)} files to {outdir.relative_to(ROOT)} and updated {args.metros}")
    print(f"next: python3 scripts/validate_cost_of_living.py --year {year}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
