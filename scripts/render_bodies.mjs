// Page bodies from Markdown to HTML, once, when the app's page files are written
// (scripts/sync_to_app.py), so the site ships no Markdown parser to the browser.
//
//   node scripts/render_bodies.mjs < {"stem": "markdown", ...}  > {"stem": "html", ...}
//
// Each <h2> gets the id the app's "On this page" links use (slugify below, which is
// the app's src/lib/siteFormat.js slugify); a table is wrapped in a scroll box; a
// cell holding only a number is marked for right alignment.
import { marked } from "marked";

const slugify = (t) => String(t).toLowerCase().replace(/[^a-z0-9\s-]/g, "").trim().replace(/\s+/g, "-");
const decode = (s) => s.replace(/<[^>]+>/g, "").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
  .replace(/&quot;/g, '"').replace(/&#39;/g, "'");
const NUMERIC = /^[\s$%+\-−–.,\d()×x/]+$/;

function render(md) {
  let html = marked.parse(md, { gfm: true, async: false });
  html = html.replace(/<h2>([\s\S]*?)<\/h2>/g, (_, inner) => `<h2 id="${slugify(decode(inner))}">${inner}</h2>`);
  html = html.replace(/<table>/g, '<div class="lc-table"><table>').replace(/<\/table>/g, "</table></div>");
  html = html.replace(/<td( align="[a-z]+")?>([\s\S]*?)<\/td>/g, (m, align, inner) =>
    NUMERIC.test(decode(inner)) && /\d/.test(decode(inner)) ? `<td class="num">${inner}</td>` : m);
  return html;
}

let input = "";
process.stdin.on("data", (c) => (input += c));
process.stdin.on("end", () => {
  const bodies = JSON.parse(input);
  const out = Object.fromEntries(Object.entries(bodies).map(([k, md]) => [k, render(md)]));
  process.stdout.write(JSON.stringify(out));
});
