/**
 * Proves the Base44 package: the bundled engine, fed only the packaged data, must
 * give exactly what the repository's engines give — cost of living, paycheck,
 * housing and everyday calculators alike.
 */
import { readFileSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import * as col from "../src/lib/col/index.js";
import { estimateWageTakeHome } from "../src/lib/tax/payroll.js";
import { closingCosts, homeAffordability, housePayment } from "../src/lib/calc/housing.js";
import { annualGrossFromHourly, propertyTax, salaryToHourly } from "../src/lib/calc/everyday.js";
import { loadEstimated, loadFederal, loadState } from "../src/lib/tax/load.js";

const dir = process.argv[2]!;
const bundle = await import(pathToFileURL(path.join(dir, "engine/lifecalc-engine.js")).href);
const read = (p: string) => JSON.parse(readFileSync(path.join(dir, p), "utf8"));
const areas = read("src/data/col/price-areas.json");
const meta = read("src/data/col/meta.json");
const baseline = read("src/data/ces-2024/baseline.json");
const years = { priceLevels: meta.years.priceLevels, rent: meta.years.rent };
const pkgTax = (slug: string) => ({
  federal: read("src/data/tax-year-2026/federal.json"),
  estimated: read("src/data/tax-year-2026/estimated.json"),
  state: read(`src/data/tax-year-2026/states/${slug}.json`),
});
const repoTax = (slug: string) => ({ federal: loadFederal(2026), estimated: loadEstimated(2026), state: loadState(2026, slug) });

let checked = 0;
const same = (label: string, a: unknown, b: unknown) => {
  const x = JSON.stringify(a), y = JSON.stringify(b);
  if (x !== y) {
    console.error(`MISMATCH ${label}\n bundle ${x.slice(0, 300)}\n repo   ${y.slice(0, 300)}`);
    process.exit(1);
  }
  checked++;
};

const colCases: [string, string, string, 1 | 2, number, string?][] = [
  ["tx", "city:Austin, TX", "texas", 1, 0],
  ["tx", "city:Houston, TX", "texas", 2, 2],
  ["ny", "city:New York, NY", "new-york", 1, 0],
  ["nc", "city:Raleigh, NC", "north-carolina", 2, 0, "37063"],
  ["ma", "area:2502507000", "massachusetts", 1, 0],
  ["il", "city:Chicago, IL", "illinois", 2, 3],
  ["ca", "city:San Francisco, CA", "california", 1, 1],
  ["fl", "city:Miami, FL", "florida", 2, 1],
];
for (const [st, key, slug, adults, children, county] of colCases) {
  const file = read(`src/data/col/places/${st}.json`);
  same(key,
    bundle.computeCostOfLiving({ taxYear: 2026, place: bundle.resolvePlace(file, areas, key, county),
      tax: pkgTax(slug), baseline, years, adults, children }),
    col.computeCostOfLiving({ taxYear: 2026, place: col.resolvePlace(file, areas, key, county),
      tax: repoTax(slug), baseline, years, adults, children }));
}
for (const [slug, wages, status, kids] of [["new-york", 150000, "single", 0], ["pennsylvania", 95000, "single", 0],
    ["maryland", 95000, "marriedJointly", 2], ["georgia", 60000, "headOfHousehold", 1]] as const) {
  const input = { taxYear: 2026, filingStatus: status, annualWages: wages, qualifyingChildren: kids };
  same(`paycheck ${slug}`, bundle.estimateWageTakeHome(input, pkgTax(slug)), estimateWageTakeHome(input, repoTax(slug)));
}
const hp = { price: 375000, downPayment: 37500, ratePercent: 6, termYears: 30,
  propertyTaxRatePercent: 1.2, insuranceAnnual: 1800, pmiRatePercent: 0.5 };
same("house payment", bundle.housePayment(hp), housePayment(hp));
const ha = { grossAnnualIncome: 120000, monthlyDebts: 500, downPayment: 80000, ratePercent: 6,
  termYears: 30, propertyTaxRatePercent: 1.2, insuranceAnnual: 1800, pmiRatePercent: 0.5 };
same("home affordability", bundle.homeAffordability(ha), homeAffordability(ha));
const cc = { price: 375000, loanAmount: 300000, ratePercent: 6, closingDay: 15, daysInClosingMonth: 30,
  propertyTaxAnnual: 4500, insuranceAnnual: 1800, escrowMonths: 3, lenderFees: 3000, titleAndSettlement: 2500, transferTax: 0 };
same("closing costs", bundle.closingCosts(cc), closingCosts(cc));
same("salary to hourly", bundle.salaryToHourly(95000), salaryToHourly(95000));
same("hourly overtime", bundle.annualGrossFromHourly({ rate: 22, hoursPerWeek: 45 }), annualGrossFromHourly({ rate: 22, hoursPerWeek: 45 }));
const pt = { marketValue: 400000, assessmentRatioPercent: 40, exemption: 0, millRate: 30 };
same("property tax", bundle.propertyTax(pt), propertyTax(pt));
console.log(`bundle matches the repository engines on ${checked} cases (every field): ` +
  "8 cost-of-living households, 4 paychecks, housing and everyday calculators");
