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
            for k in ("bedrooms1", "bedrooms2"):
                v = rent.get(k)
                if v is not None and (not isinstance(v, (int, float)) or v <= 0):
                    errors.append(f"{slug}: referenceRent.{k} is {v!r}")
            if rent.get("bedrooms1") and rent.get("bedrooms2") \
                    and rent["bedrooms1"] > rent["bedrooms2"]:
                errors.append(f"{slug}: one-bedroom rent exceeds two-bedroom — "
                              "the columns are probably swapped")
        else:
            warnings.append(f"{slug}: no referenceRent (HUD FMR) — rent scaling "
                            "cannot be shown for this metro")

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
