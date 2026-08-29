import { type Cents, atLeastZero, percentOf, toCents } from "./money.js";
import type { BracketDetail, BracketRow } from "./types.js";

/**
 * Apply a graduated rate schedule and return both the tax and the per-bracket
 * breakdown.
 *
 * The breakdown is not decoration: showing a user which dollars were taxed at
 * which rate is the single clearest way to explain a tax bill, and every value
 * in it is derived from the same pass that produces the total, so the two can
 * never disagree.
 */
export function applyBrackets(
  taxableIncome: Cents,
  rows: readonly BracketRow[],
): { tax: Cents; detail: BracketDetail[] } {
  const detail: BracketDetail[] = [];
  const income = atLeastZero(taxableIncome);
  if (income === 0 || rows.length === 0) return { tax: 0, detail };

  let tax = 0;
  for (let i = 0; i < rows.length; i += 1) {
    const row = rows[i]!;
    const lower = toCents(row.from);
    if (income <= lower) break;

    const next = rows[i + 1];
    const explicitTop = row.to == null ? null : toCents(row.to);
    const upper = explicitTop ?? (next ? toCents(next.from) : null);

    const top = upper == null ? income : Math.min(income, upper);
    const taxedAmount = atLeastZero(top - lower);
    if (taxedAmount === 0) continue;

    const taxInBracket = percentOf(taxedAmount, row.rate);
    tax += taxInBracket;
    detail.push({
      rate: row.rate,
      from: row.from,
      to: upper == null ? null : upper / 100,
      taxedAmount: taxedAmount / 100,
      taxInBracket: taxInBracket / 100,
    });
  }

  return { tax, detail };
}

/** The rate that applied to the last taxable dollar. */
export function marginalRate(
  taxableIncome: Cents,
  rows: readonly BracketRow[],
): number {
  if (rows.length === 0) return 0;
  const income = atLeastZero(taxableIncome);
  let rate = rows[0]!.rate;
  for (const row of rows) {
    if (income > toCents(row.from)) rate = row.rate;
    else break;
  }
  return rate;
}
