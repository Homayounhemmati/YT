#!/usr/bin/env python3
"""Every number in published copy must be traceable (copywriting guide, rule 5-1).

Two figures in the tool copy were wrong when this check was written — "roughly
$100,000" of price for a $600 car payment (the engine says $65,000-$80,000) and a
"$80 to $250" utilities gap that had no source — and four more were found while
building it: a 43% Qualified Mortgage cap repealed in 2021, P&I quoted as 70% of
the payment (77-80%), first-year interest as three-quarters (83-87%), and a flat
income tax floor "near 3%" (Arizona is 2.5%). None was detectable by any rule that
read the copy for tone, length or keywords.

Every numeric token in a tool body or tool FAQ must be covered by an entry in
data/claims.json that says what it is based on:

  computed   arithmetic or an engine test, named in `reference`
  dataset    a value in this repository's datasets
  statute    a law or regulation, cited
  external   a published figure from a named primary source

`status` records whether it has been checked against the source itself.
Anything not `verified` is listed as a launch-checklist item, not an error; an
UNREGISTERED number is an error.

Usage: python3 scripts/audit_claims.py [--inventory]
"""
import collections
from decimal import ROUND_HALF_UP, Decimal
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NUM = re.compile(r"\$?\d[\d,]*(?:\.\d+)?%?")


def norm(tok):
    return tok.rstrip(",.")


def sources():
    """(slug, kind, text) for every tool body and tool FAQ. State bodies
    (tools__paycheck-calculator__{state}) are checked against their own dataset
    in state_numbers() instead."""
    for f in sorted((ROOT / "content/bodies").glob("tools__*.md")):
        parts = f.stem.split("__")
        if len(parts) == 2:
            yield parts[1], "body", f.read_text()
    faq = json.loads((ROOT / "data/pages.json").read_text())["onPage"]["faqFormulas"]["ToolPage"]
    for slug, rows in faq.items():
        if slug.startswith("$"):
            continue
        yield slug, "faq", "\n".join(q + "\n" + a for q, a in rows)


def tokens(text):
    text = re.sub(r"\*\*|__", "", text)
    for m in NUM.finditer(text):
        tok = norm(m.group())
        # "401(k)", "199A", "W-4" and "MW507" are names, not quantities.
        after = text[m.end():m.end() + 3]
        before = text[max(0, m.start() - 2):m.start()]
        if (after.startswith("(k)") or after[:1].isalpha() or re.fullmatch(r"[A-Z]-", before)
                or before[-1:].isalpha()):
            continue
        yield tok


def fmt_forms(v):
    """Every way a dataset value can legitimately appear in copy."""
    out = set()
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return out
    # Half up, as the copy rules require; Python's round() goes half to even and
    # would reject "$75,663" for 75,662.50.
    whole = int(Decimal(str(v)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    out |= {f"${whole:,}", f"{whole:,}", str(whole), f"${v:,.2f}"}
    out |= {f"{v:g}%", f"{v:.2f}%", f"{v:.1f}%"}
    return out


def walk_numbers(o):
    if isinstance(o, dict):
        for x in o.values():
            yield from walk_numbers(x)
    elif isinstance(o, list):
        for x in o:
            yield from walk_numbers(x)
    elif isinstance(o, (int, float)) and not isinstance(o, bool):
        yield o


def state_numbers(covered_global):
    """A hand-written state body may only quote numbers found in that state's tax
    data, the engine's take-home figures for it, federal data, or a global claim."""
    errors = []
    fed = set().union(*(fmt_forms(v) for v in walk_numbers(
        json.loads((ROOT / "src/data/tax-year-2026/federal.json").read_text()))))
    th = json.loads((ROOT / "data/takehome-95k.json").read_text())["states"]
    for f in sorted((ROOT / "content/bodies").glob("tools__paycheck-calculator__*.md")):
        slug = f.stem.split("__")[2]
        data = json.loads((ROOT / f"src/data/tax-year-2026/states/{slug}.json").read_text())
        allowed = set(fed) | set(covered_global)
        for v in walk_numbers({k: v for k, v in data.items() if k != "provenance"}):
            allowed |= fmt_forms(v)
        row = th.get(slug, {})
        for v in walk_numbers(row):
            allowed |= fmt_forms(v)
        if row:
            for n in (26, 24, 12, 52):
                allowed |= fmt_forms(row["takeHome"] / n)
            # the effective state rate, derived from the engine's own outputs
            allowed |= fmt_forms(round(row["stateTax"] / row["gross"] * 100, 1))
        allowed |= {str(data.get("taxYear", "")), "26", "24", "12", "52"}
        for tok in tokens(f.read_text()):
            if tok not in allowed:
                errors.append(f"state body {slug}: '{tok}' matches nothing in its dataset, "
                              "the engine's figures for it, federal data, or a global claim")
    return errors


def metro_numbers(covered_global):
    """A metro body may only quote numbers from its own BEA/HUD record, the engines'
    household figures for it (data/metro-figures.json), its state's take-home
    figures, federal data, or a global claim."""
    errors = []
    figs = json.loads((ROOT / "data/metro-figures.json").read_text())["metros"] \
        if (ROOT / "data/metro-figures.json").exists() else {}
    th = json.loads((ROOT / "data/takehome-95k.json").read_text())["states"]
    fed = set().union(*(fmt_forms(v) for v in walk_numbers(
        json.loads((ROOT / "src/data/tax-year-2026/federal.json").read_text()))))
    # Comparing a metro with its neighbours is the point of the page, so every
    # metro's rents and price levels may be quoted on every metro page.
    siblings = set()
    for p in (ROOT / "src/data").glob("cost-of-living-*/us/*.json"):
        r = json.loads(p.read_text())
        for v in walk_numbers({"i": r.get("indices"), "r": r.get("referenceRent")}):
            siblings |= fmt_forms(v) | {f"{v:.1f}"}
    # Drafts are held to the same standard as published bodies: a number that is
    # wrong in a draft is wrong the day it is promoted.
    metro_files = sorted((ROOT / "content/bodies").glob("cost-of-living__*.md")) + \
        sorted((ROOT / "content/drafts").glob("cost-of-living__*.md"))
    for f in metro_files:
        slug = f.stem.split("__")[1]
        rec_path = next((ROOT / "src/data").glob(f"cost-of-living-*/us/{slug}.json"), None)
        if rec_path is None:
            errors.append(f"metro body {slug}: no dataset")
            continue
        rec = json.loads(rec_path.read_text())
        allowed = set(fed) | set(covered_global) | siblings
        for v in walk_numbers({k: v for k, v in rec.items() if k != "sources"}):
            allowed |= fmt_forms(v)
        fig = figs.get(slug, {})
        for v in walk_numbers(fig):
            allowed |= fmt_forms(v)
        for scen in ("single", "family"):
            s = fig.get(scen)
            if s:
                allowed |= fmt_forms(s["monthlyTotal"] * 12)
                allowed |= fmt_forms(round(s["monthlyRent"] / s["monthlyTotal"] * 100))
        # index gaps from 100, as copy states them ("1.9 points below average")
        for v in (rec.get("indices") or {}).values():
            allowed |= fmt_forms(round(abs(v - 100), 1)) | fmt_forms(round(v, 1))
            # index levels are quoted as plain numbers ("98.1", "1.9 points")
            allowed |= {f"{v:.1f}", f"{abs(v - 100):.1f}"}
        row = th.get(rec.get("stateSlug"), {})
        for v in walk_numbers(row):
            allowed |= fmt_forms(v)
        # the state's own rates and allowances, which the tax section names
        st_path = ROOT / f"src/data/tax-year-2026/states/{rec.get('stateSlug')}.json"
        if st_path.exists():
            st = json.loads(st_path.read_text())
            for v in walk_numbers({k: v for k, v in st.items()
                                   if k not in ("provenance", "verified")}):
                allowed |= fmt_forms(v)
        allowed |= {"100", str(rec.get("dataYear", "")), str(rec.get("fmrYear", "")), "2026",
                    "1", "2", "4"}
        for tok in tokens(f.read_text()):
            if tok not in allowed:
                errors.append(f"metro body {slug}: '{tok}' matches nothing in its BEA/HUD record, "
                              "the engines' figures for it, its state's figures or a global claim")
    return errors


def main():
    reg = json.loads((ROOT / "data/claims.json").read_text())
    covered = collections.defaultdict(set)   # slug or "*" -> tokens
    for c in reg["claims"]:
        for scope in (c["scope"] if isinstance(c["scope"], list) else [c["scope"]]):
            for t in c["tokens"]:
                covered[scope].add(t)

    inventory = collections.defaultdict(set)
    errors = []
    for slug, kind, text in sources():
        for tok in tokens(text):
            inventory[slug].add(tok)
            if tok not in covered["*"] and tok not in covered[slug]:
                errors.append(f"{slug} ({kind}): '{tok}' is not in data/claims.json")

    errors += state_numbers(covered["*"])
    errors += metro_numbers(covered["*"])

    if "--inventory" in sys.argv:
        for slug in sorted(inventory):
            print(slug, sorted(inventory[slug]))
        return 0

    # stale entries: a registered token no page uses any more
    used = set().union(*inventory.values())
    stale = [f"{c['id']}: {t}" for c in reg["claims"] for t in c["tokens"] if t not in used]

    pending = [c for c in reg["claims"] if c.get("status") != "verified"]
    for e in sorted(set(errors)):
        print("ERROR ", e)
    for s in stale:
        print("warn   registered but unused —", s)
    if pending:
        print(f"\nlaunch checklist — {len(pending)} claim(s) to check against the source:")
        for c in pending:
            print(f"  [{c['basis']}] {c['id']}: {c['means']}  <- {c['reference']}")
    n = sum(len(v) for v in inventory.values())
    print(f"\n{n} numeric tokens across {len(inventory)} tools · "
          f"{len(reg['claims'])} claims · {len(set(errors))} unregistered · "
          f"{len(pending)} awaiting source check")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
