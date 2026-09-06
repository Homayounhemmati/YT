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


def takehome_answer(st):
    """Deliberately not a computed figure. The engine can produce one; the
    cost-of-living dataset it needs for the comparison does not exist yet, and a
    number stated here without the engine behind it is exactly what section 5-3
    forbids."""
    if st["structure"] == "none":
        return ("PENDING_ENGINE: run the tax engine for $95,000 single in "
                f"{st['name']} and state the federal-only net.")
    return ("PENDING_ENGINE: run the tax engine for $95,000 single in "
            f"{st['name']} and state the net after federal and state tax.")


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
        repl = {"{TITLE}": title, "{CANONICAL}": canonical, "{ORIGIN}": origin,
                "{SITE_NAME}": site_name, "{DATE_MODIFIED}": data_year,
                "{ENTITY_NAME}": name, "{STATE_ABBR}": st["abbr"]}
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
        "pending": ["PlacePage entries require the cost-of-living dataset (section 13-6)",
                    "PENDING_ENGINE answers require a tax-engine run per state"],
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
          f"**{len(entries)} state pages** · titles {min(e['titleChars'] for e in entries)}"
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
