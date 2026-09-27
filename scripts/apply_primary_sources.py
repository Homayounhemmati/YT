#!/usr/bin/env python3
"""Apply and check the primary-source register (data/tax-primary/{year}.json).

The extracted tax dataset comes from a secondary source (policyengine-us). The
register records, for each jurisdiction checked so far, the primary sources
opened, any value those sources correct ("set"), and every value a page relies
on ("expect"). This script:

  1. applies each "set" to the extracted record (and the "coverage" flags),
  2. checks every "expect" value against the resulting record,
  3. marks the jurisdiction "verified" only when all of them match, recording
     the sources, the date and which values were computed from a statute's
     formula rather than read from a published table.

A mismatch leaves the record "pending" and exits 1, so a regeneration that
changes a checked value cannot pass silently. extract_tax_data.py runs this
after every extraction.

    python3 scripts/apply_primary_sources.py [--year 2026]
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def get(rec, dotted):
    node = rec
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return KeyError
        node = node[part]
    return node


def put(rec, dotted, value):
    parts = dotted.split(".")
    node = rec
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value


def merge(rec, patch):
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(rec.get(key), dict) and key != "byStatus":
            merge(rec[key], value)
        else:
            rec[key] = value


def same(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) < 1e-9
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def check(rec, expect):
    """List of human-readable mismatches between `expect` and `rec`."""
    problems = []
    for key, want in expect.items():
        if key == "brackets":
            for status, pairs in want.items():
                rows = rec.get("brackets", {}).get(status) or []
                have = [[r["from"], r["rate"]] for r in rows]
                if not same(have, pairs):
                    problems.append(f"brackets.{status}: have {have}, source says {pairs}")
            continue
        have = get(rec, key)
        if have is KeyError or not same(have, want):
            problems.append(f"{key}: have {None if have is KeyError else have}, source says {want}")
    return problems


def stamp(rec, entry, retrieved, year):
    rec["verification"] = "verified"
    rec["verified"] = {
        "date": retrieved,
        "against": entry["sources"],
        "register": "data/tax-primary/%d.json" % year,
    }
    if entry.get("computed"):
        rec["verified"]["computedFromStatute"] = entry["computed"]
    if entry.get("why"):
        rec["verified"]["correction"] = entry["why"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=2026)
    args = ap.parse_args()
    register = json.loads((ROOT / f"data/tax-primary/{args.year}.json").read_text())
    base = ROOT / f"src/data/tax-year-{args.year}"
    failed = False

    fed_path = base / "federal.json"
    fed = json.loads(fed_path.read_text())
    entry = register["federal"]
    merge(fed, entry.get("set", {}))
    problems = check(fed, entry["expect"])
    if problems:
        failed = True
        fed["verification"] = "pending"
        print("federal: MISMATCH\n  " + "\n  ".join(problems))
    else:
        stamp(fed, entry, entry["sources"][0]["retrieved"], args.year)
        print(f"federal: verified ({len(entry['expect'])} checks)")
    fed_path.write_text(json.dumps(fed, indent=2, ensure_ascii=False) + "\n")

    for slug, flags in register.get("coverage", {}).items():
        path = base / "states" / f"{slug}.json"
        rec = json.loads(path.read_text())
        for key, value in flags.items():
            if key != "why":
                put(rec, key, value)
        path.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
        print(f"{slug}: coverage flag applied")

    status = {}
    for slug, entry in register["states"].items():
        path = base / "states" / f"{slug}.json"
        rec = json.loads(path.read_text())
        merge(rec, entry.get("set", {}))
        problems = check(rec, entry["expect"])
        if problems:
            failed = True
            rec["verification"] = "pending"
            rec.pop("verified", None)
            print(f"{slug}: MISMATCH\n  " + "\n  ".join(problems))
        else:
            stamp(rec, entry, entry["sources"][0]["retrieved"], args.year)
            note = " (corrected)" if entry.get("set") and not entry.get("annotationOnly") else ""
            print(f"{slug}: verified{note}")
        status[slug] = rec["verification"]
        path.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")

    meta_path = base / "meta.json"
    meta = json.loads(meta_path.read_text())
    # Each row carries the state's name, so a state picker needs this one file.
    named = []
    for row in meta["summary"]:
        if row["slug"] in status:
            row["verification"] = status[row["slug"]]
        name = json.loads((base / "states" / f"{row['slug']}.json").read_text())["name"]
        named.append({"slug": row["slug"], "name": name, **{k: v for k, v in row.items() if k not in ("slug", "name")}})
    meta["summary"] = named
    meta["verifiedCount"] = sum(1 for r in meta["summary"] if r["verification"] == "verified")
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
    print(f"\n{meta['verifiedCount']} of {len(meta['summary'])} jurisdictions verified")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
