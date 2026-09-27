/**
 * Types for the cost-of-living engine (spec 4-9, data schema 5-5).
 *
 * The foundational rule: we publish INDICES, never invented dollar baskets.
 * Dollars come from the user's own numbers, or from HUD Fair Market Rent, which
 * is an official dollar figure. Every other category is a ratio applied to the
 * user's own spending.
 */

/** Categories for which BEA publishes a separate Regional Price Parity. */
export type CostCategory = "rent" | "goods" | "utilities" | "otherServices";

export const COST_CATEGORIES: readonly CostCategory[] = [
  "rent",
  "goods",
  "utilities",
  "otherServices",
];

export type Bedrooms = 0 | 1 | 2 | 3 | 4;

export interface PlaceIndices {
  /** 100 = national average. Always present. */
  allItems: number;
  /** Present only where the source publishes the component. */
  rent?: number;
  goods?: number;
  utilities?: number;
  otherServices?: number;
}

export interface PlaceCostData {
  slug: string;
  name: string;
  type: "metro" | "state" | "country";
  /** Comparisons never cross regions: BEA and Eurostat use different bases. */
  region: "us" | "eu";
  dataYear: number;
  indices: PlaceIndices;
  /**
   * HUD Fair Market Rent, monthly, by bedroom count. This is GROSS rent: shelter
   * rent plus tenant-paid utilities, set at the 40th percentile of recent movers.
   */
  referenceRent?: Partial<Record<`bedrooms${Bedrooms}`, number>> | null;
  stateSlug: string | null;
  sources: { label: string; url: string; retrieved: string }[];
  lastVerified: string;
  verification: "verified" | "pending";
}

export type MonthlyCosts = Partial<Record<CostCategory, number>>;

/**
 * National average household spending by category and household size (BLS
 * Consumer Expenditure Survey). Each category names the BEA price-parity
 * component that prices it locally. Housing and utilities are NOT categories
 * here: rent comes from HUD Fair Market Rent, which is gross rent including
 * tenant-paid utilities, and counting them again would double them.
 */
export type HouseholdSize = 1 | 2 | 3 | 4 | 5;

export interface SpendingBaseline {
  year: number;
  source: { label: string; url: string; retrieved: string };
  categories: Record<string, { label: string; index: "goods" | "otherServices" | "allItems" }>;
  /** Annual dollars; key "5" means five or more people. */
  annualByHouseholdSize: Record<`${HouseholdSize}`, Record<string, number>>;
  verification: "verified" | "pending";
}
