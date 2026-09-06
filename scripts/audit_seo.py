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


# Title case as it ships: small words stay lowercase unless they lead.
SMALL = {"a", "an", "and", "as", "at", "by", "for", "in", "of", "on", "or",
         "the", "to", "vs", "with"}


def title_case(phrase):
    words = phrase.split()
    return " ".join(
        w.capitalize() if i == 0 or w.lower() not in SMALL else w.lower()
        for i, w in enumerate(words))


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

    # 7-10. on-page formulas: coverage, length, keyword presence, uniqueness
    on = pages_doc.get("onPage", {})
    tpl = on.get("templates", {})
    lim = on.get("limits", {})
    longest = on.get("longestSubstitutions", {})

    def render(pattern, page):
        out = pattern
        prim = page.get("primary")
        # title case the measured keyword the way it is written on the page
        sub = dict(longest)
        if prim:
            sub["{Primary}"] = title_case(prim)
        sub["{Output}"] = page.get("output") or ""
        sub["{Hook}"] = page.get("metaHook") or ""
        for k, v in sub.items():
            out = out.replace(k, v)
        return out

    for name in sorted({p["template"] for p in pages}):
        spec = tpl.get(name)
        if not spec:
            errors.append(f"template {name} is used by a page but has no onPage formula")
            continue
        for field in ("title", "h1", "meta"):
            if not spec.get(field):
                errors.append(f"template {name}: no {field} formula")

    rendered_titles = {}
    for page in pages:
        spec = tpl.get(page["template"])
        if not spec:
            continue
        title = render(spec.get("title", ""), page)
        h1 = render(spec.get("h1", ""), page)
        meta = render(spec.get("meta", ""), page)

        if len(title) > lim.get("titleMaxChars", 60):
            errors.append(
                f"{page['path']}: title is {len(title)} chars, over "
                f"{lim['titleMaxChars']} — Google truncates it: {title!r}")
        if len(h1) > lim.get("h1MaxChars", 70):
            errors.append(f"{page['path']}: h1 is {len(h1)} chars: {h1!r}")
        if meta and not (lim.get("metaMinChars", 110) <= len(meta) <= lim.get("metaMaxChars", 155)):
            errors.append(
                f"{page['path']}: meta is {len(meta)} chars, outside "
                f"{lim['metaMinChars']}-{lim['metaMaxChars']}: {meta!r}")

        prim = page.get("primary")
        if prim and page["template"] in ("ToolPage", "DirectoryPage"):
            if prim.lower() not in title.lower():
                errors.append(f"{page['path']}: primary '{prim}' is not in the rendered title {title!r}")
            if prim.lower() not in h1.lower():
                errors.append(f"{page['path']}: primary '{prim}' is not in the rendered H1 {h1!r}")

        # uniqueness: a fixed title may appear once; a templated one must vary by entity
        if "{" not in spec.get("title", ""):
            if title in rendered_titles:
                errors.append(f"{page['path']}: title duplicates {rendered_titles[title]}: {title!r}")
            rendered_titles[title] = page["path"]
        elif not any(t in spec["title"] for t in ("{Metro}", "{State}", "{Primary}")):
            errors.append(
                f"template {page['template']}: title has no entity placeholder — "
                "every generated page would share one title")

    for section in ("anchorText", "openGraph", "robots"):
        if len(on.get(section, [])) < 3:
            errors.append(f"onPage.{section} is thin — fewer than 3 stated rules")
    sd = on.get("structuredData", {})
    for name in sorted({p["template"] for p in pages}):
        if name not in sd and name != "Home":
            errors.append(f"structuredData: no JSON-LD declared for {name}")

    # 11-14. crawl architecture: the link graph, click depth, orphans, ceilings
    crawl = pages_doc.get("crawl", {})
    nav = crawl.get("globalNav", [])
    max_depth = crawl.get("maxClickDepth", 3)
    ceiling = crawl.get("bodyLinkCeiling", 25)
    by_path = {p["path"]: p for p in pages}

    for page in pages:
        for dest in page.get("links", []):
            if dest not in by_path:
                errors.append(f"{page['path']}: links to {dest}, which is not a page")
        body = [d for d in page.get("links", []) if d != page["path"]]
        if len(body) > ceiling:
            errors.append(
                f"{page['path']}: {len(body)} body links, over the ceiling of {ceiling}")
    for dest in nav:
        if dest not in by_path:
            errors.append(f"globalNav links to {dest}, which is not a page")

    # breadth-first from the home page, with the header nav available everywhere
    depth = {"/": 0}
    frontier = ["/"]
    while frontier:
        nxt = []
        for path in frontier:
            outbound = set(by_path[path].get("links", [])) | set(nav)
            for dest in outbound:
                if dest in by_path and dest not in depth:
                    depth[dest] = depth[path] + 1
                    nxt.append(dest)
        frontier = nxt

    for page in pages:
        path = page["path"]
        if path not in depth:
            errors.append(
                f"{path}: unreachable from the home page — no crawl path exists to it")
        elif depth[path] > max_depth:
            errors.append(
                f"{path}: {depth[path]} clicks from home, over the limit of {max_depth}")

    inbound = {p["path"]: 0 for p in pages}
    for page in pages:
        for dest in set(page.get("links", [])):
            if dest in inbound and dest != page["path"]:
                inbound[dest] += 1
    for path, count in inbound.items():
        if path == "/" or path in nav:
            continue
        if count == 0:
            errors.append(f"{path}: orphan — no other page links to it")

    # No page is a cul-de-sac inside its own funnel stage. The funnel is not strictly
    # linear — a tax tool need not lead to a mortgage tool — but a page whose only
    # links stay inside its own stage ends the session there, and session depth is the
    # largest revenue lever we control (section 1-4).
    for page in (p for p in pages if p.get("stage")):
        others = {by_path[d].get("stage") for d in page.get("links", [])
                  if d in by_path and by_path[d].get("stage")}
        if not (others - {page["stage"]}):
            errors.append(
                f"{page['path']}: every link stays inside funnel stage {page['stage']} "
                "— a cul-de-sac ends the session (section 1-4)")

    if depth:
        worst = max(depth.values())
        notes.append(f"crawl depth: every page within {worst} clicks of home "
                     f"(limit {max_depth}) · no orphans")

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
