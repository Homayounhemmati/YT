/**
 * Acceptance cases for the calculators as built on the platform.
 *
 * Base44 implements its own calculators; this repository's engines are the
 * reference. Every case below is computed by the engine at generation time, so
 * the table cannot drift from the tested code. Enter each input into the built
 * calculator: every output must match to the cent (or to the stated rounding).
 *
 * Output: docs/calculator-acceptance.md
 */
import { writeFileSync } from "node:fs";
import { loadEstimated, loadFederal, loadState } from "../src/lib/tax/load.js";
import { estimateWageTakeHome } from "../src/lib/tax/payroll.js";
import { closingCosts, homeAffordability, housePayment } from "../src/lib/calc/housing.js";
import { addSalesTax, annualGrossFromHourly, propertyTax, removeSalesTax, salaryToHourly } from "../src/lib/calc/everyday.js";
import { readFileSync } from "node:fs";
import { referenceRentFromFmr, rentAffordability, type PlaceCostData } from "../src/lib/col/index.js";

const YEAR = 2026;
const federal = loadFederal(YEAR), estimated = loadEstimated(YEAR);
const tax = (s: string) => ({ federal, estimated, state: loadState(YEAR, s) });
const usd = (n: number) => (n < 0 ? "-$" : "$") + Math.abs(n).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const rows: string[] = [];
const section = (title: string, head: string[], body: (string | number)[][]) => {
  rows.push(`\n## ${title}\n`, `| ${head.join(" | ")} |`, `|${head.map(() => "---").join("|")}|`);
  for (const r of body) rows.push(`| ${r.join(" | ")} |`);
};

// Paycheck / take-home
const pay = (w: number, s: string, extra: Record<string, number> = {}, periods: 52 | 26 | 24 | 12 = 26) => {
  const r = estimateWageTakeHome({ taxYear: YEAR, filingStatus: "single", annualWages: w, payPeriods: periods, ...extra }, tax(s));
  return [usd(w), s, periods, usd(r.fica.total), usd(r.federalTax), usd(r.stateTax), usd(r.stateContributionsTotal), usd(r.netPay), usd(r.netPerPaycheck[0]!)];
};
section("Paycheck / take-home pay (single filer, 2026)",
  ["Salary", "State", "Checks/yr", "FICA", "Federal", "State tax", "State contrib.", "Net / year", "First check"],
  [pay(95000, "texas"), pay(95000, "pennsylvania"), pay(95000, "california"), pay(95000, "new-york", {}, 24),
   pay(60000, "florida", {}, 52), pay(250000, "texas"), pay(95000, "pennsylvania", { preTaxRetirement: 10000 }),
   pay(95000, "maryland"), pay(95000, "illinois"), pay(300000, "illinois"),
   pay(150000, "new-york"), pay(300000, "new-york")]);
rows.push("", "The Pennsylvania row with a $10,000 401(k) deferral: FICA must be unchanged from the row " +
  "without it, federal tax lower, and Pennsylvania tax unchanged (Pennsylvania taxes deferrals).",
  "", "Maryland uses the 2026 standard deduction ($3,400 single) and the $3,200 exemption; Illinois " +
  "the 2026 exemption ($2,925), which disappears above $250,000 of AGI. The New York rows at " +
  "$150,000 and $300,000 include the section 601(d-5) supplemental tax ($480.25 and $2,614.00 on " +
  "top of the bracket tax): a build that applies only the bracket table fails them.",
  "", "State contributions: New York Paid Family Leave 0.432% of gross wages (maximum $411.91) plus " +
  "disability insurance 0.5% up to $0.60 a week; Pennsylvania employee unemployment 0.07% of all wages. " +
  "Both are on gross wages, so a 401(k) deferral does not reduce them. California is shown on 2025 " +
  "brackets without its SDI contribution and is not published until both are entered.");

// Hourly mode
const hr = (rate: number, hours: number, s: string) => {
  const g = annualGrossFromHourly({ rate, hoursPerWeek: hours });
  const r = estimateWageTakeHome({ taxYear: YEAR, filingStatus: "single", annualWages: g.annual, payPeriods: 26 }, tax(s));
  return [usd(rate), hours, s, usd(g.regular), usd(g.overtime), usd(g.annual), usd(r.netPay), usd(r.netPerPaycheck[0]!)];
};
section("Paycheck, hourly mode (overtime at 1.5x above 40 hours; biweekly)",
  ["Rate", "Hours/week", "State", "Regular / yr", "Overtime / yr", "Gross / yr", "Net / yr", "First check"],
  [hr(25, 40, "texas"), hr(25, 45, "texas"), hr(18.5, 32, "florida")]);

// House payment
const hp = (price: number, down: number, rate: number, t: number) => {
  const r = housePayment({ price, downPayment: down, ratePercent: rate, termYears: 30,
    propertyTaxRatePercent: t, insuranceAnnual: 1800, pmiRatePercent: 0.5 });
  return [usd(price), usd(down), `${rate}%`, `${t}%`, usd(r.principalAndInterest), usd(r.pmi), usd(r.total), r.pmiEndsAfterMonth ?? "—"];
};
section("House payment (30 years, insurance $1,800/yr, PMI 0.5%)",
  ["Price", "Down", "Rate", "Tax rate", "P&I", "PMI", "Total / month", "PMI ends after month"],
  [hp(375000, 75000, 6, 1.2), hp(375000, 37500, 6, 1.2), hp(400000, 40000, 7, 1.5)]);

// Home affordability
const ha = (inc: number, debts: number) => {
  const r = homeAffordability({ grossAnnualIncome: inc, monthlyDebts: debts, downPayment: 80000, ratePercent: 6,
    termYears: 30, propertyTaxRatePercent: 1.2, insuranceAnnual: 1800, pmiRatePercent: 0.5 });
  return [usd(inc), usd(debts), usd(r.housingBudget), r.bindingRatio, usd(r.maxPrice)];
};
section("Home affordability (28/36, $80,000 down, 6%, 30 years, tax 1.2%, insurance $1,800, PMI 0.5%)",
  ["Income", "Monthly debts", "Housing budget", "Binding ratio", "Max price"],
  [ha(120000, 500), ha(120000, 1500), ha(80000, 0)]);

// Closing costs
const cc = closingCosts({ price: 375000, loanAmount: 300000, ratePercent: 6, closingDay: 15, daysInClosingMonth: 30,
  propertyTaxAnnual: 4500, insuranceAnnual: 1800, escrowMonths: 3, lenderFees: 3000, titleAndSettlement: 2500, transferTax: 0 });
section("Closing costs ($375,000, $300,000 loan at 6%, closing on the 15th of a 30-day month)",
  ["Prepaid interest", "Insurance (1st yr)", "Escrow (3 months)", "Lender", "Title", "Total", "% of price"],
  [[usd(cc.prepaidInterest), usd(cc.firstYearInsurance), usd(cc.escrowReserves), usd(cc.lenderFees),
    usd(cc.titleAndSettlement), usd(cc.total), cc.percentOfPrice.toFixed(2) + "%"]]);

// Salary to hourly, sales tax, property tax, rent
const h = salaryToHourly(95000), h2 = salaryToHourly(95000, { hoursPerWeek: 40, paidWeeks: 52, paidLeaveWeeks: 3 });
section("Salary to hourly", ["Salary", "Basis", "Hourly"],
  [[usd(95000), "40 h × 52 wk", usd(h.hourly)], [usd(95000), "3 weeks paid leave (effective)", usd(h2.effectiveHourly)]]);
const st = { statePercent: 6.25, countyPercent: 0.5, cityPercent: 1, specialPercent: 0.5 };
const a = addSalesTax(100, st), b = removeSalesTax(108.25, st);
section("Sales tax (6.25% + 0.5% + 1% + 0.5% = 8.25%)", ["Direction", "Input", "Pre-tax", "Tax", "Total"],
  [["add", usd(100), usd(a.preTax), usd(a.tax), usd(a.total)], ["remove", usd(108.25), usd(b.preTax), usd(b.tax), usd(b.total)]]);
const pt = propertyTax({ marketValue: 400000, assessmentRatioPercent: 40, exemption: 0, millRate: 30 });
section("Property tax", ["Market value", "Assessment", "Mills", "Annual", "Effective rate"],
  [[usd(400000), "40%", 30, usd(pt.annualTax), pt.effectiveRatePercent.toFixed(3) + "%"]]);
const ra = rentAffordability({ grossAnnualIncome: 60000 });
section("Rent affordability", ["Income", "30% ceiling", "50% line", "3× screen"],
  [[usd(60000), usd(ra.ceiling), usd(ra.severeLine), usd(ra.landlordScreenMax)]]);

// Real HUD FY2026 rents, from scripts/import_hud_fmr.py
const fmr = JSON.parse(readFileSync("src/data/rent-fy2026/fmr-counties.json", "utf8"));
const county = (fips: string): PlaceCostData => ({
  slug: fips, name: `${fmr.counties[fips].name}, ${fmr.counties[fips].state}`, type: "metro", region: "us",
  dataYear: fmr.fiscalYear, stateSlug: null, indices: { allItems: 100 },
  referenceRent: referenceRentFromFmr(fmr.counties[fips]), sources: [], lastVerified: "", verification: "pending",
});
const rr = (inc: number, fips: string, b: 0 | 1 | 2 | 3) => {
  const r = rentAffordability({ grossAnnualIncome: inc, place: county(fips), bedrooms: b });
  const m = r.market!;
  return [usd(inc), county(fips).name, b, usd(m.fairMarketRent), m.shareOfIncome.toFixed(1) + "%", m.burden, usd(m.headroom), usd(m.incomeNeededAt30)];
};
section(`Rent affordability against HUD FY${fmr.fiscalYear} Fair Market Rent (real data)`,
  ["Income", "County", "Bedrooms", "HUD rent", "Share of income", "Burden", "Headroom", "Income needed at 30%"],
  [rr(60000, "48453", 1), rr(60000, "06075", 1), rr(85000, "48201", 2), rr(45000, "48029", 0)]);

const head = [
  "# Calculator acceptance cases",
  "",
  "> **Generated by `scripts/acceptance_cases.ts` from the tested engines. Do not edit by hand.**",
  "> Base44 builds its own calculators; these are the reference answers. Enter each input into",
  "> the built calculator. A calculator that differs by more than one cent on any row is wrong,",
  "> and it is the calculator that changes, not this file.",
  "",
  "Cost-of-living, comparison and living-wage cases are added once the BEA/HUD dataset exists:",
  "their answers depend on published indices, and fixture indices must never be shown as real.",
];
writeFileSync("docs/calculator-acceptance.md", head.join("\n") + "\n" + rows.join("\n") + "\n");
console.log("wrote docs/calculator-acceptance.md");
