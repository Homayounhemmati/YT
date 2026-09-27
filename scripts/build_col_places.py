#!/usr/bin/env python3
"""Every place the cost-of-living calculator can price, from primary sources.

A place is priced by two things that come from different publishers:

  rent         HUD Fair Market Rent for the place itself — per county, or per
               town in the six New England states where HUD sets rents by town.
  price level  BEA Regional Price Parities for the area the place belongs to:
               its metropolitan statistical area when it is in one, otherwise
               the non-metropolitan portion of its state.

Which metro a county belongs to comes from the Census Bureau's July 2023
delineation (the one BEA's 2024 parities use). Cities are what people search
for, so every incorporated city in the Census Bureau's 2024 population
estimates is listed too, attached to the county holding most of its people;
a city that spans counties keeps the others as alternatives.

Outputs (all generated; never edit by hand):
  src/data/col/price-areas.json     every BEA area with its five parities
  src/data/col/places/{st}.json     counties, New England towns and cities
  src/data/col/meta.json            sources, years, counts

    python3 scripts/build_col_places.py [--cache DIR]
"""
import argparse
import csv
import datetime
import io
import json
import pathlib
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "src/data/col"
UA = "Mozilla/5.0 (LifeCalc data verification)"

SOURCES = {
    "marpp": "https://apps.bea.gov/regional/zip/MARPP.zip",
    "parpp": "https://apps.bea.gov/regional/zip/PARPP.zip",
    "hud": "https://www.huduser.gov/portal/datasets/fmr/fmr2026/FY26_FMRs_revised.xlsx",
    "delineation": ("https://www2.census.gov/programs-surveys/metro-micro/geographies/"
                    "reference-files/2023/delineation-files/list1_2023.xlsx"),
    "cities": ("https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/"
               "cities/totals/sub-est2024.csv"),
}
FMR_YEAR, RPP_YEAR, POP_YEAR, DELINEATION = 2026, "2024", 2024, "July 2023"
NEW_ENGLAND = {"CT", "ME", "MA", "NH", "RI", "VT"}
STATE_SLUGS = {
    "AL": "alabama", "AK": "alaska", "AZ": "arizona", "AR": "arkansas", "CA": "california",
    "CO": "colorado", "CT": "connecticut", "DE": "delaware", "DC": "washington-dc",
    "FL": "florida", "GA": "georgia", "HI": "hawaii", "ID": "idaho", "IL": "illinois",
    "IN": "indiana", "IA": "iowa", "KS": "kansas", "KY": "kentucky", "LA": "louisiana",
    "ME": "maine", "MD": "maryland", "MA": "massachusetts", "MI": "michigan",
    "MN": "minnesota", "MS": "mississippi", "MO": "missouri", "MT": "montana",
    "NE": "nebraska", "NV": "nevada", "NH": "new-hampshire", "NJ": "new-jersey",
    "NM": "new-mexico", "NY": "new-york", "NC": "north-carolina", "ND": "north-dakota",
    "OH": "ohio", "OK": "oklahoma", "OR": "oregon", "PA": "pennsylvania",
    "RI": "rhode-island", "SC": "south-carolina", "SD": "south-dakota", "TN": "tennessee",
    "TX": "texas", "UT": "utah", "VT": "vermont", "VA": "virginia", "WA": "washington",
    "WV": "west-virginia", "WI": "wisconsin", "WY": "wyoming",
}
COMPONENTS = {"all items": "allItems", "goods": "goods", "housing": "rent",
              "utilities": "utilities", "other": "otherServices"}
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def fetch(key, cache):
    url = SOURCES[key]
    path = cache / pathlib.Path(url).name if cache else None
    if path and path.exists():
        return path.read_bytes()
    for attempt in range(6):
        p = subprocess.run(["curl", "-sSL", "--fail", "--max-time", "300", "--retry", "3",
                            "-A", UA, url], capture_output=True)
        # HUD answers a first request with an empty 202 while it checks the client.
        if p.returncode == 0 and len(p.stdout) > 1000:
            break
        time.sleep(3 * (attempt + 1))
    else:
        sys.exit(f"cannot download {url}: {p.stderr.decode(errors='replace').strip() or 'empty body'}")
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(p.stdout)
    return p.stdout


def xlsx_rows(data):
    """First sheet as lists of cell text. The files carry document properties some
    readers reject, so the XML is read directly."""
    z = zipfile.ZipFile(io.BytesIO(data))
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    root = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    for r in root.iter("{%s}row" % NS["m"]):
        out = {}
        for c in r.findall("m:c", NS):
            col = re.match(r"[A-Z]+", c.get("r")).group()
            v, t = c.find("m:v", NS), c.get("t")
            if t == "inlineStr":
                out[col] = "".join(x.text or "" for x in c.iter("{%s}t" % NS["m"]))
            elif v is not None:
                out[col] = shared[int(v.text)] if t == "s" else v.text
        yield out


def parities(zdata, prefix):
    """{geo code: {"name", "indices"}} for the latest year, components matched by
    description (never by line number)."""
    z = zipfile.ZipFile(io.BytesIO(zdata))
    name = next(n for n in z.namelist() if n.startswith(prefix) and n.endswith(".csv"))
    out = {}
    for r in csv.DictReader(io.TextIOWrapper(z.open(name), encoding="latin-1")):
        if not r.get("GeoName") or RPP_YEAR not in r:
            continue
        desc = (r.get("Description") or "").strip().lower()
        key = next((v for k, v in COMPONENTS.items() if desc.endswith(k)), None)
        try:
            value = float((r.get(RPP_YEAR) or "").strip())
        except ValueError:
            continue
        if value <= 0:
            continue   # BEA writes 0 for portions that do not exist (New Jersey's nonmetro)
        if not key:
            continue
        code = r["GeoFIPS"].strip().strip('"')
        e = out.setdefault(code, {"name": r["GeoName"].strip().rstrip(" *"), "indices": {}})
        e["indices"][key] = value
    return out


SUFFIXES = ["city and borough", "unified government", "consolidated government",
            "metropolitan government", "metro government", "urban county",
            "metro township", "municipality", "corporation", "township", "borough",
            "village", "city", "town", "CDP"]


def display_name(name):
    """'Kansas City city' -> 'Kansas City'; 'Nashville-Davidson metropolitan
    government (balance)' -> 'Nashville-Davidson'. Maine's plantations, grants and
    gores keep their descriptor: it is part of how the place is known."""
    n = re.sub(r"\s*\(balance\)$", "", name)
    for s in SUFFIXES:
        if n.endswith(" " + s):
            return n[: -len(s) - 1].rstrip(",")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=pathlib.Path,
                    help="keep the downloaded files here and reuse them")
    args = ap.parse_args()
    retrieved = datetime.date.today().isoformat()

    # --- price areas ------------------------------------------------------
    msas = parities(fetch("marpp", args.cache), "MARPP")
    portions = parities(fetch("parpp", args.cache), "PARPP")
    areas = {}
    for code, e in msas.items():
        if code.startswith("00"):
            continue   # national rows
        areas[code] = {"name": re.sub(r" \(Metropolitan Statistical Area\)$", "", e["name"]),
                       "kind": "metro", "indices": e["indices"]}
    for code, e in portions.items():
        if code == "00000" or not e["indices"]:
            continue
        kind = "state-metro-portion" if code.endswith("998") else "state-nonmetro-portion"
        areas[code] = {"name": e["name"], "kind": kind, "indices": e["indices"]}
    incomplete = [c for c, a in areas.items() if len(a["indices"]) != 5]
    if incomplete:
        sys.exit(f"price areas without all five parities: {incomplete[:10]}")

    # --- county -> metro (Census 2023) ------------------------------------
    rows = xlsx_rows(fetch("delineation", args.cache))
    header = None
    county_cbsa = {}
    for r in rows:
        if r.get("A") == "CBSA Code":
            header = {v: k for k, v in r.items()}
            continue
        if not header or not (r.get(header["FIPS State Code"]) and r.get(header["FIPS County Code"])):
            continue
        if r.get(header["Metropolitan/Micropolitan Statistical Area"]) != "Metropolitan Statistical Area":
            continue
        fips = r[header["FIPS State Code"]].zfill(2) + r[header["FIPS County Code"]].zfill(3)
        county_cbsa[fips] = (r[header["CBSA Code"]], r[header["CBSA Title"]])

    def price_area(fips, st):
        """The BEA area for a county, and a note when it had to fall back."""
        cbsa = county_cbsa.get(fips)
        if cbsa and cbsa[0] in areas:
            return cbsa[0], None
        stfips = fips[:2]
        if cbsa:
            # A metro BEA does not publish separately: its state's metro portion.
            return f"{stfips}998", f"BEA publishes no separate parities for {cbsa[1]}; " \
                                   f"the metropolitan portion of the state is used."
        code = f"{stfips}999" if f"{stfips}999" in areas else f"{stfips}998"
        return code, None

    # --- HUD rents: counties and New England towns ------------------------
    rows = xlsx_rows(fetch("hud", args.cache))
    h = {v: k for k, v in next(rows).items()}
    get = lambda r, k: r.get(h[k]) or ""
    places = {st: [] for st in STATE_SLUGS}
    county_rent, county_name = {}, {}
    fallbacks = {}
    for r in rows:
        st = get(r, "stusps")
        if st not in STATE_SLUGS:
            continue   # territories: BEA publishes no parities for them
        fips10 = get(r, "fips")
        county5 = fips10[:5]
        rent = {f"bedrooms{i}": float(get(r, f"fmr_{i}")) for i in range(5)}
        area, note = price_area(county5, st)
        if note:
            fallbacks[county5] = note
        town = get(r, "county_town_name")
        cname = get(r, "countyname")
        county_name[county5] = cname
        base = {
            "state": st, "stateSlug": STATE_SLUGS[st], "county": county5, "countyName": cname,
            "priceArea": area, "rent": rent, "fmrArea": get(r, "hud_area_name"),
            "population": int(float(get(r, "pop2023") or 0)),
        }
        if note:
            base["note"] = note
        if fips10.endswith("99999"):
            county_rent[county5] = rent
            places[st].append({"id": county5, "name": cname, "kind": "county", **base})
        else:
            places[st].append({"id": fips10, "name": town, "kind": "town", **base})

    # --- cities (outside New England, where towns already are the cities) --
    text = fetch("cities", args.cache).decode("latin-1")
    parts = {}
    for r in csv.DictReader(io.StringIO(text)):
        # Every place-within-county row except the unincorporated remainders
        # ("Balance of Harris County"). Consolidated cities appear as "(balance)"
        # rows with status F (Indianapolis, Nashville, Louisville) and must stay;
        # Hawaii has no incorporated places, only census-designated ones.
        if r["SUMLEV"] != "157" or r["NAME"].startswith("Balance of"):
            continue
        st_fips = r["STATE"]
        county5 = st_fips + r["COUNTY"]
        if county5 not in county_rent:
            continue
        name = re.sub(r" \(pt\.\)$", "", r["NAME"])
        key = (st_fips, r["PLACE"])
        parts.setdefault(key, {"name": name, "parts": []})["parts"].append(
            (int(r[f"POPESTIMATE{POP_YEAR}"] or 0), county5))
    by_fips = {}
    for st, lst in places.items():
        for p in lst:
            if p["kind"] == "county":
                by_fips[p["id"]] = p
    cities = 0
    for (st_fips, place), e in parts.items():
        e["parts"].sort(reverse=True)
        pop, county5 = e["parts"][0]
        c = by_fips[county5]
        if c["state"] in NEW_ENGLAND:
            continue
        entry = {
            "id": f"{st_fips}{place}", "name": e["name"], "kind": "city",
            **{k: c[k] for k in ("state", "stateSlug", "county", "countyName", "priceArea",
                                 "rent", "fmrArea")},
            "population": sum(p for p, _ in e["parts"]),
        }
        if c.get("note"):
            entry["note"] = c["note"]
        others = [{"county": cf, "countyName": by_fips[cf]["name"], "population": p}
                  for p, cf in e["parts"][1:] if cf in by_fips]
        # Only worth asking which part of the city if the rent or prices differ.
        others = [o for o in others if by_fips[o["county"]]["rent"] != c["rent"]
                  or by_fips[o["county"]]["priceArea"] != c["priceArea"]]
        if others:
            entry["alsoIn"] = others
        places[c["state"]].append(entry)
        cities += 1

    # --- write ----------------------------------------------------------
    # One file per state. Counties and towns carry the numbers; a city only names
    # its county, so nothing is stored twice.
    (OUT / "places").mkdir(parents=True, exist_ok=True)
    for old in (OUT / "places").glob("*.json"):
        old.unlink()
    for st, lst in places.items():
        rentals = {}
        for p in lst:
            if p["kind"] in ("county", "town"):
                rec = {"name": p["name"], "kind": p["kind"], "priceArea": p["priceArea"],
                       "rent": [p["rent"][f"bedrooms{i}"] for i in range(5)],
                       "fmrArea": p["fmrArea"], "population": p["population"]}
                if p["kind"] == "town":
                    rec["county"] = p["county"]
                    rec["countyName"] = p["countyName"]
                if p.get("note"):
                    rec["note"] = p["note"]
                rentals[p["id"]] = rec
        cities = sorted(
            ({"name": p["name"], "county": p["county"], "population": p["population"],
              **({"alsoIn": [o["county"] for o in p["alsoIn"]]} if p.get("alsoIn") else {})}
             for p in lst if p["kind"] == "city"),
            key=lambda c: (-c["population"], c["name"]))
        # Labels: what the search box shows. Two places with the same short name
        # in one state are told apart by county.
        seen = {}
        for rec in list(rentals.values()) + cities:
            short = rec["name"] if rec.get("kind") == "county" else display_name(rec["name"])
            rec["label"] = f"{short}, {st}"
            seen.setdefault(rec["label"], []).append(rec)
        for label, recs in seen.items():
            if len(recs) > 1:
                for rec in recs:
                    cname = (rentals.get(rec.get("county"), {}).get("name")
                             or rec.get("countyName") or rec["name"])
                    if rec.get("kind") != "county":
                        rec["label"] = f"{label} ({cname})"
        # Still ambiguous (a city and a town of one name in one county): the
        # official name, which carries the distinction.
        again = {}
        for rec in list(rentals.values()) + cities:
            again.setdefault(rec["label"], []).append(rec)
        for label, recs in again.items():
            if len(recs) > 1:
                for rec in recs:
                    rec["label"] = f"{rec['name']}, {st}"
        doc = {"state": st, "stateSlug": STATE_SLUGS[st],
               "counties": {k: v for k, v in sorted(rentals.items(),
                                                     key=lambda kv: -kv[1]["population"])},
               "cities": cities}
        (OUT / "places" / f"{st.lower()}.json").write_text(
            json.dumps(doc, separators=(",", ":"), ensure_ascii=False) + "\n")
    # One small national index so a visitor can type "Austin" without choosing a
    # state first. Every county and town, and every city of 2,500 people or more;
    # smaller cities are found after the state is chosen. [label, state, key, pop]
    index = []
    for st in places:
        doc = json.loads((OUT / "places" / f"{st.lower()}.json").read_text())
        for cid, c in doc["counties"].items():
            index.append([c["label"], st, f"area:{cid}", c["population"]])
        for c in doc["cities"]:
            if c["population"] >= 2500:
                index.append([c["label"], st, f"city:{c['label']}", c["population"]])
    index.sort(key=lambda e: (-e[3], e[0]))
    (OUT / "search-index.json").write_text(json.dumps(
        {"fields": ["label", "state", "key", "population"], "entries": index},
        separators=(",", ":"), ensure_ascii=False) + "\n")

    (OUT / "price-areas.json").write_text(json.dumps(
        {"year": int(RPP_YEAR), "base": "United States = 100", "areas": areas},
        indent=1, ensure_ascii=False) + "\n")
    counts = {k: sum(1 for lst in places.values() for p in lst if p["kind"] == k)
              for k in ("county", "town", "city")}
    meta = {
        "$comment": "GENERATED by scripts/build_col_places.py from primary sources. Do not edit.",
        "retrieved": retrieved,
        "sources": {
            "priceLevels": {"label": f"BEA Regional Price Parities {RPP_YEAR} (MARPP metro areas, "
                            "PARPP state metropolitan and nonmetropolitan portions)",
                            "urls": [SOURCES["marpp"], SOURCES["parpp"]]},
            "rent": {"label": f"HUD Fair Market Rents FY{FMR_YEAR} (revised file)",
                     "url": SOURCES["hud"]},
            "metroMembership": {"label": f"Census Bureau metropolitan delineation, {DELINEATION}",
                                "url": SOURCES["delineation"]},
            "cities": {"label": f"Census Bureau population estimates, vintage {POP_YEAR}, "
                       "incorporated places by county", "url": SOURCES["cities"]},
        },
        "years": {"priceLevels": int(RPP_YEAR), "rent": FMR_YEAR, "population": POP_YEAR},
        "counts": {**counts, "priceAreas": len(areas), "fallbacks": len(fallbacks)},
        "fallbacks": fallbacks,
        "verification": "verified",
        "verifiedBy": "every value read from the publisher's own file at build time",
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    size = sum(f.stat().st_size for f in (OUT / "places").glob("*.json"))
    print(f"{len(areas)} price areas · {counts} · {len(fallbacks)} county fallbacks · "
          f"place files {size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
