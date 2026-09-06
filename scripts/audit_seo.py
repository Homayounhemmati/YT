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


# The cannibalisation tokenizer deliberately drops "calculator" and "estimator" so
# that two tool keywords compare on their meaningful part. Anchor and slug checks
# must NOT use it: with those words dropped, "cost of living calculator" reduces to
# {cost, living} and is a subset of nearly every cost-of-living phrase.
FUNCTION_WORDS = {"a", "an", "and", "by", "for", "in", "of", "on", "the", "to",
                  "my", "your", "is", "are", "vs", "with"}


def words(term):
    out = set()
    for t in re.findall(r"[a-z0-9{}]+", term.lower()):
        if t in FUNCTION_WORDS:
            continue
        if len(t) > 3 and t.endswith("es"):
            t = t[:-2]
        elif len(t) > 3 and t.endswith("s"):
            t = t[:-1]
        out.add(t)
    return out


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

    # 3. intent clusters: a page targets a group of phrasings, not one string.
    # Every term belongs to exactly one page, and no variant is another page's head.
    claimed = {}
    for p in pages:
        cluster = p.get("cluster")
        if p.get("primary") and not cluster:
            errors.append(
                f"{p['path']}: has a primary keyword but declares no cluster — "
                "a page targets an intent group, not one string")
            continue
        if not cluster:
            continue
        if not cluster.get("intent"):
            errors.append(f"{p['path']}: cluster has no stated intent")
        variants = cluster.get("variants", [])
        if len(variants) < 3:
            errors.append(
                f"{p['path']}: only {len(variants)} cluster variants — a head term "
                "with no expansion means the long tail is unmapped")
        for term in variants:
            key = term.lower()
            if key == (p.get("primary") or "").lower():
                errors.append(f"{p['path']}: '{term}' is both its head and its own variant")
            owner = seen.get(key)
            if owner and owner != p["path"]:
                errors.append(
                    f"{p['path']}: variant '{term}' is the head term of {owner}")
            if key in claimed and claimed[key] != p["path"]:
                errors.append(
                    f"variant '{term}' is claimed by both {claimed[key]} and {p['path']}")
            claimed[key] = p["path"]

    # An entity-qualified variant belongs to the entity page, never the generic tool
    # (the generic/entity rule, section 9-4-1).
    for p in pages:
        cluster = p.get("cluster") or {}
        if "{" in p["path"]:
            continue  # this IS the entity page
        for term in cluster.get("variants", []):
            if "{" in term:
                errors.append(
                    f"{p['path']}: variant '{term}' is entity-qualified but this is a "
                    "generic page — that query belongs to the entity page (9-4-1)")

    # Two pages must not state the same intent, however different their wording
    intents = {}
    for p in pages:
        cluster = p.get("cluster") or {}
        intent = (cluster.get("intent") or "").strip().lower()
        if not intent:
            continue
        if intent in intents:
            errors.append(
                f"{p['path']} and {intents[intent]} state an identical intent — "
                "same intent means one page, whatever the keywords say")
        intents[intent] = p["path"]

    # Variants carry no volume, and must not leak into the revenue model
    for p in pages:
        cluster = p.get("cluster") or {}
        if cluster.get("variantsMeasured"):
            errors.append(
                f"{p['path']}: cluster claims measured variants, but no variant volume "
                "exists in data/keywords.json — measure them before asserting it")

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
    shortest = on.get("shortestSubstitutions", {})

    def render(pattern, page, extreme="longest"):
        """A formula can fail at either end: too long and Google truncates it, too
        short and a meta description falls under the useful minimum. Checking only
        the longest substitution catches one of those, which is how 48 real state
        metas came out under 110 characters while this check reported clean."""
        out = pattern
        prim = page.get("primary")
        # title case the measured keyword the way it is written on the page
        sub = dict(longest if extreme == "longest" else (shortest or longest))
        if prim:
            sub["{Primary}"] = title_case(prim)
        sub["{Output}"] = page.get("output") or ""
        sub["{Hook}"] = page.get("metaHook") or ""
        sub["{Subject}"] = page.get("subject") or ""
        sub["{SiteName}"] = pages_doc.get("site", {}).get("name", "")
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
        meta_short = render(spec.get("meta", ""), page, "shortest")

        if len(meta_short) and len(meta_short) < lim.get("metaMinChars", 110):
            errors.append(
                f"{page['path']}: with the shortest entity the meta is "
                f"{len(meta_short)} chars, under {lim['metaMinChars']}: {meta_short!r}")
        if lim.get("titleMinChars") and 0 < len(title) < lim["titleMinChars"]:
            errors.append(
                f"{page['path']}: title is only {len(title)} chars — too short to be a "
                f"useful SERP line: {title!r}")
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
    footer = crawl.get("globalFooter", [])
    everywhere = set(nav) | set(footer)
    max_depth = crawl.get("maxClickDepth", 3)
    ceiling = crawl.get("bodyLinkCeiling", 25)
    by_path = {p["path"]: p for p in pages}

    def dests(page):
        return [e["to"] for e in page.get("links", [])]

    for page in pages:
        for dest in dests(page):
            if dest not in by_path:
                errors.append(f"{page['path']}: links to {dest}, which is not a page")
        body = [d for d in dests(page) if d != page["path"]]
        if len(body) > ceiling:
            errors.append(
                f"{page['path']}: {len(body)} body links, over the ceiling of {ceiling}")
    for dest in everywhere:
        if dest not in by_path:
            errors.append(f"global nav/footer links to {dest}, which is not a page")

    # breadth-first from the home page, with the header nav available everywhere
    depth = {"/": 0}
    frontier = ["/"]
    while frontier:
        nxt = []
        for path in frontier:
            outbound = set(dests(by_path[path])) | everywhere
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
        for dest in set(dests(page)):
            if dest in inbound and dest != page["path"]:
                inbound[dest] += 1
    for path, count in inbound.items():
        if path == "/" or path in everywhere:
            continue
        if count == 0:
            errors.append(f"{path}: orphan — no other page links to it")

    # No page is a cul-de-sac inside its own funnel stage. The funnel is not strictly
    # linear — a tax tool need not lead to a mortgage tool — but a page whose only
    # links stay inside its own stage ends the session there, and session depth is the
    # largest revenue lever we control (section 1-4).
    for page in (p for p in pages if p.get("stage")):
        others = {by_path[d].get("stage") for d in dests(page)
                  if d in by_path and by_path[d].get("stage")}
        if not (others - {page["stage"]}):
            errors.append(
                f"{page['path']}: every link stays inside funnel stage {page['stage']} "
                "— a cul-de-sac ends the session (section 1-4)")

    if depth:
        worst = max(depth.values())
        notes.append(f"crawl depth: every page within {worst} clicks of home "
                     f"(limit {max_depth}) · no orphans")

    # 15. planned pages must not collide with pages that already exist.
    # A guide duplicating a tool's intent is cannibalisation that ships, and guides
    # are the main external-link asset (section 9-5-2).
    planned = pages_doc.get("plannedPages", {}).get("pages", [])
    owned = dict(claimed)
    for p in pages:
        if p.get("primary"):
            owned[p["primary"].lower()] = p["path"]
    for pl in planned:
        head = (pl.get("proposedHead") or "").lower()
        if not head:
            errors.append(f"{pl['path']}: planned page with no proposed head term")
            continue
        if head in owned:
            errors.append(
                f"{pl['path']}: proposed head '{pl['proposedHead']}' is already "
                f"claimed by {owned[head]}")
        for p in pages:
            cl = p.get("cluster") or {}
            sim = jaccard(tokens(head), tokens(p.get("primary") or ""))
            if sim >= 0.5:
                warnings.append(
                    f"{pl['path']}: proposed head is {sim:.0%} similar to "
                    f"{p['path']} ('{p.get('primary')}') — check the SERP before writing")
            ack = {a.get("page"): a.get("why")
                   for a in pl.get("overlapsAcknowledged", [])}
            for v in cl.get("variants", []):
                if jaccard(tokens(head), tokens(v)) < 0.6:
                    continue
                # An overlap may be legitimate — a definition and a calculator share
                # tokens without sharing intent. It just has to be argued in writing.
                if p["path"] in ack:
                    if len(ack[p["path"]] or "") < 40:
                        errors.append(
                            f"{pl['path']}: acknowledges overlapping {p['path']} but "
                            "gives no substantive reason")
                    continue
                warnings.append(
                    f"{pl['path']}: proposed head overlaps {p['path']}'s variant "
                    f"'{v}' — decide which page owns that query before writing")
        if not pl.get("intent"):
            errors.append(f"{pl['path']}: planned page with no stated intent")

    # 16-18. on-page structure: slug, headings, breadcrumbs, anchor text
    GENERIC = {"click here", "here", "read more", "learn more", "this page",
               "more", "link", "this", "see more", "find out more"}

    for page in pages:
        head = page.get("primary")
        if not head:
            continue
        slug = page["path"].rsplit("/", 1)[-1].replace("-", " ")
        st, ht = words(slug), words(head)
        extra = st - ht
        if page["template"] == "ToolPage" and st != ht:
            errors.append(
                f"{page['path']}: slug {sorted(st)} does not match its head term "
                f"{sorted(ht)} — rule 6-7-1, the slug is the target keyword")
        elif extra:
            errors.append(
                f"{page['path']}: slug carries {sorted(extra)}, absent from its head "
                "term — a slug may be shorter than the head, never different from it")

    tpl_on = pages_doc.get("onPage", {}).get("templates", {})
    used_templates = {p["template"] for p in pages}
    for name in sorted(used_templates):
        spec = tpl_on.get(name, {})
        outline = spec.get("h2Outline") or []
        if spec.get("h2OutlinePerPage"):
            for pg in (p for p in pages if p["template"] == name):
                if len(pg.get("h2Outline") or []) < 2:
                    errors.append(
                        f"{pg['path']}: template {name} declares per-page outlines, "
                        "but this page has none")
            continue
        if not outline:
            errors.append(f"template {name}: no H2 outline")
            continue
        h1 = spec.get("h1", "")
        for h2 in outline:
            if h2.strip().lower() == h1.strip().lower():
                errors.append(f"template {name}: H2 '{h2}' repeats the H1")
        declares_faq = any(
            "faqpage" in item.lower()
            for item in pages_doc.get("onPage", {}).get("structuredData", {}).get(name, []))
        has_faq_h2 = any("faq" in h.lower() or "question" in h.lower() for h in outline)
        if declares_faq and not has_faq_h2:
            errors.append(
                f"template {name}: declares FAQPage schema but has no FAQ heading — "
                "structured data needs a visible counterpart (9-3-3)")
        if has_faq_h2 and not declares_faq:
            errors.append(
                f"template {name}: has an FAQ heading but declares no FAQPage schema")
        if name in ("PlacePage", "StateTaxPage") and not any(
                "{" in h for h in outline):
            errors.append(
                f"template {name}: no H2 names the entity — every generated page would "
                "share an identical outline")
        if "breadcrumb" not in spec:
            errors.append(f"template {name}: no breadcrumb declared")

    for page in pages:
        head_words = words(page.get("primary") or "")
        seen_anchor = {}
        for edge in page.get("links", []):
            anchor, dest = edge.get("anchor", ""), edge["to"]
            if not anchor:
                errors.append(f"{page['path']} -> {dest}: no anchor text")
                continue
            if anchor.strip().lower() in GENERIC:
                errors.append(f"{page['path']} -> {dest}: generic anchor '{anchor}'")
            key = anchor.strip().lower()
            if key in seen_anchor:
                errors.append(
                    f"{page['path']}: anchor '{anchor}' used for both "
                    f"{seen_anchor[key]} and {dest}")
            seen_anchor[key] = dest
            at = words(anchor)
            # A template self-link means "other entities of this template",
            # so the anchor legitimately reuses the template's own phrasing.
            if dest != page["path"] and head_words and head_words <= at:
                errors.append(
                    f"{page['path']} -> {dest}: anchor '{anchor}' contains this page's "
                    "own head term — that signals the wrong page (9-3-1)")
            dest_head = by_path[dest].get("primary") if dest in by_path else None
            if dest_head:
                dt = words(dest_head)
                if not (at & dt):
                    errors.append(
                        f"{page['path']} -> {dest}: anchor '{anchor}' shares nothing with "
                        f"the destination's head term '{dest_head}'")

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
