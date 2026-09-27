#!/usr/bin/env python3
"""Check the imported Fair Market Rents against HUD's own county file.

scripts/import_hud_fmr.py reads HUD's county FMRs from the copy bundled in the
policyengine-us package (a secondary source). This downloads HUD's spreadsheet
for the same fiscal year and compares every county, every bedroom count. Only an
exact match on every county marks the dataset verified.

    python3 scripts/verify_hud_fmr.py --year 2026
    python3 scripts/verify_hud_fmr.py --year 2026 --file FY26_FMRs_revised.xlsx

HUD publishes revisions as a separate file (FY26_FMRs_revised.xlsx); the revised
file is the one in force and is tried first.
"""
import argparse
import datetime
import io
import json
import pathlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
BASE = "https://www.huduser.gov/portal/datasets/fmr/fmr{year}/"


def xlsx_rows(data):
    """Rows of the first sheet as {column letter: text}. HUD's files carry
    document properties that openpyxl rejects, so the XML is read directly."""
    z = zipfile.ZipFile(io.BytesIO(data))
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    root = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    for r in root.iter("{%s}row" % NS["m"]):
        out = {}
        for c in r.findall("m:c", NS):
            col = re.match(r"[A-Z]+", c.get("r")).group()
            v, t = c.find("m:v", NS), c.get("t")
            if t == "inlineStr":
                out[col] = "".join(x.text or "" for x in c.iter("{%s}t" % NS["m"]))
            elif v is None:
                out[col] = None
            else:
                out[col] = shared[int(v.text)] if t == "s" else v.text
        yield out


def download(url):
    p = subprocess.run(["curl", "-sSL", "--fail", "--max-time", "120", "--retry", "3",
                        "-A", "Mozilla/5.0 (LifeCalc data verification)", url],
                       capture_output=True)
    return p.stdout if p.returncode == 0 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--file", help="HUD file name; default tries the revised file first")
    args = ap.parse_args()
    yy = str(args.year)[2:]
    names = [args.file] if args.file else [f"FY{yy}_FMRs_revised.xlsx", f"FY{yy}_FMRs.xlsx"]
    base = BASE.format(year=args.year)
    data = name = None
    for name in names:
        data = download(base + name)
        if data:
            break
    if not data:
        sys.exit(f"could not download {names} from {base}")

    rows = xlsx_rows(data)
    header = next(rows)
    col = {v: k for k, v in header.items()}
    hud = {}
    for r in rows:
        fips = r.get(col["fips"]) or ""
        if len(fips) == 10 and fips.endswith("99999"):      # county-level rows
            hud[fips[:5]] = [float(r[col[f"fmr_{i}"]]) for i in range(5)]

    path = ROOT / f"src/data/rent-fy{args.year}/fmr-counties.json"
    doc = json.loads(path.read_text())
    checked, mismatches = 0, []
    for fips, c in doc["counties"].items():
        if not c.get("rent"):
            continue
        mine = [c["rent"][f"bedrooms{i}"] for i in range(5)]
        if hud.get(fips) != mine:
            mismatches.append((fips, c.get("name"), mine, hud.get(fips)))
        checked += 1
    print(f"{name}: {len(hud)} county rows · checked {checked} · mismatches {len(mismatches)}")
    for m in mismatches[:10]:
        print("  ", m)
    if mismatches:
        doc["verification"] = "pending"
        doc.pop("verified", None)
        path.write_text(json.dumps(doc, indent=1) + "\n")
        return 1
    doc["verification"] = "verified"
    doc["verified"] = {"date": datetime.date.today().isoformat(), "against": base + name,
                       "countiesChecked": checked,
                       "method": "every county, every bedroom count, exact match"}
    path.write_text(json.dumps(doc, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
