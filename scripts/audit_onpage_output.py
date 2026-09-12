#!/usr/bin/env python3
"""Audits the GENERATED pages, not the rules that produced them.

Every defect this file catches was invisible in data/pages.json and obvious in
data/onpage.generated.json: a breadcrumb whose parent was the page itself, a
dateModified of "2026", a title that shipped the literal string "{Primary}",
thirteen tool pages with no FAQ, nine state pages sharing a byte-identical
answer, and structured data the spec declared and the generator never emitted.

A template is not reviewable. Its output is.
"""
import collections, json, re, sys

G = json.load(open("data/onpage.generated.json"))
SPEC = json.load(open("data/pages.json"))
P = G["pages"]
LIM = SPEC["onPage"]["limits"]
errors, warnings = [], []


def err(m): errors.append(m)
def warn(m): warnings.append(m)


# 1 — unresolved template tokens anywhere in the output
for p in P:
    for tok in set(re.findall(r"\{[A-Za-z_]+\}", json.dumps(p, ensure_ascii=False))):
        err(f"{p['path']}: unresolved template token {tok} in the generated page")

# 2 — breadcrumb integrity
for p in P:
    for block in p["jsonLd"]:
        if block.get("@type") != "BreadcrumbList":
            continue
        items = block["itemListElement"]
        for it in items[:-1]:
            if not it.get("item"):
                err(f"{p['path']}: breadcrumb node {it['position']} has no item URL")
            elif it["item"].rstrip("/").endswith(p["path"]) and p["path"] != "/":
                err(f"{p['path']}: breadcrumb node {it['position']} "
                    f"({it['name']}) points at the page itself")
        if items and items[-1].get("item"):
            warn(f"{p['path']}: the last breadcrumb node carries a URL; the current "
                 "page should not link to itself")
        if [i["position"] for i in items] != list(range(1, len(items) + 1)):
            err(f"{p['path']}: breadcrumb positions are not 1..n")

# 3 — schema.org dates must be ISO 8601, never a bare year
for p in P:
    for block in p["jsonLd"]:
        for key in ("dateModified", "datePublished"):
            v = block.get(key)
            if v and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(v)):
                err(f"{p['path']}: {key}={v!r} is not an ISO 8601 date")

# 4 — the spec's structuredData declarations must actually be emitted
emitted = collections.defaultdict(set)
for p in P:
    emitted[p["template"]] |= {b["@type"] for b in p["jsonLd"]}
built = {p["template"] for p in P}
for tmpl, decl in SPEC["onPage"]["structuredData"].items():
    if tmpl in ("global", "$comment") or tmpl not in built:
        continue
    for line in decl:
        if line.startswith("No "):
            forbidden = line.split()[1]
            if forbidden in emitted[tmpl]:
                err(f"{tmpl}: emits {forbidden}, which structuredData forbids")
            continue
        want = line.split()[0].rstrip(",—")
        if want not in emitted[tmpl]:
            err(f"{tmpl}: structuredData declares {want}, the generator never emits it")

# 5 — FAQ answers must be unique site-wide (section 7-2)
seen = {}
for p in P:
    for a in p["faq"]:
        if not a["answer"].strip():
            err(f"{p['path']}: empty FAQ answer for {a['question']!r}")
        key = a["answer"]
        if key in seen and seen[key] != p["path"]:
            err(f"{p['path']}: FAQ answer is byte-identical to {seen[key]} — "
                f"{a['question']!r}")
        seen[key] = p["path"]

# 6 — an H2 promising a section the page has no content for
for p in P:
    heads = [h.lower() for h in p["h2Outline"]]
    if any("frequently asked" in h for h in heads) and not p["faq"]:
        err(f"{p['path']}: H2 promises an FAQ the page does not have")
    if p["faq"] and not any("frequently asked" in h for h in heads):
        warn(f"{p['path']}: has {len(p['faq'])} FAQ entries with no H2 introducing them")

# 7 — title and meta limits, on the real strings
for p in P:
    if p["titleChars"] > LIM["titleMaxChars"]:
        err(f"{p['path']}: title {p['titleChars']} chars over {LIM['titleMaxChars']}")
    if p["titleChars"] < LIM["titleMinChars"]:
        err(f"{p['path']}: title {p['titleChars']} chars under {LIM['titleMinChars']}")
    if p["metaChars"] and not (LIM["metaMinChars"] <= p["metaChars"] <= LIM["metaMaxChars"]):
        err(f"{p['path']}: meta {p['metaChars']} chars outside "
            f"{LIM['metaMinChars']}-{LIM['metaMaxChars']}")

# 8 — duplicates across the whole site
for field in ("title", "h1", "metaDescription", "canonical"):
    c = collections.Counter(p[field] for p in P if p.get(field))
    for value, n in c.items():
        if n > 1:
            err(f"{n} pages share the same {field}: {value[:60]!r}")

# 9 — one H2 outline reused across pages of one template is template furniture
byt = collections.defaultdict(list)
for p in P:
    byt[p["template"]].append((p["path"], tuple(p["h2Outline"])))
for tmpl, rows in byt.items():
    if len(rows) < 2:
        continue
    c = collections.Counter(o for _, o in rows)
    path, n = c.most_common(1)[0]
    if n > 1 and n == len(rows):
        err(f"{tmpl}: all {n} pages share one H2 outline")

# 10 — sitemap segmentation
sm = G.get("sitemap")
if not sm:
    err("no sitemap index was generated")
else:
    listed = [u["loc"] for s in sm["segments"] for u in s["urls"]]
    if len(listed) != len(set(listed)):
        err("a URL appears in more than one sitemap segment")
    pending = {p["path"] for p in P if "PENDING_" in json.dumps(p)}
    for p in P:
        inmap = p["canonical"] in listed
        if p["path"] in pending and inmap:
            err(f"{p['path']}: carries a PENDING_ placeholder and is in a sitemap")
        if p["path"] not in pending and not inmap:
            err(f"{p['path']}: indexable but in no sitemap segment")

for e in errors:
    print(f"ERROR  {e}")
for w in warnings:
    print(f"warn   {w}")
print(f"\n{len(P)} generated pages · {len(errors)} errors · {len(warnings)} warnings")
sys.exit(1 if errors else 0)
