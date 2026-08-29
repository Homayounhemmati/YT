import { type Cents, atLeastZero, percentOf } from "./money.js";
import type { FederalData, FilingStatus, SelfEmploymentResult } from "./types.js";

export interface SeArgs {
  netProfit: Cents;
  w2Wages: Cents;
  w2SocialSecurityWages: Cents;
  filingStatus: FilingStatus;
  federal: FederalData;
}

/**
 * Self-employment tax under 26 U.S.C. 1401 and 1402.
 *
 * Three details here are the ones most commonly got wrong, and each is called
 * out at the line that implements it: the 0.9235 reduction, the Social Security
 * wage base being shared with W-2 wages, and the Additional Medicare Tax being
 * excluded from the deductible half.
 */
export function computeSelfEmploymentTax({
  netProfit,
  w2Wages,
  w2SocialSecurityWages,
  filingStatus,
  federal,
}: SeArgs): SelfEmploymentResult {
  const se = federal.selfEmployment;
  const zero: SelfEmploymentResult = {
    netEarnings: 0,
    socialSecurity: 0,
    medicare: 0,
    additionalMedicare: 0,
    total: 0,
    deductiblePortion: 0,
  };

  // Section 1402(a)(12) removes the employer-equivalent share before the tax
  // applies, so the base is 92.35% of profit, not 100%.
  const netEarnings = atLeastZero(Math.round(netProfit * se.neseFactor));

  // Section 1402(b)(2): below the minimum, no self-employment tax is due at all.
  const minimum = se.minimumEarningsThreshold * 100;
  if (netEarnings < minimum) {
    // Wages can still trigger the Additional Medicare Tax on their own, but that
    // is withheld by the employer rather than computed here.
    return { ...zero };
  }

  // The Social Security wage base is shared with W-2 wages: an employee with a
  // side business has already used part of it. Ignoring this overtaxes exactly
  // the "day job plus freelancing" case that is a large share of the audience.
  const wageBase = se.socialSecurityWageBase * 100;
  const remainingBase = atLeastZero(wageBase - w2SocialSecurityWages);
  const socialSecurityBase = Math.min(netEarnings, remainingBase);
  const socialSecurity = percentOf(socialSecurityBase, se.socialSecurityRate);

  // Medicare has no ceiling.
  const medicare = percentOf(netEarnings, se.medicareRate);

  // Additional Medicare Tax applies to wages and self-employment income
  // combined, against a threshold that Congress never indexed to inflation.
  const threshold = se.additionalMedicare.thresholds[filingStatus] * 100;
  const combined = w2Wages + netEarnings;
  const excess = atLeastZero(combined - threshold);
  const additionalMedicare = percentOf(excess, se.additionalMedicare.rate);

  const ordinary = socialSecurity + medicare;

  // Section 164(f) allows half of the tax imposed by section 1401(a) and (b),
  // which does not include the Additional Medicare Tax of 1401(b)(2).
  const deductiblePortion = percentOf(ordinary, se.deductiblePortion);

  return {
    netEarnings,
    socialSecurity,
    medicare,
    additionalMedicare,
    total: ordinary + additionalMedicare,
    deductiblePortion,
  };
}
