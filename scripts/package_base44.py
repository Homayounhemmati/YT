#!/usr/bin/env python3
"""Everything Base44 needs to build the site, in one folder and one zip.

    python3 scripts/package_base44.py

Produces dist/lifecalc-base44/ and dist/lifecalc-base44.zip. The package keeps the
repository's own paths, so every reference inside the documents works as written:

  BASE44-START.md                 the entry point: reading order and rules
  docs/                           build spec, calculator brief, acceptance, analytics
  data/onpage.generated.json      every page's SEO values (and `built`)
  data/col-hub-table.json         the /cost-of-living ranked table
  content/bodies/                 the written body of every page
  src/data/                       every JSON file the calculators load
  engine/lifecalc-engine.js       every calculator as ONE browser-ready ES module
  src/lib/                        the TypeScript it is bundled from, for reference

Before writing the zip it checks that the package is complete and consistent — every
built page has its body, every file the documents name is present — and proves the
bundle: fed only the packaged data, it must match the repository's engines figure for
figure. A package that fails either check is not written.
"""
import json
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "dist/lifecalc-base44"

INCLUDE = [
    "BASE44-START.md",
    "docs/build-spec.md",
    "docs/base44-cost-of-living-calculator.md",
    "docs/calculator-acceptance.md",
    "docs/onpage-spec.md",
    "docs/measurement.md",
    "data/onpage.generated.json",
    "data/col-hub-table.json",
    "content/bodies",
    "src/data/col",
    "src/data/ces-2024",
    "src/data/tax-year-2026",
    "src/lib/tax",
    "src/lib/col",
    "src/lib/calc",
    "src/lib/base44-entry.ts",
]
SKIP = {"__tests__", "load.ts"}   # tests, and the Node-only file loader


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f"{' '.join(cmd)} failed:\n{p.stdout}\n{p.stderr}")
    return p.stdout


def copy(rel):
    src, dest = ROOT / rel, OUT / rel
    if src.is_dir():
        shutil.copytree(src, dest, ignore=lambda d, names: [n for n in names if n in SKIP])
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def check_complete():
    """Every built page has its body; every path the start document names exists."""
    gen = json.loads((OUT / "data/onpage.generated.json").read_text())
    problems = []
    for e in gen["pages"]:
        if not e.get("built"):
            continue
        stem = "home" if e["path"] == "/" else e["path"].strip("/").replace("/", "__")
        if not (OUT / "content/bodies" / f"{stem}.md").exists():
            problems.append(f"built page {e['path']} has no body")
    # The "Ignore" section names files deliberately left out of the package.
    start = (OUT / "BASE44-START.md").read_text().split("## Ignore")[0]
    import re
    for ref in set(re.findall(r"`((?:docs|data|content|src|engine)/[^`{ ]+)`", start)):
        if not (OUT / ref.rstrip("/")).exists():
            problems.append(f"BASE44-START.md names {ref}, which is not in the package")
    if problems:
        sys.exit("package incomplete:\n  " + "\n  ".join(problems))
    built = sum(1 for e in gen["pages"] if e.get("built"))
    return built, len(gen["pages"])


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    for rel in INCLUDE:
        copy(rel)
    run(["npx", "esbuild", "src/lib/base44-entry.ts", "--bundle", "--format=esm",
         "--platform=browser", "--target=es2020", "--legal-comments=none",
         f"--outfile={OUT / 'engine/lifecalc-engine.js'}"])

    built, total = check_complete()
    print(f"complete: {built} built pages of {total}, each with its body")
    print(run(["npx", "tsx", "scripts/check_base44_package.ts", str(OUT)]).strip())

    commit = run(["git", "rev-parse", "--short", "HEAD"]).strip()
    (OUT / "PACKAGE.txt").write_text(
        f"LifeCalc Pro — package for Base44, built from commit {commit}.\n"
        "Start with BASE44-START.md.\n")
    zip_path = pathlib.Path(shutil.make_archive(str(OUT), "zip", OUT.parent, OUT.name))
    print(f"wrote {zip_path.relative_to(ROOT)} ({zip_path.stat().st_size / 1024 / 1024:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
