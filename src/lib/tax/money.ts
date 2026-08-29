/**
 * All internal tax arithmetic runs on integer cents.
 *
 * Percentages compound across half a dozen steps in this engine (SE tax, then
 * half of it as a deduction, then brackets, then state). Doing that in floating
 * point lets rounding drift accumulate until the bracket-by-bracket breakdown no
 * longer sums to the total it is supposed to explain — which is exactly the kind
 * of visible inconsistency that destroys trust in a tax tool.
 */

/** A monetary amount in whole cents. */
export type Cents = number;

const CENTS_PER_DOLLAR = 100;

export function toCents(dollars: number): Cents {
  if (!Number.isFinite(dollars)) return 0;
  return Math.round(dollars * CENTS_PER_DOLLAR);
}

export function toDollars(cents: Cents): number {
  return cents / CENTS_PER_DOLLAR;
}

/** Never let a monetary result go negative where the tax code floors it at zero. */
export function atLeastZero(cents: Cents): Cents {
  return cents > 0 ? cents : 0;
}

/**
 * Apply a percentage rate to an amount, rounding to the nearest cent.
 * `rate` is expressed in percent (15.3 means 15.3%), matching the dataset.
 */
export function percentOf(amount: Cents, ratePercent: number): Cents {
  return Math.round((amount * ratePercent) / 100);
}

/** Split an amount into `parts` whole cents that sum exactly back to it. */
export function splitEvenly(amount: Cents, parts: number): Cents[] {
  if (parts <= 0) return [];
  const base = Math.floor(amount / parts);
  const remainder = amount - base * parts;
  return Array.from({ length: parts }, (_, i) => base + (i < remainder ? 1 : 0));
}

export function sum(values: readonly Cents[]): Cents {
  return values.reduce((a, b) => a + b, 0);
}
