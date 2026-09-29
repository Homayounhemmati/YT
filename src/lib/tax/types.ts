export type FilingStatus =
  | "single"
  | "marriedJointly"
  | "marriedSeparately"
  | "headOfHousehold";

export const FILING_STATUSES: readonly FilingStatus[] = [
  "single",
  "marriedJointly",
  "marriedSeparately",
  "headOfHousehold",
];

/** A bracket row as stored in the dataset: rates in percent, thresholds in dollars. */
export interface BracketRow {
  from: number;
  to?: number | null;
  rate: number;
}

export interface FederalData {
  taxYear: number;
  brackets: Record<FilingStatus, BracketRow[]>;
  standardDeduction: Record<FilingStatus, number>;
  selfEmployment: {
    neseFactor: number;
    minimumEarningsThreshold: number;
    socialSecurityRate: number;
    medicareRate: number;
    socialSecurityWageBase: number;
    deductiblePortion: number;
    additionalMedicare: {
      rate: number;
      thresholds: Record<FilingStatus, number>;
    };
  };
  qbi: {
    maxRate: number;
    phaseOutStart: Record<FilingStatus, number>;
  };
  /** 26 U.S.C. 24 as amended; amounts from the year's Revenue Procedure. */
  childTaxCredit?: {
    perChild: number;
    refundablePerChild: number;
    perOtherDependent: number;
    earnedIncomeThreshold: number;
    refundableRatePercent: number;
    phaseOut: { threshold: Record<FilingStatus, number>; step: number; reductionPerStep: number };
  };
}

export interface StateData {
  slug: string;
  name: string;
  abbr: string;
  structure: "none" | "flat" | "progressive" | "unknown";
  brackets: Partial<Record<FilingStatus, BracketRow[]>>;
  flatRate: number | null;
  zeroBracketUpTo?: number | Record<string, number>;
  standardDeduction: Partial<Record<FilingStatus, number>>;
  surtax: BracketRow[] | null;
  /**
   * Personal exemption for the filer, subtracted after the standard deduction.
   * `agiSchedule` replaces the amount above each AGI threshold (Maryland);
   * `maxAgi` removes it above a ceiling (Illinois).
   */
  personalExemption?: {
    byStatus: Partial<Record<FilingStatus, {
      amount: number;
      agiSchedule?: { overAgi: number; amount: number }[];
      maxAgi?: number | null;
    }>>;
    staleComponent?: boolean;
    effectiveFrom?: string;
    /** The previous year's amount, kept so copy can quote the change. */
    priorYear?: { year: number; amount: number };
  } | null;
  /**
   * New York's supplemental tax (Tax Law section 601(d-5) for 2026): above an AGI
   * floor the benefit of the lower brackets is taken back, phased in over
   * `phaseWidth` dollars of AGI. Amounts are the statute's own table, not derived.
   */
  benefitRecapture?: BenefitRecapture | null;
  /**
   * Employee payroll contributions the state requires or allows on wages — paid
   * leave, disability insurance, unemployment. Not income tax, but they come out of
   * every paycheck. `weeklyMax` caps each week's contribution; `annualMax` the year's.
   */
  employeeContributions?: {
    id: string;
    name: string;
    rate: number;
    annualMax?: number | null;
    weeklyMax?: number | null;
    /** The employer may deduct it but is not required to; the estimate assumes it does. */
    optional?: boolean;
    source: string;
  }[];
  /**
   * What the state allows per dependent, subtracted like the personal exemption.
   * `childrenOnly`: only qualifying children count (North Carolina's child deduction).
   * `extraPerChild`: a further amount for each qualifying child, on top of `amount`.
   * `agiSchedule` steps the amount by federal AGI; `maxAgi` removes it above a ceiling.
   */
  dependentAllowance?: {
    childrenOnly?: boolean;
    /** Added on top of `amount` for each qualifying child (Indiana's $1,500 additional exemption). */
    extraPerChild?: number;
    byStatus: Partial<Record<FilingStatus, {
      amount: number;
      agiSchedule?: { overAgi: number; amount: number }[];
      maxAgi?: number | null;
    }>>;
    source: string;
  } | null;
  /** Whether each part of the state's model is established: a page is built only when it is. */
  modelCoverage?: {
    personalExemption: "modelled" | "none" | "not-extracted";
    /** "not-modelled": the state has a recapture the engine does not yet apply (Connecticut). */
    benefitRecapture?: "modelled" | "none" | "not-modelled";
    /** "not-modelled": the state has employee payroll contributions not yet entered. */
    payrollContributions?: "modelled" | "none" | "not-modelled";
  };
  localTaxNote: string | null;
  notes: string[];
  staleForTargetYear?: boolean;
  /** "verified" once every value a page relies on matches a primary source (data/tax-primary). */
  verification?: "verified" | "pending" | "missing";
}

export interface BenefitRecapture {
  agiFloor: number;
  /** Above this AGI the whole taxable income is taxed at `topRate`. */
  agiCeiling: number;
  topRate: number;
  phaseWidth: number;
  byStatus: Partial<Record<FilingStatus, {
    /** Taxable income at or below `below`: (rate x income - schedule tax) x phase-in fraction. */
    lowIncome: { below: number; rate: number };
    /** Taxable income over `over` and not over `notOver`. */
    rows: {
      over: number;
      notOver: number;
      recaptureBase: number;
      incrementalBenefit: number;
      /** The applicable amount is AGI minus this. */
      agiLess: number;
    }[];
  }>>;
  source: string;
}

export interface EstimatedData {
  taxYear: number;
  installments: {
    period: string;
    covers: string;
    dueDate: string;
    shifted: boolean;
    shiftReason: string | null;
  }[];
  safeHarbor: {
    currentYearPercent: number;
    priorYearPercent: number;
    priorYearPercentHighIncome: number;
    highIncomeAgiThreshold: Record<FilingStatus, number>;
    minimumTaxDueForPenalty: number;
  };
}

export interface TaxInput {
  taxYear: number;
  filingStatus: FilingStatus;
  stateSlug?: string | null;

  /** Gross business / 1099 revenue. */
  businessIncome: number;
  businessExpenses?: number;

  /** Wage income earned alongside the business, if any. */
  w2Wages?: number;
  /** Wages already subject to Social Security; defaults to `w2Wages`. */
  w2SocialSecurityWages?: number;
  w2FederalWithheld?: number;
  otherIncome?: number;

  retirementContribution?: number;
  selfEmployedHealthInsurance?: number;
  hsaContribution?: number;
  itemizedDeductions?: number;

  /** Children who qualify for the child tax credit (under 17 at year end). */
  qualifyingChildren?: number;
  /** Other dependents: the $500 credit, and state dependent allowances. */
  otherDependents?: number;

  /** Specified service trade or business, which limits QBI above the threshold. */
  isSpecifiedServiceBusiness?: boolean;
  priorYearTaxLiability?: number;
  priorYearAgi?: number;
}

export interface BracketDetail {
  rate: number;
  from: number;
  to: number | null;
  taxedAmount: number;
  taxInBracket: number;
}

export interface SelfEmploymentResult {
  netEarnings: number;
  socialSecurity: number;
  medicare: number;
  additionalMedicare: number;
  total: number;
  /** Half of the ordinary SE tax. Additional Medicare Tax is not deductible. */
  deductiblePortion: number;
}

export interface QbiResult {
  deduction: number;
  qualifiedIncome: number;
  limitedByTaxableIncome: boolean;
  aboveThreshold: boolean;
  /** Present only when the phase-in makes a single number misleading. */
  range: { low: number; high: number } | null;
}

export interface StateResult {
  slug: string | null;
  name: string | null;
  structure: string | null;
  taxableIncome: number;
  amount: number;
  surtax: number;
  brackets: BracketDetail[];
  notes: string[];
}

export interface EstimatedPaymentsResult {
  required: boolean;
  requiredAnnualPayment: number;
  basis: "currentYear" | "priorYear" | "none";
  alreadyWithheld: number;
  remaining: number;
  installments: {
    period: string;
    dueDate: string;
    amount: number;
    covers: string;
  }[];
}

export interface TaxResult {
  taxYear: number;
  filingStatus: FilingStatus;

  netProfit: number;
  selfEmployment: SelfEmploymentResult;
  adjustedGrossIncome: number;
  standardDeduction: number;
  deductionUsed: "standard" | "itemized";
  qbi: QbiResult;
  taxableIncome: number;

  federalTax: number;
  federalTaxBeforeCredits: number;
  childTaxCredit: { nonrefundable: number; refundable: number };
  federalBrackets: BracketDetail[];
  state: StateResult;

  totalTax: number;
  takeHome: number;
  effectiveRate: number;
  marginalRate: number;
  monthlySetAside: number;

  estimatedPayments: EstimatedPaymentsResult;
  warnings: string[];
}
