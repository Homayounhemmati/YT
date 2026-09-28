#!/usr/bin/env python3
"""Copy what the Base44 app needs from this repository into the app repository.

    python3 scripts/sync_to_app.py /home/user/lifecalc-pro

The app (Vite + React, created by Base44) keeps its own layout, so files are
mapped rather than mirrored:

  engine (bundled, proven)          -> src/lib/lifecalc-engine.js
  src/data/{col,ces-2024,tax-year-2026}/  -> public/data/...        (served as-is)
  data/onpage.generated.json        -> public/data/onpage.generated.json
  data/col-hub-table.json           -> public/data/col-hub-table.json
  content/bodies/*.md               -> src/content/bodies/*.md
  BASE44-START.md                   -> LIFECALC.md               (the entry point)
  docs/{build-spec,base44-cost-of-living-calculator,calculator-acceptance,
        onpage-spec,measurement}.md -> docs/lifecalc/...

Path references inside the copied documents are rewritten to the app's layout, so
the builder never reads a path that does not exist in the app. The package is built
(and its bundle proven against the tested engines) first; nothing is copied if that
fails. Files the app created itself are never touched.
"""
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PKG = ROOT / "dist/lifecalc-base44"

COPIES = [
    ("engine/lifecalc-engine.js", "src/lib/lifecalc-engine.js"),
    ("src/data/col", "public/data/col"),
    ("src/data/ces-2024", "public/data/ces-2024"),
    ("src/data/tax-year-2026", "public/data/tax-year-2026"),
    ("data/onpage.generated.json", "public/data/onpage.generated.json"),
    ("data/col-hub-table.json", "public/data/col-hub-table.json"),
    ("content/bodies", "src/content/bodies"),
]
DOCS = [
    ("BASE44-START.md", "LIFECALC.md"),
    ("docs/build-spec.md", "docs/lifecalc/build-spec.md"),
    ("docs/base44-cost-of-living-calculator.md", "docs/lifecalc/base44-cost-of-living-calculator.md"),
    ("docs/calculator-acceptance.md", "docs/lifecalc/calculator-acceptance.md"),
    ("docs/onpage-spec.md", "docs/lifecalc/onpage-spec.md"),
    ("docs/measurement.md", "docs/lifecalc/measurement.md"),
]
# Longest first, so a specific path is rewritten before its prefix.
REWRITES = [
    (r"bundled from the tested TypeScript in `src/lib/` \(included for reference\)",
     "bundled from the tested TypeScript in the LifeCalc source repository"),
    (r"`?src/lib/tax/`? and `?src/lib/col/`?", "`src/lib/lifecalc-engine.js`"),
    (r'from "src/lib/col"', 'from "@/lib/lifecalc-engine.js"'),
    (r"engine/lifecalc-engine\.js", "src/lib/lifecalc-engine.js"),
    (r"`src/lib/(?:tax|col|calc)/?`( \+ `payroll\.ts`)?", "`src/lib/lifecalc-engine.js`"),
    (r"It says which files to read, in what order,\nand which to ignore\.",
     "It says which files to read, and in what order."),
    (r"everything else in the repository is research, history or tooling\.",
     "everything else in this repository is the app itself."),
    (r"in `src/lib/tax/state\.ts`", "inside `src/lib/lifecalc-engine.js`"),
    (r"(?<![\w/])data/onpage\.generated\.json", "public/data/onpage.generated.json"),
    (r"(?<![\w/])data/col-hub-table\.json", "public/data/col-hub-table.json"),
    (r"(?<![\w/])src/data/", "public/data/"),
    (r"(?<![\w/])content/bodies", "src/content/bodies"),
    (r"(?<![\w/])docs/(build-spec|base44-cost-of-living-calculator|calculator-acceptance|onpage-spec|measurement)\.md",
     r"docs/lifecalc/\1.md"),
    (r"BASE44-START\.md", "LIFECALC.md"),
]
NOTE = ("> Copied from the LifeCalc source repository by `scripts/sync_to_app.py`, with paths\n"
        "> rewritten to this app. Do not edit here: changes are made at the source and synced.\n\n")


def rewrite(text):
    for pat, rep in REWRITES:
        text = re.sub(pat, rep, text)
    return text


TRUST = ["/about", "/methodology", "/sources", "/editorial-policy", "/privacy", "/terms", "/contact"]


def stem(path):
    return "home" if path == "/" else path.strip("/").replace("/", "__")


SMALL = {"of", "by", "and", "to", "in", "a", "the"}


def menu_label(anchor):
    """The menu shows its anchor text in title case: 'cost of living by city' -> 'Cost of Living by City'."""
    words = anchor.split()
    return " ".join(w if (i and w in SMALL) else w[:1].upper() + w[1:] for i, w in enumerate(words))


def slug(text):
    """The app's slugify (src/lib/siteFormat.js) and render_bodies.mjs's."""
    return re.sub(r"\s+", "-", re.sub(r"[^a-z0-9\s-]", "", text.lower()).strip())


def updated(entry, fallback):
    """The page's dateModified from its own JSON-LD, else the site's content date."""
    for node in entry.get("jsonLd") or []:
        if isinstance(node, dict) and node.get("dateModified"):
            return node["dateModified"]
    return fallback


def build_page_files(app):
    """One small file per built page (its SEO values and its body copy) and one
    site file (name, menu, footer, routes), so a page loads only what it shows
    and the router knows exactly which pages exist."""
    import json
    gen = json.loads((ROOT / "data/onpage.generated.json").read_text())
    pages_doc = json.loads((ROOT / "data/pages.json").read_text())
    crawl = pages_doc["crawl"]
    out = app / "public/data/pages"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    built = [e for e in gen["pages"] if e.get("built")]
    by_path = {e["path"]: e for e in built}
    bodies = {}
    for e in built:
        body_file = ROOT / "content/bodies" / f"{stem(e['path'])}.md"
        bodies[stem(e["path"])] = body_file.read_text() if body_file.exists() else ""
    # The body as HTML too, so the app needs no Markdown parser in the browser.
    r = subprocess.run(["node", str(ROOT / "scripts/render_bodies.mjs")], input=json.dumps(bodies),
                       capture_output=True, text=True, cwd=ROOT)
    if r.returncode:
        sys.exit(f"render_bodies.mjs failed:\n{r.stderr}")
    html = json.loads(r.stdout)
    for e in built:
        doc = {k: v for k, v in e.items() if k not in ("titleChars", "metaChars", "sitemap", "built")}
        doc["body"] = bodies[stem(e["path"])]
        doc["bodyHtml"] = html[stem(e["path"])]
        doc["updated"] = updated(e, pages_doc["site"]["contentUpdated"])
        # Every "On this page" link must land on a heading of the body.
        for h in e.get("h2Outline") or []:
            if h != "Frequently asked questions" and f'<h2 id="{slug(h)}">' not in doc["bodyHtml"]:
                sys.exit(f"{e['path']}: no <h2 id=\"{slug(h)}\"> in the body for the outline item {h!r}")
        (out / f"{stem(e['path'])}.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    # The calculators by the funnel stage each page belongs to; the four groups are the
    # ones the /tools page copy names ("the place calculators ... the housing calculators").
    stage_of = {p["path"]: p.get("stage") for p in pages_doc["pages"]}
    groups = [("place", "What a place costs", (1, 2)), ("income", "Income and salary", (3,)),
              ("tax", "Tax and take-home pay", (4,)), ("housing", "Buying a home", (5,))]
    tools = []
    for gid, _, stages in groups:
        for e in built:
            if e["template"] == "ToolPage" and stage_of.get(e["path"]) in stages:
                tools.append({"path": e["path"], "name": e["h1"], "summary": e["metaDescription"], "group": gid})
    missing = [e["path"] for e in built if e["template"] == "ToolPage" and e["path"] not in {t["path"] for t in tools}]
    if missing:
        sys.exit(f"tools without a group: {missing}")
    site = {
        "$comment": "GENERATED by scripts/sync_to_app.py. The pages that exist, the menu, the footer and the calculator catalogue.",
        "name": pages_doc["site"]["name"],
        "origin": gen["origin"],
        "nav": [{"path": p, "label": crawl["navAnchors"].get(p, p), "menuLabel": menu_label(crawl["navAnchors"].get(p, p))}
                for p in crawl["globalNav"] if p in by_path and p != "/"],
        "toolGroups": [{"id": gid, "label": label} for gid, label, _ in groups],
        "tools": tools,
        "footer": [{"path": p, "label": by_path[p]["h1"]} for p in TRUST if p in by_path],
        "routes": [{"path": e["path"], "template": e["template"], "file": f"/data/pages/{stem(e['path'])}.json"}
                   for e in built],
        "sitemap": gen["sitemap"],
    }
    (app / "public/data/site.json").write_text(json.dumps(site, indent=1, ensure_ascii=False) + "\n")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    app = pathlib.Path(sys.argv[1]).resolve()
    if not (app / "base44/config.jsonc").exists():
        sys.exit(f"{app} is not the Base44 app repository (no base44/config.jsonc)")

    p = subprocess.run([sys.executable, "scripts/package_base44.py"], cwd=ROOT,
                       capture_output=True, text=True)
    print(p.stdout.strip())
    if p.returncode:
        sys.exit(f"package failed; nothing copied\n{p.stderr}")

    for src, dest in COPIES:
        s, d = PKG / src, app / dest
        if d.exists():
            shutil.rmtree(d) if d.is_dir() else d.unlink()
        d.parent.mkdir(parents=True, exist_ok=True)
        (shutil.copytree if s.is_dir() else shutil.copy2)(s, d)
    for src, dest in DOCS:
        text = rewrite((PKG / src).read_text())
        if dest == "LIFECALC.md":
            # The source repository's ignore list names files that are not in the app.
            text = re.sub(r"## Ignore.*?(?=## Four rules)", "", text, flags=re.S)
            text = text.replace("## Four rules", """## How a page is loaded

- `public/data/site.json` — the site name; the header menu (`nav`: `path`, `menuLabel` to
  display, `label` the anchor text it stands for); the footer links (`footer`); `routes`:
  every page that exists, with its template and its file (the router creates exactly
  these; anything else is the 404 page); and the calculator catalogue: `toolGroups`
  (`id`, `label`) and `tools` (`path`, `name`, `summary`, `group`) for cards and menus.
- `public/data/pages/{page}.json` — one file per page: its SEO values (the same fields
  as in `public/data/onpage.generated.json`), `body` (its written copy in Markdown),
  `bodyHtml` (the same copy as HTML, with an id on each H2 matching `h2Outline`) and
  `updated` (the date its content last changed, YYYY-MM-DD). A page fetches only its
  own file and renders `bodyHtml` (`src/components/site/HtmlBody.jsx`).

## Page weight

The first JavaScript a page loads must stay under 90 KB compressed (build spec
section 6). So: render `bodyHtml`, never a Markdown parser in the browser; the Base44
SDK is imported lazily inside `src/lib/AuthContext.jsx` (after the page renders), never
at the top of a module the pages load; each calculator is its own lazy chunk; add no
dependency to the first bundle without measuring it.

## How pages reach search engines

`npm run build` is the Vite build followed by `scripts/prerender.mjs`. With
`LIFECALC_PRERENDER=1` set, that script also server-renders `src/entry-server.jsx` and
writes one HTML file per route (`dist/{path}.html`, `dist/index.html` for `/`) with the
page's title, description, canonical, robots, Open Graph and JSON-LD in the head and the
page itself in `#root`; the browser then renders over it from the data embedded in
`<script id="lifecalc-data">`. Without the flag it does nothing and `index.html` stays a
neutral shell.

The flag is off on Base44's hosting on purpose: Base44 answers every URL that is not an
exact file with `dist/index.html`, so a prerendered `index.html` would give every page
the home page's content and canonical. Base44 instead serves recognised crawlers its own
rendered copy of each page on a custom domain. The flag is for a host that serves
`dist/{path}.html` at `/{path}` (Cloudflare Pages, Netlify, Vercel).

- Keep `scripts/prerender.mjs`, `src/entry-server.jsx`, `src/lib/preload.js` and
  `usePageData`'s use of it, and the build script.
- Keep `index.html` with an empty `<div id="root"></div>` and one `<title>`.
- Page components must render from their page file without waiting for anything
  else (no login check, no spinner).
- `public/robots.txt` blocks all crawling until launch (build spec section 7).

## Four rules""", 1)
        d = app / dest
        d.parent.mkdir(parents=True, exist_ok=True)
        lines = text.split("\n", 1)
        d.write_text(lines[0] + "\n\n" + NOTE + (lines[1].lstrip("\n") if len(lines) > 1 else ""))

    build_page_files(app)

    # Every path the entry point names must exist in the app.
    start = (app / "LIFECALC.md").read_text()
    missing = [ref for ref in set(re.findall(r"`((?:docs|public|src)/[^`{ ]+)`", start))
               if not (app / ref.rstrip("/")).exists()]
    if missing:
        sys.exit(f"LIFECALC.md names paths missing from the app: {missing}")
    print(f"synced into {app}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
