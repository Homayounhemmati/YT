/**
 * Resolving a place from the nationwide calculator data (src/data/col).
 *
 * A state file holds counties and New England towns (each with its HUD rents and
 * BEA price area) and cities (each naming the county that holds most of its
 * people, plus any others it spans). `resolvePlace` turns any of them into the
 * CalculatorPlace the engine takes. Pure: the caller loads the JSON.
 */
import type { CalculatorPlace } from "./calculator.js";
import type { PlaceIndices } from "./types.js";

export interface StatePlacesFile {
  state: string;
  stateSlug: string;
  counties: Record<string, {
    name: string;
    kind: "county" | "town";
    label: string;
    priceArea: string;
    rent: [number, number, number, number, number];
    fmrArea: string;
    population: number;
    county?: string;
    countyName?: string;
    note?: string;
  }>;
  cities: { name: string; label: string; county: string; population: number; alsoIn?: string[] }[];
}

export interface PriceAreasFile {
  year: number;
  areas: Record<string, {
    name: string;
    kind: "metro" | "state-metro-portion" | "state-nonmetro-portion";
    indices: PlaceIndices;
  }>;
}

/** What the search box offers: every city, county and town, largest first. */
export function searchEntries(file: StatePlacesFile): { key: string; label: string; population: number }[] {
  const out = [
    ...file.cities.map((c) => ({ key: `city:${c.label}`, label: c.label, population: c.population })),
    ...Object.entries(file.counties).map(([id, c]) => ({ key: `area:${id}`, label: c.label, population: c.population })),
  ];
  return out.sort((a, b) => b.population - a.population || a.label.localeCompare(b.label));
}

/**
 * `key` is a searchEntries key. For a city that spans counties, `countyId` picks
 * the part the visitor lives in; it defaults to the part with most people.
 */
export function resolvePlace(
  file: StatePlacesFile,
  areas: PriceAreasFile,
  key: string,
  countyId?: string,
): CalculatorPlace {
  let areaId: string;
  let label: string;
  if (key.startsWith("city:")) {
    const city = file.cities.find((c) => `city:${c.label}` === key);
    if (!city) throw new Error(`No city ${key} in ${file.state}`);
    const allowed = [city.county, ...(city.alsoIn ?? [])];
    if (countyId && !allowed.includes(countyId)) {
      throw new Error(`${city.label} is not in county ${countyId}`);
    }
    areaId = countyId ?? city.county;
    label = city.label;
  } else {
    areaId = key.replace(/^area:/, "");
    if (!file.counties[areaId]) throw new Error(`No county or town ${areaId} in ${file.state}`);
    label = file.counties[areaId]!.label;
  }
  const c = file.counties[areaId]!;
  const a = areas.areas[c.priceArea];
  if (!a) throw new Error(`Price area ${c.priceArea} missing for ${label}`);
  return {
    id: key.startsWith("city:") ? `${key}@${areaId}` : areaId,
    label,
    state: file.state,
    stateSlug: file.stateSlug,
    rent: c.rent,
    fmrArea: c.fmrArea,
    priceArea: { code: c.priceArea, name: a.name, kind: a.kind, indices: a.indices },
  };
}
