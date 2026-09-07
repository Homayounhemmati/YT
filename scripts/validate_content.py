#!/usr/bin/env python3
"""Measure the uniqueness budget from spec section 6-10-4.

Section 6-10-4 sets numeric anti-doorway thresholds and says a script enforces
them. That script did not exist, which meant the one standard most likely to sink
a programmatic site was the one standard nothing checked.

It measures what actually exists. Today that is the generated scaffolding —
titles, metas, headings, FAQ — because no body copy is written yet. That is the
useful time to measure it: if the scaffolding for 51 pages is already 90% identical,
no amount of body copy written later fixes the shape of the thing.

Point --bodies at a directory of {slug}.md files once body copy exists, and the
same thresholds apply to the real page.
"""
import argparse
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORD = re.compile(r"[a-z0-9$%.,-]+")

# Only entity-driven templates must carry their own numbers. A tool page's
# numbers come from the calculator at runtime, not from its copy.
ENTITY_TEMPLATES = {"StateTaxPage", "PlacePage"}
PAGES_DOC = {}


def words(text):
    return WORD.findall(text.lower())


def page_text(entry):
    """Every human-visible string the generated spec defines for this page."""
    parts = [entry.get("title", ""), entry.get("metaDescription", ""),
             entry.get("h1", "")]
    parts += entry.get("h2Outline", [])
    for f in entry.get("faq", []):
        parts += [f.get("question", ""), f.get("answer", "")]
    return " ".join(p for p in parts if p)


def keyword_coverage(entry, pages_doc, body):
    """A page can be perfectly unique and still not target its own keyword.
    The uniqueness rules push toward varied phrasing; nothing pushed back, and the
    first four pilot bodies hit 0 of 5 cluster variants as a result."""
    template_path = {"StateTaxPage": "/state-taxes/{state}",
                     "PlacePage": "/cost-of-living/{metro}"}.get(entry["template"])
    if not template_path:
        return None
    spec = next((p for p in pages_doc["pages"] if p["path"] == template_path), None)
    cluster = (spec or {}).get("cluster") or {}
    variants = cluster.get("variants", [])
    if not variants:
        return None

    # Resolve {state}/{metro} from the page's own H1, which always names the entity.
    name = entry["h1"].replace(" Income Tax Calculator", "") \
                      .replace("Cost of Living in ", "")
    low = body.lower()
    hits = [v for v in variants
            if v.replace("{state}", name).replace("{metro}", name).lower() in low]
    return {"name": name, "hits": hits, "total": len(variants)}


def analyse(group_name, entries, thresholds, body_lookup=None):
    """A token is boilerplate if it appears on most pages of the template."""
    texts = {}
    for e in entries:
        text = page_text(e)
        if body_lookup:
            extra = body_lookup.get(e["path"])
            if extra:
                text += " " + extra
        texts[e["path"]] = words(text)

    n = len(texts)
    if n < 2:
        return [], []

    doc_freq = collections.Counter()
    for toks in texts.values():
        doc_freq.update(set(toks))

    # present on 80%+ of the template's pages = shared furniture
    shared = {t for t, c in doc_freq.items() if c >= 0.8 * n}

    errors, warnings, rows = [], [], []
    for path, toks in sorted(texts.items()):
        if not toks:
            errors.append(f"{path}: no text at all")
            continue
        unique = [t for t in toks if t not in shared]
        ratio = len(unique) / len(toks)
        numbers = len([t for t in toks if re.search(r"\d", t)])
        entry = next(e for e in entries if e["path"] == path)
        faq_with_numbers = sum(
            1 for f in entry.get("faq", []) if re.search(r"\d", f.get("answer", "")))
        pending = sum(
            1 for f in entry.get("faq", []) if "PENDING" in f.get("answer", ""))

        rows.append((path, len(toks), ratio, numbers, faq_with_numbers, pending))

        if body_lookup and body_lookup.get(path):
            cov = keyword_coverage(entry, PAGES_DOC, body_lookup[path])
            if cov is not None and len(cov["hits"]) < thresholds["minVariantsInBody"]:
                errors.append(
                    f"{path}: body contains {len(cov['hits'])} of {cov['total']} "
                    f"cluster variants, under {thresholds['minVariantsInBody']} — "
                    "unique copy that never uses its own target phrasing (9-2-1)")

        if ratio < thresholds["minUniqueRatio"]:
            msg = (f"{path}: {ratio:.0%} of its words are unique to it, under "
                   f"{thresholds['minUniqueRatio']:.0%} — the rest is template "
                   f"furniture shared with the other {n - 1} {group_name} pages")
            # The threshold judges the finished page. Before body copy exists there
            # is nothing to judge, so a thin scaffolding is a warning about what the
            # body must carry, not a failure.
            (errors if body_lookup else warnings).append(msg)
        if (group_name in ENTITY_TEMPLATES
                and numbers < thresholds["minEntityNumbers"]):
            errors.append(
                f"{path}: only {numbers} numeric tokens — an entity page with no "
                "numbers of its own is a template with a name substituted in")
    return errors, warnings, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bodies", help="directory of {slug}.md body copy, once written")
    ap.add_argument("--pilot", action="store_true",
                    help="compare only the pages that have body copy, against each "
                         "other. Measuring a few written pages against many unwritten "
                         "ones scores them falsely high, because their body words are "
                         "trivially absent from pages that have no body")
    ap.add_argument("--strict", action="store_true",
                    help="also fail on unresolved PENDING_ placeholders")
    args = ap.parse_args()

    global PAGES_DOC
    pages_doc = json.loads((ROOT / "data/pages.json").read_text())
    PAGES_DOC = pages_doc
    gen = json.loads((ROOT / "data/onpage.generated.json").read_text())
    budget = pages_doc.get("contentBudget", {})
    thresholds = {
        "minUniqueRatio": budget.get("minUniqueRatio", 0.40),
        "minEntityNumbers": budget.get("minEntityNumbers", 3),
        "minVariantsInBody": budget.get("minVariantsInBody", 2),
    }

    body_lookup = {}
    if args.bodies:
        d = pathlib.Path(args.bodies)
        for f in d.glob("*.md"):
            body_lookup["/" + f.stem.replace("__", "/")] = f.read_text()
        print(f"loaded {len(body_lookup)} body files from {d}\n")

    groups = collections.defaultdict(list)
    for e in gen["pages"]:
        if args.pilot and e["path"] not in body_lookup:
            continue
        groups[e["template"]].append(e)
    if args.pilot:
        print(f"PILOT: comparing only the {sum(len(v) for v in groups.values())} "
              "pages that have body copy, against each other.\n")

    all_errors, all_warnings, pending_total = [], [], 0
    print(f"{'template':<16}{'pages':>7}{'median unique':>15}{'worst':>9}"
          f"{'numbers':>9}{'FAQ w/ num':>12}")
    for name, entries in sorted(groups.items()):
        if len(entries) < 2:
            continue
        errs, warns, rows = analyse(name, entries, thresholds, body_lookup or None)
        all_errors += errs
        all_warnings += warns
        if not rows:
            continue
        ratios = sorted(r[2] for r in rows)
        median = ratios[len(ratios) // 2]
        worst = ratios[0]
        med_nums = sorted(r[3] for r in rows)[len(rows) // 2]
        med_faq = sorted(r[4] for r in rows)[len(rows) // 2]
        pending_total += sum(r[5] for r in rows)
        print(f"{name:<16}{len(entries):>7}{median:>14.0%}{worst:>9.0%}"
              f"{med_nums:>9}{med_faq:>12}")

    print()
    for e in all_errors[:20]:
        print(f"ERROR  {e}")
    if len(all_errors) > 20:
        print(f"       ... and {len(all_errors) - 20} more")
    if all_warnings:
        groups_short = collections.Counter(w.split(":")[0].rsplit("/", 1)[0]
                                           for w in all_warnings)
        for prefix, count in groups_short.most_common():
            print(f"warn   {count} pages under the uniqueness threshold on "
                  f"scaffolding alone ({prefix}/...) — see the body-copy "
                  "requirement below")

    if pending_total:
        msg = (f"{pending_total} FAQ answers are still PENDING_ placeholders "
               "(section 9-3-9)")
        if args.strict:
            print(f"ERROR  {msg}")
            all_errors.append(msg)
        else:
            print(f"warn   {msg}")

    print(f"\n{len(gen['pages'])} pages measured · {len(all_errors)} errors · "
          f"{len(all_warnings)} warnings")
    if not args.bodies:
        print("\nMeasuring generated scaffolding only — no body copy exists yet.")
        for name, entries in sorted(groups.items()):
            if name not in ENTITY_TEMPLATES or len(entries) < 2:
                continue
            scaffold = sum(len(words(page_text(e))) for e in entries) // len(entries)
            _, _, rows = analyse(name, entries, thresholds)
            ratios = sorted(r[2] for r in rows)
            cur = ratios[len(ratios) // 2]
            for body in (900, 1200, 1400):
                need = (thresholds["minUniqueRatio"] * (scaffold + body)
                        - cur * scaffold) / body
                print(f"  {name}: {scaffold}-word scaffolding at {cur:.0%} unique "
                      f"+ {body} words of body -> body must be {need:.0%} unique")
        print("\nRe-run with --bodies once copy exists; the threshold then fails "
              "the build.")
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
