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


def build_state(st, pages_doc, page_spec, tpl, origin, site_name, data_year):
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
                "{SITE_NAME}": site_name, "{DATE_MODIFIED}": data_year,
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
        "internalLinks": [
            {"to": e["to"].replace("{state}", st["slug"]),
             "anchor": e["anchor"].replace("{state}", name)}
            for e in page_spec.get("links", [])],
        "dataVerification": st.get("verification", "unknown"),
        "staleForTargetYear": st.get("staleForTargetYear", False),
    }


def build_metro(m, pages_doc, page_spec, tpl, origin, site_name, data_year, ld,
                takehome):
    """Everything a place page needs except the numbers BEA and HUD will supply.
    Generated now so the shape is reviewable and the gap is explicit, rather than
    the whole page waiting on a dataset (section 13-6)."""
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
        "jsonLd": [bc, place],
        "internalLinks": [
            {"to": e["to"].replace("{state}", m["stateSlug"])
                          .replace("{metro}", m["slug"]),
             "anchor": e["anchor"].replace("{state}", state)
                                  .replace("{metro}", display)}
            for e in page_spec.get("links", [])],
        "dataVerification": m["dataStatus"], "staleForTargetYear": False,
    }


def build_static(page, pages_doc, tpl, origin, site_name, data_year, ld):
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

    breadcrumb_items = [
        {"@type": "ListItem", "position": i + 1, "name": c,
         **({"item": origin if i == 0 else canonical} if i < len(crumbs) - 1 else {})}
        for i, c in enumerate(crumbs)]

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
                         .replace("{DATE_MODIFIED}", year))
        w["publisher"] = {"@type": "Organization", "name": site_name, "url": origin}
        blocks.append(w)

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
        "faq": [],
        "jsonLd": blocks,
        "internalLinks": page.get("links", []),
        "dataVerification": "n/a",
        "staleForTargetYear": False,
    }


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
    for page in pages_doc["pages"]:
        if "{" in page["path"]:
            continue  # entity template, resolved per row below
        entries.append(build_static(page, pages_doc, templates[page["template"]],
                                    origin, site_name, data_year, ld))

    metros_file = ROOT / "data/metros.json"
    if metros_file.exists():
        metros = json.loads(metros_file.read_text())["metros"]
        place_tpl = templates["PlacePage"]
        place_spec = next(p for p in pages_doc["pages"]
                          if p["path"] == "/cost-of-living/{metro}")
        th = {}
        thf = ROOT / "data/takehome-95k.json"
        if thf.exists():
            th = json.loads(thf.read_text())["states"]
        for m in metros:
            entries.append(build_metro(m, pages_doc, place_spec, place_tpl, origin,
                                       site_name, data_year, ld, th))

    for st in states:
        e = build_state(st, pages_doc, page_spec, tpl, origin, site_name, data_year)
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
