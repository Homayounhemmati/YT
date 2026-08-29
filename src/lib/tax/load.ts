import { readFileSync } from "node:fs";
import path from "node:path";
import type { EstimatedData, FederalData, StateData } from "./types.js";

/**
 * Build-time data loading. Kept apart from the engine so the engine stays pure
 * and can be tested, and rendered in a browser, without touching the filesystem.
 */
const DATA_ROOT = path.join(process.cwd(), "src", "data");

function read<T>(taxYear: number, ...segments: string[]): T {
  const file = path.join(DATA_ROOT, `tax-year-${taxYear}`, ...segments);
  return JSON.parse(readFileSync(file, "utf8")) as T;
}

export function loadFederal(taxYear: number): FederalData {
  return read<FederalData>(taxYear, "federal.json");
}

export function loadEstimated(taxYear: number): EstimatedData {
  return read<EstimatedData>(taxYear, "estimated.json");
}

export function loadState(taxYear: number, slug: string): StateData {
  return read<StateData>(taxYear, "states", `${slug}.json`);
}
