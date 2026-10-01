import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { loadEstimated, loadFederal, loadState } from "../../tax/load.js";
import { estimateWageTakeHome } from "../../tax/payroll.js";
import type { EngineData } from "../../tax/index.js";
import {
  computeCostOfLiving,
  resolvePlace,
  searchEntries,
  type PriceAreasFile,
  type SpendingBaseline,
  type StatePlacesFile,
} from "../index.js";

// REAL data throughout: src/data/col (BEA, HUD, Census), src/data/ces-2024 (BLS, CPI).
const YEAR = 2026;
const federal = loadFederal(YEAR);
const estimated = loadEstimated(YEAR);
const areas: PriceAreasFile = JSON.parse(readFileSync("src/data/col/price-areas.json", "utf8"));
const meta = JSON.parse(readFileSync("src/data/col/meta.json", "utf8"));
const baseline: SpendingBaseline = JSON.parse(readFileSync("src/data/ces-2024/baseline.json", "utf8"));
const file = (st: string): StatePlacesFile =>
  JSON.parse(readFileSync(`src/data/col/places/${st}.json`, "utf8"));
const tax = (slug: string): EngineData => ({ federal, estimated, state: loadState(YEAR, slug) });
const years = { priceLevels: meta.years.priceLevels, rent: meta.years.rent };
const place = (st: string, key: string, county?: string) => resolvePlace(file(st), areas, key, county);

describe("places", () => {
  it("a city resolves to the county holding most of its people", () => {
    const p = place("tx", "city:Austin, TX");
    expect(p.rent[1]).toBe(1562);            // Travis County, HUD FY2026
    expect(p.priceArea.code).toBe("12420");   // Austin-Round Rock-San Marcos
    expect(p.priceArea.indices.allItems).toBe(98.066);
  });
  it("a city spanning counties with different rents can be priced by its other part", () => {
    const wake = place("nc", "city:Raleigh, NC");
    const durham = place("nc", "city:Raleigh, NC", "37063");
    expect(wake.rent[1]).toBe(1596);
    expect(durham.rent[1]).toBe(1507);
    expect(() => place("nc", "city:Raleigh, NC", "37001")).toThrow();
  });
  it("New England is priced by town", () => {
    const boston = place("ma", "area:2502507000");
    expect(boston.label).toBe("Boston, MA");
    expect(boston.rent[1]).toBe(2476);
  });
  it("a county outside any metro takes its state's nonmetropolitan price level", () => {
    const f = file("tx");
    const [id] = Object.entries(f.counties).find(([, c]) => c.priceArea === "48999")!;
    expect(place("tx", `area:${id}`).priceArea.kind).toBe("state-nonmetro-portion");
  });
  it("search lists the largest places first", () => {
    const list = searchEntries(file("tx"));
    expect(list[0]!.label).toBe("Harris County, TX");
    expect(list.every((e, i) => i === 0 || list[i - 1]!.population >= e.population)).toBe(true);
    expect(list.some((e) => e.label === "Houston, TX")).toBe(true);
  });
});

describe("computeCostOfLiving: one person in Austin", () => {
  const r = computeCostOfLiving({
    taxYear: YEAR, place: place("tx", "city:Austin, TX"), tax: tax("texas"), baseline, years,
    adults: 1, children: 0,
  });
  it("uses one bedroom and single filing by default", () => {
    expect(r.household).toMatchObject({ bedrooms: 1, suggestedBedrooms: 1, filingStatus: "single" });
  });
  it("lists rent plus every spending category, each with its basis", () => {
    expect(r.lines).toHaveLength(1 + Object.keys(baseline.categories).length);
    expect(r.lines[0]).toMatchObject({ key: "rent", monthly: 1562, basis: "HUD Fair Market Rent" });
    expect(r.lines.slice(1).every((l) => l.basis === "national average at local prices")).toBe(true);
  });
  it("totals exactly to its lines", () => {
    const sum = r.lines.reduce((a, l) => a + Math.round(l.monthly * 100), 0) / 100;
    expect(r.monthlyTotal).toBe(sum);
    expect(r.annualTotal).toBe(Math.round(sum * 1200) / 100);
  });
  it("solves the salary to the cent: its take-home covers the year, a cent less does not", () => {
    const net = (g: number) => estimateWageTakeHome(
      { taxYear: YEAR, filingStatus: "single", annualWages: g }, tax("texas")).netPay;
    expect(net(r.salary.gross)).toBeGreaterThanOrEqual(r.annualTotal);
    expect(net(Math.round((r.salary.gross - 0.01) * 100) / 100)).toBeLessThan(r.annualTotal);
    expect(r.salary.breakdown.netPay).toBe(net(r.salary.gross));
    expect(r.salary.breakdown.stateTax).toBe(0);
  });
  it("marks verified state data as verified and names every source year", () => {
    expect(r.salary.stateDataStatus).toBe("verified");
    expect(r.sources.priceLevels).toContain("2024");
    expect(r.sources.rent).toContain("2026");
    expect(r.sources.spending).toContain(baseline.priceUpdate!.toMonth);
  });
});

describe("computeCostOfLiving: households, own figures, other states", () => {
  it("two adults and two children default to two bedrooms and joint filing", () => {
    const r = computeCostOfLiving({
      taxYear: YEAR, place: place("tx", "city:Houston, TX"), tax: tax("texas"), baseline, years,
      adults: 2, children: 2,
    });
    expect(r.household).toMatchObject({ bedrooms: 2, filingStatus: "marriedJointly" });
    expect(r.lines[0]!.monthly).toBe(1573);
  });
  it("one adult with children files as head of household and gets the child tax credit", () => {
    const base = { taxYear: YEAR, place: place("tx", "city:Austin, TX"), tax: tax("texas"), baseline, years };
    const parent = computeCostOfLiving({ ...base, adults: 1, children: 2 });
    expect(parent.household).toMatchObject({ size: 3, bedrooms: 2, filingStatus: "headOfHousehold" });
    // Same month, priced without the credit, needs a higher salary.
    const noCredit = computeCostOfLiving({ ...base, adults: 1, children: 2, filingStatus: "single" });
    expect(parent.salary.gross).toBeLessThan(noCredit.salary.gross);
    expect(parent.warnings.join(" ")).toMatch(/child tax credit for 2 children/);
  });
  it("households above five use the five-or-more spending averages and say so", () => {
    const r = computeCostOfLiving({
      taxYear: YEAR, place: place("tx", "city:Austin, TX"), tax: tax("texas"), baseline, years,
      adults: 2, children: 5,
    });
    expect(r.household.size).toBe(5);
    expect(r.household.bedrooms).toBe(4);
    expect(r.warnings.join(" ")).toMatch(/five or more/);
  });
  it("an own figure replaces its line and moves the total by the difference", () => {
    const base = computeCostOfLiving({
      taxYear: YEAR, place: place("tx", "city:Austin, TX"), tax: tax("texas"), baseline, years,
      adults: 1, children: 0,
    });
    const own = computeCostOfLiving({
      taxYear: YEAR, place: place("tx", "city:Austin, TX"), tax: tax("texas"), baseline, years,
      adults: 1, children: 0, own: { food_home: 400 }, rentOverride: 1400,
    });
    const g = base.lines.find((l) => l.key === "food_home")!.monthly;
    expect(own.lines.find((l) => l.key === "food_home")).toMatchObject({ monthly: 400, basis: "your figure" });
    expect(own.monthlyTotal).toBeCloseTo(base.monthlyTotal - g + 400 - 1562 + 1400, 2);
    expect(own.allOwnFigures).toBe(false);
  });
  it("New York's salary includes its supplemental tax rules and payroll contributions", () => {
    const r = computeCostOfLiving({
      taxYear: YEAR, place: place("ny", "city:New York, NY"), tax: tax("new-york"), baseline, years,
      adults: 1, children: 0,
    });
    expect(r.salary.stateDataStatus).toBe("verified");
    expect(r.salary.breakdown.stateContributions).toBeGreaterThan(0);
    expect(r.salary.notes.join(" ")).toMatch(/City of New York|Yonkers|local/i);
  });
  it("a state not yet verified is flagged, with the reasons", () => {
    const r = computeCostOfLiving({
      taxYear: YEAR, place: place("or", "city:Portland, OR"), tax: tax("oregon"), baseline, years,
      adults: 1, children: 0,
    });
    expect(r.salary.stateDataStatus).toBe("unverified");
    expect(r.salary.notes.join(" ")).toMatch(/2025|payroll contributions/);
  });
  it("compares with where you live now, after tax and on prices alone", () => {
    const r = computeCostOfLiving({
      taxYear: YEAR, place: place("tx", "city:Austin, TX"), tax: tax("texas"), baseline, years,
      adults: 1, children: 0,
      compare: { place: place("ny", "city:New York, NY"), tax: tax("new-york"), salary: 95_000 },
    });
    const c = r.comparison!;
    expect(c.from.label).toBe("New York, NY");
    expect(c.monthlyDifference).toBeCloseTo(r.monthlyTotal - c.from.monthlyTotal, 2);
    // Moving from a taxed, pricier place to Texas: after tax you need less than on prices alone.
    expect(c.equivalentSalary).toBeLessThan(c.priceOnlyEquivalent);
    expect(c.equivalentSalary).toBeLessThan(95_000);
  });
});
