import { describe, expect, it } from "vitest";
import { loadEstimated, loadFederal, loadState } from "../load.js";
import { estimateWageTakeHome } from "../payroll.js";
import { applyBrackets } from "../brackets.js";
import { computeStateTax, exemptionCredits, supplementalTax } from "../state.js";

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
                        "illinois", "maryland", "new-york", "tennessee", "virginia",
                        "michigan", "indiana", "california"]) {
      expect(loadState(YEAR, slug)!.verification, slug).toBe("verified");
    }
  });
});

describe("California exemption credits, 2026", () => {
  const ca = loadState(YEAR, "california")!;
  const rule = ca.exemptionCredits!;
  it("are $158 per filer and $491 per dependent below the threshold", () => {
    expect(exemptionCredits(rule, "single", cents(95_000), 0)).toBe(15_800);
    expect(exemptionCredits(rule, "marriedJointly", cents(95_000), 2)).toBe(31_600 + 98_200);
  });
  it("lose $6 each for every $2,500, or part of it, above $260,778 single", () => {
    // 300,000 - 260,778 = 39,222 -> 16 steps -> 96 off each credit
    expect(exemptionCredits(rule, "single", cents(300_000), 0)).toBe(6_200);
    // $1,250 steps when married filing separately: 32 steps -> 192, so the credit is gone
    expect(exemptionCredits(rule, "marriedSeparately", cents(300_000), 0)).toBe(0);
  });
  it("cannot take the tax below zero", () => {
    const r = computeStateTax({ federalAgi: cents(12_000), filingStatus: "single", state: ca });
    // taxable 6,100 x 1% = 61.00, less 158 -> 0
    expect(r.amount).toBe(0);
  });
  it("leave the 1% Behavioral Health Services Tax above $1,000,000 untouched", () => {
    const r = computeStateTax({ federalAgi: cents(1_105_900), filingStatus: "single", state: ca });
    expect(r.surtax).toBe(cents(1_000));
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
  it("California: SDI at 1.3% of all wages, no wage limit", () => {
    expect(pay("california", 95_000).stateContributionsTotal).toBe(1_235);
    expect(pay("california", 500_000).stateContributionsTotal).toBe(6_500);
  });
  it("states without contributions add nothing", () => {
    expect(pay("texas", 95_000).stateContributionsTotal).toBe(0);
  });
});

describe("children: the federal child tax credit and state allowances, 2026", () => {
  const federal = loadFederal(YEAR);
  const estimated = loadEstimated(YEAR);
  const pay = (slug: string, wages: number, status: "single" | "marriedJointly" | "headOfHousehold", kids: number) =>
    estimateWageTakeHome({ taxYear: YEAR, filingStatus: status, annualWages: wages, qualifyingChildren: kids },
      { federal, estimated, state: loadState(YEAR, slug) });

  it("credit of $2,200 a child against federal tax (joint, $95,000, two children)", () => {
    // taxable 95,000 - 32,200 = 62,800: 24,800 x 10% + 38,000 x 12% = 7,040; less 4,400
    expect(pay("texas", 95_000, "marriedJointly", 2).federalTax).toBe(2_640);
  });
  it("refundable up to $1,700 a child when there is no tax to offset", () => {
    // $30,000 joint: taxable 0, so the whole 4,400 is unused;
    // refundable = min(4,400, 2 x 1,700, 15% x (30,000 - 2,500) = 4,125) = 3,400
    expect(pay("texas", 30_000, "marriedJointly", 2).federalTax).toBe(-3_400);
  });
  it("phases out by $50 per $1,000 (or part) above $200,000 for a head of household", () => {
    // AGI 210,500: 10,500 over, 11 steps, 550 off a 2,200 credit
    const withKid = pay("texas", 210_500, "headOfHousehold", 1).federalTax;
    const without = pay("texas", 210_500, "headOfHousehold", 0).federalTax;
    expect(without - withKid).toBe(1_650);
  });
  it("Illinois: dependents at the $2,925 exemption", () => {
    // (95,000 - 5,850 - 2 x 2,925) x 4.95% = 4,123.35
    expect(pay("illinois", 95_000, "marriedJointly", 2).stateTax).toBe(4_123.35);
  });
  it("North Carolina: $1,500 a child between $80,000 and $100,000 of joint AGI", () => {
    // (95,000 - 25,500 - 3,000) x 3.99% = 2,653.35
    expect(pay("north-carolina", 95_000, "marriedJointly", 2).stateTax).toBe(2_653.35);
  });
  it("Georgia: $5,000 a dependent", () => {
    // (95,000 - 30,000 - 10,000) x 4.99% = 2,744.50
    expect(pay("georgia", 95_000, "marriedJointly", 2).stateTax).toBe(2_744.5);
  });
  it("New York: $1,000 a dependent", () => {
    // taxable 95,000 - 16,050 - 2,000 = 76,950
    // 668.85 + 283.80 + 221.45 + 5.4% x 49,050 (2,648.70) = 3,822.80
    expect(pay("new-york", 95_000, "marriedJointly", 2).stateTax).toBe(3_822.8);
  });
  it("Maryland: two personal exemptions on a joint return, plus $3,200 a dependent", () => {
    // 95,000 - 6,850 - 6,400 - 6,400 = 75,350; 20 + 30 + 40 + 4.75% x 72,350 = 3,526.63
    expect(pay("maryland", 95_000, "marriedJointly", 2).stateTax).toBe(3_526.63);
  });
  it("Virginia: $8,750 / $17,500 standard deduction and $930 a person, dependents included", () => {
    // single: 95,000 - 8,750 - 930 = 85,320; 60 + 60 + 600 + 5.75% x 68,320 (3,928.40) = 4,648.40
    expect(pay("virginia", 95_000, "single", 0).stateTax).toBe(4_648.4);
    // joint, two children: 95,000 - 17,500 - 4 x 930 = 73,780; 720 + 5.75% x 56,780 = 3,984.85
    expect(pay("virginia", 95_000, "marriedJointly", 2).stateTax).toBe(3_984.85);
  });
  it("Michigan: 4.25% after $5,900 for each person", () => {
    // (95,000 - 5,900) x 4.25% = 3,786.75
    expect(pay("michigan", 95_000, "single", 0).stateTax).toBe(3_786.75);
    // (95,000 - 4 x 5,900) x 4.25% = 3,034.50
    expect(pay("michigan", 95_000, "marriedJointly", 2).stateTax).toBe(3_034.5);
  });
  it("Indiana: 2.95% after $1,000 a person and a further $1,500 a child", () => {
    // (95,000 - 1,000) x 2.95% = 2,773.00
    expect(pay("indiana", 95_000, "single", 0).stateTax).toBe(2_773);
    // (95,000 - 2,000 - 2 x 1,000 - 2 x 1,500) x 2.95% = 2,596.00
    expect(pay("indiana", 95_000, "marriedJointly", 2).stateTax).toBe(2_596);
  });
  it("Tennessee takes nothing from wages", () => {
    expect(pay("tennessee", 95_000, "marriedJointly", 2).stateTax).toBe(0);
  });
  it("California: $5,900 standard deduction, then the schedule, less the $158 exemption credit", () => {
    // taxable 89,100: 3,310.88 + 9.3% x 13,903 (1,292.98) = 4,603.86; less 158 = 4,445.86
    expect(pay("california", 95_000, "single", 0).stateTax).toBe(4_445.86);
    // joint, two children: taxable 83,200: 857.16 + 4% x 28,886 = 2,012.60;
    // less 2 x 158 and 2 x 491 = 1,298 -> 714.60
    expect(pay("california", 95_000, "marriedJointly", 2).stateTax).toBe(714.6);
  });
  it("Pennsylvania allows nothing for dependents", () => {
    expect(pay("pennsylvania", 95_000, "marriedJointly", 2).stateTax).toBe(2_916.5);
  });
});
