#!/usr/bin/env python3
"""
Extract federal and 51-jurisdiction state income tax parameters into the
project's own JSON schema.

Source: the `policyengine-us` package parameter tree (an open-source, actively
maintained model of the US tax system). Each parameter file carries `reference`
links to the underlying statute / IRS Revenue Procedure / state DOR page; those
links are copied into the output so every number we ship keeps its citation.

This is a SECONDARY source. Per SPEC.md rule #1, every value emitted here is
marked `"verification": "pending"` until a human checks it against the primary
source named in `sources`. The verification checklist lives in
docs/data-verification.md.

Usage:
    python3 scripts/extract_tax_data.py --year 2026
"""
import argparse, datetime, io, json, os, pathlib, re, sys, urllib.request, zipfile

WHEEL_CACHE = os.environ.get("PE_WHEEL", "/tmp/policyengine_us.whl")
PARAM_ROOT = "policyengine_us/parameters/"

FILING_STATUSES = {  # ours -> policyengine's
    "single": "SINGLE",
    "marriedJointly": "JOINT",
    "marriedSeparately": "SEPARATE",
    "headOfHousehold": "HEAD_OF_HOUSEHOLD",
}
STATE_RATE_FILES = {  # ours -> policyengine state rates/<file>.yaml
    "single": "single",
    "marriedJointly": "joint",
    "marriedSeparately": "separate",
    "headOfHousehold": "head_of_household",
}

JURISDICTIONS = {
    "al": ("Alabama", "alabama"), "ak": ("Alaska", "alaska"),
    "az": ("Arizona", "arizona"), "ar": ("Arkansas", "arkansas"),
    "ca": ("California", "california"), "co": ("Colorado", "colorado"),
    "ct": ("Connecticut", "connecticut"), "de": ("Delaware", "delaware"),
    "fl": ("Florida", "florida"), "ga": ("Georgia", "georgia"),
    "hi": ("Hawaii", "hawaii"), "id": ("Idaho", "idaho"),
    "il": ("Illinois", "illinois"), "in": ("Indiana", "indiana"),
    "ia": ("Iowa", "iowa"), "ks": ("Kansas", "kansas"),
    "ky": ("Kentucky", "kentucky"), "la": ("Louisiana", "louisiana"),
    "me": ("Maine", "maine"), "md": ("Maryland", "maryland"),
    "ma": ("Massachusetts", "massachusetts"), "mi": ("Michigan", "michigan"),
    "mn": ("Minnesota", "minnesota"), "ms": ("Mississippi", "mississippi"),
    "mo": ("Missouri", "missouri"), "mt": ("Montana", "montana"),
    "ne": ("Nebraska", "nebraska"), "nv": ("Nevada", "nevada"),
    "nh": ("New Hampshire", "new-hampshire"), "nj": ("New Jersey", "new-jersey"),
    "nm": ("New Mexico", "new-mexico"), "ny": ("New York", "new-york"),
    "nc": ("North Carolina", "north-carolina"), "nd": ("North Dakota", "north-dakota"),
    "oh": ("Ohio", "ohio"), "ok": ("Oklahoma", "oklahoma"),
    "or": ("Oregon", "oregon"), "pa": ("Pennsylvania", "pennsylvania"),
    "ri": ("Rhode Island", "rhode-island"), "sc": ("South Carolina", "south-carolina"),
    "sd": ("South Dakota", "south-dakota"), "tn": ("Tennessee", "tennessee"),
    "tx": ("Texas", "texas"), "ut": ("Utah", "utah"),
    "vt": ("Vermont", "vermont"), "va": ("Virginia", "virginia"),
    "wa": ("Washington", "washington"), "wv": ("West Virginia", "west-virginia"),
    "wi": ("Wisconsin", "wisconsin"), "wy": ("Wyoming", "wyoming"),
    "dc": ("Washington, D.C.", "washington-dc"),
}

# States with no broad-based individual income tax on earned income.
NO_INCOME_TAX = {"ak", "fl", "nv", "nh", "sd", "tn", "tx", "wa", "wy"}


# ---------------------------------------------------------------- package I/O

def fetch_wheel():
    if os.path.exists(WHEEL_CACHE):
        return WHEEL_CACHE
    meta = json.load(urllib.request.urlopen(
        "https://pypi.org/pypi/policyengine-us/json", timeout=120))
    url = next(f["url"] for f in meta["urls"] if f["packagetype"] == "bdist_wheel")
    sys.stderr.write("downloading %s\n" % url)
    urllib.request.urlretrieve(url, WHEEL_CACHE)
    return WHEEL_CACHE


def package_version(z):
    for n in z.namelist():
        m = re.match(r"policyengine_us-([^/]+)\.dist-info/METADATA$", n)
        if m:
            return m.group(1)
    return "unknown"


class _PlainLoader:
    """SafeLoader that keeps date-like keys as strings.

    The parameter files use `0000-01-01` as a sentinel for "always", which
    PyYAML's timestamp resolver rejects (year 0 is not a valid date).
    """

    _loader = None

    @classmethod
    def get(cls):
        if cls._loader is None:
            import yaml

            class L(yaml.SafeLoader):
                pass

            L.add_constructor(
                "tag:yaml.org,2002:timestamp",
                lambda loader, node: loader.construct_scalar(node),
            )
            cls._loader = L
        return cls._loader


def load(z, rel):
    import yaml
    try:
        raw = z.read(PARAM_ROOT + rel).decode()
    except KeyError:
        return None
    return yaml.load(raw, Loader=_PlainLoader.get())


# ------------------------------------------------------- value-at-date helper

def _date_map(node):
    """Return {date_string: value} from either a bare map or a `values:` map."""
    if not isinstance(node, dict):
        return {}
    src = node.get("values", node)
    if not isinstance(src, dict):
        return {}
    return {str(k): v for k, v in src.items()
            if re.match(r"^\d{4}-\d{2}-\d{2}$", str(k))}


def _is_inf(v):
    if isinstance(v, str):
        return v.strip() in (".inf", "+.inf", ".Inf", ".INF")
    return isinstance(v, float) and v == float("inf")


def value_at(node, on_date):
    """Latest value effective on or before `on_date`, plus the date it took effect."""
    dates = _date_map(node)
    applicable = sorted(d for d in dates if d <= on_date)
    if not applicable:
        return None, None
    d = applicable[-1]
    v = dates[d]
    return (None if _is_inf(v) else v), d


def is_uprated(node):
    """True if the parameter is inflation-indexed, i.e. expected to change yearly.

    A flat rate set years ago and never amended is still the current rate; only
    an indexed parameter that has not been refreshed is genuinely out of date.
    """
    if not isinstance(node, dict):
        return False
    if "uprating" in (node.get("metadata") or {}):
        return True
    for v in node.values():
        if isinstance(v, dict) and is_uprated(v):
            return True
        if isinstance(v, list):
            for item in v:
                if isinstance(item, dict) and is_uprated(item):
                    return True
    return False


def references(node):
    out = []
    if not isinstance(node, dict):
        return out
    meta = node.get("metadata") or {}
    for ref in (meta.get("reference") or []):
        if isinstance(ref, dict) and ref.get("href"):
            out.append({"title": ref.get("title", ""), "url": ref["href"]})
    return out


# ------------------------------------------------------------------- federal

def build_federal(z, year):
    on = "%d-12-31" % year
    bracket = load(z, "gov/irs/income/bracket.yaml") or {}
    rates_node = bracket.get("rates", {})
    thr_node = bracket.get("thresholds", {})

    rates = {}
    for i in range(1, 8):
        v, _ = value_at(rates_node.get(i, {}), on)
        if v is not None:
            rates[i] = round(float(v) * 100, 4)

    brackets, effective = {}, set()
    for ours, theirs in FILING_STATUSES.items():
        rows, lower = [], 0.0
        for i in range(1, 8):
            if i not in rates:
                continue
            top, d = value_at((thr_node.get(i) or {}).get(theirs, {}), on)
            if d:
                effective.add(d)
            rows.append({"from": lower, "to": top, "rate": rates[i]})
            if top is None:
                break
            lower = float(top)
        brackets[ours] = rows

    std_node = load(z, "gov/irs/deductions/standard/amount.yaml") or {}
    std = {}
    for ours, theirs in FILING_STATUSES.items():
        v, d = value_at(std_node.get(theirs, {}), on)
        if v is not None:
            std[ours] = v
            effective.add(d)

    ss_cap, ss_d = value_at(load(z, "gov/irs/payroll/social_security/cap.yaml") or {}, on)
    se_ss, _ = value_at(load(z, "gov/irs/self_employment/rate/social_security.yaml") or {}, on)
    se_med, _ = value_at(load(z, "gov/irs/self_employment/rate/medicare.yaml") or {}, on)
    min_node = load(z, "gov/irs/self_employment/net_earnings_exemption.yaml") or {}
    min_earnings, _ = value_at(min_node, on)

    qbi_start_node = load(z, "gov/irs/deductions/qbi/phase_out/start.yaml") or {}
    qbi_rate, _ = value_at(load(z, "gov/irs/deductions/qbi/max/rate.yaml") or {}, on)
    qbi_start = {}
    for ours, theirs in FILING_STATUSES.items():
        v, _ = value_at(qbi_start_node.get(theirs, {}), on)
        if v is not None:
            qbi_start[ours] = v

    # 26 U.S.C. 1402(a)(12): net earnings are reduced by the employer-equivalent
    # half of the combined SE tax rate, giving the familiar 0.9235 multiplier.
    nese_factor = None
    if se_ss is not None and se_med is not None:
        nese_factor = round(1 - (float(se_ss) + float(se_med)) / 2, 6)

    return {
        "taxYear": year,
        "brackets": brackets,
        "standardDeduction": std,
        "selfEmployment": {
            "neseFactor": nese_factor,
            "neseFactorDerivation": "1 - (socialSecurityRate + medicareRate) / 2",
            "minimumEarningsThreshold": min_earnings,
            "socialSecurityRate": round(float(se_ss) * 100, 4) if se_ss else None,
            "medicareRate": round(float(se_med) * 100, 4) if se_med else None,
            "socialSecurityWageBase": ss_cap,
            "deductiblePortion": 50.0,
            "additionalMedicare": {
                "rate": 0.9,
                "inflationIndexed": False,
                "thresholds": {
                    "single": 200000, "marriedJointly": 250000,
                    "marriedSeparately": 125000, "headOfHousehold": 200000,
                },
            },
        },
        "qbi": {
            "maxRate": round(float(qbi_rate) * 100, 4) if qbi_rate else None,
            "phaseOutStart": qbi_start,
        },
        "provenance": {
            "extractedFrom": "policyengine-us",
            "sourcePaths": [
                "gov/irs/income/bracket.yaml",
                "gov/irs/deductions/standard/amount.yaml",
                "gov/irs/payroll/social_security/cap.yaml",
                "gov/irs/self_employment/rate/social_security.yaml",
                "gov/irs/self_employment/rate/medicare.yaml",
                "gov/irs/self_employment/net_earnings_exemption.yaml",
                "gov/irs/deductions/qbi/*",
            ],
            "valuesEffectiveFrom": sorted(effective),
            "socialSecurityCapEffectiveFrom": ss_d,
            "sources": references(bracket.get("thresholds", {})),
        },
        "verification": "pending",
    }


# --------------------------------------------------------------------- states

# Per-status bracket file layouts, tried in order. PolicyEngine is not
# consistent across states, so resolution is probed and then RECORDED in the
# output, rather than assumed.
PER_STATUS_LAYOUTS = [
    "rates/{s}.yaml",
    "main/{s}.yaml",
    "main/by_filing_status/{s}.yaml",
]
# One bracket table shared by every filing status.
SHARED_BRACKET_FILES = ["rates.yaml", "rate.yaml", "rates/main/rate.yaml"]
# A single flat rate, no brackets.
FLAT_SCALAR_FILES = ["rate.yaml", "main/rate.yaml", "agi_rate.yaml",
                     "rates/part_b.yaml"]

# States whose layout does not fit any generic pattern.
SPECIAL = {
    # Iowa splits into joint vs. everyone else.
    "ia": {"kind": "per_status_map", "files": {
        "single": "rates/by_filing_status/other.yaml",
        "marriedJointly": "rates/by_filing_status/joint.yaml",
        "marriedSeparately": "rates/by_filing_status/other.yaml",
        "headOfHousehold": "rates/by_filing_status/other.yaml"}},
    # Massachusetts: flat Part B rate plus a surtax over a high threshold.
    "ma": {"kind": "flat_plus_surtax", "flat": "rates/part_b.yaml",
           "surtax": "rates/additional.yaml"},
    # Indiana: flat state rate, plus county income taxes on top.
    "in": {"kind": "flat_scalar", "flat": "agi_rate.yaml",
           "local": "county_rates.yaml"},
}

# Extra brackets levied on top of the ordinary schedule. Without these a state's
# headline top rate is understated: California's well-known 13.3% is the 12.3%
# ordinary top rate plus the 1% mental health services tax.
STATE_SURTAX_FILES = {
    "ca": "mental_health_services.yaml",
}

# States that replaced a progressive schedule with a flat rate. The legacy
# bracket files are still present in the parameter tree, so without consulting
# the switch we would ship a repealed schedule: Georgia went flat in 2024
# (HB 1015) and Louisiana in 2025 (RS 47:32).
FLAT_SWITCHES = {
    "ga": {"switch": "main/flat_applies.yaml", "rate": "main/flat_rate.yaml"},
    "la": {"switch": "main/flat/applies.yaml", "rate": "main/flat/rate.yaml"},
}

LOCAL_TAX_NOTES = {
    "in": "Indiana counties levy their own income tax on top of the state rate. "
          "The county rate depends on the county of residence and is not "
          "included in this calculation.",
    "ny": "New York City and Yonkers levy resident income taxes on top of the "
          "state tax. Not included in this calculation.",
    "oh": "Many Ohio municipalities and school districts levy their own income "
          "tax. Not included in this calculation.",
    "pa": "Most Pennsylvania municipalities levy a local earned income tax. "
          "Philadelphia additionally imposes BIRT and the Net Profits Tax, "
          "which apply directly to freelancers. Not included here.",
    "md": "Every Maryland county and Baltimore City levies a local income tax "
          "on top of the state tax. Not included in this calculation.",
    "mo": "Kansas City and St. Louis levy a 1% earnings tax. Not included.",
    "mi": "Several Michigan cities, including Detroit, levy a local income tax. "
          "Not included in this calculation.",
    "al": "Some Alabama municipalities levy an occupational tax. Not included.",
    "ky": "Many Kentucky counties and cities levy occupational license taxes on "
          "net profits. Not included in this calculation.",
}


def _bracket_rows(node, on):
    """Parse a `brackets:` list into ordered {from, rate} rows."""
    raw = node.get("brackets") if isinstance(node, dict) else None
    if not isinstance(raw, list):
        return [], set()
    rows, effective = [], set()
    for b in raw:
        thr, td = value_at(b.get("threshold", {}), on)
        # Some states express the marginal rate under `amount` rather than `rate`.
        rate, rd = value_at(b.get("rate", {}), on)
        if rate is None:
            rate, rd = value_at(b.get("amount", {}), on)
        # `value_at` maps the `.inf` sentinel to None; such rows are padding.
        if rate is None:
            continue
        if thr is None and any(_is_inf(v)
                               for v in _date_map(b.get("threshold", {})).values()):
            continue
        for d in (td, rd):
            if d and not d.startswith("0000"):
                effective.add(d)
        rows.append({"from": float(thr or 0), "rate": round(float(rate) * 100, 4)})
    rows.sort(key=lambda r: r["from"])
    # Drop duplicate thresholds, keeping the first (lowest-index) definition.
    seen, dedup = set(), []
    for r in rows:
        if r["from"] in seen:
            continue
        seen.add(r["from"])
        dedup.append(r)
    return dedup, effective


def resolve_state_rates(z, code, year):
    """Return (brackets, flat_rate, effective_dates, sources, resolved_paths, extra)."""
    on = "%d-12-31" % year
    base = "gov/states/%s/tax/income/" % code
    effective, sources, resolved, extra = set(), [], {}, {}

    special = SPECIAL.get(code)
    if special and special["kind"] == "per_status_map":
        brackets = {}
        for ours, rel in special["files"].items():
            node = load(z, base + rel)
            if node is None:
                continue
            rows, eff = _bracket_rows(node, on)
            if rows:
                brackets[ours] = rows
                effective |= eff
                sources.extend(references(node))
                resolved[ours] = rel
        if brackets:
            return brackets, None, effective, sources, resolved, extra

    if special and special["kind"] == "flat_plus_surtax":
        node = load(z, base + special["flat"])
        v, d = value_at(node or {}, on)
        if v is not None:
            if d:
                effective.add(d)
            sources.extend(references(node))
            resolved["flat"] = special["flat"]
            sur = load(z, base + special["surtax"])
            if sur is not None:
                rows, eff = _bracket_rows(sur, on)
                if rows:
                    extra["surtax"] = rows
                    effective |= eff
                    sources.extend(references(sur))
                    resolved["surtax"] = special["surtax"]
            return {}, round(float(v) * 100, 4), effective, sources, resolved, extra

    if special and special["kind"] == "flat_scalar":
        node = load(z, base + special["flat"])
        v, d = value_at(node or {}, on)
        if v is not None:
            if d:
                effective.add(d)
            sources.extend(references(node))
            resolved["flat"] = special["flat"]
            return {}, round(float(v) * 100, 4), effective, sources, resolved, extra

    switch = FLAT_SWITCHES.get(code)
    if switch:
        sw = load(z, base + switch["switch"])
        on_flat, sd = value_at(sw or {}, on)
        if on_flat is True:
            node = load(z, base + switch["rate"])
            v, d = value_at(node or {}, on)
            if v is not None:
                for x in (sd, d):
                    if x and not x.startswith("0000"):
                        effective.add(x)
                sources.extend(references(sw))
                sources.extend(references(node))
                resolved["flatSwitch"] = switch["switch"]
                resolved["flat"] = switch["rate"]
                extra["replacedProgressiveSchedule"] = True
                return {}, round(float(v) * 100, 4), effective, sources, resolved, extra

    surtax_rel = STATE_SURTAX_FILES.get(code)
    if surtax_rel:
        sur = load(z, base + surtax_rel)
        if sur is not None:
            rows, eff = _bracket_rows(sur, on)
            rows = [r for r in rows if r["rate"] > 0]
            if rows:
                extra["surtax"] = rows
                effective |= eff
                sources.extend(references(sur))
                resolved["surtax"] = surtax_rel

    # Generic: per-filing-status bracket files.
    for layout in PER_STATUS_LAYOUTS:
        brackets = {}
        for ours, name in STATE_RATE_FILES.items():
            rel = layout.format(s=name)
            node = load(z, base + rel)
            if node is None:
                continue
            rows, eff = _bracket_rows(node, on)
            if rows:
                brackets[ours] = rows
                effective |= eff
                sources.extend(references(node))
                resolved[ours] = rel
                if is_uprated(node):
                    extra["indexed"] = True
        if brackets:
            return brackets, None, effective, sources, resolved, extra

    # Generic: one bracket table shared by all statuses.
    for rel in SHARED_BRACKET_FILES:
        node = load(z, base + rel)
        if node is None:
            continue
        rows, eff = _bracket_rows(node, on)
        if rows:
            effective |= eff
            sources.extend(references(node))
            if is_uprated(node):
                extra["indexed"] = True
            brackets = {k: [dict(r) for r in rows] for k in STATE_RATE_FILES}
            resolved = {k: rel for k in STATE_RATE_FILES}
            extra["sharedAcrossFilingStatuses"] = True
            return brackets, None, effective, sources, resolved, extra

    # Generic: a single flat scalar rate.
    for rel in FLAT_SCALAR_FILES:
        node = load(z, base + rel)
        if node is None:
            continue
        v, d = value_at(node, on)
        if v is not None:
            if d:
                effective.add(d)
            sources.extend(references(node))
            resolved["flat"] = rel
            return {}, round(float(v) * 100, 4), effective, sources, resolved, extra

    return {}, None, effective, sources, resolved, extra


def state_standard_deduction(z, code, year):
    on = "%d-12-31" % year
    node = load(z, "gov/states/%s/tax/income/deductions/standard/amount.yaml" % code)
    if node is None:
        return {}, []
    out = {}
    for ours, theirs in FILING_STATUSES.items():
        v, _ = value_at(node.get(theirs, {}) if isinstance(node, dict) else {}, on)
        if v is None:
            v, _ = value_at(node, on)  # single scalar covering all statuses
        if v is not None:
            out[ours] = v
    return out, references(node)


def build_state(z, code, year):
    name, slug = JURISDICTIONS[code]
    rec = {
        "slug": slug, "name": name, "abbr": code.upper(), "taxYear": year,
        "structure": "none", "brackets": {}, "flatRate": None,
        "standardDeduction": {}, "surtax": None,
        "localTaxNote": LOCAL_TAX_NOTES.get(code),
        "notes": [], "provenance": {}, "verification": "pending",
    }

    if code in NO_INCOME_TAX:
        rec["notes"].append(
            "No broad-based individual income tax on earned income. Federal "
            "income tax and self-employment tax still apply in full.")
        if code == "wa":
            rec["notes"].append(
                "Washington levies a tax on certain long-term capital gains; it "
                "does not apply to ordinary self-employment income.")
        if code == "nh":
            rec["notes"].append(
                "New Hampshire's interest and dividends tax has been phased out; "
                "confirm the current status for the target tax year.")
        rec["provenance"] = {"extractedFrom": "classification",
                             "resolvedPaths": {}, "sources": []}
        rec["staleForTargetYear"] = False
        return rec

    brackets, frate, eff, refs, resolved, extra = resolve_state_rates(z, code, year)
    std, srefs = state_standard_deduction(z, code, year)

    if brackets:
        distinct = {r["rate"] for rows in brackets.values() for r in rows}
        nonzero = {r for r in distinct if r > 0}
        rec["brackets"] = brackets
        if len(distinct) == 1:
            rec["structure"] = "flat"
            rec["flatRate"] = next(iter(distinct))
        elif len(nonzero) == 1 and 0 in distinct:
            # One rate preceded by a zero-rate band: a flat tax with an
            # exempt amount, not a graduated schedule.
            rec["structure"] = "flat"
            rec["flatRate"] = next(iter(nonzero))
            starts = {rows[-1]["from"] for rows in brackets.values() if rows}
            rec["zeroBracketUpTo"] = (starts.pop() if len(starts) == 1
                                      else {k: v[-1]["from"] for k, v in brackets.items()})
            rec["notes"].append(
                "Flat rate applied above an exempt amount; income below "
                "`zeroBracketUpTo` is not taxed.")
        else:
            rec["structure"] = "progressive"
    elif frate is not None:
        rec["structure"] = "flat"
        rec["flatRate"] = frate
    else:
        rec["structure"] = "unknown"
        rec["verification"] = "missing"
        rec["notes"].append(
            "Rate structure could not be extracted automatically. Enter manually "
            "from the state revenue department before shipping.")

    if extra.get("surtax"):
        rec["surtax"] = extra["surtax"]
        rec["notes"].append(
            "An additional surtax applies above a high income threshold; see "
            "the `surtax` field.")
    if extra.get("replacedProgressiveSchedule"):
        rec["notes"].append(
            "This state replaced its progressive schedule with a single flat "
            "rate; the older bracket table no longer applies.")
    if extra.get("sharedAcrossFilingStatuses"):
        rec["notes"].append(
            "This state applies one bracket table to every filing status.")

    rec["standardDeduction"] = std

    seen, sources = set(), []
    for r in refs + srefs:
        if r["url"] not in seen:
            seen.add(r["url"])
            sources.append(r)

    eff = sorted(eff)
    latest = eff[-1] if eff else None
    rec["provenance"] = {
        "extractedFrom": "policyengine-us",
        "resolvedPaths": resolved,
        "valuesEffectiveFrom": eff,
        "sources": sources,
    }
    indexed = bool(extra.get("indexed"))
    rec["provenance"]["inflationIndexed"] = indexed
    if indexed and latest and int(latest[:4]) < year:
        rec["notes"].append(
            "These figures are inflation-indexed but the latest published values "
            "take effect %s, so they are %s figures, not %d. The state had not "
            "released uprated brackets when this was extracted. Do not label "
            "them as %d on the site until confirmed."
            % (latest, latest[:4], year, year))
        rec["staleForTargetYear"] = True
    else:
        rec["staleForTargetYear"] = False
        if latest and int(latest[:4]) < year:
            rec["notes"].append(
                "Latest change took effect %s and the figures are not "
                "inflation-indexed, so they carry forward to %d unchanged."
                % (latest, year))
    return rec


# ----------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=2026)
    ap.add_argument("--out", default="src/data")
    args = ap.parse_args()

    z = zipfile.ZipFile(fetch_wheel())
    version = package_version(z)
    outdir = pathlib.Path(args.out) / ("tax-year-%d" % args.year)
    (outdir / "states").mkdir(parents=True, exist_ok=True)

    fed = build_federal(z, args.year)
    (outdir / "federal.json").write_text(
        json.dumps(fed, indent=2, ensure_ascii=False) + "\n")

    summary = []
    for code in sorted(JURISDICTIONS):
        rec = build_state(z, code, args.year)
        (outdir / "states" / ("%s.json" % rec["slug"])).write_text(
            json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
        summary.append({
            "slug": rec["slug"], "abbr": rec["abbr"], "structure": rec["structure"],
            "flatRate": rec["flatRate"],
            "bracketCount": len(rec["brackets"].get("single", [])),
            "hasStandardDeduction": bool(rec["standardDeduction"]),
            "stale": rec.get("staleForTargetYear", False),
            "verification": rec["verification"],
        })

    meta = {
        "taxYear": args.year,
        "generatedAt": datetime.datetime.now(datetime.timezone.utc)
                        .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generatedBy": "scripts/extract_tax_data.py",
        "upstream": {"package": "policyengine-us", "version": version,
                     "url": "https://pypi.org/project/policyengine-us/"},
        "sourceClass": "secondary",
        "verificationPolicy": (
            "Every value is 'pending' until checked against the primary source "
            "listed in its provenance.sources. See docs/data-verification.md."),
        "jurisdictionCount": len(summary),
        "summary": summary,
    }
    (outdir / "meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n")

    stale = [s["slug"] for s in summary if s["stale"]]
    missing = [s["slug"] for s in summary if s["verification"] == "missing"]
    print("jurisdictions: %d" % len(summary))
    print("  none/flat/progressive: %d/%d/%d" % (
        sum(1 for s in summary if s["structure"] == "none"),
        sum(1 for s in summary if s["structure"] == "flat"),
        sum(1 for s in summary if s["structure"] == "progressive")))
    print("  stale for %d: %d %s" % (args.year, len(stale), stale))
    print("  extraction gaps: %d %s" % (len(missing), missing))
    print("upstream policyengine-us %s" % version)


if __name__ == "__main__":
    main()
