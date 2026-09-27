import { estimateTax, type EngineData } from "./index.js";
import { computeStateTax } from "./state.js";
import {
  type Cents,
  atLeastZero,
  percentOf,
  splitEvenly,
  toCents,
  toDollars,
} from "./money.js";
import type { FilingStatus } from "./types.js";

/**
 * The salary path. The core engine models a self-employed person: it applies
 * self-employment tax and never subtracts the FICA an employer withholds. Using
 * it for a salary overstated take-home by roughly 7.65% of wages, and every page
 * that quoted "a $95,000 salary" was in fact quoting a self-employment figure.
 *
 * This module adds what an employee actually pays and reuses the core engine only
 * for the income-tax layer, where wages and profit are treated alike.
 */

export type PayPeriods = 52 | 26 | 24 | 12;

export interface WageInput {
  taxYear: number;
  filingStatus: FilingStatus;
  /** Gross annual salary before any deduction. */
  annualWages: number;
  /**
   * Traditional 401(k)/403(b) deferrals. Reduce income-tax wages but NOT FICA
   * wages (26 U.S.C. 3121(v)(1)(A)) — the most common error in paycheck tools.
   */
  preTaxRetirement?: number;
  /**
   * Section 125 cafeteria-plan deductions: health, dental and vision premiums,
   * and HSA contributions made through payroll. Reduce both income-tax wages
   * and FICA wages.
   */
  section125?: number;
  payPeriods?: PayPeriods;
  /** Children who qualify for the child tax credit, and other dependents. */
  qualifyingChildren?: number;
  otherDependents?: number;
}

export interface FicaResult {
  ficaWages: number;
  socialSecurity: number;
  medicare: number;
  additionalMedicare: number;
  total: number;
}

export interface WageResult {
  grossWages: number;
  incomeTaxWages: number;
  fica: FicaResult;
  federalTax: number;
  stateTax: number;
  stateName: string | null;
  totalTax: number;
  preTaxDeductions: number;
  /** State-mandated employee contributions (paid leave, disability, unemployment). */
  stateContributions: { id: string; name: string; amount: number }[];
  stateContributionsTotal: number;
  /** What lands in the account over a year: gross less taxes, contributions and pre-tax deductions. */
  netPay: number;
  netPayMonthly: number;
  payPeriods: PayPeriods;
  /** Per-check net pay; the checks sum exactly to `netPay`. */
  netPerPaycheck: number[];
  effectiveRate: number;
  marginalRate: number;
  warnings: string[];
}

/**
 * Pennsylvania does not follow the federal exclusion for elective deferrals: an
 * employee's 401(k) contribution is taxable Pennsylvania compensation. New Jersey
 * is often listed alongside it, wrongly for 401(k) plans — N.J.S.A. 54A:6-21
 * excludes them — but it does tax 403(b) and 457 deferrals.
 */
const STATES_TAXING_401K_DEFERRALS = new Set(["pennsylvania"]);
const STATES_TAXING_403B_457_DEFERRALS = new Set(["new-jersey"]);

/**
 * Employee FICA. The employee pays half of each self-employment rate; the rates
 * are derived from the dataset rather than restated here so that one annual
 * update moves both paths.
 */
export function computeEmployeeFica(
  ficaWages: Cents,
  filingStatus: FilingStatus,
  data: EngineData,
): { socialSecurity: Cents; medicare: Cents; additionalMedicare: Cents } {
  const se = data.federal.selfEmployment;
  const wageBase = toCents(se.socialSecurityWageBase);
  const socialSecurity = percentOf(
    Math.min(ficaWages, wageBase),
    se.socialSecurityRate / 2,
  );
  const medicare = percentOf(ficaWages, se.medicareRate / 2);
  // The Additional Medicare Tax has no employer share. The employer withholds it
  // above $200,000 regardless of filing status, but the liability — which is what
  // take-home depends on over a year — uses the filing-status threshold.
  const threshold = toCents(se.additionalMedicare.thresholds[filingStatus]);
  const additionalMedicare = percentOf(
    atLeastZero(ficaWages - threshold),
    se.additionalMedicare.rate,
  );
  return { socialSecurity, medicare, additionalMedicare };
}

export function estimateWageTakeHome(
  input: WageInput,
  data: EngineData,
): WageResult {
  const warnings: string[] = [];
  const periods: PayPeriods = input.payPeriods ?? 26;

  const gross = toCents(input.annualWages);
  const retirement = toCents(input.preTaxRetirement ?? 0);
  const cafeteria = toCents(input.section125 ?? 0);
  if (retirement + cafeteria > gross) {
    warnings.push("Pre-tax deductions exceed gross wages; they were capped at gross.");
  }
  const ficaWages = atLeastZero(gross - cafeteria);
  const incomeTaxWages = atLeastZero(gross - retirement - cafeteria);

  const fica = computeEmployeeFica(ficaWages, input.filingStatus, data);
  const ficaTotal = fica.socialSecurity + fica.medicare + fica.additionalMedicare;

  // The income-tax layer: wages and business profit are taxed alike once they
  // reach the brackets, so the core engine is reused with no business income.
  const core = estimateTax(
    {
      taxYear: input.taxYear,
      filingStatus: input.filingStatus,
      businessIncome: 0,
      w2Wages: toDollars(incomeTaxWages),
      w2SocialSecurityWages: toDollars(ficaWages),
      qualifyingChildren: input.qualifyingChildren ?? 0,
      otherDependents: input.otherDependents ?? 0,
    },
    data,
  );
  // The core engine warns that it does not subtract employee FICA. This path does,
  // so that warning no longer applies and would be false on a salary page.
  for (const w of core.warnings) {
    if (!w.startsWith("Wage income is included for bracket")) warnings.push(w);
  }

  let stateTax = toCents(core.state.amount + core.state.surtax);
  const slug = data.state?.slug ?? null;
  if (slug && retirement > 0 && STATES_TAXING_401K_DEFERRALS.has(slug)) {
    // Recompute the state layer on wages that include the deferral. The first
    // version only warned, and the acceptance table showed Pennsylvania tax
    // falling by $307 on a $10,000 deferral that Pennsylvania does not exclude.
    const s = computeStateTax({
      federalAgi: toCents(core.adjustedGrossIncome) + retirement,
      filingStatus: input.filingStatus,
      state: data.state,
      dependents: { children: input.qualifyingChildren ?? 0, others: input.otherDependents ?? 0 },
    });
    stateTax = s.amount + s.surtax;
  }
  if (slug && retirement > 0 && STATES_TAXING_403B_457_DEFERRALS.has(slug)) {
    warnings.push(
      `${data.state?.name} excludes 401(k) deferrals but taxes 403(b) and 457 ` +
        "deferrals; the state figure assumes a 401(k).",
    );
  }

  // Contributions are levied on gross wages: a 401(k) deferral does not reduce them.
  const contributions = (data.state?.employeeContributions ?? []).map((c) => {
    let amount = percentOf(gross, c.rate);
    if (c.weeklyMax != null) amount = Math.min(amount, toCents(c.weeklyMax) * 52);
    if (c.annualMax != null) amount = Math.min(amount, toCents(c.annualMax));
    if (c.optional) {
      warnings.push(`${c.name}: employers may deduct this but are not required to; the figure assumes yours does.`);
    }
    return { id: c.id, name: c.name, amount };
  });
  if (data.state?.modelCoverage?.payrollContributions === "not-modelled") {
    warnings.push(
      `${data.state.name} requires employee payroll contributions (such as paid leave or ` +
        "disability insurance) that are not yet included, so take-home is slightly overstated.",
    );
  }
  const contributionsTotal = contributions.reduce((a, c) => a + c.amount, 0);

  const federalTax = toCents(core.federalTax);
  const totalTax = ficaTotal + federalTax + stateTax;
  const preTax = retirement + cafeteria;
  const netPay = atLeastZero(gross - totalTax - preTax - contributionsTotal);
  const netPerPaycheck = splitEvenly(netPay, periods).map(toDollars);

  if (fica.additionalMedicare > 0 && input.filingStatus !== "single") {
    warnings.push(
      "Your employer withholds Additional Medicare Tax only above $200,000 of " +
        "your own wages; the liability shown uses your filing-status threshold, " +
        "so withholding and liability can differ.",
    );
  }

  return {
    grossWages: toDollars(gross),
    incomeTaxWages: toDollars(incomeTaxWages),
    fica: {
      ficaWages: toDollars(ficaWages),
      socialSecurity: toDollars(fica.socialSecurity),
      medicare: toDollars(fica.medicare),
      additionalMedicare: toDollars(fica.additionalMedicare),
      total: toDollars(ficaTotal),
    },
    federalTax: toDollars(federalTax),
    stateTax: toDollars(stateTax),
    stateName: data.state?.name ?? null,
    totalTax: toDollars(totalTax),
    preTaxDeductions: toDollars(preTax),
    stateContributions: contributions.map((c) => ({ ...c, amount: toDollars(c.amount) })),
    stateContributionsTotal: toDollars(contributionsTotal),
    netPay: toDollars(netPay),
    netPayMonthly: toDollars(Math.round(netPay / 12)),
    payPeriods: periods,
    netPerPaycheck,
    effectiveRate: gross > 0 ? (totalTax / gross) * 100 : 0,
    marginalRate:
      core.marginalRate +
      (ficaWages < toCents(data.federal.selfEmployment.socialSecurityWageBase)
        ? data.federal.selfEmployment.socialSecurityRate / 2
        : 0) +
      data.federal.selfEmployment.medicareRate / 2,
    warnings,
  };
}
