#!/usr/bin/env python3
"""Resolve the on-page formulas into concrete values, one entry per generated page.

The formulas in data/pages.json describe what every page must contain. Base44 needs
those values *entered*, per page. Typing 51 titles by hand is 51 chances to drift
from the formula, and drift is invisible until a rankings report shows it — so the
values are produced here, validated against the same limits scripts/audit_seo.py
enforces, and imported rather than typed (rule 3-7-6).

Output:
  data/onpage.generated.json   machine-readable, for import
  docs/onpage-spec.md          human-readable, for review

Metro pages appear once the cost-of-living dataset exists (section 13-6).
"""
import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SMALL = {"a", "an", "and", "as", "at", "by", "for", "in", "of", "on", "or",
         "the", "to", "vs", "with"}


def title_case(phrase):
    return " ".join(w.capitalize() if i == 0 or w.lower() not in SMALL else w.lower()
                    for i, w in enumerate(phrase.split()))


def money(n):
    return f"${n:,.0f}"


def rate(r):
    return f"{r:g}"


def rate_sentence(st):
    if st["structure"] == "none":
        return f"{st['name']} levies no individual income tax on earned income."
    if st["structure"] == "flat":
        return (f"{st['name']} taxes income at a flat {rate(st['flatRate'])}%, "
                "the same rate at every income level.")
    br = st["brackets"].get("single") or next(iter(st["brackets"].values()))
    return (f"{st['name']} has {len(br)} tax brackets for a single filer, "
            f"from {rate(br[0]['rate'])}% to {rate(br[-1]['rate'])}%.")


def top_rate(st):
    if st["structure"] == "flat":
        return rate(st["flatRate"]), "every dollar of taxable income"
    br = st["brackets"].get("single") or next(iter(st["brackets"].values()))
    top = br[-1]
    return rate(top["rate"]), money(top["from"])


def local_answer(st):
    note = st.get("localTaxNote")
    if note:
        return note
    return (f"No. {st['name']} has no local income tax on top of the state rate, "
            "so the figure above is the whole state-level picture.")


TAKEHOME = {}
_th = ROOT / "data/takehome-95k.json"
if _th.exists():
    TAKEHOME = json.loads(_th.read_text())["states"]


def takehome_answer(st):
    """Computed by the engine, not estimated. scripts/compute_takehome.ts produces
    data/takehome-95k.json; if it has not been run, the placeholder stays visible
    rather than a plausible number being written (rule 5-3)."""
    row = TAKEHOME.get(st["slug"])
    if not row:
        return (f"PENDING_ENGINE: run scripts/compute_takehome.ts to resolve "
                f"{st['name']}.")
    keep = f"${row['takeHome']:,.0f}"
    rate = f"{row['effectiveRate']:.1f}%"
    if st["structure"] == "none":
        return (f"About {keep} of a $95,000 self-employment profit, an effective "
                f"{rate} once federal income tax and the 15.3% self-employment tax "
                f"are taken. There is no {st['name']} state layer to add.")
    state_cost = f"${row['stateTax']:,.0f}"
    return (f"About {keep} of a $95,000 self-employment profit, an effective "
            f"{rate}. Of that, {state_cost} is {st['name']} state tax — the rest is "
            "federal income tax and the 15.3% self-employment tax.")


def federal_only_answer(st):
    """Two FAQ answers on the nine no-tax state pages were byte-identical across all
    nine — the question carried the entity and the answer did not. Section 7-2 exists
    to prevent exactly that, so both now resolve against the engine's per-state figures."""
    row = TAKEHOME.get(st["slug"])
    if not row:
        return f"PENDING_ENGINE: run scripts/compute_takehome.ts to resolve {st['name']}."
    return (f"Federal income tax and, if self-employed, the 15.3% federal "
            f"self-employment tax both apply in full. On $95,000 of self-employment "
            f"profit that is ${row['totalTax']:,.0f} in {st['name']} — an effective "
            f"{row['effectiveRate']:.1f}% with no state layer on top of it.")


def cheaper_answer(st):
    """Per-state, against the worst jurisdiction in the same computed set."""
    row = TAKEHOME.get(st["slug"])
    if not row or not TAKEHOME:
        return f"PENDING_ENGINE: run scripts/compute_takehome.ts to resolve {st['name']}."
    worst = min(TAKEHOME.values(), key=lambda r: r["takeHome"])
    gap = row["takeHome"] - worst["takeHome"]
    return (f"Not automatically. On income tax alone {st['name']} leaves "
            f"${row['takeHome']:,.0f} of a $95,000 profit against "
            f"${worst['takeHome']:,.0f} in {worst['name']}, a gap of ${gap:,.0f} a year. "
            f"But states without an income tax usually recover it through sales and "
            f"property tax, so compare the total a place costs rather than one line of it.")


def _faq_block(ld, faq):
    """The spec's structuredData declares FAQPage for PlacePage and it was never
    emitted. Declared-but-not-generated is the recurring defect in this project:
    the rule reads correct and the output does not carry it."""
    fp = json.loads(json.dumps(ld["FAQPage"]))
    fp["mainEntity"] = [
        {"@type": "Question", "name": a["question"],
         "acceptedAnswer": {"@type": "Answer", "text": a["answer"]}} for a in faq]
    return fp


def _dataset_block(ld, entity_name, data_year, content_updated):
    ds = json.loads(json.dumps(ld["Dataset"]))
    for k, v in ds.items():
        if isinstance(v, str):
            ds[k] = (v.replace("{ENTITY_NAME}", entity_name)
                      .replace("{DATA_YEAR}", str(data_year))
                      .replace("{DATE_MODIFIED}", content_updated))
    ds["isBasedOn"] = ["https://www.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area",
                       "https://www.huduser.gov/portal/datasets/fmr.html"]
    return ds


def _itemlist_block(ld, title, links, origin):
    """DirectoryPage declares ItemList in the spec. A directory whose rows are not
    marked up is a list Google has to infer."""
    il = json.loads(json.dumps(ld["ItemList"]))
    il["name"] = title
    il["numberOfItems"] = len(links)
    il["itemListElement"] = [
        {"@type": "ListItem", "position": i + 1, "name": l["anchor"],
         "url": origin + l["to"]} for i, l in enumerate(links)]
    return il


def _organization_block(ld, origin, site_name, author_name):
    org = json.loads(json.dumps(ld["Organization"]))
    def fill(v):
        return (v.replace("{SITE_NAME}", site_name).replace("{ORIGIN}", origin)
                 .replace("{AUTHOR_NAME}", author_name))
    for k, v in list(org.items()):
        if isinstance(v, str):
            org[k] = fill(v)
        elif isinstance(v, dict):
            org[k] = {kk: (fill(vv) if isinstance(vv, str) else vv) for kk, vv in v.items()}
    return org


# Directories, entity pages and tool pages each declare links to entity templates
# like /cost-of-living/{metro}. Nothing resolved them, so 54 generated pages shipped
# a link to a literal "{metro}" URL — a 404 on every one of them. The three cases are
# genuinely different and each needs its own answer.
ENTITY_FAMILIES = {"{metro}": "/cost-of-living", "{state}": "/state-taxes"}


def resolve_entity_links(links, *, metros, states, state_slug=None, expand=False):
    """`expand` is for a directory, whose link to a template means every row.
    Elsewhere the link resolves to a sibling in the same state where one exists,
    and falls back to the family's directory where none does — never to a token."""
    out = []
    for l in links:
        token = next((k for k in ENTITY_FAMILIES if k in l["to"]), None)
        if token is None:
            out.append(l)
            continue
        rows = metros if token == "{metro}" else states
        if expand:
            for r in rows:
                out.append({"to": l["to"].replace(token, r["slug"]),
                            "anchor": l["anchor"].replace(token, r["display"])})
            continue
        pick = None
        if state_slug:
            same = [r for r in rows if r.get("stateSlug") == state_slug]
            pick = max(same, key=lambda r: r.get("volume", 0)) if same else None
        if pick:
            out.append({"to": l["to"].replace(token, pick["slug"]),
                        "anchor": l["anchor"].replace(token, pick["display"])})
        else:
            directory = ENTITY_FAMILIES[token]
            anchor = ("cost of living by city" if token == "{metro}"
                      else "state income tax rates")
            if not any(o["to"] == directory for o in out):
                out.append({"to": directory, "anchor": anchor})
    seen, deduped = set(), []
    for l in out:
        if l["to"] in seen:
            continue
        seen.add(l["to"])
        deduped.append(l)
    return deduped


def build_state(st, pages_doc, page_spec, tpl, origin, site_name, data_year,
                metros=(), states=()):
    content_updated = pages_doc["site"].get("contentUpdated", str(data_year))
    name = st["name"]
    taxed = st["structure"] != "none"
    key = "StateTaxPage.taxed" if taxed else "StateTaxPage.none"

    def sub(text):
        top, thr = top_rate(st) if taxed else ("0", "n/a")
        return (text.replace("{State}", name)
                    .replace("{RATE_SENTENCE}", rate_sentence(st))
                    .replace("{TOP_RATE}", top)
                    .replace("{TOP_THRESHOLD}", thr)
                    .replace("{LOCAL_ANSWER}", local_answer(st))
                    .replace("{TAKEHOME_ANSWER}", takehome_answer(st))
                    .replace("{FEDERAL_ONLY}", federal_only_answer(st))
                    .replace("{CHEAPER_ANSWER}", cheaper_answer(st))
                    .replace("{year}", str(st["taxYear"])))

    variants = pages_doc["onPage"]["h2Variants"]
    outline = variants.get(f"StateTaxPage.{st['structure']}") or variants[key]

    path = f"/state-taxes/{st['slug']}"
    canonical = origin + path
    title = sub(tpl["title"])
    h1 = sub(tpl["h1"])
    meta = sub(pages_doc["onPage"]["metaFormulas"][key])
    crumbs = [c.replace("{State}", name) for c in tpl["breadcrumb"]]

    faq = [{"question": sub(q), "answer": sub(a)}
           for q, a in pages_doc["onPage"]["faqFormulas"][key]]

    ld = pages_doc["onPage"]["jsonLd"]
    breadcrumb_items = [
        {"@type": "ListItem", "position": i + 1, "name": c,
         **({"item": origin + ("" if i == 0 else "/state-taxes")} if i < len(crumbs) - 1 else {})}
        for i, c in enumerate(crumbs)]

    def fill(block, extra=None):
        out = json.loads(json.dumps(block))
        author = pages_doc["site"].get("author", {}).get("name", "")
        repl = {"{TITLE}": title, "{CANONICAL}": canonical, "{ORIGIN}": origin,
                "{SITE_NAME}": site_name, "{DATE_MODIFIED}": content_updated,
                "{ENTITY_NAME}": name, "{STATE_ABBR}": st["abbr"],
                "{AUTHOR_NAME}": author}
        repl.update(extra or {})

        def walk(o):
            if isinstance(o, dict):
                return {k: walk(v) for k, v in o.items()}
            if isinstance(o, list):
                return [walk(v) for v in o]
            if isinstance(o, str):
                if o == "{BREADCRUMB_ITEMS}":
                    return breadcrumb_items
                if o == "{FAQ_ITEMS}":
                    return [{"@type": "Question", "name": f["question"],
                             "acceptedAnswer": {"@type": "Answer", "text": f["answer"]}}
                            for f in faq]
                for k, v in repl.items():
                    o = o.replace(k, v)
            return o
        return walk(out)

    return {
        "path": path,
        "template": "StateTaxPage",
        "entity": st["slug"],
        "title": title,
        "titleChars": len(title),
        "h1": h1,
        "metaDescription": meta,
        "metaChars": len(meta),
        "canonical": canonical,
        "breadcrumb": crumbs,
        "h2Outline": [sub(h) for h in outline],
        "faq": faq,
        "jsonLd": [fill(ld["BreadcrumbList"]), fill(ld["WebApplication"]),
                   fill(ld["FAQPage"])],
        "internalLinks": resolve_entity_links(
            [{"to": e["to"].replace("{state}", st["slug"]),
              "anchor": e["anchor"].replace("{state}", name)}
             for e in page_spec.get("links", [])],
            metros=metros, states=states, state_slug=st["slug"]),
        "dataVerification": st.get("verification", "unknown"),
        "staleForTargetYear": st.get("staleForTargetYear", False),
    }


def build_metro(m, pages_doc, page_spec, tpl, origin, site_name, data_year, ld,
                takehome, metros_all=(), states_all=()):
    """Everything a place page needs except the numbers BEA and HUD will supply.
    Generated now so the shape is reviewable and the gap is explicit, rather than
    the whole page waiting on a dataset (section 13-6)."""
    content_updated = pages_doc["site"].get("contentUpdated", str(data_year))
    display, state = m["displayName"], m["stateName"]

    def sub(text):
        return (text.replace("{Metro}", display).replace("{State}", state)
                    .replace("{year}", str(data_year)))

    path = f"/cost-of-living/{m['slug']}"
    canonical = origin + path
    title = sub(tpl["title"])
    h1 = sub(tpl["h1"])
    meta = sub(pages_doc["onPage"]["metaFormulas"]["PlacePage"])
    crumbs = [sub(c) for c in tpl["breadcrumb"]]
    outline = [sub(h) for h in tpl["h2Outline"]]

    th = takehome.get(m["stateSlug"], {})
    faq = []
    for q, a in pages_doc["onPage"]["faqFormulas"]["PlacePage"]:
        answer = sub(a)
        if "{INDEX_SENTENCE}" in answer or "{RENT_SENTENCE}" in answer \
                or "{SALARY_SENTENCE}" in answer:
            answer = f"PENDING_DATA: needs BEA/HUD figures for {m['name']} (13-6)."
        elif "{TAX_SENTENCE}" in answer:
            answer = (
                f"Yes. On a $95,000 self-employment profit, a {state} resident keeps "
                f"about ${th.get('takeHome', 0):,.0f} — an effective "
                f"{th.get('effectiveRate', 0):.1f}%. That figure applies anywhere in "
                f"{state}, so it is the same in {display} as in the rest of the state, "
                "and it is the half of the comparison most cost-of-living tools omit."
            ) if th else f"PENDING_ENGINE: {state}"
        elif "{DATA_YEAR}" in answer:
            answer = answer.replace("{DATA_YEAR}", str(data_year))
        faq.append({"question": sub(q), "answer": answer})

    breadcrumb_items = [
        {"@type": "ListItem", "position": i + 1, "name": c,
         **({"item": origin + ("" if i == 0 else "/cost-of-living")}
            if i < len(crumbs) - 1 else {})}
        for i, c in enumerate(crumbs)]
    bc = json.loads(json.dumps(ld["BreadcrumbList"]))
    bc["itemListElement"] = breadcrumb_items
    place = json.loads(json.dumps(ld["Place"]))
    place["name"] = m["name"]
    place["address"]["addressRegion"] = m["name"].rsplit(", ", 1)[-1]

    return {
        "path": path, "template": "PlacePage", "entity": m["slug"],
        "title": title, "titleChars": len(title), "h1": h1,
        "metaDescription": meta, "metaChars": len(meta), "canonical": canonical,
        "breadcrumb": crumbs, "h2Outline": outline, "faq": faq,
        "jsonLd": [bc, place, _faq_block(ld, faq),
                   _dataset_block(ld, m["name"], data_year, content_updated)],
        "internalLinks": resolve_entity_links(
            [{"to": e["to"].replace("{state}", m["stateSlug"])
                           .replace("{metro}", m["slug"]),
              "anchor": e["anchor"].replace("{state}", state)
                                   .replace("{metro}", display)}
             for e in page_spec.get("links", [])],
            metros=metros_all, states=states_all, state_slug=m["stateSlug"]),
        "dataVerification": m["dataStatus"], "staleForTargetYear": False,
    }


def build_static(page, pages_doc, tpl, origin, site_name, data_year, ld,
                 metros=(), states=()):
    content_updated = pages_doc["site"].get("contentUpdated", str(data_year))
    """Resolve a page that has no entity behind it — tools, directories, trust pages.
    Sixteen of these were left to be typed by hand into a dashboard, which is
    sixteen chances to drift from the formula for no reason."""
    name = title_case(page["primary"]) if page.get("primary") else None
    year = str(data_year)

    def sub(text):
        if text is None:
            return None
        out = (text.replace("{year}", year)
                   .replace("{Hook}", page.get("metaHook") or "")
                   .replace("{Subject}", page.get("subject") or "")
                   .replace("{SiteName}", site_name))
        if name:
            out = out.replace("{Primary}", name)
        elif page.get("displayName"):
            out = out.replace("{Primary}", page["displayName"])
        return out

    path = page["path"]
    canonical = origin + ("" if path == "/" else path)
    title = sub(tpl.get("title")) or page.get("displayName") or site_name
    h1 = sub(tpl.get("h1")) or page.get("displayName") or ""
    meta = sub(tpl.get("meta")) or ""
    crumbs = [sub(c) for c in (tpl.get("breadcrumb") or [])]
    outline = page.get("h2Outline") or [sub(h) for h in (tpl.get("h2Outline") or [])]

    # Each intermediate crumb must point at its own ancestor URL. Pointing it at
    # `canonical` makes the parent node identical to the child, which is not a
    # breadcrumb — it is a self-reference Google discards. Derived from the path so
    # it stays correct at any depth and for templates added later.
    segments = [s for s in path.split("/") if s]
    breadcrumb_items = []
    for i, c in enumerate(crumbs):
        node = {"@type": "ListItem", "position": i + 1, "name": c}
        if i < len(crumbs) - 1:
            node["item"] = origin if i == 0 else origin + "/" + "/".join(segments[:i])
        breadcrumb_items.append(node)

    blocks = []
    if crumbs:
        b = json.loads(json.dumps(ld["BreadcrumbList"]))
        b["itemListElement"] = breadcrumb_items
        blocks.append(b)
    if page["template"] in ("ToolPage",):
        w = json.loads(json.dumps(ld["WebApplication"]))
        for k, v in w.items():
            if isinstance(v, str):
                w[k] = (v.replace("{TITLE}", title).replace("{CANONICAL}", canonical)
                         .replace("{ORIGIN}", origin).replace("{SITE_NAME}", site_name)
                         .replace("{DATE_MODIFIED}", content_updated))
        w["publisher"] = {"@type": "Organization", "name": site_name, "url": origin}
        blocks.append(w)

    author_name = pages_doc["site"].get("author", {}).get("name", "")
    # Resolved first: the ItemList marks up the rows a visitor actually sees, so
    # feeding it the raw declared links puts "{metro}" into the structured data.
    resolved_links = resolve_entity_links(
        page.get("links", []), metros=metros, states=states,
        expand=(page["template"] == "DirectoryPage"))
    if page["template"] == "DirectoryPage" and resolved_links:
        blocks.append(_itemlist_block(ld, title, resolved_links, origin))
    # Organization carries the author identity section 7-4 requires for AdSense.
    # It belongs on the home page and on /about, not on every page.
    if path in ("/", "/about") and author_name:
        blocks.append(_organization_block(ld, origin, site_name, author_name))

    # Tool pages carry authored FAQs — one outline across thirteen tools would
    # produce the defect recorded in 20-19, so they are keyed by slug rather than
    # generated from a formula.
    faq = []
    if page["template"] == "ToolPage":
        slug = path.rsplit("/", 1)[-1]
        pairs = pages_doc["onPage"]["faqFormulas"].get("ToolPage", {}).get(slug)
        if not pairs:
            raise SystemExit(f"ERROR  {path}: ToolPage has no FAQ in faqFormulas.ToolPage")
        faq = [{"question": q, "answer": a} for q, a in pairs]
        fp = json.loads(json.dumps(ld["FAQPage"]))
        fp["mainEntity"] = [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]
        blocks.append(fp)
        if "Frequently asked questions" not in outline:
            outline = outline + ["Frequently asked questions"]

    return {
        "path": path,
        "template": page["template"],
        "entity": None,
        "title": title,
        "titleChars": len(title),
        "h1": h1,
        "metaDescription": meta,
        "metaChars": len(meta),
        "canonical": canonical,
        "breadcrumb": crumbs,
        "h2Outline": outline,
        "faq": faq,
        "jsonLd": blocks,
        "internalLinks": resolved_links,
        "dataVerification": "n/a",
        "staleForTargetYear": False,
    }


def sitemap_segment(pages_doc, template):
    """Which sitemap file a page belongs in. Derived rather than hand-assigned so a
    template added later cannot silently land in no segment at all."""
    for seg in pages_doc["sitemaps"]["segments"]:
        if template in seg["templates"]:
            return seg["file"]
    raise SystemExit(f"ERROR  template {template} belongs to no sitemap segment")


def main():
    pages_doc = json.loads((ROOT / "data/pages.json").read_text())
    origin = pages_doc["site"]["origin"].rstrip("/")
    site_name = pages_doc["site"].get("name", "LifeCalc Pro")
    limits = pages_doc["onPage"]["limits"]
    tpl = pages_doc["onPage"]["templates"]["StateTaxPage"]
    page_spec = next(p for p in pages_doc["pages"] if p["path"] == "/state-taxes/{state}")

    state_dir = ROOT / "src/data/tax-year-2026/states"
    states = [json.loads(f.read_text()) for f in sorted(state_dir.glob("*.json"))]
    data_year = "2026"

    entries, errors = [], []
    ld = pages_doc["onPage"]["jsonLd"]
    templates = pages_doc["onPage"]["templates"]

    # The entity rows have to exist before any page is built, because links into
    # them are resolved at build time rather than shipped as "{metro}".
    metros_file = ROOT / "data/metros.json"
    metros = (json.loads(metros_file.read_text())["metros"]
              if metros_file.exists() else [])
    metro_rows = [{"slug": m["slug"], "display": m["displayName"],
                   "stateSlug": m["stateSlug"], "volume": m.get("volume", 0)}
                  for m in metros]
    state_rows = [{"slug": s["slug"], "display": s["name"],
                   "stateSlug": s["slug"], "volume": 0} for s in states]

    for page in pages_doc["pages"]:
        if "{" in page["path"]:
            continue  # entity template, resolved per row below
        entries.append(build_static(page, pages_doc, templates[page["template"]],
                                    origin, site_name, data_year, ld,
                                    metros=metro_rows, states=state_rows))

    if metros:
        place_tpl = templates["PlacePage"]
        place_spec = next(p for p in pages_doc["pages"]
                          if p["path"] == "/cost-of-living/{metro}")
        th = {}
        thf = ROOT / "data/takehome-95k.json"
        if thf.exists():
            th = json.loads(thf.read_text())["states"]
        for m in metros:
            entries.append(build_metro(m, pages_doc, place_spec, place_tpl, origin,
                                       site_name, data_year, ld, th,
                                       metros_all=metro_rows, states_all=state_rows))

    for st in states:
        e = build_state(st, pages_doc, page_spec, tpl, origin, site_name,
                        data_year, metros=metro_rows, states=state_rows)
        if e["titleChars"] > limits["titleMaxChars"]:
            errors.append(f"{e['path']}: title {e['titleChars']} chars")
        if not (limits["metaMinChars"] <= e["metaChars"] <= limits["metaMaxChars"]):
            errors.append(f"{e['path']}: meta {e['metaChars']} chars — "
                          f"outside {limits['metaMinChars']}-{limits['metaMaxChars']}")
        if len(e["faq"]) < 3:
            errors.append(f"{e['path']}: only {len(e['faq'])} FAQ entries")
        entries.append(e)

    for e in entries:
        if e["titleChars"] > limits["titleMaxChars"]:
            errors.append(f"{e['path']}: title {e['titleChars']} chars")
        if e["metaChars"] and not (
                limits["metaMinChars"] <= e["metaChars"] <= limits["metaMaxChars"]):
            errors.append(f"{e['path']}: meta {e['metaChars']} chars")

    # Assign every page to a sitemap segment and build the index the spec describes.
    # Pages carrying an unresolved PENDING_ placeholder are excluded: rule 5-3 says
    # they are not built, and a sitemap listing a page that does not exist teaches
    # Search Console to distrust the file.
    lastmod = pages_doc["site"].get("contentUpdated", data_year)
    segments = collections.OrderedDict(
        (s["file"], []) for s in pages_doc["sitemaps"]["segments"])
    for e in entries:
        e["sitemap"] = sitemap_segment(pages_doc, e["template"])
        if "PENDING_" in json.dumps(e):
            e["sitemap"] = None          # not built yet, so not listed
            continue
        segments[e["sitemap"]].append({"loc": e["canonical"], "lastmod": lastmod})
    sitemap_index = {
        "$comment": "The file tree to produce. Section 6-8-6 and data/pages.json sitemaps.",
        "index": pages_doc["sitemaps"]["index"],
        "lastmod": lastmod,
        "segments": [{"file": f, "urlCount": len(u), "urls": u}
                     for f, u in segments.items()],
        "excluded": [e["path"] for e in entries if e["sitemap"] is None],
    }

    titles = {}
    for e in entries:
        if e["title"] in titles:
            errors.append(f"{e['path']}: duplicate title with {titles[e['title']]}")
        titles[e["title"]] = e["path"]

    out = {
        "$comment": "GENERATED by scripts/generate_onpage.py. Do not edit by hand — "
                    "re-run the script. Imported into the platform rather than typed "
                    "(rule 3-7-6).",
        "generatedFrom": "data/pages.json + src/data/tax-year-2026/states/",
        "origin": origin,
        "pending": ["PlacePage index and rent answers require the BEA/HUD dataset (13-6)"],
        "sitemap": sitemap_index,
        "pages": entries,
    }
    (ROOT / "data/onpage.generated.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n")

    md = ["# Generated on-page specification",
          "",
          "> **Generated by `scripts/generate_onpage.py`. Do not edit by hand.**",
          "> These are the values imported into the platform's SEO fields, not typed "
          "(rule 3-7-6). Re-run after any dataset change.",
          "",
          f"**{len(entries)} pages** "
          f"({sum(1 for e in entries if e['entity'])} generated from entities, "
          f"{sum(1 for e in entries if not e['entity'])} static) · titles {min(e['titleChars'] for e in entries)}"
          f"–{max(e['titleChars'] for e in entries)} chars · metas "
          f"{min(e['metaChars'] for e in entries)}–{max(e['metaChars'] for e in entries)} chars",
          "",
          "Metro pages appear here once the cost-of-living dataset exists (section 13-6).",
          "",
          "## Titles and meta descriptions",
          "",
          "| Path | Title | Chars | Meta chars | Data |",
          "|---|---|---|---|---|"]
    for e in entries:
        flag = "⚠️ 2025" if e["staleForTargetYear"] else e["dataVerification"]
        md.append(f"| `{e['path']}` | {e['title']} | {e['titleChars']} | "
                  f"{e['metaChars']} | {flag} |")

    sample = next(e for e in entries if e["entity"] == "california")
    notax = next(e for e in entries if e["entity"] == "texas")
    for label, e in (("A progressive state", sample), ("A no-tax state", notax)):
        md += ["", f"## {label} — `{e['path']}` in full", "",
               f"- **Title** ({e['titleChars']}) — {e['title']}",
               f"- **H1** — {e['h1']}",
               f"- **Meta** ({e['metaChars']}) — {e['metaDescription']}",
               f"- **Canonical** — `{e['canonical']}`",
               f"- **Breadcrumb** — {' › '.join(e['breadcrumb'])}", "",
               "**H2 outline**", ""]
        md += [f"{i+1}. {h}" for i, h in enumerate(e["h2Outline"])]
        md += ["", "**FAQ**", ""]
        for f in e["faq"]:
            md += [f"- **{f['question']}**", f"  {f['answer']}"]
        md += ["", "**Internal links**", "",
               "| To | Anchor |", "|---|---|"]
        md += [f"| `{l['to']}` | {l['anchor']} |" for l in e["internalLinks"]]
        md += ["", "**JSON-LD**", "", "```json",
               json.dumps(e["jsonLd"], indent=2, ensure_ascii=False), "```"]

    (ROOT / "docs/onpage-spec.md").write_text("\n".join(md) + "\n")

    for err in errors:
        print(f"ERROR  {err}")
    print(f"\n{len(entries)} pages generated · {len(errors)} errors")
    print("wrote data/onpage.generated.json and docs/onpage-spec.md")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
