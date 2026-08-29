import { applyBrackets, marginalRate } from "./brackets.js";
import { computeEstimatedPayments } from "./estimated.js";
import { atLeastZero, toCents, toDollars } from "./money.js";
import { computeQbiDeduction } from "./qbi.js";
import { computeSelfEmploymentTax } from "./selfEmployment.js";
import { computeStateTax } from "./state.js";
import type {
  EstimatedData,
  FederalData,
  StateData,
  TaxInput,
  TaxResult,
} from "./types.js";

export * from "./types.js";
export { applyBrackets, marginalRate } from "./brackets.js";

export interface EngineData {
  federal: FederalData;
  estimated: EstimatedData;
  state: StateData | null;
}

/**
 * The single entry point for every tax number the site displays.
 *
 * Order matters here and is the thing most calculators get wrong: the
 * self-employment tax is computed first because half of it reduces AGI; the
 * standard deduction comes off before the QBI deduction, not after; and the
 * brackets apply last, to what survives all of it.
 */
export function estimateTax(input: TaxInput, data: EngineData): TaxResult {
  const { federal, estimated, state } = data;
  const status = input.filingStatus;
  const warnings: string[] = [];

  if (federal.taxYear !== input.taxYear) {
    warnings.push(
      `Federal data is for ${federal.taxYear} but ${input.taxYear} was requested.`,
    );
  }

  // 1. Net business profit.
  const businessIncome = toCents(input.businessIncome);
  const businessExpenses = toCents(input.businessExpenses ?? 0);
  const netProfit = businessIncome - businessExpenses;
  if (netProfit < 0) {
    warnings.push(
      "The business shows a loss. Loss limitation rules are not modelled, and " +
        "no self-employment tax applies to a loss.",
    );
  }

  const w2Wages = toCents(input.w2Wages ?? 0);
  const w2SocialSecurityWages = toCents(
    input.w2SocialSecurityWages ?? input.w2Wages ?? 0,
  );
  const otherIncome = toCents(input.otherIncome ?? 0);

  // 2-5. Self-employment tax and the half of it that is deductible.
  const se = computeSelfEmploymentTax({
    netProfit: atLeastZero(netProfit),
    w2Wages,
    w2SocialSecurityWages,
    filingStatus: status,
    federal,
  });

  // 6. Adjusted gross income.
  const retirement = toCents(input.retirementContribution ?? 0);
  const healthInsurance = toCents(input.selfEmployedHealthInsurance ?? 0);
  const hsa = toCents(input.hsaContribution ?? 0);
  const aboveTheLine = se.deductiblePortion + retirement + healthInsurance + hsa;
  const adjustedGrossIncome =
    netProfit + w2Wages + otherIncome - aboveTheLine;

  // 7. Taxable income before the QBI deduction.
  const standardDeduction = toCents(federal.standardDeduction[status]);
  const itemized = toCents(input.itemizedDeductions ?? 0);
  const deductionUsed = itemized > standardDeduction ? "itemized" : "standard";
  const deduction = Math.max(standardDeduction, itemized);
  const taxableBeforeQbi = atLeastZero(adjustedGrossIncome - deduction);

  // 8. QBI. Qualified income is business profit net of the business-related
  // above-the-line deductions, not gross profit.
  const qbi = computeQbiDeduction({
    qualifiedIncome: atLeastZero(
      netProfit - se.deductiblePortion - healthInsurance - retirement,
    ),
    taxableIncomeBeforeQbi: taxableBeforeQbi,
    filingStatus: status,
    isSpecifiedServiceBusiness: input.isSpecifiedServiceBusiness ?? false,
    businessW2Wages: 0,
    federal,
  });
  if (qbi.aboveThreshold) {
    warnings.push(
      "Taxable income is above the QBI threshold, where the deduction depends " +
        "on the type of business and the wages it pays. The conservative end of " +
        "the range is used, so the tax shown may be higher than the true figure.",
    );
  }

  // 9. Taxable income.
  const taxableIncome = atLeastZero(taxableBeforeQbi - qbi.deduction);

  // 10. Federal income tax.
  const federalRows = federal.brackets[status];
  const { tax: federalTax, detail: federalBrackets } = applyBrackets(
    taxableIncome,
    federalRows,
  );
  const federalMarginal = marginalRate(taxableIncome, federalRows);

  // 11. State income tax.
  const stateResult = computeStateTax({
    federalAgi: atLeastZero(adjustedGrossIncome),
    filingStatus: status,
    state,
  });

  // 12-15. Totals.
  const stateTotal = stateResult.amount + stateResult.surtax;
  const totalTax = se.total + federalTax + stateTotal;
  const grossIncome = businessIncome + w2Wages + otherIncome;
  const takeHome = netProfit + w2Wages + otherIncome - totalTax;
  const effectiveRate =
    grossIncome > 0 ? (totalTax / grossIncome) * 100 : 0;

  const withheld = toCents(input.w2FederalWithheld ?? 0);
  const estimatedPayments = computeEstimatedPayments({
    currentYearTax: totalTax,
    priorYearTaxLiability:
      input.priorYearTaxLiability != null
        ? toCents(input.priorYearTaxLiability)
        : null,
    priorYearAgi:
      input.priorYearAgi != null ? toCents(input.priorYearAgi) : null,
    alreadyWithheld: withheld,
    filingStatus: status,
    data: estimated,
  });

  if (w2Wages > 0) {
    // The employee half of FICA is withheld by the employer, so it never passes
    // through this engine. Take-home therefore overstates what actually lands in
    // the bank for the wage portion. Closing this gap is the work that turns the
    // engine into a take-home pay calculator.
    warnings.push(
      "Wage income is included for bracket and wage-base purposes, but the " +
        "Social Security and Medicare withheld from your paycheck is not " +
        "subtracted. Take-home is overstated by roughly 7.65% of wages up to " +
        "the wage base.",
    );
  }

  if (state?.staleForTargetYear) {
    warnings.push(
      `${state.name} figures are from the prior tax year; the state had not ` +
        "published updated brackets.",
    );
  }

  return {
    taxYear: input.taxYear,
    filingStatus: status,

    netProfit: toDollars(netProfit),
    selfEmployment: {
      netEarnings: toDollars(se.netEarnings),
      socialSecurity: toDollars(se.socialSecurity),
      medicare: toDollars(se.medicare),
      additionalMedicare: toDollars(se.additionalMedicare),
      total: toDollars(se.total),
      deductiblePortion: toDollars(se.deductiblePortion),
    },
    adjustedGrossIncome: toDollars(adjustedGrossIncome),
    standardDeduction: toDollars(standardDeduction),
    deductionUsed,
    qbi: {
      deduction: toDollars(qbi.deduction),
      qualifiedIncome: toDollars(qbi.qualifiedIncome),
      limitedByTaxableIncome: qbi.limitedByTaxableIncome,
      aboveThreshold: qbi.aboveThreshold,
      range: qbi.range,
    },
    taxableIncome: toDollars(taxableIncome),

    federalTax: toDollars(federalTax),
    federalBrackets,
    state: {
      slug: stateResult.slug,
      name: stateResult.name,
      structure: stateResult.structure,
      taxableIncome: toDollars(stateResult.taxableIncome),
      amount: toDollars(stateResult.amount),
      surtax: toDollars(stateResult.surtax),
      brackets: stateResult.brackets,
      notes: stateResult.notes,
    },

    totalTax: toDollars(totalTax),
    takeHome: toDollars(takeHome),
    effectiveRate,
    marginalRate: federalMarginal + stateResult.marginalRate,
    monthlySetAside: toDollars(Math.round(totalTax / 12)),

    estimatedPayments: {
      required: estimatedPayments.required,
      requiredAnnualPayment: toDollars(estimatedPayments.requiredAnnualPayment),
      basis: estimatedPayments.basis,
      alreadyWithheld: toDollars(estimatedPayments.alreadyWithheld),
      remaining: toDollars(estimatedPayments.remaining),
      installments: estimatedPayments.installments.map((i) => ({
        period: i.period,
        dueDate: i.dueDate,
        covers: i.covers,
        amount: toDollars(i.amount),
      })),
    },
    warnings,
  };
}
