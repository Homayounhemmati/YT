import { describe, expect, it } from "vitest";
import {
  closingCosts,
  homeAffordability,
  housePayment,
  principalAndInterest,
} from "../housing.js";
import {
  addSalesTax,
  combinedRate,
  hourlyToSalary,
  propertyTax,
  removeSalesTax,
  salaryToHourly,
} from "../everyday.js";

const cents = (n: number) => Math.round(n * 100);

describe("principal and interest", () => {
  // The textbook case: $300,000 at 6% for 30 years.
  //   r = 0.005, n = 360, (1.005)^360 = 6.022575...
  //   300,000 x 0.005 / (1 - 1/6.022575) = 1,798.65
  it("matches the standard amortisation formula to the cent", () => {
    expect(principalAndInterest(30_000_000, { ratePercent: 6, termYears: 30 })).toBe(179_865);
  });
  it("handles a zero rate without dividing by zero", () => {
    expect(principalAndInterest(36_000_000, { ratePercent: 0, termYears: 30 })).toBe(100_000);
  });
});

describe("house payment (PITI)", () => {
  const base = {
    price: 375_000, downPayment: 75_000, ratePercent: 6, termYears: 30,
    propertyTaxRatePercent: 1.2, insuranceAnnual: 1_800,
  };
  it("adds tax, insurance and HOA to principal and interest", () => {
    // P&I 1,798.65 + tax 375,000 x 1.2% / 12 = 375.00 + insurance 150.00 = 2,323.65
    const r = housePayment(base);
    expect(r.loanAmount).toBe(300_000);
    expect(r.loanToValue).toBe(80);
    expect(r.pmi).toBe(0);
    expect(cents(r.total)).toBe(232_365);
    expect(r.pmiEndsAfterMonth).toBeNull();
  });
  it("charges PMI only above 80% loan-to-value, and schedules its end at 78%", () => {
    const r = housePayment({ ...base, downPayment: 37_500, pmiRatePercent: 0.5 });
    // loan 337,500 x 0.5% / 12 = 140.63
    expect(cents(r.pmi)).toBe(14_063);
    expect(r.pmiEndsAfterMonth).toBeGreaterThan(0);
    expect(r.pmiEndsAfterMonth!).toBeLessThan(360);
  });
  it("warns rather than guesses when PMI or property tax is missing", () => {
    const r = housePayment({ ...base, downPayment: 10_000, propertyTaxRatePercent: undefined as never });
    expect(r.warnings.join(" ")).toMatch(/property tax/);
    expect(r.warnings.join(" ")).toMatch(/mortgage insurance/);
  });
  it("refuses a down payment larger than the price", () => {
    expect(() => housePayment({ ...base, downPayment: 400_000 })).toThrow();
  });
});

describe("home affordability", () => {
  const input = {
    grossAnnualIncome: 120_000, monthlyDebts: 500, downPayment: 80_000,
    ratePercent: 6, termYears: 30, propertyTaxRatePercent: 1.2,
    insuranceAnnual: 1_800, pmiRatePercent: 0.5,
  };
  it("stays inside the binding ratio, and one dollar more would not", () => {
    // Front-end 28% of 10,000 = 2,800; back-end 36% = 3,600 - 500 debts = 3,100.
    const r = homeAffordability(input);
    expect(r.housingBudget).toBe(2_800);
    expect(r.bindingRatio).toBe("front-end");
    expect(r.payment!.total).toBeLessThanOrEqual(2_800);
    const over = housePayment({ ...input, price: r.maxPrice + 100 });
    expect(over.total).toBeGreaterThan(2_800);
  });
  it("lets debts take over as the binding ratio", () => {
    const r = homeAffordability({ ...input, monthlyDebts: 1_500 });
    expect(r.bindingRatio).toBe("back-end");
    expect(r.housingBudget).toBe(2_100);
  });
  it("allows more under a 43% manual-underwriting ceiling", () => {
    expect(homeAffordability({ ...input, mode: "maximum" }).maxPrice)
      .toBeGreaterThan(homeAffordability(input).maxPrice);
  });
  it("returns zero, not a fake payment, when debt uses the whole ratio", () => {
    const r = homeAffordability({ ...input, monthlyDebts: 5_000 });
    expect(r.maxPrice).toBe(0);
    expect(r.payment).toBeNull();
  });
  it("backs the published claim: $600 of monthly debt costs $65,000-$80,000 of price", () => {
    // The home-affordability body and FAQ quote this range. It was first written
    // as "roughly $100,000", which ignored that tax and insurance scale with price.
    for (const ratePercent of [6, 6.5, 7]) {
      const a = homeAffordability({ ...input, ratePercent, monthlyDebts: 1_000 }).maxPrice;
      const b = homeAffordability({ ...input, ratePercent, monthlyDebts: 1_600 }).maxPrice;
      expect(a - b).toBeGreaterThan(65_000);
      expect(a - b).toBeLessThan(80_000);
    }
  });
});

describe("closing costs", () => {
  it("computes per-diem interest from closing to month end", () => {
    // 300,000 x 6% / 365 x 16 days (15th to 30th inclusive) = 789.04
    const r = closingCosts({
      price: 375_000, loanAmount: 300_000, ratePercent: 6, closingDay: 15,
      daysInClosingMonth: 30, propertyTaxAnnual: 4_500, insuranceAnnual: 1_800,
      escrowMonths: 3, lenderFees: 3_000, titleAndSettlement: 2_500, transferTax: 0,
    });
    expect(cents(r.prepaidInterest)).toBe(78_904);
    // escrow: (4,500 + 1,800) / 12 x 3 = 1,575.00
    expect(cents(r.escrowReserves)).toBe(157_500);
    expect(cents(r.total)).toBe(78_904 + 180_000 + 157_500 + 300_000 + 250_000);
    expect(r.warnings.join(" ")).toMatch(/transfer tax/);
  });
});

describe("salary and hourly", () => {
  it("divides by 2,080 paid hours for full time", () => {
    expect(salaryToHourly(95_000).hourly).toBe(45.67);
  });
  it("shows the effective rate once paid leave is removed", () => {
    const r = salaryToHourly(95_000, { hoursPerWeek: 40, paidWeeks: 52, paidLeaveWeeks: 3 });
    expect(r.workedHours).toBe(1_960);
    expect(r.effectiveHourly).toBe(48.47);
  });
  it("converts back", () => {
    expect(hourlyToSalary(25)).toBe(52_000);
  });
});

describe("sales tax", () => {
  const rates = { statePercent: 6.25, countyPercent: 0.5, cityPercent: 1.0, specialPercent: 0.5 };
  it("sums component rates without floating-point drift", () => {
    expect(combinedRate(rates)).toBe(8.25);
  });
  it("adds tax to a price", () => {
    expect(addSalesTax(100, rates)).toEqual({ preTax: 100, tax: 8.25, total: 108.25, combinedPercent: 8.25 });
  });
  it("recovers the pre-tax price from a receipt total", () => {
    expect(removeSalesTax(108.25, rates).preTax).toBe(100);
  });
});

describe("property tax", () => {
  it("applies assessment ratio, exemption and mills", () => {
    // 400,000 x 100% = 400,000 - 25,000 homestead = 375,000 x 20 mills = 7,500
    const r = propertyTax({ marketValue: 400_000, assessmentRatioPercent: 100, exemption: 25_000, millRate: 20 });
    expect(r.annualTax).toBe(7_500);
    expect(r.monthlyTax).toBe(625);
    expect(r.effectiveRatePercent).toBeCloseTo(1.875, 10);
  });
});
