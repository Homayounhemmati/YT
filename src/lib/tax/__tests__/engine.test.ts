import { readdirSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { estimateTax, type EngineData } from "../index.js";
import { loadEstimated, loadFederal, loadState } from "../load.js";
import type { FilingStatus, TaxInput } from "../types.js";

const YEAR = 2026;
const federal = loadFederal(YEAR);
const estimated = loadEstimated(YEAR);

function data(stateSlug: string | null): EngineData {
  return {
    federal,
    estimated,
    state: stateSlug ? loadState(YEAR, stateSlug) : null,
  };
}

function run(input: Partial<TaxInput> & { businessIncome: number }, state: string | null = "texas") {
  const full: TaxInput = {
    taxYear: YEAR,
    filingStatus: "single",
    ...input,
  };
  return estimateTax(full, data(state));
}

/** Compare dollar amounts to the cent. */
const cents = (n: number) => Math.round(n * 100);

describe("golden scenario: $80,000 profit, single, no state tax", () => {
  // Worked by hand from the statute, step by step:
  //   NESE            80,000 x 0.9235          = 73,880.00
  //   Social Security 73,880 x 12.4%           =  9,161.12   (under the wage base)
  //   Medicare        73,880 x 2.9%            =  2,142.52   (no ceiling)
  //   SE tax                                   = 11,303.64
  //   Half deductible                          =  5,651.82
  //   AGI             80,000 - 5,651.82        = 74,348.18
  //   Less standard deduction 16,100           = 58,248.18
  //   QBI  min(20% x 74,348.18, 20% x 58,248.18) = 11,649.64
  //   Taxable         58,248.18 - 11,649.64    = 46,598.54
  //   Federal 10% x 12,400 + 12% x 34,198.54   =  5,343.82
  //   Total           11,303.64 + 5,343.82     = 16,647.46
  const r = run({ businessIncome: 80_000 });

  it("computes net earnings from self-employment", () => {
    expect(cents(r.selfEmployment.netEarnings)).toBe(cents(73_880));
  });
  it("computes the Social Security portion", () => {
    expect(cents(r.selfEmployment.socialSecurity)).toBe(cents(9_161.12));
  });
  it("computes the Medicare portion", () => {
    expect(cents(r.selfEmployment.medicare)).toBe(cents(2_142.52));
  });
  it("deducts exactly half the self-employment tax", () => {
    expect(cents(r.selfEmployment.deductiblePortion)).toBe(cents(5_651.82));
  });
  it("computes adjusted gross income", () => {
    expect(cents(r.adjustedGrossIncome)).toBe(cents(74_348.18));
  });
  it("computes the QBI deduction", () => {
    expect(cents(r.qbi.deduction)).toBe(cents(11_649.64));
  });
  it("computes taxable income", () => {
    expect(cents(r.taxableIncome)).toBe(cents(46_598.54));
  });
  it("computes federal income tax", () => {
    expect(cents(r.federalTax)).toBe(cents(5_343.82));
  });
  it("computes the total and take-home", () => {
    expect(cents(r.totalTax)).toBe(cents(16_647.46));
    expect(cents(r.takeHome)).toBe(cents(63_352.54));
  });
  it("reports an effective rate below the marginal rate", () => {
    expect(r.effectiveRate).toBeCloseTo(20.809, 2);
    expect(r.marginalRate).toBe(12);
  });
});

describe("ordering of operations", () => {
  it("applies the standard deduction before QBI, not after", () => {
    // If QBI came off first, taxable income would be lower and the tax smaller.
    const r = run({ businessIncome: 80_000 });
    const qbiBase = r.adjustedGrossIncome - r.standardDeduction;
    expect(r.qbi.deduction).toBeCloseTo(
      Math.min(qbiBase * 0.2, r.qbi.qualifiedIncome * 0.2),
      2,
    );
  });

  it("reduces AGI by half the SE tax, never the whole amount", () => {
    const r = run({ businessIncome: 80_000 });
    expect(r.selfEmployment.deductiblePortion * 2).toBeCloseTo(
      r.selfEmployment.total,
      2,
    );
    expect(r.adjustedGrossIncome).toBeCloseTo(
      r.netProfit - r.selfEmployment.deductiblePortion,
      2,
    );
  });
});

describe("edge cases", () => {
  it("handles zero income without dividing by zero", () => {
    const r = run({ businessIncome: 0 });
    expect(r.totalTax).toBe(0);
    expect(r.effectiveRate).toBe(0);
    expect(r.taxableIncome).toBe(0);
  });

  it("handles a business loss and warns about it", () => {
    const r = run({ businessIncome: 20_000, businessExpenses: 35_000 });
    expect(r.netProfit).toBe(-15_000);
    expect(r.selfEmployment.total).toBe(0);
    expect(r.taxableIncome).toBe(0);
    expect(r.federalTax).toBe(0);
    expect(r.warnings.join(" ")).toMatch(/loss/i);
  });

  it("charges no SE tax below the statutory minimum earnings", () => {
    // $430 profit is $397.11 of net earnings, just under the $400 floor.
    const below = run({ businessIncome: 430 });
    expect(below.selfEmployment.netEarnings).toBeLessThan(400);
    expect(below.selfEmployment.total).toBe(0);

    const above = run({ businessIncome: 500 });
    expect(above.selfEmployment.total).toBeGreaterThan(0);
  });

  it("caps the Social Security portion at the wage base", () => {
    const base = federal.selfEmployment.socialSecurityWageBase;
    const big = run({ businessIncome: 400_000 });
    const capped = base * (federal.selfEmployment.socialSecurityRate / 100);
    expect(cents(big.selfEmployment.socialSecurity)).toBe(cents(capped));
  });

  it("leaves Medicare uncapped above the wage base", () => {
    const a = run({ businessIncome: 300_000 });
    const b = run({ businessIncome: 400_000 });
    expect(b.selfEmployment.medicare).toBeGreaterThan(a.selfEmployment.medicare);
    expect(cents(a.selfEmployment.socialSecurity)).toBe(
      cents(b.selfEmployment.socialSecurity),
    );
  });

  it("shares the wage base with W-2 wages", () => {
    const base = federal.selfEmployment.socialSecurityWageBase;
    // Wages already consume the entire base, so no SE Social Security remains.
    const r = run({ businessIncome: 50_000, w2Wages: base + 10_000 });
    expect(r.selfEmployment.socialSecurity).toBe(0);
    expect(r.selfEmployment.medicare).toBeGreaterThan(0);
  });

  it("applies the Additional Medicare Tax above the statutory threshold", () => {
    const threshold = federal.selfEmployment.additionalMedicare.thresholds.single;
    const under = run({ businessIncome: threshold - 50_000 });
    expect(under.selfEmployment.additionalMedicare).toBe(0);

    const over = run({ businessIncome: threshold + 100_000 });
    expect(over.selfEmployment.additionalMedicare).toBeGreaterThan(0);
  });

  it("excludes the Additional Medicare Tax from the deductible half", () => {
    const r = run({ businessIncome: 400_000 });
    expect(r.selfEmployment.additionalMedicare).toBeGreaterThan(0);
    const ordinary = r.selfEmployment.socialSecurity + r.selfEmployment.medicare;
    expect(cents(r.selfEmployment.deductiblePortion)).toBe(cents(ordinary / 2));
    // The naive version would have used the full total including the surtax.
    expect(r.selfEmployment.deductiblePortion).toBeLessThan(
      r.selfEmployment.total / 2,
    );
  });
});

describe("filing statuses", () => {
  const statuses: FilingStatus[] = [
    "single",
    "marriedJointly",
    "marriedSeparately",
    "headOfHousehold",
  ];

  it.each(statuses)("produces a coherent result for %s", (filingStatus) => {
    const r = run({ businessIncome: 120_000, filingStatus });
    expect(r.totalTax).toBeGreaterThan(0);
    expect(r.standardDeduction).toBe(federal.standardDeduction[filingStatus]);
  });

  it("taxes a joint filer less than a single filer on the same income", () => {
    const single = run({ businessIncome: 120_000, filingStatus: "single" });
    const joint = run({ businessIncome: 120_000, filingStatus: "marriedJointly" });
    expect(joint.federalTax).toBeLessThan(single.federalTax);
  });
});

describe("state engine", () => {
  it("charges nothing in a state with no income tax", () => {
    const r = run({ businessIncome: 100_000 }, "texas");
    expect(r.state.amount).toBe(0);
    expect(r.state.structure).toBe("none");
    expect(r.state.notes.join(" ")).toMatch(/self-employment tax still apply/i);
  });

  it("applies a flat rate", () => {
    const r = run({ businessIncome: 100_000 }, "colorado");
    const co = loadState(YEAR, "colorado");
    expect(co.structure).toBe("flat");
    expect(cents(r.state.amount)).toBe(
      cents((r.state.taxableIncome * co.flatRate!) / 100),
    );
  });

  it("applies a graduated schedule", () => {
    const r = run({ businessIncome: 100_000 }, "new-york");
    expect(r.state.structure).toBe("progressive");
    expect(r.state.amount).toBeGreaterThan(0);
    expect(r.state.brackets.length).toBeGreaterThan(1);
  });

  it("adds California's mental health services surtax only above $1M", () => {
    const under = run({ businessIncome: 500_000 }, "california");
    expect(under.state.surtax).toBe(0);

    const over = run({ businessIncome: 2_000_000 }, "california");
    expect(over.state.surtax).toBeGreaterThan(0);
  });

  it("surfaces local tax warnings where they exist", () => {
    const r = run({ businessIncome: 100_000 }, "pennsylvania");
    expect(r.state.notes.join(" ")).toMatch(/Philadelphia/i);
  });

  it("loads and computes for every jurisdiction without throwing", () => {
    const dir = path.join(process.cwd(), "src", "data", `tax-year-${YEAR}`, "states");
    const slugs = readdirSync(dir).map((f) => f.replace(/\.json$/, ""));
    expect(slugs).toHaveLength(51);

    for (const slug of slugs) {
      const r = run({ businessIncome: 95_000 }, slug);
      expect(Number.isFinite(r.totalTax), slug).toBe(true);
      expect(r.state.amount, slug).toBeGreaterThanOrEqual(0);
      expect(r.totalTax, slug).toBeGreaterThan(0);
    }
  });
});

describe("QBI", () => {
  it("gives the full 20% below the threshold", () => {
    const r = run({ businessIncome: 80_000 });
    expect(r.qbi.aboveThreshold).toBe(false);
    expect(r.qbi.range).toBeNull();
  });

  it("returns a range and a warning above the threshold", () => {
    const r = run({ businessIncome: 400_000 });
    expect(r.qbi.aboveThreshold).toBe(true);
    expect(r.qbi.range).not.toBeNull();
    expect(r.warnings.join(" ")).toMatch(/QBI threshold/i);
  });

  it("removes the deduction for a specified service business past the phase-in", () => {
    const r = run({ businessIncome: 400_000, isSpecifiedServiceBusiness: true });
    expect(r.qbi.deduction).toBe(0);
  });
});

describe("estimated payments", () => {
  it("uses the prior-year safe harbour when it is lower", () => {
    const r = run({ businessIncome: 200_000, priorYearTaxLiability: 10_000 });
    expect(r.estimatedPayments.basis).toBe("priorYear");
    expect(cents(r.estimatedPayments.requiredAnnualPayment)).toBe(cents(10_000));
  });

  it("requires 110% of prior-year tax when prior-year AGI was high", () => {
    const r = run({
      businessIncome: 300_000,
      priorYearTaxLiability: 40_000,
      priorYearAgi: 200_000,
    });
    expect(cents(r.estimatedPayments.requiredAnnualPayment)).toBe(cents(44_000));
  });

  it("falls back to 90% of the current year with no prior-year figures", () => {
    const r = run({ businessIncome: 90_000 });
    expect(r.estimatedPayments.basis).toBe("currentYear");
    expect(cents(r.estimatedPayments.requiredAnnualPayment)).toBe(
      cents(Math.round(r.totalTax * 100 * 0.9) / 100),
    );
  });

  it("is not required when the balance due is under the statutory minimum", () => {
    const r = run({ businessIncome: 3_000 });
    expect(r.estimatedPayments.required).toBe(false);
    expect(r.estimatedPayments.installments.every((i) => i.amount === 0)).toBe(true);
  });

  it("splits into four installments that sum exactly to the remainder", () => {
    const r = run({ businessIncome: 123_457 });
    const p = r.estimatedPayments;
    expect(p.installments).toHaveLength(4);
    const total = p.installments.reduce((a, i) => a + cents(i.amount), 0);
    expect(total).toBe(cents(p.remaining));
  });

  it("credits withholding against the requirement", () => {
    const withheld = run({
      businessIncome: 90_000,
      w2Wages: 40_000,
      w2FederalWithheld: 30_000,
    });
    expect(withheld.estimatedPayments.remaining).toBeLessThan(
      withheld.estimatedPayments.requiredAnnualPayment,
    );
  });

  it("carries the derived due dates through, never on a weekend", () => {
    const r = run({ businessIncome: 90_000 });
    for (const inst of r.estimatedPayments.installments) {
      const day = new Date(`${inst.dueDate}T12:00:00Z`).getUTCDay();
      expect(day, inst.dueDate).not.toBe(0);
      expect(day, inst.dueDate).not.toBe(6);
    }
  });
});

describe("internal consistency", () => {
  const scenarios: TaxInput[] = [
    { taxYear: YEAR, filingStatus: "single", businessIncome: 45_000 },
    { taxYear: YEAR, filingStatus: "marriedJointly", businessIncome: 180_000, businessExpenses: 20_000 },
    { taxYear: YEAR, filingStatus: "headOfHousehold", businessIncome: 95_000, w2Wages: 25_000 },
    { taxYear: YEAR, filingStatus: "marriedSeparately", businessIncome: 260_000 },
  ];

  it.each(scenarios)("bracket detail sums to the federal tax (%#)", (input) => {
    const r = estimateTax(input, data("california"));
    const summed = r.federalBrackets.reduce((a, b) => a + cents(b.taxInBracket), 0);
    expect(summed).toBe(cents(r.federalTax));
  });

  it.each(scenarios)("income minus total tax equals take-home (%#)", (input) => {
    const r = estimateTax(input, data("new-york"));
    const income = r.netProfit + (input.w2Wages ?? 0) + (input.otherIncome ?? 0);
    expect(cents(income - r.totalTax)).toBe(cents(r.takeHome));
  });

  it.each(scenarios)("total equals its parts (%#)", (input) => {
    const r = estimateTax(input, data("colorado"));
    const parts =
      cents(r.selfEmployment.total) + cents(r.federalTax) +
      cents(r.state.amount) + cents(r.state.surtax);
    expect(parts).toBe(cents(r.totalTax));
  });

  it("never lets tax exceed income", () => {
    for (let income = 1_000; income <= 500_000; income += 7_500) {
      const r = run({ businessIncome: income }, "california");
      expect(r.totalTax, `income ${income}`).toBeLessThan(income);
      expect(r.effectiveRate, `income ${income}`).toBeLessThan(100);
    }
  });

  it("increases tax monotonically with income", () => {
    let previous = -1;
    for (let income = 10_000; income <= 400_000; income += 10_000) {
      const r = run({ businessIncome: income }, "new-york");
      expect(r.totalTax, `income ${income}`).toBeGreaterThan(previous);
      previous = r.totalTax;
    }
  });

  it("keeps the effective rate at or below the marginal rate", () => {
    for (const income of [30_000, 90_000, 250_000]) {
      const r = run({ businessIncome: income }, "texas");
      expect(r.effectiveRate).toBeLessThan(r.marginalRate + 20);
    }
  });
});

describe("known limits are stated rather than hidden", () => {
  it("warns that employee FICA on wages is not subtracted", () => {
    const r = run({ businessIncome: 60_000, w2Wages: 50_000 });
    expect(r.warnings.join(" ")).toMatch(/withheld from your paycheck/i);
  });

  it("says so when a state's figures predate the tax year", () => {
    const r = run({ businessIncome: 100_000 }, "california");
    const ca = loadState(YEAR, "california");
    if (ca.staleForTargetYear) {
      expect(r.warnings.join(" ") + r.state.notes.join(" ")).toMatch(
        /prior tax year|had not published/i,
      );
    }
  });

  it("tells the user state conformity rules are not modelled", () => {
    const r = run({ businessIncome: 100_000 }, "new-york");
    expect(r.state.notes.join(" ")).toMatch(/not modelled/i);
  });
});
