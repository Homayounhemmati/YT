#!/usr/bin/env python3
"""
Cannibalisation and canonical audit.

Two pages competing for one query is the most common way a programmatic site
quietly loses rankings to itself, and it is invisible until Search Console shows
two URLs alternating on the same term. This checks the plan before any of it is
built.

Checks:
  1. every page declares exactly one primary target
  2. no primary is claimed twice
  3. no primary is also another page's secondary
  4. lexically similar primaries are flagged and must have distinct outputs
  5. every primary exists in the measured keyword set (or is a template)
  6. canonical is declared on every page and query params are stripped

Usage:
    python3 scripts/audit_seo.py
"""
import json, pathlib, re, sys
from itertools import combinations

STOP = {"calculator", "estimator", "by", "in", "to", "the", "a", "of", "for",
        "and", "vs", "your", "my"}
SIMILARITY_FLAG = 0.30


def tokens(term):
    return {t for t in re.findall(r"[a-z0-9{}]+", term.lower()) if t not in STOP}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main():
    pages_doc = json.loads(pathlib.Path("data/pages.json").read_text())
    kw_doc = json.loads(pathlib.Path("data/keywords.json").read_text())
    pages = pages_doc["pages"]

    measured = {k["term"].lower() for k in kw_doc["keywords"]}
    for s in kw_doc["programmaticSets"]:
        for o in s.get("observed", []):
            measured.add(o["term"].lower())

    errors, warnings, notes = [], [], []

    # 1-2. one primary each, never claimed twice
    seen = {}
    for p in pages:
        prim = p.get("primary")
        if prim is None:
            if "note" not in p:
                errors.append(f"{p['path']}: primary is null with no explanation")
            continue
        key = prim.lower()
        if key in seen:
            errors.append(f"primary '{prim}' claimed by both {seen[key]} and {p['path']}")
        seen[key] = p["path"]

    # 3. a primary must not appear as another page's secondary
    for p in pages:
        for sec in p.get("secondary", []):
            owner = seen.get(sec.lower())
            if owner and owner != p["path"]:
                errors.append(
                    f"{p['path']} lists '{sec}' as secondary but it is the primary of {owner}")

    # 4. lexical proximity -> must be differentiated by output
    for a, b in combinations([p for p in pages if p.get("primary")], 2):
        sim = jaccard(tokens(a["primary"]), tokens(b["primary"]))
        if sim < SIMILARITY_FLAG:
            continue
        oa, ob = a.get("output"), b.get("output")
        label = (f"{a['path']} ('{a['primary']}') vs {b['path']} ('{b['primary']}') "
                 f"— similarity {sim:.0%}")
        if not oa or not ob:
            errors.append(label + " : both need a declared distinct `output`")
        elif oa == ob:
            errors.append(label + " : identical `output` — genuine cannibalisation")
        else:
            notes.append(label + " : differentiated by output ✓")

    # 5. is the target actually measured
    for p in pages:
        prim = p.get("primary")
        if not prim:
            continue
        if "{" in prim:
            continue  # template, measured at the set level
        if prim.lower() not in measured:
            warnings.append(f"{p['path']}: '{prim}' is not in data/keywords.json — unmeasured target")

    # 6. canonical hygiene
    for p in pages:
        if p.get("canonical") != "self":
            errors.append(f"{p['path']}: canonical must be 'self' unless explicitly justified")
        if p["template"] == "ToolPage" and not p.get("stripsParams"):
            errors.append(f"{p['path']}: tool pages carry UI state in params and must strip them from canonical")
    if len(pages_doc.get("canonicalRules", [])) < 5:
        errors.append("canonicalRules is thin: host, scheme, trailing slash, case and params must all be covered")

    for e in errors:
        print(f"ERROR  {e}")
    for w in warnings:
        print(f"warn   {w}")
    for n in notes:
        print(f"ok     {n}")
    print(f"\n{len(pages)} pages · {len(errors)} errors · {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
