#!/usr/bin/env python3
"""Structural validation for the cost-of-living dataset, per spec 5-5.

The equivalent of validate_tax_data.py for the second dataset. Section 5-5 requires
it and it did not exist; without it the dataset that carries 158,000 searches a
month would ship with less checking than the one carrying 1,880.

Enforces the rules in 5-3 that the original city dataset broke:
  1. no derived value stored
  2. every field defined, every row using the same definition
  3. a category with no official index is absent, never filled with a substitute
"""
import argparse
import json
import pathlib
import sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent.parent
REQUIRED_INDICES = ["allItems", "rent", "goods", "otherServices"]
MAX_AGE_DAYS = 550  # BEA publishes annually; 18 months per 5-5


def validate_places(errors, warnings):
    """The nationwide calculator data (scripts/build_col_places.py): every state
    present, every place priced, every reference resolvable, rents sane."""
    base = ROOT / "src/data/col"
    if not (base / "meta.json").exists():
        errors.append("src/data/col is missing: run scripts/build_col_places.py")
        return
    areas = json.loads((base / "price-areas.json").read_text())["areas"]
    for code, a in areas.items():
        ix = a["indices"]
        if set(ix) != {"allItems", "goods", "rent", "utilities", "otherServices"}:
            errors.append(f"price area {code}: indices {sorted(ix)}")
        if not all(40 < v < 250 for v in ix.values()):
            errors.append(f"price area {code}: implausible parity {ix}")
    files = sorted((base / "places").glob("*.json"))
    if len(files) != 51:
        errors.append(f"expected 51 state place files, found {len(files)}")
    n_places = 0
    for f in files:
        doc = json.loads(f.read_text())
        counties = doc["counties"]
        labels = set()
        for cid, c in counties.items():
            n_places += 1
            if c["priceArea"] not in areas:
                errors.append(f"{f.name} {cid}: price area {c['priceArea']} unknown")
            r = c["rent"]
            if len(r) != 5 or any(x <= 0 for x in r):
                errors.append(f"{f.name} {cid}: rent {r}")
            elif any(r[i + 1] < r[i] for i in range(1, 4)):
                warnings.append(f"{f.name} {c['label']}: rent not rising with bedrooms {r}")
            if c["label"] in labels:
                errors.append(f"{f.name}: duplicate label {c['label']}")
            labels.add(c["label"])
        for city in doc["cities"]:
            n_places += 1
            for cid in [city["county"], *city.get("alsoIn", [])]:
                if cid not in counties:
                    errors.append(f"{f.name} {city['label']}: county {cid} not in file")
            if city["label"] in labels:
                errors.append(f"{f.name}: duplicate label {city['label']}")
            labels.add(city["label"])
    # The metro pages and the calculator must never disagree about a metro.
    for p in (ROOT / "src/data").glob("cost-of-living-*/us/*.json"):
        rec = json.loads(p.read_text())
        a = areas.get(rec.get("msaCode"))
        if a is None:
            errors.append(f"{p.name}: MSA {rec.get('msaCode')} not in price-areas.json")
        elif any(abs(a["indices"][k] - v) > 1e-9 for k, v in rec["indices"].items()):
            errors.append(f"{p.name}: indices differ from price-areas.json")
    print(f"calculator data: {len(areas)} price areas · {n_places} places in {len(files)} states")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--strict", action="store_true", help="fail on warnings too")
    args = ap.parse_args()

    d = ROOT / f"src/data/cost-of-living-{args.year}/us"
    if not d.exists():
        print(f"dataset not built: {d.relative_to(ROOT)}")
        print("run scripts/fetch_cost_of_living.py outside the sandbox first (13-6)")
        return 0  # not an error — it is simply not built yet

    files = sorted(d.glob("*.json"))
    errors, warnings = [], []
    seen_index_sets = {}

    for f in files:
        doc = json.loads(f.read_text())
        slug = doc.get("slug", f.stem)

        if doc.get("slug") != f.stem:
            errors.append(f"{f.name}: slug '{doc.get('slug')}' does not match filename")

        idx = doc.get("indices") or {}
        for key in REQUIRED_INDICES:
            if key not in idx:
                warnings.append(f"{slug}: no '{key}' index — the category must be "
                                "omitted from the page, not substituted (5-3 rule 3)")
            elif not isinstance(idx[key], (int, float)) or idx[key] <= 0:
                errors.append(f"{slug}: index '{key}' is {idx[key]!r}, not a positive number")

        # 5-3 rule 1: no derived value stored. A total or an average of the
        # components is computable at runtime and must not be in the file.
        for banned in ("total", "average", "overallScore", "compositeIndex"):
            if banned in doc:
                errors.append(f"{slug}: stores derived value '{banned}' — compute it "
                              "at runtime (5-3 rule 1)")

        # 5-3 rule 2: one definition per column, used by every row.
        seen_index_sets[slug] = tuple(sorted(idx.keys()))

        rent = doc.get("referenceRent")
        if rent:
            sizes = [f"bedrooms{n}" for n in range(5)]
            for k, v in rent.items():
                if k not in sizes:
                    errors.append(f"{slug}: unknown referenceRent key '{k}'")
                elif not isinstance(v, (int, float)) or v <= 0:
                    errors.append(f"{slug}: referenceRent.{k} is {v!r}")
            present = [rent[k] for k in sizes if k in rent]
            if present != sorted(present):
                errors.append(f"{slug}: Fair Market Rent does not rise with bedroom "
                              "count — the columns are probably misaligned")
            if "bedrooms1" not in rent:
                errors.append(f"{slug}: no one-bedroom FMR — the rent tool's default")
        else:
            # Rent is the largest line in every metro and the rent tool cannot run
            # without it. A metro without rent is not a cost-of-living page.
            errors.append(f"{slug}: no referenceRent (HUD FMR)")

        if doc.get("region") not in ("us", "eu"):
            errors.append(f"{slug}: region must be 'us' or 'eu' — the engine refuses "
                          "to compare across regions and needs to know which")
        for src in doc.get("sources") or []:
            if not src.get("retrieved"):
                errors.append(f"{slug}: source '{src.get('label')}' has no retrieval date")

        if not doc.get("sources"):
            errors.append(f"{slug}: no sources (rule 5-1)")
        if not doc.get("stateSlug"):
            errors.append(f"{slug}: no stateSlug — the cross-link to the state tax "
                          "page is the differentiator no competitor has (12-2)")
        elif not (ROOT / f"src/data/tax-year-2026/states/{doc['stateSlug']}.json").exists():
            errors.append(f"{slug}: stateSlug '{doc['stateSlug']}' has no tax dataset")

        if doc.get("verification") != "verified":
            warnings.append(f"{slug}: verification is "
                            f"'{doc.get('verification')}' — no page ships until a "
                            "human has checked it (13-4 rule 1)")
        if not doc.get("dataYear"):
            errors.append(f"{slug}: no dataYear — the vintage must be displayed (16-2-1)")

    validate_places(errors, warnings)

    if len(set(seen_index_sets.values())) > 1:
        shapes = {}
        for slug, shape in seen_index_sets.items():
            shapes.setdefault(shape, []).append(slug)
        errors.append("index categories differ between rows — one definition per "
                      "column, every row following it (5-3 rule 2): "
                      + " | ".join(f"{list(k)}: {len(v)} rows" for k, v in shapes.items()))

    for e in errors:
        print(f"ERROR  {e}")
    for w in warnings[:15]:
        print(f"warn   {w}")
    if len(warnings) > 15:
        print(f"       ... and {len(warnings) - 15} more warnings")

    print(f"\n{len(files)} metros · {len(errors)} errors · {len(warnings)} warnings")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
