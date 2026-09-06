#!/usr/bin/env python3
"""Fail the build if non-English text appears anywhere in the project.

The site is English, the data is English, and the documentation is English. That
was not always true, and the one place it mattered most is instructive: `output`
in `data/pages.json` held an internal Persian description, and wiring it into
the meta formula would have shipped 15 Persian meta descriptions.

The first fix drew a boundary — English under `data/`, Persian under `docs/`.
The second removed the boundary instead of policing it, because a rule you have
to remember is the kind of rule that fails. The whole project is now one
language, and this check is what keeps it that way.

`docs/archive/` is the single exception. Those are the three original
specifications as they were written; translating a historical record destroys
it, so the archive stays verbatim and is skipped here.
"""
import pathlib
import re
import sys

# Arabic, Arabic Supplement, Extended-A, Presentation Forms, plus ZWNJ.
# Written as escapes rather than literals so this file does not trip its own
# check — the detector must not contain what it detects.
PERSIAN = re.compile(
    "[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff"
    "\ufb50-\ufdff\ufe70-\ufeff\u200c]")

# Everything that ships, plus everything that documents it.
CHECKED = ("data", "src", "app", "public", "components", "content", "docs",
           "scripts")

# The originals, kept verbatim as a historical record.
EXEMPT = (pathlib.PurePath("docs/archive"),)

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

    for top in CHECKED:
        base = root / top
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if any(exempt in path.parents for exempt in EXEMPT):
                continue
            if path.suffix.lower() in SKIP_SUFFIXES:
                continue
            scanned += 1
            for line_no, text in offending_lines(path):
                excerpt = text if len(text) <= 90 else text[:87] + "..."
                errors.append(f"{path}:{line_no}: non-English text — {excerpt}")

    for error in errors:
        print(f"ERROR  {error}")

    print(f"\n{scanned} files scanned · {len(errors)} errors")
    if errors:
        print("\nThe whole project is English — the site, the data and the "
              "docs. Translate the text, or, if it is a historical record, "
              "put it in docs/archive/.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
