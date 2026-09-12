#!/usr/bin/env python3
"""Internal link equity against the demand each page has to win.

The link graph in data/pages.json declares entity templates as single rows
(`/cost-of-living/{metro}`), but the crawler sees 30 metro pages and 51 state
pages. Collapsing them understates the equity the programmatic sets pass on by
roughly two orders of magnitude, so this expands them before running PageRank.

A page whose share of internal equity is far below its share of the demand it
targets will not rank for it, however good the page is. That ratio is the
output.
"""
import json, collections, sys

d = json.load(open("data/pages.json"))
k = json.load(open("data/keywords.json"))
vol = {x["slug"]: x["volume"] for x in k["keywords"]}

# how many real URLs each declared row becomes
EXPANSION = {"/cost-of-living/{metro}": 30, "/state-taxes/{state}": 51}

nav = d["crawl"]["globalNav"]
foot = d["crawl"]["globalFooter"]
rows = {p["path"]: p for p in d["pages"]}

# expand templates into concrete nodes
nodes, origin = [], {}
for p in d["pages"]:
    n = EXPANSION.get(p["path"], 1)
    for i in range(n):
        nid = p["path"] if n == 1 else f"{p['path']}#{i}"
        nodes.append(nid); origin[nid] = p["path"]

def targets(template_path):
    """Concrete nodes a declared link target resolves to."""
    n = EXPANSION.get(template_path, 1)
    if n == 1:
        return [template_path]
    return [f"{template_path}#{i}" for i in range(n)]

out = collections.defaultdict(set)
for nid in nodes:
    src = origin[nid]
    for l in rows[src].get("links", []):
        for t in targets(l["to"]):
            if t != nid:
                out[nid].add(t)
    for g in nav + foot:
        for t in targets(g):
            if t != nid:
                out[nid].add(t)

N = len(nodes); pr = {n: 1 / N for n in nodes}; DAMP = 0.85
for _ in range(100):
    new = {n: (1 - DAMP) / N for n in nodes}
    for src in nodes:
        dst = out[src]
        if not dst:
            for n in nodes: new[n] += DAMP * pr[src] / N
        else:
            share = DAMP * pr[src] / len(dst)
            for t in dst: new[t] += share
    pr = new
s = sum(pr.values()); pr = {n: v / s for n, v in pr.items()}

agg = collections.Counter()
for nid, v in pr.items(): agg[origin[nid]] += v

scored = []
for p in d["pages"]:
    v = vol.get(p["path"].split("/")[-1], 0)
    if v: scored.append((p["path"], v, agg[p["path"]]))
tv = sum(r[1] for r in scored); tp = sum(r[2] for r in scored)

print(f"{len(nodes)} real URLs from {len(d['pages'])} declared rows\n")
print(f"{'PAGE':<44}{'VOLUME':>9}{'demand':>8}{'equity':>8}  support")
bad = []
for path, v, p in sorted(scored, key=lambda r: -r[1]):
    ds, es = v / tv * 100, p / tp * 100
    r = es / ds
    tag = "UNDER-LINKED" if r < 0.7 else ("over-linked" if r > 2.0 else "ok")
    if r < 0.7: bad.append((path, r))
    print(f"{path:<44}{v:>9,}{ds:>7.1f}%{es:>7.1f}%  {r:>5.2f}x {tag}")

print(f"\n{len(bad)} under-linked page(s)")
sys.exit(1 if bad else 0)
