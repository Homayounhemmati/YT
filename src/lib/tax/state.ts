import { applyBrackets, marginalRate } from "./brackets.js";
import { type Cents, atLeastZero, percentOf, toCents } from "./money.js";
import type { BracketRow, FilingStatus, StateData, StateResult } from "./types.js";

export interface StateArgs {
  federalAgi: Cents;
  filingStatus: FilingStatus;
  state: StateData | null;
}

export interface StateComputation extends Omit<StateResult, "amount" | "surtax" | "taxableIncome"> {
  amount: Cents;
  surtax: Cents;
  taxableIncome: Cents;
  marginalRate: number;
}

const EMPTY: StateComputation = {
  slug: null,
  name: null,
  structure: null,
  taxableIncome: 0,
  amount: 0,
  surtax: 0,
  brackets: [],
  notes: [],
  marginalRate: 0,
};

/**
 * State income tax.
 *
 * Deliberately simple: start from federal AGI, subtract the state standard
 * deduction, apply the schedule. States differ on what they conform to — some
 * start from federal taxable income, some disallow the self-employment tax
 * deduction, most disallow QBI — and the dataset does not yet carry those
 * conformity rules. Rather than model them half-way and be quietly wrong, the
 * engine says so in `notes`.
 */
export function computeStateTax({
  federalAgi,
  filingStatus,
  state,
}: StateArgs): StateComputation {
  if (!state) return { ...EMPTY };

  const notes: string[] = [];
  if (state.localTaxNote) notes.push(state.localTaxNote);
  if (state.staleForTargetYear) {
    notes.push(
      "This state had not published inflation-adjusted figures for the target " +
        "tax year when the data was gathered, so the previous year's brackets " +
        "are shown.",
    );
  }

  if (state.structure === "none") {
    return {
      ...EMPTY,
      slug: state.slug,
      name: state.name,
      structure: state.structure,
      notes: [...notes, ...state.notes],
    };
  }

  if (state.structure === "unknown") {
    return {
      ...EMPTY,
      slug: state.slug,
      name: state.name,
      structure: state.structure,
      notes: [
        ...notes,
        "This state's rate schedule has not been entered yet, so no state tax " +
          "is included in the total.",
      ],
    };
  }

  notes.push(
    "State tax is estimated from federal adjusted gross income less the state " +
      "standard deduction. State-specific additions, subtractions and credits " +
      "are not modelled.",
  );

  const standardDeduction = toCents(state.standardDeduction[filingStatus] ?? 0);
  const taxableIncome = atLeastZero(federalAgi - standardDeduction);

  let amount: Cents;
  let brackets: StateResult["brackets"] = [];
  let marginal = 0;

  const rows: BracketRow[] | undefined = state.brackets[filingStatus];
  if (rows && rows.length > 0) {
    const applied = applyBrackets(taxableIncome, rows);
    amount = applied.tax;
    brackets = applied.detail;
    marginal = marginalRate(taxableIncome, rows);
  } else if (state.flatRate != null) {
    amount = percentOf(taxableIncome, state.flatRate);
    marginal = state.flatRate;
    brackets = [
      {
        rate: state.flatRate,
        from: 0,
        to: null,
        taxedAmount: taxableIncome / 100,
        taxInBracket: amount / 100,
      },
    ];
  } else {
    amount = 0;
    notes.push("No rate schedule available for this filing status.");
  }

  // A separate levy stacked on the ordinary schedule, such as California's
  // mental health services tax.
  let surtax: Cents = 0;
  if (state.surtax && state.surtax.length > 0) {
    const applied = applyBrackets(taxableIncome, state.surtax);
    surtax = applied.tax;
    if (surtax > 0) {
      const top = state.surtax[state.surtax.length - 1]!;
      marginal += top.rate;
    }
  }

  return {
    slug: state.slug,
    name: state.name,
    structure: state.structure,
    taxableIncome,
    amount,
    surtax,
    brackets,
    notes: [...notes, ...state.notes],
    marginalRate: marginal,
  };
}
