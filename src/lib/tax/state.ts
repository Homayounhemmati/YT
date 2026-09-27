import { applyBrackets, marginalRate } from "./brackets.js";
import { type Cents, atLeastZero, percentOf, toCents } from "./money.js";
import type { BenefitRecapture, BracketRow, FilingStatus, StateData, StateResult } from "./types.js";

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
/** The filer's personal exemption in cents at a given federal AGI. */
export function personalExemption(
  state: StateData,
  filingStatus: StateArgs["filingStatus"],
  federalAgi: Cents,
): Cents {
  const rule = state.personalExemption?.byStatus[filingStatus];
  if (!rule) return 0;
  if (rule.maxAgi != null && federalAgi > toCents(rule.maxAgi)) return 0;
  let amount = rule.amount;
  for (const step of rule.agiSchedule ?? []) {
    if (federalAgi > toCents(step.overAgi)) amount = step.amount;
  }
  return toCents(amount);
}

/**
 * New York's supplemental tax, in cents, on top of the schedule tax `scheduleTax`.
 * Follows the statute clause by clause: recapture base plus incremental benefit
 * times the phase-in fraction (the lesser of $50,000 or the applicable amount,
 * over $50,000); below the first row, (rate x income - schedule tax) times the
 * fraction measured from the AGI floor; above the ceiling, top rate on all of it.
 */
export function supplementalTax(
  rule: BenefitRecapture,
  filingStatus: FilingStatus,
  federalAgi: Cents,
  taxableIncome: Cents,
  scheduleTax: Cents,
): Cents {
  const agi = federalAgi;
  if (agi <= toCents(rule.agiFloor) || taxableIncome <= 0) return 0;
  if (agi > toCents(rule.agiCeiling)) {
    return atLeastZero(percentOf(taxableIncome, rule.topRate) - scheduleTax);
  }
  const table = rule.byStatus[filingStatus];
  if (!table) return 0;
  const width = toCents(rule.phaseWidth);
  const fraction = (applicable: Cents) => Math.min(width, atLeastZero(applicable)) / width;

  if (taxableIncome <= toCents(table.lowIncome.below)) {
    const full = percentOf(taxableIncome, table.lowIncome.rate) - scheduleTax;
    return atLeastZero(Math.round(full * fraction(agi - toCents(rule.agiFloor))));
  }
  const row = table.rows.find(
    (r) => taxableIncome > toCents(r.over) && taxableIncome <= toCents(r.notOver),
  );
  if (!row) return 0;
  return (
    toCents(row.recaptureBase) +
    Math.round(toCents(row.incrementalBenefit) * fraction(agi - toCents(row.agiLess)))
  );
}

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
  const exemption = personalExemption(state, filingStatus, federalAgi);
  if (state.modelCoverage?.personalExemption === "not-extracted") {
    notes.push(
      "Any personal exemption this state allows is not yet modelled, so its tax " +
        "may be slightly overstated.",
    );
  }
  const taxableIncome = atLeastZero(federalAgi - standardDeduction - exemption);

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

  if (state.benefitRecapture) {
    const extra = supplementalTax(
      state.benefitRecapture, filingStatus, federalAgi, taxableIncome, amount,
    );
    if (extra > 0) {
      amount += extra;
      // Inside the phase-in the next dollar costs more than the bracket rate says;
      // measure it rather than report the schedule's rate.
      const step = toCents(100);
      const rowsNow = rows && rows.length > 0 ? rows : null;
      const scheduleAt = (ti: Cents) =>
        rowsNow ? applyBrackets(ti, rowsNow).tax : percentOf(ti, state.flatRate ?? 0);
      const next =
        scheduleAt(taxableIncome + step) +
        supplementalTax(
          state.benefitRecapture, filingStatus, federalAgi + step,
          taxableIncome + step, scheduleAt(taxableIncome + step),
        );
      marginal = Math.round(((next - amount) / step) * 10000) / 100;
      const floor = state.benefitRecapture.agiFloor.toLocaleString("en-US");
      notes.push(
        `Above $${floor} of adjusted gross income ${state.name} takes back the ` +
          "benefit of its lower brackets (a supplemental tax), phased in over the " +
          `next $${state.benefitRecapture.phaseWidth.toLocaleString("en-US")}. It is included here.`,
      );
    }
  }
  if (state.modelCoverage?.benefitRecapture === "not-modelled") {
    notes.push(
      "This state takes back the benefit of its lower brackets at higher incomes; " +
        "that recapture is not yet modelled, so tax at high incomes is understated.",
    );
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
