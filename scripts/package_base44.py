#!/usr/bin/env python3
"""Everything Base44 needs for the cost-of-living calculator, in one folder and one zip.

    python3 scripts/package_base44.py

Produces dist/base44-cost-of-living-calculator/ and a .zip of it:

  README-FIRST.md       what to upload and in what order
  BRIEF.md              docs/base44-cost-of-living-calculator.md
  ACCEPTANCE.md         docs/calculator-acceptance.md
  engine/col-engine.js  the engine as ONE browser-ready ES module (no dependencies)
  engine/src/           the TypeScript source it was built from, for reference
  data/...              every JSON file the calculator loads, same relative paths

Then it proves the bundle: it imports engine/col-engine.js with the packaged data,
runs every cost-of-living acceptance case and compares each figure with the
engine in this repository. A package that disagrees is not written.
"""
import json
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "dist/base44-cost-of-living-calculator"

DATA = [
    "src/data/col/meta.json",
    "src/data/col/price-areas.json",
    "src/data/col/search-index.json",
    "src/data/col/places",
    "src/data/ces-2024/baseline.json",
    "src/data/tax-year-2026/federal.json",
    "src/data/tax-year-2026/estimated.json",
    "src/data/tax-year-2026/states",
]

README = """# Cost of Living Calculator — package for Base44

1. Read **BRIEF.md** first. It is the whole specification.
2. Add **engine/col-engine.js** to the app as a code file and import from it:
   `import {{ computeCostOfLiving, resolvePlace, searchEntries }} from "./col-engine.js"`.
   Do not rewrite it. It is generated from tested code and proven against ACCEPTANCE.md.
3. Add everything under **data/** as static files, keeping the paths
   (for example `data/col/places/tx.json`). Load them as BRIEF.md section 2 says:
   small files on page load, the search index when the search box gets focus,
   a state's files when a place in that state is chosen.
4. Build the page from BRIEF.md sections 4-7.
5. Check the finished calculator against **ACCEPTANCE.md** (the cost-of-living
   sections). Every figure must match to the cent. If one does not, the build is
   wrong — not the table.

Paths: BRIEF.md names files as they are in the repository. In this package,
`src/data/...` is `data/...`, and the modules `src/lib/tax` and `src/lib/col` are
the one file `engine/col-engine.js` (their source is in `engine/src/` for reference).

Package built from commit {commit}. Data: BEA {rpp}, HUD FY{fmr}, BLS CE {ces} in {month} prices, tax year 2026.
"""


def run(cmd, **kw):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, **kw)
    if p.returncode:
        sys.exit(f"{' '.join(cmd)} failed:\n{p.stdout}\n{p.stderr}")
    return p.stdout


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "engine").mkdir(parents=True)

    # 1. The engine as one ES module.
    run(["npx", "esbuild", "src/lib/base44-entry.ts", "--bundle", "--format=esm",
         "--platform=browser", "--target=es2020", "--legal-comments=none",
         f"--outfile={OUT / 'engine/col-engine.js'}"])
    for sub in ("tax", "col"):
        for f in (ROOT / "src/lib" / sub).glob("*.ts"):
            if f.name == "load.ts":
                continue   # reads files from disk; the app loads JSON itself
            dest = OUT / "engine/src" / sub / f.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
    shutil.copy2(ROOT / "src/lib/base44-entry.ts", OUT / "engine/src/base44-entry.ts")

    # 2. Data, same relative paths under data/.
    for item in DATA:
        src = ROOT / item
        dest = OUT / "data" / pathlib.Path(item).relative_to("src/data")
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    # 3. Documents.
    shutil.copy2(ROOT / "docs/base44-cost-of-living-calculator.md", OUT / "BRIEF.md")
    shutil.copy2(ROOT / "docs/calculator-acceptance.md", OUT / "ACCEPTANCE.md")
    meta = json.loads((ROOT / "src/data/col/meta.json").read_text())
    ces = json.loads((ROOT / "src/data/ces-2024/baseline.json").read_text())
    commit = run(["git", "rev-parse", "--short", "HEAD"]).strip()
    (OUT / "README-FIRST.md").write_text(README.format(
        commit=commit, rpp=meta["years"]["priceLevels"], fmr=meta["years"]["rent"],
        ces=ces["year"], month=ces.get("priceUpdate", {}).get("toMonth", "survey-year")))

    # 4. Prove the bundle against the repository's engine, case by case.
    out = run(["npx", "tsx", "scripts/check_base44_package.ts", str(OUT)])
    print(out.strip())

    # 5. Zip.
    zip_path = shutil.make_archive(str(OUT), "zip", OUT.parent, OUT.name)
    size = pathlib.Path(zip_path).stat().st_size / 1024 / 1024
    print(f"wrote {pathlib.Path(zip_path).relative_to(ROOT)} ({size:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
