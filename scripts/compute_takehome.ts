/**
 * Compute the $95,000 figures the site quotes, in every jurisdiction, using the
 * engines rather than an estimate.
 *
 * Two scenarios, because they are different people with different tax bills:
 *
 *   salary        — an employee on a $95,000 salary. This is what every "salary"
 *                   question on the site asks about, and what the top-level
 *                   fields below carry.
 *   selfEmployed  — $95,000 of self-employment profit, which pays both halves of
 *                   FICA. Earlier versions quoted THIS figure under the word
 *                   "salary" on 51 state pages; it understated an employee's
 *                   take-home by several thousand dollars.
 *
 * Output: data/takehome-95k.json, consumed by scripts/generate_onpage.py.
 */
import { readdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { estimateTax, type EngineData } from "../src/lib/tax/index.js";
import { loadEstimated, loadFederal, loadState } from "../src/lib/tax/load.js";
import { estimateWageTakeHome } from "../src/lib/tax/payroll.js";
import { applyBrackets } from "../src/lib/tax/brackets.js";
import { computeStateTax } from "../src/lib/tax/state.js";

const YEAR = 2026;
const AMOUNT = 95_000;

const federal = loadFederal(YEAR);
const estimated = loadEstimated(YEAR);

const statesDir = path.join(process.cwd(), "src/data/tax-year-2026/states");
const slugs = readdirSync(statesDir)
  .filter((f) => f.endsWith(".json"))
  .map((f) => f.replace(/\.json$/, ""))
  .sort();

const round = (n: number) => Math.round(n * 100) / 100;
const pct = (tax: number) => +((tax / AMOUNT) * 100).toFixed(1);

const out: Record<string, unknown> = {};
for (const slug of slugs) {
  const state = loadState(YEAR, slug);
  const data: EngineData = { federal, estimated, state };

  const w = estimateWageTakeHome(
    { taxYear: YEAR, filingStatus: "single", annualWages: AMOUNT },
    data,
  );

  const se = estimateTax(
    { taxYear: YEAR, filingStatus: "single", businessIncome: AMOUNT },
    data,
  );
  const seBaseline = estimateTax(
    { taxYear: YEAR, filingStatus: "single", businessIncome: AMOUNT },
    { federal, estimated, state: null },
  );

  // A state that recaptures its lower brackets (New York) gets a second worked
  // example inside the phase-in range, so the copy that explains it can quote
  // engine figures rather than hand arithmetic.
  let recaptureExample: Record<string, number> | undefined;
  const rule = state.benefitRecapture;
  const rows = state.brackets.single;
  if (rule && rows) {
    const salary = 150_000;
    const agi = salary * 100;
    const r = computeStateTax({ federalAgi: agi, filingStatus: "single", state });
    const scheduleOnly = applyBrackets(r.taxableIncome, rows).tax;
    recaptureExample = {
      salary,
      stateTax: r.amount / 100,
      scheduleOnly: scheduleOnly / 100,
      supplemental: (r.amount - scheduleOnly) / 100,
      marginalInPhaseIn: r.marginalRate,
      phaseInEnds: rule.agiFloor + rule.phaseWidth,
    };
  }

  out[slug] = {
    ...(recaptureExample ? { recaptureExample } : {}),
    name: state.name,
    structure: state.structure,
    scenario: "salary",
    gross: AMOUNT,
    totalTax: round(w.totalTax),
    takeHome: round(w.netPay),
    stateTax: round(w.stateTax),
    fica: round(w.fica.total),
    contributions: round(w.stateContributionsTotal),
    contributionItems: w.stateContributions.map((c) => ({ name: c.name, amount: round(c.amount) })),
    federalTax: round(w.federalTax),
    effectiveRate: pct(w.totalTax),
    warnings: w.warnings,
    selfEmployed: {
      totalTax: round(se.totalTax),
      takeHome: round(se.takeHome),
      stateTax: round(se.totalTax - seBaseline.totalTax),
      effectiveRate: pct(se.totalTax),
    },
  };
}

// Cross-state figures quoted in copy use VERIFIED states only (data/tax-primary):
// an unverified state's model can be missing a whole provision (Oregon's federal
// tax subtraction), and a national "best minus worst" would inherit that error.
type Out = { name: string; takeHome: number; stateTax: number; contributions: number; selfEmployed: { takeHome: number } };
const verified = slugs.filter((s) => loadState(YEAR, s).verification === "verified");
const vrows = verified.map((s) => [s, out[s] as Out] as const);
const best = vrows.reduce((a, b) => (b[1].takeHome > a[1].takeHome ? b : a));
const worst = vrows.reduce((a, b) => (b[1].takeHome < a[1].takeHome ? b : a));
const seGap = vrows.map(([, r]) => round(r.takeHome - r.selfEmployed.takeHome));
const verifiedSpread = {
  states: verified,
  best: { slug: best[0], takeHome: best[1].takeHome },
  worst: { slug: worst[0], takeHome: worst[1].takeHome, stateTax: worst[1].stateTax,
           contributions: worst[1].contributions },
  spread: round(best[1].takeHome - worst[1].takeHome),
  spreadPctOfGross: +(((best[1].takeHome - worst[1].takeHome) / AMOUNT) * 100).toFixed(1),
  selfEmployedGapMin: Math.min(...seGap),
  selfEmployedGapMax: Math.max(...seGap),
};
console.log(`verified   ${verified.length} states · spread $${verifiedSpread.spread} ` +
  `(${verifiedSpread.spreadPctOfGross}%) · self-employed gap $${verifiedSpread.selfEmployedGapMin}` +
  `-$${verifiedSpread.selfEmployedGapMax}`);

writeFileSync(
  "data/takehome-95k.json",
  JSON.stringify(
    {
      $comment:
        "GENERATED by scripts/compute_takehome.ts. Do not edit by hand. Single " +
        "filer, $95,000, no other income or deductions. Top-level fields are the " +
        "SALARY scenario (employee FICA); `selfEmployed` holds the self-employment " +
        "scenario. Never quote a selfEmployed figure under the word 'salary'.",
      taxYear: YEAR,
      scenario: { filingStatus: "single", amount: AMOUNT },
      verifiedSpread,
      states: out,
    },
    null,
    2,
  ) + "\n",
);

type Row = { name: string; takeHome: number; selfEmployed: { takeHome: number } };
const values = Object.values(out) as Row[];
const report = (label: string, pick: (r: Row) => number) => {
  const s = [...values].sort((a, b) => pick(b) - pick(a));
  const best = s[0]!, worst = s[s.length - 1]!;
  console.log(
    `${label.padEnd(14)} best ${best.name} $${pick(best).toLocaleString()} · ` +
      `worst ${worst.name} $${pick(worst).toLocaleString()} · ` +
      `spread $${round(pick(best) - pick(worst)).toLocaleString()}`,
  );
};
console.log(`computed ${values.length} jurisdictions at $${AMOUNT.toLocaleString()}`);
report("salary", (r) => r.takeHome);
report("self-employed", (r) => r.selfEmployed.takeHome);
