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
  localTaxNote: string | null;
  notes: string[];
  staleForTargetYear?: boolean;
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
