# Questions for Base44 support

Context to give them, in one line: *we are building a calculator site whose SEO
depends on ~80 pages generated from a data table (51 US states, ~30 metro areas),
each needing its own title, meta description and structured data.*

**Please ask them to answer with a concrete example or a `curl` output rather than
yes/no.** Every question below is written so that a vague answer is visibly a
non-answer — that is deliberate, because the public documentation and the public
feedback board currently contradict each other on questions 1 to 4.

---

## Tier 1 — decisive. The build plan depends on these four

**1. Server-rendered content.**
For a page generated from an entity row, does the HTML returned by the server —
before any JavaScript executes — contain the page's visible text content?

> Concretely: if I run `curl https://myapp.com/state/california` with no JavaScript
> engine, do I see the page's headings and body text, or an empty `<div id="root">`?
> Please paste a real example.

**2. Per-entity meta tags in that same initial HTML.**
Are `<title>`, `<meta name="description">` and `<link rel="canonical">` present in
the initial server response, and **different for every row** of the entity?

> Concretely: do `curl .../state/california` and `curl .../state/texas` return two
> different `<title>` tags in the raw HTML?
>
> We are not asking whether they differ in the browser. We know they will. We are
> asking about the response before JavaScript runs.

**3. Setting those values at scale, from data — not by hand.**
We have ~80 generated pages. Is there a way to populate each page's SEO fields
**from the entity row's own fields** (for example `seo_title`, `seo_description`)?

> Or is the SEO panel a per-page manual form? If manual: is there an API, CSV
> import, or bulk method, or would someone have to type 80 entries and re-type them
> whenever the underlying data changes?

**4. Social crawlers.**
Do Facebook, X/Twitter, LinkedIn and Slack receive the **per-entity** Open Graph
tags, or the app-level defaults?

> Concretely, what does this return:
> `curl -A "facebookexternalhit/1.1" https://myapp.com/state/california | grep "og:"`
>
> We ask specifically because your public feedback board has open requests stating
> that social crawlers see only generic app-level tags. Is that still the case?

---

## Tier 2 — needed, but each has a workaround

**5. Prerendering behaviour.** If there is a prerendering layer:
- Is it **user-agent gated**? (i.e. does Googlebot get different HTML than a browser?)
- When an entity's data changes, **how long** until the prerendered HTML updates?
- Which crawler user-agents are covered? Googlebot only, or Bingbot, GPTBot, social crawlers too?

**6. Arbitrary JSON-LD.** Can we inject our own JSON-LD blocks per page, in the
initial HTML? We need `WebApplication`, `FAQPage`, `BreadcrumbList`, `Place`,
`Dataset` and `ItemList` — with values that differ per entity row. Is there a
free-form `<head>` injection, or only a fixed set of schema types?

**7. Internal links.** Are internal navigation links rendered as real
`<a href="/path">` elements in the HTML, or as JavaScript click handlers on
non-anchor elements?

> This matters more than it sounds: a crawler follows `<a href>` and passes ranking
> signal through it. A `<div onClick={navigate}>` is invisible to it. Our whole
> internal linking plan assumes real anchors.

**8. Sitemaps.** The docs say a sitemap is generated automatically.
- Can we use a **sitemap index with multiple child sitemaps** (we want one per page
  type, so we can read indexation per type in Search Console)?
- Can we control which URLs are included and excluded?
- Does it emit `<lastmod>`, and is that based on **actual content change** or on
  every publish? (If every publish, we would rather it were omitted.)

**9. robots.txt.** Can we edit it directly, or is it fully managed?

**10. HTTP 404.** Does an unknown path return **HTTP status 404**, or status 200
with a not-found page rendered?

> Please confirm with `curl -I https://myapp.com/no-such-page` — we need the status
> line, not the visual appearance of the page.

---

## Tier 3 — configuration we need to confirm

**11. Custom domain and the platform subdomain.** After connecting a custom domain,
does the original `*.base44.app` URL stay publicly accessible and indexable? Can it
be disabled or 301-redirected to the custom domain?

> If both serve the same content, search engines see two copies of the entire site.

**12. URL shape.** Are routes clean paths (`/state/california`) rather than hash
routes (`/#/state/california`)? Do a trailing slash and an uppercase path redirect
(301) to the canonical lowercase, slash-free form, or do all variants serve 200?

**13. Response headers.** Can we set custom headers — specifically
`Strict-Transport-Security` and `Cache-Control` on HTML?

**14. Headings.** Can we control the exact heading structure per page — one `<h1>`
with text we specify, and `<h2>` values that differ per entity row?

**15. Third-party scripts.** Can we add Google AdSense and a lightweight analytics
script? Any restriction on ad placement or on the `ads.txt` file at the domain
root? (`ads.txt` must be reachable at `https://domain.com/ads.txt`.)

**16. Page speed.** Is there server-side control over the initial payload — code
splitting, or a way to keep the initial JS bundle small? We are working to a budget
of 90 KB of initial JavaScript.

---

## The single most useful thing they could send

A live URL of any existing Base44 app that has **many pages generated from a data
table**, so we can run our own checks against it directly.

That would answer questions 1, 2, 4, 7, 10 and 12 at once, and it is the fastest
route to a decision for both sides.
