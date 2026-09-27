import { estimateWageTakeHome, type WageInput } from "../tax/payroll.js";
import type { EngineData } from "../tax/index.js";
import { type Cents, toCents, toDollars } from "../tax/money.js";
import type { FilingStatus } from "../tax/types.js";
import {
  COST_CATEGORIES,
  type Bedrooms,
  type CostCategory,
  type HouseholdSize,
  type MonthlyCosts,
  type PlaceCostData,
  type SpendingBaseline,
} from "./types.js";

export * from "./types.js";
export * from "./calculator.js";
export * from "./places.js";

/**
 * The cost-of-living engine. It shares nothing with the tax engine except money
 * arithmetic, and it calls the salary path of the tax engine where a comparison
 * has to include tax (spec 4-9-5).
 */

function assertComparable(from: PlaceCostData, to: PlaceCostData): void {
  if (from.region !== to.region) {
    throw new Error(
      `${from.name} and ${to.name} are priced on different bases (BEA against ` +
        "Eurostat); a ratio between them would be meaningless.",
    );
  }
  for (const p of [from, to]) {
    if (!(p.indices.allItems > 0)) {
      throw new Error(`${p.name} has no all-items index.`);
    }
  }
}

/** Multiply cents by a ratio of two indices, rounding once, at the end. */
function scale(amount: Cents, target: number, source: number): Cents {
  return Math.round((amount * target) / source);
}

// ---------------------------------------------------------------------------
// 4-9-2. Category scaling
// ---------------------------------------------------------------------------

export interface ScaledRow {
  category: CostCategory;
  origin: number;
  destination: number;
  /** Which index produced the ratio — the category's own, or all items. */
  indexUsed: "category" | "allItems";
}

export interface ScaledCosts {
  rows: ScaledRow[];
  originTotal: number;
  destinationTotal: number;
  difference: number;
  percentDifference: number;
  warnings: string[];
}

export function scaleCosts(
  costs: MonthlyCosts,
  from: PlaceCostData,
  to: PlaceCostData,
): ScaledCosts {
  assertComparable(from, to);
  const warnings: string[] = [];
  const rows: ScaledRow[] = [];
  let originTotal = 0;
  let destinationTotal = 0;

  for (const category of COST_CATEGORIES) {
    const value = costs[category];
    if (value == null) continue;
    if (value < 0) throw new Error(`${category} cannot be negative.`);
    const amount = toCents(value);
    const src = from.indices[category];
    const dst = to.indices[category];
    let scaled: Cents;
    let indexUsed: ScaledRow["indexUsed"];
    if (src != null && dst != null && src > 0) {
      scaled = scale(amount, dst, src);
      indexUsed = "category";
    } else {
      // No invented substitute (rule 5-3): the official all-items ratio is used,
      // and the page says so.
      scaled = scale(amount, to.indices.allItems, from.indices.allItems);
      indexUsed = "allItems";
      warnings.push(
        `No separate ${category} index is published for both places, so the ` +
          "overall price level was used for that line.",
      );
    }
    rows.push({
      category,
      origin: toDollars(amount),
      destination: toDollars(scaled),
      indexUsed,
    });
    originTotal += amount;
    destinationTotal += scaled;
  }

  return {
    rows,
    originTotal: toDollars(originTotal),
    destinationTotal: toDollars(destinationTotal),
    difference: toDollars(destinationTotal - originTotal),
    percentDifference:
      originTotal > 0 ? (destinationTotal / originTotal - 1) * 100 : 0,
    warnings,
  };
}

/** The salary that buys the same basket in the destination. */
export function equivalentSalary(
  salary: number,
  from: PlaceCostData,
  to: PlaceCostData,
): number {
  assertComparable(from, to);
  return toDollars(scale(toCents(salary), to.indices.allItems, from.indices.allItems));
}

// ---------------------------------------------------------------------------
// 4-9-5. The comparison that includes tax — the moat
// ---------------------------------------------------------------------------

export interface PlaceTax {
  place: PlaceCostData;
  tax: EngineData;
}

export interface FullComparisonInput {
  taxYear: number;
  filingStatus: FilingStatus;
  originSalary: number;
  /** Defaults to the origin salary: "the same job, moved". Set it for a job offer. */
  destinationSalary?: number;
}

export interface FullComparison {
  originNetPay: number;
  destinationNetPay: number;
  /** Destination net pay expressed in origin prices. */
  destinationNetInOriginPrices: number;
  /** Net pay change from tax and salary alone, before prices. */
  taxAndSalaryEffect: number;
  /** What the price level adds or removes. */
  priceEffect: number;
  /**
   * The answer: positive means better off at the destination, in origin
   * dollars. Always equals taxAndSalaryEffect + priceEffect.
   */
  realAnnualDifference: number;
  warnings: string[];
}

/**
 * Spec 4-9-5 writes the answer as "tax difference minus cost difference". It is
 * implemented here as destination net pay deflated by the price-level ratio,
 * which is the same idea without needing the user's spending basket — and it
 * decomposes exactly into a tax-and-salary part and a price part.
 */
export function compareWithTax(
  input: FullComparisonInput,
  origin: PlaceTax,
  destination: PlaceTax,
): FullComparison {
  assertComparable(origin.place, destination.place);
  const wage = (salary: number, tax: EngineData) =>
    estimateWageTakeHome(
      {
        taxYear: input.taxYear,
        filingStatus: input.filingStatus,
        annualWages: salary,
      } satisfies WageInput,
      tax,
    );

  const o = wage(input.originSalary, origin.tax);
  const d = wage(input.destinationSalary ?? input.originSalary, destination.tax);
  const oNet = toCents(o.netPay);
  const dNet = toCents(d.netPay);
  const dInOrigin = scale(
    dNet,
    origin.place.indices.allItems,
    destination.place.indices.allItems,
  );

  const warnings = [...new Set([...o.warnings, ...d.warnings])];
  warnings.push(
    "Assumes net pay is spent at local prices. Savings and money sent elsewhere " +
      "are not affected by the local price level.",
  );
  if (origin.place.dataYear !== destination.place.dataYear) {
    warnings.push("The two places use price data from different years.");
  }

  return {
    originNetPay: toDollars(oNet),
    destinationNetPay: toDollars(dNet),
    destinationNetInOriginPrices: toDollars(dInOrigin),
    taxAndSalaryEffect: toDollars(dNet - oNet),
    priceEffect: toDollars(dInOrigin - dNet),
    realAnnualDifference: toDollars(dInOrigin - oNet),
    warnings,
  };
}

// ---------------------------------------------------------------------------
// Rent affordability
// ---------------------------------------------------------------------------

export type BurdenLevel = "not burdened" | "cost burdened" | "severely cost burdened";

/** HUD's definitions: above 30% of income on gross rent, and above 50%. */
export const COST_BURDEN_PERCENT = 30;
export const SEVERE_BURDEN_PERCENT = 50;

export function burdenLevel(rentShare: number): BurdenLevel {
  if (rentShare > SEVERE_BURDEN_PERCENT) return "severely cost burdened";
  if (rentShare > COST_BURDEN_PERCENT) return "cost burdened";
  return "not burdened";
}

export interface RentAffordabilityInput {
  grossAnnualIncome: number;
  place?: PlaceCostData;
  bedrooms?: Bedrooms;
}

export interface RentAffordability {
  monthlyIncome: number;
  /** 30% of gross monthly income: the federal cost-burden line. */
  ceiling: number;
  /** 50%: above this a household is severely cost burdened. */
  severeLine: number;
  /** The common landlord screen: gross monthly income of at least 3x rent. */
  landlordScreenMax: number;
  market: null | {
    fairMarketRent: number;
    bedrooms: Bedrooms;
    shareOfIncome: number;
    burden: BurdenLevel;
    /** Positive: the ceiling clears the market rent by this much. */
    headroom: number;
    /** Income at which the market rent sits exactly on the 30% line. */
    incomeNeededAt30: number;
  };
  warnings: string[];
}

export function rentAffordability(input: RentAffordabilityInput): RentAffordability {
  const warnings: string[] = [];
  const monthly = Math.round(toCents(input.grossAnnualIncome) / 12);
  const ceiling = Math.round((monthly * COST_BURDEN_PERCENT) / 100);
  const severe = Math.round((monthly * SEVERE_BURDEN_PERCENT) / 100);
  const landlord = Math.floor(monthly / 3);

  let market: RentAffordability["market"] = null;
  if (input.place) {
    const bedrooms = input.bedrooms ?? 1;
    const fmr = input.place.referenceRent?.[`bedrooms${bedrooms}`];
    if (fmr == null) {
      warnings.push(
        `No Fair Market Rent is published for a ${bedrooms}-bedroom unit in ` +
          `${input.place.name}; the market comparison is omitted.`,
      );
    } else {
      const rent = toCents(fmr);
      const share = monthly > 0 ? (rent / monthly) * 100 : Infinity;
      market = {
        fairMarketRent: toDollars(rent),
        bedrooms,
        shareOfIncome: share,
        burden: burdenLevel(share),
        headroom: toDollars(ceiling - rent),
        incomeNeededAt30: toDollars(Math.round((rent * 12 * 100) / COST_BURDEN_PERCENT)),
      };
    }
  }
  warnings.push(
    "Fair Market Rent is gross rent — shelter rent plus tenant-paid utilities. " +
      "If a listing excludes utilities, add them before comparing.",
  );
  return {
    monthlyIncome: toDollars(monthly),
    ceiling: toDollars(ceiling),
    severeLine: toDollars(severe),
    landlordScreenMax: toDollars(landlord),
    market,
    warnings,
  };
}

// ---------------------------------------------------------------------------
// Living wage: solve for the gross salary that covers a place's costs
// ---------------------------------------------------------------------------

export interface LivingWageInput {
  taxYear: number;
  filingStatus: FilingStatus;
  place: PlaceCostData;
  tax: EngineData;
  bedrooms: Bedrooms;
  /**
   * The household's other monthly costs. If `costsFrom` is given they are the
   * user's costs where they live now and are scaled into `place`; otherwise they
   * are taken as already priced in `place`. No default basket is invented.
   */
  otherMonthlyCosts: Omit<MonthlyCosts, "rent">;
  costsFrom?: PlaceCostData;
  /** Rent the user actually expects to pay; defaults to Fair Market Rent. */
  rentOverride?: number;
}

export interface LivingWage {
  monthlyRent: number;
  rentSource: "HUD Fair Market Rent" | "user";
  monthlyOther: number;
  requiredNetAnnual: number;
  grossSalary: number;
  hourlyAt2080: number;
  netPayAtThatSalary: number;
  warnings: string[];
}

const HOURS_PER_YEAR = 2080;

export function livingWage(input: LivingWageInput): LivingWage {
  const warnings: string[] = [];

  let rent: Cents;
  let rentSource: LivingWage["rentSource"];
  if (input.rentOverride != null) {
    rent = toCents(input.rentOverride);
    rentSource = "user";
  } else {
    const fmr = input.place.referenceRent?.[`bedrooms${input.bedrooms}`];
    if (fmr == null) {
      throw new Error(
        `No Fair Market Rent for a ${input.bedrooms}-bedroom unit in ` +
          `${input.place.name}; enter a rent instead.`,
      );
    }
    rent = toCents(fmr);
    rentSource = "HUD Fair Market Rent";
  }

  let other: Cents;
  if (input.costsFrom) {
    const s = scaleCosts(input.otherMonthlyCosts, input.costsFrom, input.place);
    other = toCents(s.destinationTotal);
    warnings.push(...s.warnings);
  } else {
    other = COST_CATEGORIES.filter((c) => c !== "rent").reduce(
      (acc, c) => acc + toCents(input.otherMonthlyCosts[c as Exclude<CostCategory, "rent">] ?? 0),
      0,
    );
  }

  const required = (rent + other) * 12;
  const netAt = netPayFn(input.taxYear, input.filingStatus, input.tax);
  const gross = grossForNet(required, netAt);

  warnings.push(
    "A break-even figure: it covers the costs entered and nothing else — no " +
      "savings, debt repayment or discretionary spending.",
  );

  return {
    monthlyRent: toDollars(rent),
    rentSource,
    monthlyOther: toDollars(other),
    requiredNetAnnual: toDollars(required),
    grossSalary: toDollars(gross),
    hourlyAt2080: toDollars(Math.round(gross / HOURS_PER_YEAR)),
    netPayAtThatSalary: toDollars(netAt(gross)),
    warnings,
  };
}



// ---------------------------------------------------------------------------
// Shared: solve for the gross salary that yields a given net
// ---------------------------------------------------------------------------

function netPayFn(taxYear: number, filingStatus: FilingStatus, tax: EngineData) {
  return (grossCents: Cents): Cents =>
    toCents(
      estimateWageTakeHome(
        { taxYear, filingStatus, annualWages: toDollars(grossCents) },
        tax,
      ).netPay,
    );
}

/**
 * Smallest gross (in cents) whose net pay reaches `targetNet`. Net pay rises with
 * gross everywhere — no combined marginal rate reaches 100% — so bisection finds
 * it to the cent.
 */
export function grossForNet(targetNet: Cents, netAt: (g: Cents) => Cents): Cents {
  if (targetNet <= 0) return 0;
  let lo: Cents = targetNet;
  let hi: Cents = Math.max(targetNet * 3, 100);
  while (netAt(hi) < targetNet) hi *= 2;
  while (hi - lo > 1) {
    const mid = Math.floor((lo + hi) / 2);
    if (netAt(mid) >= targetNet) hi = mid;
    else lo = mid;
  }
  return netAt(lo) >= targetNet ? lo : hi;
}

// ---------------------------------------------------------------------------
// Equivalent salary AFTER tax — the figure no price-only tool can give
// ---------------------------------------------------------------------------

export interface EquivalentAfterTax {
  originNetPay: number;
  /** Net pay needed at the destination to buy what origin net pay buys. */
  targetNetAtDestination: number;
  /** Gross salary at the destination that produces that net pay. */
  equivalentGross: number;
  /** The price-only answer, for contrast: salary x index ratio. */
  priceOnlyEquivalent: number;
  /** How far tax moves the answer away from the price-only one. */
  taxAdjustment: number;
  warnings: string[];
}

export function equivalentSalaryAfterTax(
  input: { taxYear: number; filingStatus: FilingStatus; salary: number },
  origin: PlaceTax,
  destination: PlaceTax,
): EquivalentAfterTax {
  assertComparable(origin.place, destination.place);
  const oNet = netPayFn(input.taxYear, input.filingStatus, origin.tax)(toCents(input.salary));
  const target = scale(oNet, destination.place.indices.allItems, origin.place.indices.allItems);
  const gross = grossForNet(target, netPayFn(input.taxYear, input.filingStatus, destination.tax));
  const priceOnly = toCents(equivalentSalary(input.salary, origin.place, destination.place));
  return {
    originNetPay: toDollars(oNet),
    targetNetAtDestination: toDollars(target),
    equivalentGross: toDollars(gross),
    priceOnlyEquivalent: toDollars(priceOnly),
    taxAdjustment: toDollars(gross - priceOnly),
    warnings: [
      "Holds after-tax spending power constant: the destination salary buys, after " +
        "that state's tax, what the current salary buys after the current state's tax.",
    ],
  };
}

// ---------------------------------------------------------------------------
// What one place costs a household, by category
// ---------------------------------------------------------------------------

export interface CityCostRow {
  key: string;
  label: string;
  monthly: number;
  basis: "HUD Fair Market Rent" | "national average at local prices" | "your figure";
}

export interface CityCostInput {
  place: PlaceCostData;
  householdSize: HouseholdSize;
  bedrooms: Bedrooms;
  baseline: SpendingBaseline;
  /** The household's own monthly figures, replacing a category's estimate. */
  own?: Partial<Record<string, number>>;
  rentOverride?: number;
}

export interface CityCost {
  rows: CityCostRow[];
  monthlyTotal: number;
  annualTotal: number;
  warnings: string[];
}

/**
 * Rent is HUD's figure for the bedroom count; every other category is the
 * national average for a household of this size, priced at the place's own
 * price level. Nothing is invented: a category the baseline does not carry is
 * not shown, and a place without price indices is refused rather than guessed.
 */
export function cityMonthlyCost(input: CityCostInput): CityCost {
  const { place, baseline } = input;
  if (!(place.indices?.allItems > 0)) {
    throw new Error(`${place.name} has no price level yet; its costs cannot be estimated.`);
  }
  const warnings: string[] = [];
  const rows: CityCostRow[] = [];

  const fmr = place.referenceRent?.[`bedrooms${input.bedrooms}`];
  if (input.rentOverride != null) {
    rows.push({ key: "rent", label: "Rent and utilities", monthly: toDollars(toCents(input.rentOverride)), basis: "your figure" });
  } else if (fmr != null) {
    rows.push({ key: "rent", label: "Rent and utilities", monthly: toDollars(toCents(fmr)), basis: "HUD Fair Market Rent" });
  } else {
    throw new Error(`No Fair Market Rent for ${input.bedrooms} bedrooms in ${place.name}; enter a rent.`);
  }

  const annual = baseline.annualByHouseholdSize[`${input.householdSize}`];
  for (const [key, cat] of Object.entries(baseline.categories)) {
    const own = input.own?.[key];
    if (own != null) {
      rows.push({ key, label: cat.label, monthly: toDollars(toCents(own)), basis: "your figure" });
      continue;
    }
    const base = annual?.[key];
    if (base == null) continue;
    let index = place.indices[cat.index];
    if (index == null) {
      index = place.indices.allItems;
      warnings.push(`${cat.label}: no separate ${cat.index} index for ${place.name}; the overall price level was used.`);
    }
    const factor = (cat.cpiSeries && baseline.priceUpdate?.series[cat.cpiSeries]?.factor) || 1;
    const monthly = Math.round((toCents(base) * factor * index) / 100 / 12);
    rows.push({ key, label: cat.label, monthly: toDollars(monthly), basis: "national average at local prices" });
  }

  const total = rows.reduce((a, r) => a + toCents(r.monthly), 0);
  warnings.push(
    "Categories other than rent are an estimate for a typical household of this size " +
      "at local prices, not your own spending. Replace any line with your figure.",
  );
  if (baseline.priceUpdate) {
    warnings.push(
      `Spending is the ${baseline.year} national average for this household size, carried to ` +
        `${baseline.priceUpdate.toMonth} prices category by category with the Consumer Price Index.`,
    );
  } else if (baseline.year !== place.dataYear) {
    warnings.push(`Spending averages are for ${baseline.year}; price levels for ${place.dataYear}.`);
  }
  return { rows, monthlyTotal: toDollars(total), annualTotal: toDollars(total * 12), warnings };
}

/** A default the user can change: two people per bedroom, never fewer than one bedroom. */
export function suggestedBedrooms(people: number): Bedrooms {
  return Math.min(4, Math.max(1, Math.ceil(people / 2))) as Bedrooms;
}

/** HUD county rents to the engine's `referenceRent` shape. */
export function referenceRentFromFmr(
  county: { rent: Record<string, number> | null } | undefined,
): NonNullable<PlaceCostData["referenceRent"]> | null {
  if (!county?.rent) return null;
  return { ...county.rent } as NonNullable<PlaceCostData["referenceRent"]>;
}
