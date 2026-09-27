#!/usr/bin/env python3
"""Confirm registered claims against their sources.

A claim in data/claims.json may carry `check`: a list of {url, phrases}. This
script fetches each url (HTML, PDF or JSON), normalises whitespace and looks for
every phrase, case-insensitively. When every phrase of every check is found,
the claim is marked verified and stamped with the date and the urls; when any
is missing, or a source cannot be fetched, the claim keeps its status and the
reason is printed. Nothing is marked verified from a search summary.

    python3 scripts/verify_claims.py            # check every claim that has `check`
    python3 scripts/verify_claims.py --id qm-2021

Needs network access and pypdf for PDF sources. Not run in CI: sources change
their markup, and a launch should not depend on a third-party page being up.
"""
import argparse
import datetime
import html
import io
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (LifeCalc data verification)"


def fetch(url):
    p = subprocess.run(["curl", "-sSL", "--fail", "--max-time", "90", "--retry", "2",
                        "-A", UA, url], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode(errors="replace").strip() or f"curl exit {p.returncode}")
    return p.stdout


def text_of(data):
    if data[:4] == b"%PDF":
        import logging
        import warnings
        import pypdf
        logging.disable(logging.CRITICAL)
        warnings.filterwarnings("ignore")
        return "\n".join((pg.extract_text() or "") for pg in pypdf.PdfReader(io.BytesIO(data)).pages)
    t = data.decode("utf-8", "replace")
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", t)
    return html.unescape(re.sub(r"<[^>]+>", " ", t))


def norm(s):
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip().lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id")
    args = ap.parse_args()
    path = ROOT / "data/claims.json"
    reg = json.loads(path.read_text())
    today = datetime.date.today().isoformat()
    cache, done, failed = {}, 0, 0
    for c in reg["claims"]:
        if not c.get("check") or (args.id and c["id"] != args.id):
            continue
        problems = []
        for chk in c["check"]:
            url = chk["url"]
            try:
                if url not in cache:
                    cache[url] = norm(text_of(fetch(url)))
            except Exception as e:  # noqa: BLE001 — report and move on
                problems.append(f"cannot fetch {url}: {e}")
                continue
            for phrase in chk["phrases"]:
                if norm(phrase) not in cache[url]:
                    problems.append(f"not found in {url}: {phrase!r}")
        if problems:
            failed += 1
            print(f"{c['id']}: NOT CONFIRMED\n  " + "\n  ".join(problems))
            continue
        c["status"] = "verified"
        c["confirmed"] = {"date": today, "sources": [chk["url"] for chk in c["check"]]}
        done += 1
        print(f"{c['id']}: confirmed")
    path.write_text(json.dumps(reg, indent=2, ensure_ascii=False) + "\n")
    print(f"\n{done} confirmed · {failed} not confirmed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
