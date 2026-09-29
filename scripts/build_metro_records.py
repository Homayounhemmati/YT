#!/usr/bin/env python3
"""Build the metro-page records (src/data/cost-of-living-2024/us/{slug}.json) from
the nationwide dataset the calculators already use.

fetch_cost_of_living.py was written to call the BEA and HUD APIs directly and was
never run: the development sandbox could not reach them. The same two publishers'
files were later read in full by scripts/build_col_places.py, which wrote every
metro's price parities (src/data/col/price-areas.json) and every county's Fair
Market Rents (src/data/rent-fy2026/fmr-counties.json). A metro page needs one row
of each, so this script takes them from there instead of fetching them again.

It proves itself before writing anything: the four records that already exist were
checked by hand against the publishers' files, and each must be reproduced value
for value. A mismatch stops the run.

    python3 scripts/build_metro_records.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "src/data/cost-of-living-2024/us"
AREAS = json.loads((ROOT / "src/data/col/price-areas.json").read_text())
FMR = json.loads((ROOT / "src/data/rent-fy2026/fmr-counties.json").read_text())
META = json.loads((ROOT / "src/data/col/meta.json").read_text())


def record(m):
    area = AREAS["areas"].get(m["msaCode"])
    county = FMR["counties"].get(m["principalCountyFips"])
    if area is None or area["kind"] != "metro":
        sys.exit(f"{m['slug']}: no BEA metro price area {m['msaCode']}")
    if county is None:
        sys.exit(f"{m['slug']}: no HUD county {m['principalCountyFips']}")
    if county["state"] != m["stateAbbr"]:
        sys.exit(f"{m['slug']}: county {county['name']} is in {county['state']}, not {m['stateAbbr']}")
    return {
        "slug": m["slug"],
        "name": f"{area['name']} (Metropolitan Statistical Area)",
        "displayName": m["displayName"],
        "type": "metro",
        "region": "us",
        "msaCode": m["msaCode"],
        "dataYear": AREAS["year"],
        "fmrYear": FMR["fiscalYear"],
        "indices": area["indices"],
        "referenceRent": county["rent"],
        "rentCounty": f"{county['name']}, {county['state']}",
        "stateSlug": m["stateSlug"],
        "sources": [
            {"label": META["sources"]["priceLevels"]["label"],
             "url": "https://www.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area",
             "retrieved": META["retrieved"]},
            {"label": META["sources"]["rent"]["label"],
             "url": META["sources"]["rent"]["url"],
             "retrieved": META["retrieved"]},
        ],
        "lastVerified": META["retrieved"],
        "verification": "verified",
        "verifiedBy": ("price parities and rents taken from src/data/col/price-areas.json and "
                       "src/data/rent-fy2026/fmr-counties.json, which scripts/build_col_places.py "
                       "read from BEA's MARPP file and HUD's FY2026 county file themselves"),
    }


def main():
    metros = json.loads((ROOT / "data/metros.json").read_text())["metros"]
    compared = 0
    for m in metros:
        path = OUT / f"{m['slug']}.json"
        new = record(m)
        if path.exists():
            old = json.loads(path.read_text())
            for key in ("msaCode", "dataYear", "fmrYear", "indices", "referenceRent",
                        "rentCounty", "stateSlug"):
                if old.get(key) != new[key]:
                    sys.exit(f"{m['slug']}: {key} differs from the hand-checked record — "
                             f"{old.get(key)} vs {new[key]}")
            compared += 1
            continue
        path.write_text(json.dumps(new, indent=2, ensure_ascii=False) + "\n")
        print(f"wrote {path.relative_to(ROOT)}")
    print(f"{compared} existing records reproduced exactly")


if __name__ == "__main__":
    main()
