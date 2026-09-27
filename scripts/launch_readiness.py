#!/usr/bin/env python3
"""One answer to "can this site launch?" — every blocker, from every check.

The other scripts each guard one property and pass or fail on it. None of them
says whether the SITE is ready, because several blockers are not code: a dataset
that cannot be fetched from the build environment, copy that has not been
written, a biography only a human can write, a domain not yet bought. This
collects all of them, marks each BLOCKER (the site must not launch), TODO (it
can launch, but the weakness is real) or OK, and names who clears it.

    python3 scripts/launch_readiness.py            report; always exits 0
    python3 scripts/launch_readiness.py --strict   exits 1 while any BLOCKER remains
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
rows = []


def add(level, area, what, who):
    rows.append((level, area, what, who))


def run(*args):
    p = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


pages = json.loads((ROOT / "data/pages.json").read_text())
gen = json.loads((ROOT / "data/onpage.generated.json").read_text())
gate = gen["sitemap"]["gate"]
bodies = {("/" if f.stem == "home" else "/" + f.stem.replace("__", "/"))
          for f in (ROOT / "content/bodies").glob("*.md")}

# --- data -----------------------------------------------------------------
col = sorted((ROOT / "src/data").glob("cost-of-living-*/us/*.json"))
if not col:
    add("BLOCKER", "data", "Cost-of-living dataset (BEA RPP + HUD FMR) does not exist. Four "
        "tools cannot compute without it: cost of living, comparison, rent affordability "
        "(market side), living wage.",
        "you: allow apps.bea.gov and www.huduser.gov in the environment, or run "
        "scripts/fetch_cost_of_living.py locally with free keys")
states = [json.loads(f.read_text()) for f in (ROOT / "src/data/tax-year-2026/states").glob("*.json")]
unverified = [s["slug"] for s in states if s.get("verification") != "verified"]
if unverified:
    add("BLOCKER", "data", f"{len(unverified)} of {len(states)} state tax datasets are not yet checked "
        "against a primary source (rule 13-4-1: no page ships until a human has checked it).",
        "you or me with network access to state revenue sites; checklist in docs/data-verification.md")
stale = [s["name"] for s in states if s.get("staleForTargetYear")]
if stale:
    add("TODO", "data", f"{len(stale)} states carry prior-year brackets and are held behind the gate: "
        + ", ".join(sorted(stale)), "re-run scripts/extract_tax_data.py when upstream publishes 2026")

# --- programmatic gate ----------------------------------------------------
if gate["metrosBuilt"] < 5:
    add("BLOCKER", "pages", f"{gate['metrosBuilt']} of {gate['metrosTotal']} metro pages built; the gate "
        "(6-10-3) launches with 5 samples. Each needs data plus a written body.",
        "me, once the dataset exists (and metros.json needs a fifth metro)")
if gate["statesBuilt"] < 8:
    add("BLOCKER", "pages", f"{gate['statesBuilt']} of {gate['statesTotal']} state pages built; the first "
        "release is 8 (6-0).", "me: write state bodies (current data only)")

# --- copy -----------------------------------------------------------------
about = ROOT / "content/bodies/about.md"
if about.exists() and "PENDING_HUMAN" in about.read_text():
    add("BLOCKER", "copy", "/about has no biography: the 'Who writes this' section is marked "
        "PENDING_HUMAN. AdSense reviewers and readers look for a real person here (7-4).",
        "you: replace the marked block with a true first-person paragraph")
for p in pages["pages"]:
    if p["template"] in ("TrustPage", "DirectoryPage", "Home") and p["path"] not in bodies:
        lvl = "BLOCKER" if p["template"] == "TrustPage" else "TODO"
        who = "you (a human biography)" if p["path"] == "/about" else "me"
        add(lvl, "copy", f"{p['path']} has no body copy.", who)

# --- identity and domain --------------------------------------------------
if "example.com" in pages["site"]["origin"]:
    add("BLOCKER", "domain", "site.origin is the placeholder https://example.com; every canonical, "
        "sitemap URL and JSON-LD url is built from it.",
        "you: buy the domain, then set site.origin and regenerate")

# --- checks that run elsewhere -------------------------------------------
code, out = run("scripts/audit_claims.py")
pending = [l for l in out.splitlines() if l.strip().startswith("[")]
if code:
    add("BLOCKER", "accuracy", "Unregistered numbers in published copy (audit_claims.py).", "me")
if pending:
    add("TODO", "accuracy", f"{len(pending)} published claims cite a statute or statistic not yet "
        "opened and confirmed from this environment.", "you or me with network access")
code, out = run("scripts/analyze_link_equity.py")
under = [l.split()[0] for l in out.splitlines() if "UNDER-LINKED" in l]
if under:
    add("TODO", "links", f"Under-linked on launch day: {', '.join(under)}. Clears as gated pages "
        "(state and metro) are written, each of which links to it.", "me: more state bodies")
if not (ROOT / "docs/link-building.md").exists():
    add("TODO", "links", "No link-building plan (audit 21-3).", "me")
add("TODO", "legal", "Consent: a Google-certified CMP for EEA/UK/CH visitors before ads serve "
    "there, a US-state 'Do not sell or share' link with AdSense restricted data processing, and "
    "GA4 Consent Mode (docs/measurement.md section 5).",
    "you: enable Google's CMP in AdSense Privacy & messaging (the privacy text is written)")
add("TODO", "platform", "Build promises made in the published copy — in-browser calculation, "
    "value-free analytics, footer consent links, contact form, state citations — not yet "
    "verified on the built site (build-spec section 5).", "you, after the build")
add("TODO", "platform", "Base44 calculators not yet checked against docs/calculator-acceptance.md "
    "— every row must match to the cent.", "you, after the build")
add("BLOCKER", "platform", "Base44 build not yet verified against R1-R9 (server-rendered content, "
    "per-page meta, real 404, sitemap, robots) with the checks in section 3-5.",
    "you: build, then run the three verification commands")

order = {"BLOCKER": 0, "TODO": 1}
rows.sort(key=lambda r: order[r[0]])
for level, area, what, who in rows:
    print(f"{level:<8} [{area}] {what}\n         -> {who}")
b = sum(1 for r in rows if r[0] == "BLOCKER")
print(f"\n{b} blocker(s) · {len(rows) - b} todo(s)")
sys.exit(1 if b and "--strict" in sys.argv else 0)
