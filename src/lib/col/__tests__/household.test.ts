import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import type { EngineData } from "../../tax/index.js";
import { loadEstimated, loadFederal, loadState } from "../../tax/load.js";
import { estimateWageTakeHome } from "../../tax/payroll.js";
import {
  cityMonthlyCost,
  equivalentSalaryAfterTax,
  grossForNet,
  referenceRentFromFmr,
  suggestedBedrooms,
  type PlaceCostData,
  type SpendingBaseline,
} from "../index.js";

// REAL: HUD FY2026 Fair Market Rents imported by scripts/import_hud_fmr.py.
const fmr = JSON.parse(readFileSync("src/data/rent-fy2026/fmr-counties.json", "utf8"));

// FIXTURES: price indices and the spending baseline are synthetic until the BEA
// and BLS datasets are fetched. They test arithmetic, never real-world claims.
const place = (slug: string, name: string, fips: string, allItems: number, goods: number, other: number, state: string): PlaceCostData => ({
  slug, name, type: "metro", region: "us", dataYear: 2024, stateSlug: state,
  indices: { allItems, goods, otherServices: other },
  referenceRent: referenceRentFromFmr(fmr.counties[fips]),
  sources: [], lastVerified: "", verification: "pending",
});
const AUSTIN = place("austin-tx", "Austin, TX", "48453", 100, 100, 100, "texas");
const SF = place("san-francisco-ca", "San Francisco, CA", "06075", 120, 105, 110, "california");

const baseline: SpendingBaseline = {
  year: 2024, verification: "pending",
  source: { label: "FIXTURE", url: "", retrieved: "" },
  categories: {
    food_home: { label: "Groceries", index: "goods" },
    food_away: { label: "Eating out", index: "otherServices" },
    transport: { label: "Transportation", index: "goods" },
    health: { label: "Health care", index: "otherServices" },
  },
  annualByHouseholdSize: {
    "1": { food_home: 3600, food_away: 2400, transport: 6000, health: 3000 },
    "2": { food_home: 6000, food_away: 3600, transport: 10800, health: 6000 },
    "3": { food_home: 7200, food_away: 4200, transport: 12000, health: 7200 },
    "4": { food_home: 8400, food_away: 4800, transport: 13200, health: 8400 },
    "5": { food_home: 9600, food_away: 4800, transport: 13200, health: 9000 },
  },
};

const YEAR = 2026;
const federal = loadFederal(YEAR), estimated = loadEstimated(YEAR);
const tax = (s: string): EngineData => ({ federal, estimated, state: loadState(YEAR, s) });
const cents = (n: number) => Math.round(n * 100);

describe("HUD rent data is wired through", () => {
  it("reads Travis County's FY2026 one-bedroom Fair Market Rent", () => {
    expect(AUSTIN.referenceRent?.bedrooms1).toBe(1562);
    expect(SF.referenceRent?.bedrooms2).toBe(3604);
  });
  it("gives no single figure for a county HUD prices by town", () => {
    const town = fmr.townLevelCounties[0];
    expect(referenceRentFromFmr(fmr.counties[town])).toBeNull();
  });
});

describe("what one place costs a household", () => {
  const r = cityMonthlyCost({ place: AUSTIN, householdSize: 1, bedrooms: 1, baseline });
  it("puts HUD rent first and prices every other line locally", () => {
    expect(r.rows[0]).toMatchObject({ key: "rent", monthly: 1562, basis: "HUD Fair Market Rent" });
    // at an index of 100: 3,600 / 12 = 300 groceries
    expect(r.rows.find((x) => x.key === "food_home")!.monthly).toBe(300);
  });
  it("totals to the cent", () => {
    // 1,562 + (3,600 + 2,400 + 6,000 + 3,000) / 12 = 1,562 + 1,250 = 2,812
    expect(r.monthlyTotal).toBe(2812);
    expect(r.annualTotal).toBe(33_744);
  });
  it("applies each category's own price index", () => {
    const s = cityMonthlyCost({ place: SF, householdSize: 1, bedrooms: 1, baseline });
    // goods 105: 300 x 1.05 = 315 ; services 110: 200 x 1.10 = 220
    expect(s.rows.find((x) => x.key === "food_home")!.monthly).toBe(315);
    expect(s.rows.find((x) => x.key === "food_away")!.monthly).toBe(220);
  });
  it("lets the household replace any line with its own figure", () => {
    const own = cityMonthlyCost({ place: AUSTIN, householdSize: 1, bedrooms: 1, baseline, own: { transport: 250 } });
    expect(own.rows.find((x) => x.key === "transport")).toMatchObject({ monthly: 250, basis: "your figure" });
  });
  it("scales with household size and bedrooms from data, not a multiplier", () => {
    const four = cityMonthlyCost({ place: AUSTIN, householdSize: 4, bedrooms: suggestedBedrooms(4), baseline });
    expect(four.rows[0]!.monthly).toBe(1852);          // HUD 2-bedroom
    expect(four.monthlyTotal).toBeGreaterThan(r.monthlyTotal);
  });
  it("refuses a place with no price level instead of guessing", () => {
    const bare = { ...AUSTIN, indices: { allItems: 0 } };
    expect(() => cityMonthlyCost({ place: bare, householdSize: 1, bedrooms: 1, baseline })).toThrow(/no price level/);
  });
});

describe("suggested bedrooms", () => {
  it("defaults to two people per bedroom, at least one", () => {
    expect([1, 2, 3, 4, 5].map(suggestedBedrooms)).toEqual([1, 1, 2, 2, 3]);
  });
});

describe("equivalent salary after tax", () => {
  const r = equivalentSalaryAfterTax(
    { taxYear: YEAR, filingStatus: "single", salary: 95_000 },
    { place: AUSTIN, tax: tax("texas") },
    { place: SF, tax: tax("california") },
  );
  it("holds after-tax spending power constant", () => {
    // Texas net 75,662.50 x 120/100 = 90,795.00 needed in California
    expect(cents(r.originNetPay)).toBe(7_566_250);
    expect(cents(r.targetNetAtDestination)).toBe(9_079_500);
    const net = estimateWageTakeHome({ taxYear: YEAR, filingStatus: "single", annualWages: r.equivalentGross }, tax("california")).netPay;
    expect(net).toBeGreaterThanOrEqual(90_795);
    const below = estimateWageTakeHome({ taxYear: YEAR, filingStatus: "single", annualWages: r.equivalentGross - 0.01 }, tax("california")).netPay;
    expect(below).toBeLessThan(90_795);
  });
  it("needs more than the price-only answer when moving to a taxed state", () => {
    expect(r.priceOnlyEquivalent).toBe(114_000);
    expect(r.equivalentGross).toBeGreaterThan(114_000);
    expect(cents(r.taxAdjustment)).toBe(cents(r.equivalentGross - 114_000));
  });
  it("returns the same salary for the same place", () => {
    const same = equivalentSalaryAfterTax(
      { taxYear: YEAR, filingStatus: "single", salary: 95_000 },
      { place: AUSTIN, tax: tax("texas") }, { place: AUSTIN, tax: tax("texas") });
    expect(same.equivalentGross).toBe(95_000);
  });
});

describe("gross for net", () => {
  it("is zero for a zero target", () => {
    expect(grossForNet(0, () => 0)).toBe(0);
  });
});
