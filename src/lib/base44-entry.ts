/**
 * The single module the platform imports: every calculator engine on the site.
 * Bundled by scripts/package_base44.py into one browser-ready JavaScript file.
 * Pure: no filesystem, no network — the app loads the JSON files and passes them in.
 */
export * from "./col/index.js";
export { estimateTax } from "./tax/index.js";
export type { EngineData } from "./tax/index.js";
export { estimateWageTakeHome, computeEmployeeFica } from "./tax/payroll.js";
export type { WageInput, WageResult } from "./tax/payroll.js";
export * from "./calc/housing.js";
export * from "./calc/everyday.js";
