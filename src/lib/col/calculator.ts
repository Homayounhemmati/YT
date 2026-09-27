/**
 * The cost-of-living calculator in one call.
 *
 * `computeCostOfLiving()` returns everything the result card shows, in the order it
 * shows it: what a month costs this household in this place, line by line with
 * the basis of every line; the salary that covers it after federal tax, FICA and
 * the place's state tax and payroll contributions; how far the state's tax data
 * has been checked; an optional comparison with where the visitor lives now; the
 * year of every source; and every warning. The platform renders it and computes
 * nothing of its own.
 *
 * Places come from src/data/col (scripts/build_col_places.py): every US county,
 * every New England town and every incorporated city, each with HUD's rent for
 * that place and the BEA price level of the area it belongs to.
 */
import { estimateWageTakeHome } from "../tax/payroll.js";
import type { EngineData } from "../tax/index.js";
import { toCents, toDollars } from "../tax/money.js";
import type { FilingStatus } from "../tax/types.js";
import {
  cityMonthlyCost,
  equivalentSalaryAfterTax,
  grossForNet,
  suggestedBedrooms,
  type CityCostRow,
} from "./index.js";
import type { Bedrooms, HouseholdSize, PlaceCostData, PlaceIndices, SpendingBaseline } from "./types.js";

/** A place as the calculator receives it: one row of a state file, resolved. */
export interface CalculatorPlace {
  id: string;
  label: string;
  state: string;
  stateSlug: string;
  /** HUD Fair Market Rent by bedroom count, studio to four bedrooms (monthly, gross). */
  rent: [number, number, number, number, number];
  fmrArea: string;
  priceArea: {
    code: string;
    name: string;
    kind: "metro" | "state-metro-portion" | "state-nonmetro-portion";
    indices: PlaceIndices;
  };
}

export interface CostOfLivingInput {
  taxYear: number;
  place: CalculatorPlace;
  /** Federal data plus the tax data for `place.stateSlug`. */
  tax: EngineData;
  baseline: SpendingBaseline;
  /** Price-level year (BEA) and rent year (HUD), shown with the result. */
  years: { priceLevels: number; rent: number };
  /** Adults in the household: 1 or 2. */
  adults: 1 | 2;
  /** Children under 17 (they qualify for the child tax credit). */
  children: number;
  /** Defaults to suggestedBedrooms(adults + children). */
  bedrooms?: Bedrooms;
  /** Defaults: two adults file jointly; one adult with children as head of household; otherwise single. */
  filingStatus?: FilingStatus;
  /** The visitor's own monthly figures, by line key; each replaces that line. */
  own?: Record<string, number>;
  /** The visitor's own rent, replacing HUD's. */
  rentOverride?: number;
  /** Where the visitor lives now and what they earn there. */
  compare?: { place: CalculatorPlace; tax: EngineData; salary: number };
}

export type StateDataStatus = "verified" | "unverified";

export interface SalaryNeeded {
  /** Gross annual salary whose take-home equals the annual total. */
  gross: number;
  hourlyAt2080: number;
  filingStatus: FilingStatus;
  stateName: string | null;
  breakdown: {
    federalTax: number;
    fica: number;
    stateTax: number;
    stateContributions: number;
    netPay: number;
  };
  /** "unverified": the state's figures are not yet checked against its 2026 publications. */
  stateDataStatus: StateDataStatus;
  notes: string[];
}

export interface CostOfLivingResult {
  place: { id: string; label: string; state: string; priceAreaName: string; fmrArea: string };
  household: {
    adults: 1 | 2;
    children: number;
    /** Size used for spending averages: BLS publishes one to "five or more". */
    size: HouseholdSize;
    bedrooms: Bedrooms;
    suggestedBedrooms: Bedrooms;
    filingStatus: FilingStatus;
  };
  lines: CityCostRow[];
  monthlyTotal: number;
  annualTotal: number;
  /** True when every line is the visitor's own: the total is then not an estimate. */
  allOwnFigures: boolean;
  salary: SalaryNeeded;
  comparison?: {
    from: { label: string; monthlyTotal: number; annualTotal: number };
    /** This household's month here minus the same household's month there. */
    monthlyDifference: number;
    currentSalary: number;
    /** The salary here that keeps after-tax spending power equal. */
    equivalentSalary: number;
    /** The same with prices only, no tax: shown beside it so the tax effect is visible. */
    priceOnlyEquivalent: number;
    fromStateDataStatus: StateDataStatus;
  };
  sources: {
    priceLevels: string;
    rent: string;
    spending: string;
    tax: string;
  };
  warnings: string[];
}

const HOURS_PER_YEAR = 2080;

/** A calculator place in the shape the lower-level engines take. */
export function toPlaceCostData(p: CalculatorPlace, dataYear: number): PlaceCostData {
  return {
    slug: p.id,
    name: p.label,
    type: "metro",
    region: "us",
    dataYear,
    indices: p.priceArea.indices,
    referenceRent: {
      bedrooms0: p.rent[0], bedrooms1: p.rent[1], bedrooms2: p.rent[2],
      bedrooms3: p.rent[3], bedrooms4: p.rent[4],
    },
    stateSlug: p.stateSlug,
    sources: [],
    lastVerified: "",
    verification: "verified",
  };
}

/** Whether a state's figures are checked and complete enough to show without a caveat. */
export function stateDataStatus(tax: EngineData): { status: StateDataStatus; notes: string[] } {
  const s = tax.state;
  if (!s) return { status: "verified", notes: [] };
  const notes: string[] = [];
  if (s.verification !== "verified") {
    notes.push(`${s.name}'s tax figures have not yet been checked against its 2026 publications.`);
  }
  if (s.staleForTargetYear) {
    notes.push(`${s.name}'s brackets are the 2025 figures; 2026's were not yet published when gathered.`);
  }
  if (s.modelCoverage?.payrollContributions === "not-modelled") {
    notes.push(`${s.name}'s employee payroll contributions (paid leave, disability) are not yet included.`);
  }
  if (s.modelCoverage?.benefitRecapture === "not-modelled") {
    notes.push(`${s.name}'s high-income bracket recapture is not yet included.`);
  }
  if (s.modelCoverage?.personalExemption === "not-extracted") {
    notes.push(`${s.name}'s personal exemption is not yet included.`);
  }
  return { status: notes.length ? "unverified" : "verified", notes };
}

function netPayAt(taxYear: number, filingStatus: FilingStatus, tax: EngineData, children = 0) {
  return (grossCents: number) =>
    toCents(estimateWageTakeHome(
      { taxYear, filingStatus, annualWages: toDollars(grossCents), qualifyingChildren: children }, tax).netPay);
}

export function computeCostOfLiving(input: CostOfLivingInput): CostOfLivingResult {
  const children = Math.max(0, Math.floor(input.children));
  const people = input.adults + children;
  const size = Math.min(5, people) as HouseholdSize;
  const suggested = suggestedBedrooms(people);
  const bedrooms = input.bedrooms ?? suggested;
  const filingStatus: FilingStatus = input.filingStatus ??
    (input.adults === 2 ? "marriedJointly" : children > 0 ? "headOfHousehold" : "single");
  const place = toPlaceCostData(input.place, input.years.priceLevels);

  const cost = cityMonthlyCost({
    place, householdSize: size, bedrooms, baseline: input.baseline,
    ...(input.own ? { own: input.own } : {}),
    ...(input.rentOverride != null ? { rentOverride: input.rentOverride } : {}),
  });
  const warnings = [...cost.warnings];

  // The salary: the smallest gross whose take-home covers the year.
  const requiredNet = toCents(cost.annualTotal);
  const grossCents = grossForNet(requiredNet, netPayAt(input.taxYear, filingStatus, input.tax, children));
  const wage = estimateWageTakeHome(
    { taxYear: input.taxYear, filingStatus, annualWages: toDollars(grossCents), qualifyingChildren: children },
    input.tax);
  const status = stateDataStatus(input.tax);
  const stateNotes = [...status.notes];
  if (input.tax.state?.localTaxNote) stateNotes.push(input.tax.state.localTaxNote);
  for (const w of wage.warnings) if (!stateNotes.includes(w)) stateNotes.push(w);

  const salary: SalaryNeeded = {
    gross: toDollars(grossCents),
    hourlyAt2080: toDollars(Math.round(grossCents / HOURS_PER_YEAR)),
    filingStatus,
    stateName: input.tax.state?.name ?? null,
    breakdown: {
      federalTax: wage.federalTax,
      fica: wage.fica.total,
      stateTax: wage.stateTax,
      stateContributions: wage.stateContributionsTotal,
      netPay: wage.netPay,
    },
    stateDataStatus: status.status,
    notes: stateNotes,
  };
  warnings.push(
    "The salary is a break-even figure: it covers the lines above and nothing else — " +
      "no savings, debt repayment, child care or retirement contributions.",
  );
  if (input.adults === 2 && filingStatus === "marriedJointly") {
    warnings.push("The salary assumes one earner filing jointly; two earners pay slightly different tax.");
  }
  if (children > 0) {
    warnings.push(`The salary applies the federal child tax credit for ${children} ` +
      `${children === 1 ? "child" : "children"} under 17` +
      (input.tax.state?.dependentAllowance ? ` and ${input.tax.state.name}'s allowance for dependents.` : "."));
  }
  if (people > 5) {
    warnings.push("Spending averages are for households of five or more; a larger household spends more.");
  }

  const ownKeys = Object.keys(input.own ?? {});
  const allOwn = cost.rows.every((r) => r.basis === "your figure") && ownKeys.length > 0;

  let comparison: CostOfLivingResult["comparison"];
  if (input.compare) {
    const from = toPlaceCostData(input.compare.place, input.years.priceLevels);
    const there = cityMonthlyCost({
      place: from, householdSize: size, bedrooms, baseline: input.baseline,
    });
    const eq = equivalentSalaryAfterTax(
      { taxYear: input.taxYear, filingStatus, salary: input.compare.salary, qualifyingChildren: children },
      { place: from, tax: input.compare.tax },
      { place, tax: input.tax },
    );
    comparison = {
      from: { label: input.compare.place.label, monthlyTotal: there.monthlyTotal,
              annualTotal: there.annualTotal },
      monthlyDifference: toDollars(toCents(cost.monthlyTotal) - toCents(there.monthlyTotal)),
      currentSalary: input.compare.salary,
      equivalentSalary: eq.equivalentGross,
      priceOnlyEquivalent: eq.priceOnlyEquivalent,
      fromStateDataStatus: stateDataStatus(input.compare.tax).status,
    };
    if (input.own && ownKeys.length) {
      warnings.push(`The ${input.compare.place.label} month uses the typical-household estimate for ` +
        "every line; your own figures apply only to the place you are pricing.");
    }
  }

  const b = input.baseline;
  return {
    place: {
      id: input.place.id, label: input.place.label, state: input.place.state,
      priceAreaName: input.place.priceArea.name, fmrArea: input.place.fmrArea,
    },
    household: { adults: input.adults, children, size, bedrooms, suggestedBedrooms: suggested, filingStatus },
    lines: cost.rows,
    monthlyTotal: cost.monthlyTotal,
    annualTotal: cost.annualTotal,
    allOwnFigures: allOwn,
    salary,
    ...(comparison ? { comparison } : {}),
    sources: {
      priceLevels: `BEA Regional Price Parities, ${input.years.priceLevels} (${input.place.priceArea.name})`,
      rent: `HUD Fair Market Rent, fiscal ${input.years.rent} (${input.place.fmrArea})`,
      spending: `BLS Consumer Expenditure Survey, ${b.year}, by household size` +
        (b.priceUpdate ? `, in ${b.priceUpdate.toMonth} prices (CPI)` : ""),
      tax: `${input.taxYear} federal and ${input.tax.state?.name ?? "state"} rules`,
    },
    warnings,
  };
}
