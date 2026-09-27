import { describe, expect, it } from "vitest";
import { loadEstimated, loadFederal, loadState } from "../load.js";
import { estimateWageTakeHome } from "../payroll.js";
import { applyBrackets } from "../brackets.js";
import { computeStateTax, supplementalTax } from "../state.js";

const YEAR = 2026;
const ny = loadState(YEAR, "new-york")!;
const cents = (n: number) => Math.round(n * 100);
const rule = ny.benefitRecapture!;
const schedule = (ti: number) => applyBrackets(cents(ti), ny.brackets.single!).tax;
const supp = (agi: number, ti: number) =>
  supplementalTax(rule, "single", cents(agi), cents(ti), schedule(ti));

// Every expected figure below is Tax Law section 601(d-5) (chapter 59 of the
// Laws of 2025, Part B) worked by hand for a single filer.
describe("New York supplemental tax, 2026", () => {
  it("does not apply at or below $107,650 of AGI", () => {
    expect(supp(107_650, 99_650)).toBe(0);
    expect(supp(60_000, 52_000)).toBe(0);
  });
  it("phases in the $567 incremental benefit from $107,650", () => {
    // 567 x (108,000 - 107,650) / 50,000 = 3.969
    expect(supp(108_000, 100_000)).toBe(397);
    // 567 x 42,350 / 50,000 = 480.249
    expect(supp(150_000, 142_000)).toBe(48_025);
    // fully phased in from $157,650
    expect(supp(160_000, 152_000)).toBe(56_700);
  });
  it("uses the recapture base and the next row above $215,400 of taxable income", () => {
    // 567 + 2,047 x min(50,000, 300,000 - 215,400) / 50,000 = 2,614
    expect(supp(300_000, 292_000)).toBe(261_400);
    // 567 + 2,047 x 10,000 / 50,000 = 976.40
    expect(supp(225_400, 217_400)).toBe(97_640);
  });
  it("below the first row takes (5.9% x income - schedule tax) x the phase-in fraction", () => {
    // schedule tax on 70,000: 331.50 + 140.80 + 113.30 + 3,029.40 = 3,615.00
    // (4,130.00 - 3,615.00) x (120,000 - 107,650) / 50,000 = 127.205
    expect(schedule(70_000)).toBe(361_500);
    expect(supp(120_000, 70_000)).toBe(12_721);
  });
  it("above $25,000,000 of AGI taxes all taxable income at 10.9%", () => {
    const ti = 30_000_000;
    expect(schedule(ti) + supp(30_008_000, ti)).toBe(cents(ti * 0.109));
  });
  it("is added to the state tax, with the higher effective marginal rate reported", () => {
    const r = computeStateTax({ federalAgi: cents(150_000), filingStatus: "single", state: ny });
    // schedule 7,809.75 + supplemental 480.25
    expect(r.amount).toBe(cents(8_290));
    // 5.9% + 567 / 50,000 = 7.034%
    expect(r.marginalRate).toBeCloseTo(7.03, 1);
    expect(r.notes.some((n) => n.includes("takes back the benefit"))).toBe(true);
  });
  it("leaves a $95,000 salary untouched", () => {
    const r = computeStateTax({ federalAgi: cents(95_000), filingStatus: "single", state: ny });
    expect(r.amount).toBe(schedule(87_000));
  });
});

describe("corrections from the primary-source register", () => {
  it("Illinois 2026 exemption is $2,925 per exemption (Bulletin FY 2026-15)", () => {
    const il = loadState(YEAR, "illinois")!;
    const r = computeStateTax({ federalAgi: cents(95_000), filingStatus: "single", state: il });
    // (95,000 - 2,925) x 4.95% = 4,557.7125
    expect(r.amount).toBe(455_771);
    const joint = computeStateTax({ federalAgi: cents(95_000), filingStatus: "marriedJointly", state: il });
    // (95,000 - 5,850) x 4.95% = 4,412.925
    expect(joint.amount).toBe(441_293);
  });
  it("Maryland 2026 standard deduction is $3,400 single (Comptroller) and $6,850 joint (section 10-217(c))", () => {
    const md = loadState(YEAR, "maryland")!;
    expect(md.standardDeduction.single).toBe(3_400);
    expect(md.standardDeduction.marriedJointly).toBe(6_850);
  });
  it("every launch state is marked verified", () => {
    for (const slug of ["texas", "florida", "pennsylvania", "north-carolina", "georgia",
                        "illinois", "maryland", "new-york"]) {
      expect(loadState(YEAR, slug)!.verification, slug).toBe("verified");
    }
  });
});

describe("state employee payroll contributions, 2026", () => {
  const federal = loadFederal(YEAR);
  const estimated = loadEstimated(YEAR);
  const pay = (slug: string, wages: number) =>
    estimateWageTakeHome({ taxYear: YEAR, filingStatus: "single", annualWages: wages },
      { federal, estimated, state: loadState(YEAR, slug) });

  it("New York: PFL 0.432% and disability 0.5% up to $0.60 a week", () => {
    const r = pay("new-york", 95_000);
    const by = Object.fromEntries(r.stateContributions.map((c) => [c.id, c.amount]));
    expect(by["ny-pfl"]).toBe(410.4);   // 95,000 x 0.432%, under the $411.91 cap
    expect(by["ny-dbl"]).toBe(31.2);    // 0.60 x 52
    expect(r.stateContributionsTotal).toBe(441.6);
    // take-home falls by exactly the contributions; tax is unchanged
    expect(r.netPay).toBe(70_656.15);
  });
  it("New York PFL stops at the $411.91 annual maximum", () => {
    const r = pay("new-york", 200_000);
    expect(r.stateContributions.find((c) => c.id === "ny-pfl")!.amount).toBe(411.91);
  });
  it("New York disability is pro-rata below $120 a week", () => {
    // 5,000 a year = 96.15 a week; 0.5% = 0.48 < 0.60, so 25.00 a year
    const r = pay("new-york", 5_000);
    expect(r.stateContributions.find((c) => c.id === "ny-dbl")!.amount).toBe(25);
  });
  it("Pennsylvania: employee UC 0.07% of all wages, no cap", () => {
    expect(pay("pennsylvania", 95_000).stateContributionsTotal).toBe(66.5);
    expect(pay("pennsylvania", 500_000).stateContributionsTotal).toBe(350);
  });
  it("contributions are on gross wages: a 401(k) deferral does not reduce them", () => {
    const r = estimateWageTakeHome(
      { taxYear: YEAR, filingStatus: "single", annualWages: 95_000, preTaxRetirement: 10_000 },
      { federal, estimated, state: loadState(YEAR, "pennsylvania") });
    expect(r.stateContributionsTotal).toBe(66.5);
  });
  it("states without contributions add nothing", () => {
    expect(pay("texas", 95_000).stateContributionsTotal).toBe(0);
  });
});
