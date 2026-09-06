#!/usr/bin/env python3
"""Fail the build if Persian text reaches anything that ships.

The site is English. The spec is written in Persian because its readers are,
but the spec never ships. The dangerous boundary is between the two: a Persian
string in `data/` becomes a Persian meta description on a live page, which is
exactly what nearly happened when `output` — an internal spec field — was first
wired into the meta formula.

So this draws the boundary as a check rather than a convention: SHIPPING paths
must be pure English, DOC paths may be Persian, and nothing is left to memory.
"""
import pathlib
import re
import sys

# Arabic, Arabic Supplement, Extended-A, Presentation Forms, plus ZWNJ.
PERSIAN = re.compile(r"[؀-ۿݐ-ݿࢠ-ࣿ"
                     r"ﭐ-﷿ﹰ-﻿‌]")

# Everything that can reach a rendered page or the JS bundle.
SHIPPING = ("data", "src", "app", "public", "components", "content")

SKIP_DIRS = {".git", "node_modules", ".next", "out", "dist", "coverage",
             "__pycache__", ".venv"}
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".woff",
                 ".woff2", ".ttf", ".pdf", ".zip", ".whl"}


def offending_lines(path):
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    return [(n, line.strip())
            for n, line in enumerate(text.splitlines(), 1)
            if PERSIAN.search(line)]


def main():
    root = pathlib.Path(".")
    errors = []
    scanned = 0

    for top in SHIPPING:
        base = root / top
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.suffix.lower() in SKIP_SUFFIXES:
                continue
            scanned += 1
            for line_no, text in offending_lines(path):
                excerpt = text if len(text) <= 90 else text[:87] + "..."
                errors.append(f"{path}:{line_no}: Persian text in a shipping "
                              f"file — {excerpt}")

    for error in errors:
        print(f"ERROR  {error}")

    print(f"\n{scanned} shipping files scanned · {len(errors)} errors")
    if errors:
        print("\nThe site is English. Persian belongs in docs/, which never "
              "ships — move the text there, or translate it.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
