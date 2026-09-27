/**
 * The single module the platform imports for the cost-of-living calculator.
 * Bundled by scripts/package_base44.py into one browser-ready JavaScript file.
 * Pure: no filesystem, no network — the app loads the JSON files and passes them in.
 */
export * from "./col/index.js";
export { estimateWageTakeHome } from "./tax/payroll.js";
