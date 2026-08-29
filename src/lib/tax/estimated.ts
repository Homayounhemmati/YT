import { type Cents, atLeastZero, percentOf, splitEvenly, toCents } from "./money.js";
import type { EstimatedData, EstimatedPaymentsResult, FilingStatus } from "./types.js";

export interface EstimatedArgs {
  currentYearTax: Cents;
  priorYearTaxLiability: Cents | null;
  priorYearAgi: Cents | null;
  alreadyWithheld: Cents;
  filingStatus: FilingStatus;
  data: EstimatedData;
}

export interface EstimatedComputation
  extends Omit<EstimatedPaymentsResult, "requiredAnnualPayment" | "alreadyWithheld" | "remaining" | "installments"> {
  requiredAnnualPayment: Cents;
  alreadyWithheld: Cents;
  remaining: Cents;
  installments: { period: string; dueDate: string; amount: Cents; covers: string }[];
}

/**
 * Required estimated tax payments under 26 U.S.C. 6654.
 *
 * The safe harbour is the point of this calculation. A freelancer who pays the
 * prior-year amount owes no penalty even if this year turns out far better,
 * which is usually the cheapest way to stay compliant — so the engine picks
 * whichever of the two tests is lower and says which one it used.
 */
export function computeEstimatedPayments({
  currentYearTax,
  priorYearTaxLiability,
  priorYearAgi,
  alreadyWithheld,
  filingStatus,
  data,
}: EstimatedArgs): EstimatedComputation {
  const sh = data.safeHarbor;
  const minimum = toCents(sh.minimumTaxDueForPenalty);

  const currentYearTest = percentOf(currentYearTax, sh.currentYearPercent);

  let requiredAnnualPayment = currentYearTest;
  let basis: EstimatedComputation["basis"] = "currentYear";

  if (priorYearTaxLiability != null && priorYearTaxLiability > 0) {
    // The higher percentage applies when prior-year AGI cleared the threshold.
    const threshold = toCents(sh.highIncomeAgiThreshold[filingStatus]);
    const highIncome = priorYearAgi != null && priorYearAgi > threshold;
    const percent = highIncome ? sh.priorYearPercentHighIncome : sh.priorYearPercent;
    const priorYearTest = percentOf(priorYearTaxLiability, percent);

    if (priorYearTest < requiredAnnualPayment) {
      requiredAnnualPayment = priorYearTest;
      basis = "priorYear";
    }
  }

  // Withholding is treated as paid evenly across the year no matter when it
  // happened, which is why topping up withholding late still cures a shortfall.
  const remaining = atLeastZero(requiredAnnualPayment - alreadyWithheld);
  const balanceDue = atLeastZero(currentYearTax - alreadyWithheld);
  const required = balanceDue >= minimum && remaining > 0;

  const amounts = required
    ? splitEvenly(remaining, data.installments.length)
    : data.installments.map(() => 0);

  return {
    required,
    requiredAnnualPayment,
    basis: required ? basis : "none",
    alreadyWithheld,
    remaining,
    installments: data.installments.map((inst, i) => ({
      period: inst.period,
      dueDate: inst.dueDate,
      covers: inst.covers,
      amount: amounts[i] ?? 0,
    })),
  };
}
