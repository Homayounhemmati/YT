import { type Cents, atLeastZero, percentOf } from "./money.js";
import type { FederalData, FilingStatus, QbiResult } from "./types.js";

/**
 * Phase-in range above the threshold amount, section 199A(b)(3)(B)(ii). Unlike
 * the threshold itself, these are fixed statutory amounts and are not indexed.
 */
const PHASE_IN_RANGE: Record<FilingStatus, number> = {
  single: 50_000,
  marriedJointly: 100_000,
  marriedSeparately: 50_000,
  headOfHousehold: 50_000,
};

export interface QbiArgs {
  /** Business profit already reduced by the deductions attributable to it. */
  qualifiedIncome: Cents;
  taxableIncomeBeforeQbi: Cents;
  filingStatus: FilingStatus;
  isSpecifiedServiceBusiness: boolean;
  /** W-2 wages the business itself paid out. Solo freelancers pay none. */
  businessW2Wages: Cents;
  federal: FederalData;
}

/**
 * Section 199A qualified business income deduction.
 *
 * Below the threshold this is a clean 20%. Above it the answer depends on the
 * kind of business and the wages it pays, and a single confident number would be
 * a guess. So above the threshold this returns a range, sets the deduction to
 * the conservative end, and raises a warning — overstating tax is the safe
 * direction for someone deciding how much to set aside.
 */
export function computeQbiDeduction({
  qualifiedIncome,
  taxableIncomeBeforeQbi,
  filingStatus,
  isSpecifiedServiceBusiness,
  businessW2Wages,
  federal,
}: QbiArgs): QbiResult {
  const income = atLeastZero(qualifiedIncome);
  const empty: QbiResult = {
    deduction: 0,
    qualifiedIncome: income,
    limitedByTaxableIncome: false,
    aboveThreshold: false,
    range: null,
  };
  if (income === 0 || taxableIncomeBeforeQbi <= 0) return empty;

  const rate = federal.qbi.maxRate;
  const tentative = percentOf(income, rate);
  // The deduction can never exceed 20% of taxable income. Net capital gain
  // would also reduce this base; the engine has no capital gain input yet.
  const taxableIncomeCap = percentOf(taxableIncomeBeforeQbi, rate);
  const unlimited = Math.min(tentative, taxableIncomeCap);
  const limitedByTaxableIncome = taxableIncomeCap < tentative;

  const threshold = federal.qbi.phaseOutStart[filingStatus] * 100;
  const aboveThreshold = taxableIncomeBeforeQbi > threshold;

  if (!aboveThreshold) {
    return {
      deduction: unlimited,
      qualifiedIncome: income,
      limitedByTaxableIncome,
      aboveThreshold: false,
      range: null,
    };
  }

  // Above the threshold the wage limit bites: 50% of the W-2 wages the business
  // paid. A solo freelancer pays none, so the limited figure is usually zero.
  const wageLimit = percentOf(businessW2Wages, 50);
  const range = atLeastZero(PHASE_IN_RANGE[filingStatus] * 100);
  const over = taxableIncomeBeforeQbi - threshold;

  let floorValue: Cents;
  if (over >= range) {
    // Fully phased in: an SSTB loses the deduction outright; anyone else is
    // capped by wages.
    floorValue = isSpecifiedServiceBusiness ? 0 : Math.min(unlimited, wageLimit);
  } else {
    const phasedOutShare = over / range;
    const reduction = Math.round((unlimited - Math.min(unlimited, wageLimit)) * phasedOutShare);
    const sstbReduction = Math.round(unlimited * phasedOutShare);
    floorValue = isSpecifiedServiceBusiness
      ? atLeastZero(unlimited - sstbReduction)
      : atLeastZero(unlimited - reduction);
  }

  return {
    deduction: floorValue,
    qualifiedIncome: income,
    limitedByTaxableIncome,
    aboveThreshold: true,
    range: { low: floorValue / 100, high: unlimited / 100 },
  };
}
