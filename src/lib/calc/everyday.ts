import { toCents, toDollars } from "../tax/money.js";

// ---------------------------------------------------------------------------
// Salary <-> hourly
// ---------------------------------------------------------------------------

export interface HoursBasis {
  hoursPerWeek: number;
  /** Weeks paid per year; 52 for a salaried employee. */
  paidWeeks: number;
  /** Weeks of paid leave inside those paid weeks. */
  paidLeaveWeeks?: number;
}

export const FULL_TIME: HoursBasis = { hoursPerWeek: 40, paidWeeks: 52 };

export interface HourlyResult {
  /** Salary over paid hours — what payroll divides by (2,080 for full time). */
  hourly: number;
  /** Salary over hours actually worked, once paid leave is taken out. */
  effectiveHourly: number;
  paidHours: number;
  workedHours: number;
}

export function salaryToHourly(salary: number, basis: HoursBasis = FULL_TIME): HourlyResult {
  const paidHours = basis.hoursPerWeek * basis.paidWeeks;
  const workedHours = basis.hoursPerWeek * (basis.paidWeeks - (basis.paidLeaveWeeks ?? 0));
  if (paidHours <= 0 || workedHours <= 0) throw new Error("Hours must be positive.");
  const s = toCents(salary);
  return {
    hourly: toDollars(Math.round(s / paidHours)),
    effectiveHourly: toDollars(Math.round(s / workedHours)),
    paidHours,
    workedHours,
  };
}

export function hourlyToSalary(hourly: number, basis: HoursBasis = FULL_TIME): number {
  return toDollars(Math.round(toCents(hourly) * basis.hoursPerWeek * basis.paidWeeks));
}

// ---------------------------------------------------------------------------
// Sales tax
// ---------------------------------------------------------------------------

export interface SalesTaxRates {
  statePercent: number;
  countyPercent?: number;
  cityPercent?: number;
  specialPercent?: number;
}

export function combinedRate(r: SalesTaxRates): number {
  // Summed in basis points so 6.25 + 2.0 does not become 8.250000000000002.
  const bp = [r.statePercent, r.countyPercent, r.cityPercent, r.specialPercent]
    .map((x) => Math.round((x ?? 0) * 100))
    .reduce((a, b) => a + b, 0);
  return bp / 100;
}

export interface SalesTaxResult {
  preTax: number;
  tax: number;
  total: number;
  combinedPercent: number;
}

/** Forward: from a shelf price to what is paid. */
export function addSalesTax(price: number, rates: SalesTaxRates): SalesTaxResult {
  const pct = combinedRate(rates);
  const p = toCents(price);
  const tax = Math.round((p * pct) / 100);
  return { preTax: toDollars(p), tax: toDollars(tax), total: toDollars(p + tax), combinedPercent: pct };
}

/** Reverse: from a receipt total back to the pre-tax price. */
export function removeSalesTax(total: number, rates: SalesTaxRates): SalesTaxResult {
  const pct = combinedRate(rates);
  const t = toCents(total);
  const pre = Math.round((t * 100) / (100 + pct));
  return { preTax: toDollars(pre), tax: toDollars(t - pre), total: toDollars(t), combinedPercent: pct };
}

// ---------------------------------------------------------------------------
// Property tax
// ---------------------------------------------------------------------------

export interface PropertyTaxInput {
  marketValue: number;
  /** Share of market value the county assesses, in percent; 100 where assessed at full value. */
  assessmentRatioPercent: number;
  /** Homestead or other exemption, in dollars of assessed value. */
  exemption?: number;
  /** Combined levy in mills (dollars per $1,000 of taxable value). */
  millRate: number;
}

export interface PropertyTaxResult {
  assessedValue: number;
  taxableValue: number;
  annualTax: number;
  monthlyTax: number;
  effectiveRatePercent: number;
}

export function propertyTax(input: PropertyTaxInput): PropertyTaxResult {
  const mv = toCents(input.marketValue);
  const assessed = Math.round((mv * input.assessmentRatioPercent) / 100);
  const taxable = Math.max(0, assessed - toCents(input.exemption ?? 0));
  const annual = Math.round((taxable * input.millRate) / 1000);
  return {
    assessedValue: toDollars(assessed),
    taxableValue: toDollars(taxable),
    annualTax: toDollars(annual),
    monthlyTax: toDollars(Math.round(annual / 12)),
    effectiveRatePercent: mv > 0 ? (annual / mv) * 100 : 0,
  };
}
