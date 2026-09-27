/**
 * Proves the Base44 package: the bundled engine, fed only the packaged data,
 * must give exactly what the repository's engine gives for every case.
 */
import { readFileSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import * as repo from "../src/lib/col/index.js";
import { loadEstimated, loadFederal, loadState } from "../src/lib/tax/load.js";

const dir = process.argv[2]!;
const bundle = await import(pathToFileURL(path.join(dir, "engine/col-engine.js")).href);
const read = (p: string) => JSON.parse(readFileSync(path.join(dir, "data", p), "utf8"));
const areas = read("col/price-areas.json");
const meta = read("col/meta.json");
const baseline = read("ces-2024/baseline.json");
const years = { priceLevels: meta.years.priceLevels, rent: meta.years.rent };
const pkgTax = (slug: string) => ({
  federal: read("tax-year-2026/federal.json"), estimated: read("tax-year-2026/estimated.json"),
  state: read(`tax-year-2026/states/${slug}.json`),
});
const repoTax = (slug: string) => ({ federal: loadFederal(2026), estimated: loadEstimated(2026), state: loadState(2026, slug) });

const cases: [string, string, string, 1 | 2, number, string?][] = [
  ["tx", "city:Austin, TX", "texas", 1, 0],
  ["tx", "city:Houston, TX", "texas", 2, 2],
  ["ny", "city:New York, NY", "new-york", 1, 0],
  ["nc", "city:Raleigh, NC", "north-carolina", 2, 0, "37063"],
  ["ma", "area:2502507000", "massachusetts", 1, 0],
  ["il", "city:Chicago, IL", "illinois", 2, 3],
  ["ca", "city:San Francisco, CA", "california", 1, 1],
  ["fl", "city:Miami, FL", "florida", 2, 1],
];
let checked = 0;
for (const [st, key, slug, adults, children, county] of cases) {
  const file = read(`col/places/${st}.json`);
  const a = bundle.computeCostOfLiving({
    taxYear: 2026, place: bundle.resolvePlace(file, areas, key, county), tax: pkgTax(slug),
    baseline, years, adults, children,
  });
  const b = repo.computeCostOfLiving({
    taxYear: 2026, place: repo.resolvePlace(file, areas, key, county), tax: repoTax(slug),
    baseline, years, adults, children,
  });
  const x = JSON.stringify(a), y = JSON.stringify(b);
  if (x !== y) {
    console.error(`MISMATCH ${key}\n bundle ${x.slice(0, 300)}\n repo   ${y.slice(0, 300)}`);
    process.exit(1);
  }
  checked++;
}
console.log(`bundle matches the repository engine on ${checked} households (every field)`);
