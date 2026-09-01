#!/usr/bin/env python3
"""
Traffic and revenue model, computed from data/keywords.json.

This is a MODEL, not a forecast. Every assumption is named, defaulted in one
place, and adjustable from the command line, so a disagreement about the outcome
becomes a disagreement about a specific number rather than about a vibe.

Replace the assumptions with real data as it arrives:
  - positions      -> Google Search Console, from month 3
  - sessionDepth   -> analytics, from month 2
  - rpmMultiplier  -> the AdSense dashboard, from month 3

Usage:
    python3 scripts/model_revenue.py
    python3 scripts/model_revenue.py --rpm-multiplier 3.0 --session-depth 1.8
"""
import argparse, json, pathlib, statistics

# --- Assumptions -----------------------------------------------------------

# Organic click-through by position. Published curves vary; these are mid-range
# and deliberately conservative. Positions beyond 30 are treated as noise.
CTR_BY_POSITION = {
    1: 0.280, 2: 0.150, 3: 0.110, 4: 0.080, 5: 0.065,
    6: 0.050, 7: 0.040, 8: 0.033, 9: 0.028, 10: 0.025,
}
CTR_RANGES = [(15, 0.018), (20, 0.011), (30, 0.006)]
CTR_BEYOND = 0.002

# A keyword's difficulty is proxied by its volume: the bigger the term, the more
# entrenched the incumbents. Crude, but honest — real difficulty needs a SERP
# check per keyword, which the spec requires before any page is built.
DIFFICULTY_TIERS = [(50_000, "hard"), (10_000, "medium"), (0, "easy")]

# Where a well-executed new domain plausibly sits over time.
SCENARIOS = {
    "year1": {"label": "سال ۱ — دامنه‌ی جوان", "hard": 25, "medium": 18, "easy": 12},
    "year2": {"label": "سال ۲ — اقتدار اولیه", "hard": 14, "medium": 10, "easy": 6},
    "year3": {"label": "سال ۳ — تثبیت‌شده", "hard": 8, "medium": 6, "easy": 4},
}

DEFAULTS = {
    # AI Overviews absorb clicks on informational queries. Measured present on
    # the tax head term; assumed across the cluster until per-keyword data exists.
    "aiOverviewPenalty": 0.30,
    # Pages per session. Calculator sites without a funnel sit near 1.1; the
    # funnel in SPEC 2-2-2 is the reason to expect more.
    "sessionDepth": 2.2,
    # RPM is estimated as CPC x this. Calibrate against the real dashboard as
    # soon as there is one; it is the single least certain number here.
    "rpmMultiplier": 4.0,
}


def ctr(position: int) -> float:
    if position in CTR_BY_POSITION:
        return CTR_BY_POSITION[position]
    for limit, value in CTR_RANGES:
        if position <= limit:
            return value
    return CTR_BEYOND


def difficulty(volume: int) -> str:
    for threshold, tier in DIFFICULTY_TIERS:
        if volume >= threshold:
            return tier
    return "easy"


def load(path="data/keywords.json"):
    return json.loads(pathlib.Path(path).read_text())


def rows_from(data):
    """Flatten single keywords and programmatic sets into one comparable list."""
    rows = []
    for k in data["keywords"]:
        rows.append({
            "name": k["term"], "volume": k["volume"], "cpc": k["cpc"],
            "step": k["step"], "pages": 1, "kind": "tool",
        })
    for s in data["programmaticSets"]:
        m = s["modelled"]
        rows.append({
            "name": s["id"], "volume": m["medianVolume"] * m["pages"],
            "cpc": m["cpc"], "step": s["step"], "pages": m["pages"],
            "kind": "programmatic",
            "perPageVolume": m["medianVolume"],
        })
    return rows


def model(rows, scenario, opts):
    cluster_volume = sum(r["volume"] for r in rows)
    cluster_value = sum(r["volume"] * r["cpc"] for r in rows)
    weighted_cpc = cluster_value / cluster_volume if cluster_volume else 0
    cluster_rpm = weighted_cpc * opts["rpmMultiplier"]

    out, entries_total, revenue_total = [], 0.0, 0.0
    for r in rows:
        # Programmatic pages are ranked per page, not for the summed volume.
        volume_for_ranking = r.get("perPageVolume", r["volume"])
        position = scenario[difficulty(volume_for_ranking)]
        click_rate = ctr(position) * (1 - opts["aiOverviewPenalty"])
        entries = r["volume"] * click_rate

        entry_rpm = r["cpc"] * opts["rpmMultiplier"]
        depth = opts["sessionDepth"]
        # The entry page earns at its own RPM; the rest of the session earns at
        # the cluster average, since the visitor moves across the funnel.
        revenue = entries * (entry_rpm + cluster_rpm * (depth - 1)) / 1000

        entries_total += entries
        revenue_total += revenue
        out.append({**r, "position": position, "entries": entries,
                    "pageviews": entries * depth, "revenue": revenue})

    return {
        "clusterVolume": cluster_volume,
        "weightedCpc": weighted_cpc,
        "clusterRpm": cluster_rpm,
        "entries": entries_total,
        "pageviews": entries_total * opts["sessionDepth"],
        "revenue": revenue_total,
        "capture": entries_total / cluster_volume if cluster_volume else 0,
        "rows": sorted(out, key=lambda x: -x["revenue"]),
    }


def fmt(n, d=0):
    return f"{n:,.{d}f}"


def main():
    ap = argparse.ArgumentParser()
    for key, val in DEFAULTS.items():
        ap.add_argument("--" + key.replace("_", "-").lower()
                        .replace("aioverviewpenalty", "ai-overview-penalty")
                        .replace("sessiondepth", "session-depth")
                        .replace("rpmmultiplier", "rpm-multiplier"),
                        type=float, default=val, dest=key)
    ap.add_argument("--out", default="docs/revenue-model.md")
    args = ap.parse_args()
    opts = {k: getattr(args, k) for k in DEFAULTS}

    data = load()
    rows = rows_from(data)
    results = {name: model(rows, sc, opts) for name, sc in SCENARIOS.items()}
    base = results["year1"]

    L = []
    w = L.append
    w("# مدل ترافیک و درآمد\n")
    w("> **تولیدشده با `scripts/model_revenue.py` از `data/keywords.json`.** دستی ویرایش نکنید.\n")
    w(f"> اندازه‌گیری کیوردها: {data['measuredAt']} · بازار: {data['market']['location']}\n")
    w("\n> ⚠️ **این یک مدل است، نه پیش‌بینی.** هر فرض نام‌گذاری و پارامتری شده تا اختلاف‌نظر درباره‌ی نتیجه، به اختلاف‌نظر درباره‌ی یک عدد مشخص تبدیل شود.\n")

    w("\n## فرض‌ها\n")
    w("| فرض | مقدار | جایگزین می‌شود با |")
    w("|---|---|---|")
    w(f"| جریمه‌ی AI Overview | {opts['aiOverviewPenalty']:.0%} | بررسی SERP هر کیورد |")
    w(f"| صفحه‌به‌نشست | {opts['sessionDepth']} | تحلیل ترافیک، از ماه ۲ |")
    w(f"| ضریب RPM از CPC | ×{opts['rpmMultiplier']} | داشبورد AdSense، از ماه ۳ |")
    w("| جایگاه‌ها | جدول سناریو پایین | Search Console، از ماه ۳ |")
    w("\n**نامطمئن‌ترین عدد، ضریب RPM است.** تحلیل حساسیت پایین دقیقاً برای همین است.\n")

    w("\n## خوشه\n")
    w("| معیار | مقدار |")
    w("|---|---|")
    w(f"| حجم ماهانه‌ی خوشه | **{fmt(base['clusterVolume'])}** |")
    w(f"| CPC میانگین وزنی | **${base['weightedCpc']:.2f}** |")
    w(f"| RPM ضمنی خوشه | ${base['clusterRpm']:.2f} |")
    w(f"| تعداد ابزار | {sum(1 for r in rows if r['kind']=='tool')} |")
    w(f"| تعداد صفحه‌ی programmatic | {sum(r['pages'] for r in rows if r['kind']=='programmatic')} |")

    w("\n## سناریوها\n")
    w("| سناریو | جایگاه (سخت/متوسط/آسان) | ورود/ماه | بازدید/ماه | سهم | درآمد/ماه |")
    w("|---|---|---|---|---|---|")
    for name, sc in SCENARIOS.items():
        r = results[name]
        w(f"| {sc['label']} | {sc['hard']} / {sc['medium']} / {sc['easy']} | "
          f"{fmt(r['entries'])} | {fmt(r['pageviews'])} | {r['capture']:.1%} | "
          f"**${fmt(r['revenue'])}** |")

    target_low, target_high = 500, 700
    w(f"\n### کِی به ${target_low}-{target_high} می‌رسیم\n")
    for name, sc in SCENARIOS.items():
        r = results[name]
        mark = "✅" if r["revenue"] >= target_low else "❌"
        w(f"- {mark} **{sc['label']}**: ${fmt(r['revenue'])}/ماه")

    w("\n## تحلیل حساسیت — ضریب RPM\n")
    w("| ضریب | سال ۱ | سال ۲ | سال ۳ |")
    w("|---|---|---|---|")
    for mult in (2.0, 3.0, 4.0, 5.0, 6.0):
        o = {**opts, "rpmMultiplier": mult}
        vals = [model(rows, SCENARIOS[n], o)["revenue"] for n in SCENARIOS]
        w(f"| ×{mult} | ${fmt(vals[0])} | ${fmt(vals[1])} | ${fmt(vals[2])} |")

    w("\n## تحلیل حساسیت — عمق نشست\n")
    w("عمقی که قیف بخش ۲-۲-۲ می‌سازد، مستقیماً ضریب درآمد است.\n")
    w("| صفحه‌به‌نشست | سال ۲ | تفاوت با ۱.۱ |")
    w("|---|---|---|")
    baseline = model(rows, SCENARIOS["year2"], {**opts, "sessionDepth": 1.1})["revenue"]
    for depth in (1.1, 1.5, 2.2, 3.0):
        v = model(rows, SCENARIOS["year2"], {**opts, "sessionDepth": depth})["revenue"]
        w(f"| {depth} | ${fmt(v)} | {'—' if depth==1.1 else f'+{v/baseline-1:.0%}'} |")

    w("\n## سهم هر ابزار (سناریوی سال ۲)\n")
    w("| ابزار | مرحله | حجم | CPC | جایگاه | ورود/ماه | درآمد/ماه |")
    w("|---|---|---|---|---|---|---|")
    for r in results["year2"]["rows"]:
        w(f"| {r['name']} | {r['step']} | {fmt(r['volume'])} | ${r['cpc']:.2f} | "
          f"{r['position']} | {fmt(r['entries'])} | ${fmt(r['revenue'])} |")

    w("\n## آنچه عمداً بیرون گذاشته شد\n")
    ex = data["excluded"]
    w(f"{len(ex)} کیورد با جمع **{fmt(sum(e['volume'] for e in ex))}** جستجوی ماهانه:\n")
    w("| کیورد | حجم | CPC | دلیل |")
    w("|---|---|---|---|")
    for e in sorted(ex, key=lambda x: -x["volume"]):
        w(f"| {e['term']} | {fmt(e['volume'])} | ${e['cpc']:.2f} | {e['reason']} |")
    w("\nاین حجم عمداً رها شده تا context واحد بماند. قید صریح پروژه (بخش ۲-۲) این را بر درآمد کوتاه‌مدت مقدم می‌داند.\n")

    pathlib.Path(args.out).write_text("\n".join(L) + "\n")
    print(f"wrote {args.out}")
    print(f"cluster {fmt(base['clusterVolume'])} @ ${base['weightedCpc']:.2f} CPC")
    for name, sc in SCENARIOS.items():
        r = results[name]
        print(f"  {name:6} pos {sc['hard']}/{sc['medium']}/{sc['easy']}  "
              f"{fmt(r['pageviews']):>9} pv  {r['capture']:5.1%}  ${fmt(r['revenue']):>7}/mo")


if __name__ == "__main__":
    main()
