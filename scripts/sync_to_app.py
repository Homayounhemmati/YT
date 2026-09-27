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
        d = app / dest
        d.parent.mkdir(parents=True, exist_ok=True)
        lines = text.split("\n", 1)
        d.write_text(lines[0] + "\n\n" + NOTE + (lines[1].lstrip("\n") if len(lines) > 1 else ""))

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
