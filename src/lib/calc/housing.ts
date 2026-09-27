import { type Cents, atLeastZero, toCents, toDollars } from "../tax/money.js";

/**
 * Housing calculators: house payment (PITI), home affordability and closing
 * costs. Pure arithmetic on the user's inputs — no location data is assumed.
 * Where a figure depends on a place (property tax rate, transfer tax) it is an
 * input, and the page must say where to find it.
 */

export interface LoanTerms {
  /** Annual interest rate in percent, e.g. 6.5. */
  ratePercent: number;
  termYears: number;
}

/** Monthly principal and interest, rounded once to the cent. */
export function principalAndInterest(loan: Cents, terms: LoanTerms): Cents {
  if (loan <= 0) return 0;
  const n = Math.round(terms.termYears * 12);
  if (n <= 0) throw new Error("The loan term must be positive.");
  const r = terms.ratePercent / 100 / 12;
  if (r === 0) return Math.ceil(loan / n);
  return Math.round((loan * r) / (1 - Math.pow(1 + r, -n)));
}

export interface HousePaymentInput extends LoanTerms {
  price: number;
  downPayment: number;
  /** Annual property tax as a percent of price, or a dollar figure. */
  propertyTaxRatePercent?: number;
  propertyTaxAnnual?: number;
  insuranceAnnual: number;
  hoaMonthly?: number;
  /** Annual PMI as a percent of the loan; charged only above 80% loan-to-value. */
  pmiRatePercent?: number;
}

export interface HousePayment {
  loanAmount: number;
  loanToValue: number;
  principalAndInterest: number;
  propertyTax: number;
  insurance: number;
  pmi: number;
  hoa: number;
  total: number;
  /** Month number when scheduled balance first reaches 78% of the price. */
  pmiEndsAfterMonth: number | null;
  totalInterest: number;
  warnings: string[];
}

export function housePayment(input: HousePaymentInput): HousePayment {
  const warnings: string[] = [];
  const price = toCents(input.price);
  const down = toCents(input.downPayment);
  if (price <= 0) throw new Error("Enter a price.");
  if (down > price) throw new Error("The down payment exceeds the price.");
  const loan = price - down;
  const ltv = (loan / price) * 100;
  const pi = principalAndInterest(loan, input);

  let tax: Cents;
  if (input.propertyTaxAnnual != null) {
    tax = Math.round(toCents(input.propertyTaxAnnual) / 12);
  } else if (input.propertyTaxRatePercent != null) {
    tax = Math.round((price * input.propertyTaxRatePercent) / 100 / 12);
  } else {
    tax = 0;
    warnings.push(
      "No property tax was entered. It is set by the county and is usually the " +
        "second-largest line in the payment.",
    );
  }
  const insurance = Math.round(toCents(input.insuranceAnnual) / 12);
  const hoa = toCents(input.hoaMonthly ?? 0);

  let pmi: Cents = 0;
  let pmiEnds: number | null = null;
  if (ltv > 80) {
    if (input.pmiRatePercent == null) {
      warnings.push(
        "The down payment is under 20%, so mortgage insurance applies. Enter the " +
          "rate your lender quotes; it varies with credit score.",
      );
    } else {
      pmi = Math.round((loan * input.pmiRatePercent) / 100 / 12);
    }
    // Homeowners Protection Act: automatic termination when the scheduled
    // balance reaches 78% of the original value.
    pmiEnds = monthBalanceReaches(loan, pi, input, Math.floor(price * 0.78));
  }

  const n = Math.round(input.termYears * 12);
  const totalInterest = atLeastZero(pi * n - loan);

  return {
    loanAmount: toDollars(loan),
    loanToValue: ltv,
    principalAndInterest: toDollars(pi),
    propertyTax: toDollars(tax),
    insurance: toDollars(insurance),
    pmi: toDollars(pmi),
    hoa: toDollars(hoa),
    total: toDollars(pi + tax + insurance + pmi + hoa),
    pmiEndsAfterMonth: pmiEnds,
    totalInterest: toDollars(totalInterest),
    warnings,
  };
}

function monthBalanceReaches(
  loan: Cents,
  payment: Cents,
  terms: LoanTerms,
  target: Cents,
): number | null {
  const r = terms.ratePercent / 100 / 12;
  let balance = loan;
  const n = Math.round(terms.termYears * 12);
  for (let m = 1; m <= n; m++) {
    const interest = Math.round(balance * r);
    balance -= payment - interest;
    if (balance <= target) return m;
  }
  return null;
}

// ---------------------------------------------------------------------------
// Home affordability: the highest price the lender ratios allow
// ---------------------------------------------------------------------------

export type RatioMode = "conventional" | "maximum";

/**
 * 28/36 is conventional guidance. 43% was the General Qualified Mortgage DTI cap
 * until the CFPB replaced it with a price-based test in 2021; it survives as a
 * common manual-underwriting ceiling, which is what "maximum" models here.
 */
export const RATIOS: Record<RatioMode, { front: number | null; back: number }> = {
  conventional: { front: 28, back: 36 },
  maximum: { front: null, back: 43 },
};

export interface AffordabilityInput extends LoanTerms {
  grossAnnualIncome: number;
  monthlyDebts: number;
  downPayment: number;
  propertyTaxRatePercent: number;
  insuranceAnnual: number;
  hoaMonthly?: number;
  pmiRatePercent?: number;
  mode?: RatioMode;
}

export interface Affordability {
  maxPrice: number;
  /** Null when existing debt already uses the whole ratio. */
  payment: HousePayment | null;
  housingBudget: number;
  bindingRatio: "front-end" | "back-end";
  warnings: string[];
}

export function homeAffordability(input: AffordabilityInput): Affordability {
  const mode = input.mode ?? "conventional";
  const ratio = RATIOS[mode];
  const monthly = toCents(input.grossAnnualIncome) / 12;
  const debts = toCents(input.monthlyDebts);
  const front = ratio.front == null ? Infinity : Math.floor((monthly * ratio.front) / 100);
  const back = Math.floor((monthly * ratio.back) / 100) - debts;
  const budget = Math.min(front, back);
  const warnings: string[] = [];
  if (budget <= 0) {
    return {
      maxPrice: 0,
      payment: null,
      housingBudget: 0,
      bindingRatio: "back-end",
      warnings: ["Existing debt payments already use the whole back-end ratio."],
    };
  }

  const pay = (priceCents: Cents) =>
    housePayment({
      ...input,
      price: toDollars(priceCents),
      downPayment: Math.min(input.downPayment, toDollars(priceCents)),
    });
  const fits = (priceCents: Cents) => toCents(pay(priceCents).total) <= budget;

  // The payment rises with price, with one upward jump where PMI starts; the
  // search finds the highest price that fits either side of that jump.
  let lo: Cents = toCents(input.downPayment);
  if (!fits(lo)) lo = 0;
  let hi: Cents = Math.max(lo, 100) * 2;
  while (fits(hi)) hi *= 2;
  while (hi - lo > 100) {
    const mid = Math.floor((lo + hi) / 2);
    if (fits(mid)) lo = mid;
    else hi = mid;
  }
  const maxPrice = Math.floor(lo / 100) * 100; // whole dollars
  const payment = pay(maxPrice);
  warnings.push(...payment.warnings);
  if (mode === "conventional") {
    warnings.push(
      "28/36 is conventional guidance, not law. 43% is a common manual-" +
        "underwriting ceiling, and automated underwriting approves some loans higher.",
    );
  }
  warnings.push(
    "Closing costs and maintenance are not in any lender ratio; budget for both separately.",
  );
  return {
    maxPrice: toDollars(maxPrice),
    payment,
    housingBudget: toDollars(budget),
    bindingRatio: front <= back ? "front-end" : "back-end",
    warnings,
  };
}

// ---------------------------------------------------------------------------
// Closing costs
// ---------------------------------------------------------------------------

export interface ClosingCostInput {
  price: number;
  loanAmount: number;
  ratePercent: number;
  /** Day of the month the loan closes; interest runs to month end. */
  closingDay: number;
  daysInClosingMonth: number;
  propertyTaxAnnual: number;
  insuranceAnnual: number;
  /** Months of tax and insurance the lender holds in escrow at closing. */
  escrowMonths: number;
  /** Lender charges: origination, points, underwriting, appraisal, credit report. */
  lenderFees: number;
  /** Title insurance, settlement, recording. */
  titleAndSettlement: number;
  /** State and local transfer tax payable by the buyer. */
  transferTax: number;
}

export interface ClosingCosts {
  prepaidInterest: number;
  firstYearInsurance: number;
  escrowReserves: number;
  lenderFees: number;
  titleAndSettlement: number;
  transferTax: number;
  total: number;
  percentOfPrice: number;
  warnings: string[];
}

export function closingCosts(input: ClosingCostInput): ClosingCosts {
  const warnings: string[] = [];
  const loan = toCents(input.loanAmount);
  const days = input.daysInClosingMonth - input.closingDay + 1;
  if (days < 0 || input.closingDay < 1) throw new Error("Check the closing date.");
  // Per-diem interest on a 365-day year, from closing to the end of the month.
  const prepaidInterest = Math.round((loan * input.ratePercent) / 100 / 365 * days);
  const insurance = toCents(input.insuranceAnnual);
  const escrow = Math.round(
    ((toCents(input.propertyTaxAnnual) + insurance) / 12) * input.escrowMonths,
  );
  const lender = toCents(input.lenderFees);
  const title = toCents(input.titleAndSettlement);
  const transfer = toCents(input.transferTax);
  const total = prepaidInterest + insurance + escrow + lender + title + transfer;
  const price = toCents(input.price);
  if (transfer === 0) {
    warnings.push(
      "No transfer tax was entered. Some states charge none; others charge above " +
        "1% of the price, and custom decides whether buyer or seller pays.",
    );
  }
  warnings.push("Seller-paid items and lender credits, if any, reduce this total.");
  return {
    prepaidInterest: toDollars(prepaidInterest),
    firstYearInsurance: toDollars(insurance),
    escrowReserves: toDollars(escrow),
    lenderFees: toDollars(lender),
    titleAndSettlement: toDollars(title),
    transferTax: toDollars(transfer),
    total: toDollars(total),
    percentOfPrice: price > 0 ? (total / price) * 100 : 0,
    warnings,
  };
}
