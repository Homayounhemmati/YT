import { describe, expect, it } from "vitest";
import type { EngineData } from "../index.js";
import { loadEstimated, loadFederal, loadState } from "../load.js";
import { computeEmployeeFica, estimateWageTakeHome, type WageInput } from "../payroll.js";

const YEAR = 2026;
const federal = loadFederal(YEAR);
const estimated = loadEstimated(YEAR);
const data = (slug: string | null): EngineData => ({
  federal,
  estimated,
  state: slug ? loadState(YEAR, slug) : null,
});
const run = (w: Partial<WageInput> & { annualWages: number }, slug: string | null = "texas") =>
  estimateWageTakeHome({ taxYear: YEAR, filingStatus: "single", ...w }, data(slug));
const cents = (n: number) => Math.round(n * 100);

describe("golden: $95,000 salary, single, Texas", () => {
  // Worked by hand:
  //   Social Security  95,000 x 6.2%                 =  5,890.00
  //   Medicare         95,000 x 1.45%                =  1,377.50
  //   Taxable          95,000 - 16,100               = 78,900.00
  //   Federal          12,400 x 10%                  =  1,240.00
  //                    38,000 x 12%                  =  4,560.00
  //                    28,500 x 22%                  =  6,270.00   -> 12,070.00
  //   Total tax        7,267.50 + 12,070.00          = 19,337.50
  //   Net pay          95,000 - 19,337.50            = 75,662.50
  const r = run({ annualWages: 95_000 });
  it("computes employee FICA at half the self-employment rates", () => {
    expect(cents(r.fica.socialSecurity)).toBe(589_000);
    expect(cents(r.fica.medicare)).toBe(137_750);
    expect(r.fica.additionalMedicare).toBe(0);
  });
  it("computes federal income tax on wages less the standard deduction", () => {
    expect(cents(r.federalTax)).toBe(1_207_000);
  });
  it("has no state layer in Texas", () => {
    expect(r.stateTax).toBe(0);
  });
  it("arrives at net pay to the cent", () => {
    expect(cents(r.totalTax)).toBe(1_933_750);
    expect(cents(r.netPay)).toBe(7_566_250);
  });
  it("does not carry the self-employment engine's FICA warning", () => {
    expect(r.warnings.some((w) => w.includes("Social Security and Medicare withheld"))).toBe(false);
  });
});

describe("golden: $95,000 salary, single, Pennsylvania flat 3.07%", () => {
  // 95,000 x 3.07% = 2,916.50; net = 75,662.50 - 2,916.50 = 72,746.00
  const r = run({ annualWages: 95_000 }, "pennsylvania");
  it("applies the flat state rate to gross wages", () => {
    expect(cents(r.stateTax)).toBe(291_650);
    expect(cents(r.netPay)).toBe(7_274_600);
  });
});

describe("the salary path is not the self-employment path", () => {
  it("leaves an employee more than a self-employed person on the same gross", () => {
    // The self-employed person pays both FICA halves (less the half deduction);
    // the employee pays one. This is the error the old figures carried.
    const wage = run({ annualWages: 95_000 });
    expect(wage.netPay).toBeGreaterThan(74_159.76);
  });
});

describe("pre-tax deductions follow different FICA rules", () => {
  it("401(k) deferrals reduce income tax but not FICA", () => {
    const base = run({ annualWages: 95_000 });
    const k = run({ annualWages: 95_000, preTaxRetirement: 10_000 });
    expect(k.fica.total).toBe(base.fica.total);
    expect(k.federalTax).toBeLessThan(base.federalTax);
  });
  it("section 125 premiums reduce both", () => {
    const base = run({ annualWages: 95_000 });
    const s = run({ annualWages: 95_000, section125: 3_000 });
    // 3,000 x 7.65% = 229.50 less FICA
    expect(cents(base.fica.total - s.fica.total)).toBe(22_950);
  });
  it("Pennsylvania taxes 401(k) deferrals: its state tax does not fall", () => {
    const base = run({ annualWages: 95_000 }, "pennsylvania");
    const pa = run({ annualWages: 95_000, preTaxRetirement: 10_000 }, "pennsylvania");
    expect(pa.stateTax).toBe(base.stateTax);          // 2,916.50 both ways
    expect(pa.federalTax).toBeLessThan(base.federalTax);
  });
  it("New Jersey excludes 401(k) deferrals, and says 403(b)/457 differ", () => {
    const base = run({ annualWages: 95_000 }, "new-jersey");
    const nj = run({ annualWages: 95_000, preTaxRetirement: 10_000 }, "new-jersey");
    expect(nj.stateTax).toBeLessThan(base.stateTax);
    expect(nj.warnings.some((w) => w.includes("403(b)"))).toBe(true);
  });
});

describe("Social Security wage base and Additional Medicare", () => {
  it("stops Social Security at the wage base", () => {
    const r = run({ annualWages: 300_000 });
    expect(cents(r.fica.socialSecurity)).toBe(Math.round(184_500 * 6.2));
  });
  it("applies 0.9% above the single threshold", () => {
    const f = computeEmployeeFica(25_000_000, "single", data(null));
    // (250,000 - 200,000) x 0.9% = 450.00
    expect(f.additionalMedicare).toBe(45_000);
  });
});

describe("pay periods", () => {
  for (const p of [52, 26, 24, 12] as const) {
    it(`${p} checks sum exactly to annual net pay`, () => {
      const r = run({ annualWages: 95_000, payPeriods: p });
      expect(r.netPerPaycheck).toHaveLength(p);
      const total = r.netPerPaycheck.reduce((a, b) => a + cents(b), 0);
      expect(total).toBe(cents(r.netPay));
    });
  }
  it("a biweekly check is smaller than a semi-monthly one", () => {
    const bw = run({ annualWages: 95_000, payPeriods: 26 });
    const sm = run({ annualWages: 95_000, payPeriods: 24 });
    expect(bw.netPerPaycheck[0]!).toBeLessThan(sm.netPerPaycheck[0]!);
  });
});

describe("personal exemptions and the Maryland flat deduction", () => {
  // Maryland, $95,000 salary: AGI 95,000 - standard 3,400 - exemption 3,200 = 88,400
  //   2% x 1,000 = 20.00 · 3% x 1,000 = 30.00 · 4% x 1,000 = 40.00
  //   4.75% x (88,400 - 3,000) = 4,056.50   -> 4,146.50
  it("Maryland subtracts its flat standard deduction and $3,200 exemption", () => {
    expect(cents(run({ annualWages: 95_000 }, "maryland").stateTax)).toBe(414_650);
  });
  it("Maryland's exemption steps down above $100,000 of AGI", () => {
    const at100 = run({ annualWages: 100_000 }, "maryland").stateTax;
    const at110 = run({ annualWages: 110_000 }, "maryland").stateTax;
    // 10,000 more income at 4.75%-5% plus 1,600 of lost exemption
    expect(at110 - at100).toBeGreaterThan(10_000 * 0.0475 + 1_600 * 0.0475);
  });
  // Illinois, $95,000: (95,000 - 2,925) x 4.95% = 4,557.71
  it("Illinois subtracts its personal exemption before the flat rate", () => {
    expect(cents(run({ annualWages: 95_000 }, "illinois").stateTax)).toBe(455_771);
  });
  it("Illinois allows no exemption above $250,000 of AGI", () => {
    // 300,000 x 4.95% = 14,850.00
    expect(cents(run({ annualWages: 300_000 }, "illinois").stateTax)).toBe(1_485_000);
  });
});
