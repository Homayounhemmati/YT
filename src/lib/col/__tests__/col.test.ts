import { describe, expect, it } from "vitest";
import type { EngineData } from "../../tax/index.js";
import { loadEstimated, loadFederal, loadState } from "../../tax/load.js";
import { estimateWageTakeHome } from "../../tax/payroll.js";
import {
  burdenLevel,
  compareWithTax,
  equivalentSalary,
  livingWage,
  rentAffordability,
  scaleCosts,
  type PlaceCostData,
} from "../index.js";

// FIXTURES. These index values are synthetic, chosen so the arithmetic can be
// checked by hand. They are NOT BEA or HUD figures and must never be published.
const base = {
  type: "metro" as const,
  region: "us" as const,
  dataYear: 2024,
  sources: [],
  lastVerified: "",
  verification: "pending" as const,
};
const A: PlaceCostData = {
  ...base,
  slug: "fixture-a",
  name: "Fixture A",
  stateSlug: "texas",
  indices: { allItems: 100, rent: 100, goods: 100, otherServices: 100 },
  referenceRent: { bedrooms1: 1200, bedrooms2: 1500 },
};
const B: PlaceCostData = {
  ...base,
  slug: "fixture-b",
  name: "Fixture B",
  stateSlug: "oregon",
  indices: { allItems: 120, rent: 150, goods: 105, otherServices: 110 },
  referenceRent: { bedrooms1: 1800 },
};
const EU: PlaceCostData = { ...A, slug: "fixture-eu", name: "Fixture EU", region: "eu" };

const YEAR = 2026;
const federal = loadFederal(YEAR);
const estimated = loadEstimated(YEAR);
const tax = (slug: string): EngineData => ({ federal, estimated, state: loadState(YEAR, slug) });
const cents = (n: number) => Math.round(n * 100);

describe("category scaling (4-9-2)", () => {
  const r = scaleCosts({ rent: 1000, goods: 500, utilities: 200 }, A, B);
  it("uses each category's own index where both places publish one", () => {
    expect(r.rows.find((x) => x.category === "rent")).toMatchObject({ destination: 1500, indexUsed: "category" });
    expect(r.rows.find((x) => x.category === "goods")).toMatchObject({ destination: 525, indexUsed: "category" });
  });
  it("falls back to the all-items ratio, and says so, where a category has no index", () => {
    expect(r.rows.find((x) => x.category === "utilities")).toMatchObject({ destination: 240, indexUsed: "allItems" });
    expect(r.warnings.some((w) => w.includes("utilities"))).toBe(true);
  });
  it("totals and differences agree to the cent", () => {
    expect(r.originTotal).toBe(1700);
    expect(r.destinationTotal).toBe(2265);
    expect(r.difference).toBe(565);
  });
  it("rejects negative costs", () => {
    expect(() => scaleCosts({ rent: -1 }, A, B)).toThrow();
  });
});

describe("region boundary (4-9-3)", () => {
  it("refuses to compare a BEA place with a Eurostat place", () => {
    expect(() => equivalentSalary(95_000, A, EU)).toThrow(/different bases/);
  });
});

describe("equivalent salary", () => {
  it("scales by the all-items ratio", () => {
    expect(equivalentSalary(95_000, A, B)).toBe(114_000);
  });
});

describe("the comparison that includes tax (4-9-5)", () => {
  // Texas net on $95,000 = 75,662.50 (payroll golden test)
  // Oregon net on $95,000 = 67,908.06 (engine)
  // Oregon net in Fixture A prices = 6,790,806c x 100/120 = 5,659,005c = 56,590.05
  const r = compareWithTax(
    { taxYear: YEAR, filingStatus: "single", originSalary: 95_000 },
    { place: A, tax: tax("texas") },
    { place: B, tax: tax("oregon") },
  );
  it("computes net pay in both places with the salary path", () => {
    expect(cents(r.originNetPay)).toBe(7_566_250);
    expect(cents(r.destinationNetPay)).toBe(6_790_806);
  });
  it("deflates destination net pay into origin prices", () => {
    expect(cents(r.destinationNetInOriginPrices)).toBe(5_659_005);
  });
  it("decomposes exactly into a tax part and a price part", () => {
    expect(cents(r.taxAndSalaryEffect)).toBe(-775_444);
    expect(cents(r.priceEffect)).toBe(-1_131_801);
    expect(cents(r.realAnnualDifference)).toBe(cents(r.taxAndSalaryEffect) + cents(r.priceEffect));
    expect(cents(r.realAnnualDifference)).toBe(-1_907_245);
  });
  it("answers the job-offer question: what destination salary breaks even", () => {
    const offer = compareWithTax(
      { taxYear: YEAR, filingStatus: "single", originSalary: 95_000, destinationSalary: 140_000 },
      { place: A, tax: tax("texas") },
      { place: B, tax: tax("oregon") },
    );
    expect(offer.realAnnualDifference).toBeGreaterThan(r.realAnnualDifference);
  });
});

describe("rent affordability", () => {
  const r = rentAffordability({ grossAnnualIncome: 60_000, place: B, bedrooms: 1 });
  it("computes the 30% ceiling, the 50% line and the 3x landlord screen", () => {
    expect(r.monthlyIncome).toBe(5000);
    expect(r.ceiling).toBe(1500);
    expect(r.severeLine).toBe(2500);
    expect(r.landlordScreenMax).toBe(1666.66);
  });
  it("sets the ceiling beside the market's Fair Market Rent", () => {
    expect(r.market).toMatchObject({
      fairMarketRent: 1800,
      burden: "cost burdened",
      headroom: -300,
      incomeNeededAt30: 72_000,
    });
    expect(r.market!.shareOfIncome).toBeCloseTo(36, 10);
  });
  it("omits the market comparison rather than inventing a rent", () => {
    const none = rentAffordability({ grossAnnualIncome: 60_000, place: B, bedrooms: 3 });
    expect(none.market).toBeNull();
    expect(none.warnings.some((w) => w.includes("No Fair Market Rent"))).toBe(true);
  });
  it("classifies burden on HUD's definitions", () => {
    expect(burdenLevel(30)).toBe("not burdened");
    expect(burdenLevel(30.01)).toBe("cost burdened");
    expect(burdenLevel(50.01)).toBe("severely cost burdened");
  });
});

describe("living wage", () => {
  const args = {
    taxYear: YEAR,
    filingStatus: "single" as const,
    bedrooms: 1 as const,
    otherMonthlyCosts: { goods: 800, otherServices: 400 },
  };
  const tx = livingWage({ ...args, place: A, tax: tax("texas") });

  it("takes rent from Fair Market Rent and totals the requirement", () => {
    expect(tx.monthlyRent).toBe(1200);
    expect(tx.rentSource).toBe("HUD Fair Market Rent");
    expect(tx.requiredNetAnnual).toBe(28_800);
  });
  it("finds the smallest gross salary that clears it, to the cent", () => {
    const net = (g: number) =>
      estimateWageTakeHome({ taxYear: YEAR, filingStatus: "single", annualWages: g }, tax("texas")).netPay;
    expect(net(tx.grossSalary)).toBeGreaterThanOrEqual(28_800);
    expect(net(tx.grossSalary - 0.01)).toBeLessThan(28_800);
  });
  it("reports the hourly equivalent over 2,080 hours", () => {
    expect(tx.hourlyAt2080).toBe(Math.round((tx.grossSalary * 100) / 2080) / 100);
  });
  it("is higher where both costs and tax are higher", () => {
    const or = livingWage({ ...args, place: B, tax: tax("oregon"), costsFrom: A });
    expect(or.monthlyRent).toBe(1800);
    expect(or.grossSalary).toBeGreaterThan(tx.grossSalary);
  });
  it("refuses to invent a rent where none is published", () => {
    expect(() => livingWage({ ...args, bedrooms: 4, place: A, tax: tax("texas") })).toThrow(/No Fair Market Rent/);
  });
  it("uses a rent the user supplies instead", () => {
    const own = livingWage({ ...args, bedrooms: 4, rentOverride: 2000, place: A, tax: tax("texas") });
    expect(own.rentSource).toBe("user");
    expect(own.monthlyRent).toBe(2000);
  });
});
