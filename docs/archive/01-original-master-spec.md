# LifeCalc Pro — سند جامع نهایی

> این سند مرجع کامل پروژه است: معماری، دیتاست‌ها، فرمول‌ها، فیچرهای جدید، استراتژی محتوا و برنامه‌ی اجرایی ۶ ماهه.
> هدف: **$500/ماه از AdSense طی ۶ ماه**، از طریق دو نیش: Freelance Tax + Cost of Living.

---

## بخش A — تصمیمات استراتژیک پروژه

| موضوع | تصمیم |
|---|---|
| نیش | فقط Freelance Tax + Cost of Living. مهاجرت به‌عنوان نیش کامل فعلاً کنار گذاشته شد؛ فقط به‌صورت یک پاراگراف context (ویزا/اقامت) داخل صفحات cost-of-living می‌آید |
| گردشگری | رد شد — خارج از context مالی، رقیب‌سازی با نیش‌های پرترافیک و بی‌ربط (Lonely Planet, TripAdvisor)، رقیق‌کردن topical authority |
| دامنه | یک سایت واحد برای هر دو نیش — نه سایت جدا |
| پوشش جغرافیایی | ۵۱ استیت آمریکا (آماده) + ۲۵ شهر آمریکا (آماده) + ۵۵-۶۰ شهر بین‌المللی جدید + صفحات سطح کشور (جدید) |
| مدل درآمد فاز ۱ | فقط AdSense |
| مسیرهای موازی (خارج از این پروژه) | اشتراک آموزشی ماهانه و سرویس دلاری — این‌ها مسیرهای جدا برای رسیدن به هدف ۵۰۰ میلیون تومانی کلی هستند، نه بخشی از LifeCalc Pro |

---

## بخش B — معماری کلی

**استراتژی:** Static-First + Programmatic SEO

- محاسبات کاملاً **client-side** (بدون رفت‌وبرگشت به سرور)
- هر ابزار یک صفحه مستقل با URL اختصاصی
- ابزارهای programmatic: **یک قالب + یک دیتاست = صدها صفحه سئو**
- بدون بک‌اند — همه داده‌ها ماژول‌های JS استاتیک

**سه نوع ابزار (به‌روزشده):**

1. **ابزارهای مستقل** (۶ عدد) — فرمول ثابت، بدون دیتاست location
2. **ابزارهای programmatic تک‌سطحی** (۱ عدد: state tax) — از دیتاست state تولید می‌شود
3. **ابزارهای programmatic سلسله‌مراتبی** (۱ عدد: cost of living) — سه سطح: **country → city**، به‌علاوه‌ی state آمریکا

**پکیج‌ها:** React، react-router-dom، tailwindcss، shadcn/ui، lucide-react

---

## بخش C — رجیستری ابزارها (`src/lib/tools.js`)

### دسته‌بندی‌ها

| id | نام | توضیح |
|---|---|---|
| `freelance` | Freelancer Tools | Calculators for taxes, rates and project profits. |
| `immigration` | Immigration & Travel Tools | Plan your move or trip abroad with accurate numbers. |

### لیست ابزارها

| slug | name | category | icon |
|---|---|---|---|
| `freelance-tax-calculator` | Freelance Tax Calculator | freelance | Calculator |
| `hourly-rate-calculator` | Freelance Hourly Rate Calculator | freelance | DollarSign |
| `project-profit-calculator` | Project Profit Calculator | freelance | Briefcase |
| `cost-of-living-calculator` | Cost of Living Calculator | immigration | Globe |
| `money-transfer-fee-calculator` | Money Transfer Fee Calculator | immigration | ArrowRightLeft |
| `travel-budget-calculator` | Travel & Relocation Budget Calculator | immigration | Plane |
| `location-compare` *(جدید)* | Cost of Living Comparison | immigration | GitCompare |
| `salary-converter` *(جدید)* | Salary / Purchasing Power Converter | immigration | Wallet |

### توابع کمکی
- `getToolsByCategory(categoryId)`
- `getRelatedTools(slug, limit=3)`

---

## بخش D — ثابت‌های مالی (`src/lib/statesTax.js`)

| ثابت | مقدار | توضیح |
|---|---|---|
| `TAX_DATA_UPDATED` | `"2026-01-15"` | تاریخ آخرین به‌روزرسانی داده |
| `TAX_YEAR` | `2026` | سال مالیاتی |
| `FEDERAL_SE_RATE` | `15.3` | نرخ مالیات خوداشتغالی |
| `FEDERAL_INCOME_RATE` | `14` | نرخ مؤثر فدرال برای درآمد متوسط |

---

## بخش E — دیتاست ایالت‌های آمریکا (۵۱ ردیف — آماده)

فیلدها: `slug`, `name`, `abbr`, `structure` (`none`|`flat`|`progressive`), `topRate`, `stateRate`, `note`

| ایالت | abbr | structure | topRate | stateRate |
|---|---|---|---|---|
| Alabama | AL | progressive | 5.0 | 4.6 |
| Alaska | AK | none | 0 | 0 |
| Arizona | AZ | flat | 2.5 | 2.5 |
| Arkansas | AR | progressive | 3.9 | 3.7 |
| California | CA | progressive | 13.3 | 8.0 |
| Colorado | CO | flat | 4.4 | 4.4 |
| Connecticut | CT | progressive | 6.99 | 5.5 |
| Delaware | DE | progressive | 6.6 | 5.5 |
| Florida | FL | none | 0 | 0 |
| Georgia | GA | flat | 5.39 | 5.19 |
| Hawaii | HI | progressive | 11.0 | 7.6 |
| Idaho | ID | flat | 5.695 | 5.695 |
| Illinois | IL | flat | 4.95 | 4.95 |
| Indiana | IN | flat | 3.05 | 3.05 |
| Iowa | IA | flat | 3.8 | 3.8 |
| Kansas | KS | progressive | 5.58 | 5.2 |
| Kentucky | KY | flat | 4.0 | 4.0 |
| Louisiana | LA | flat | 3.0 | 3.0 |
| Maine | ME | progressive | 7.15 | 6.75 |
| Maryland | MD | progressive | 5.75 | 5.0 |
| Massachusetts | MA | flat | 9.0 | 5.0 |
| Michigan | MI | flat | 4.25 | 4.25 |
| Minnesota | MN | progressive | 9.85 | 7.85 |
| Mississippi | MS | flat | 4.4 | 4.4 |
| Missouri | MO | progressive | 4.7 | 4.4 |
| Montana | MT | progressive | 5.9 | 5.4 |
| Nebraska | NE | progressive | 5.2 | 4.9 |
| Nevada | NV | none | 0 | 0 |
| New Hampshire | NH | none | 0 | 0 |
| New Jersey | NJ | progressive | 10.75 | 5.5 |
| New Mexico | NM | progressive | 5.9 | 4.9 |
| New York | NY | progressive | 10.9 | 6.25 |
| North Carolina | NC | flat | 4.25 | 4.25 |
| North Dakota | ND | progressive | 2.5 | 1.95 |
| Ohio | OH | progressive | 3.5 | 2.75 |
| Oklahoma | OK | progressive | 4.75 | 4.5 |
| Oregon | OR | progressive | 9.9 | 8.75 |
| Pennsylvania | PA | flat | 3.07 | 3.07 |
| Rhode Island | RI | progressive | 5.99 | 4.75 |
| South Carolina | SC | progressive | 6.2 | 5.9 |
| South Dakota | SD | none | 0 | 0 |
| Tennessee | TN | none | 0 | 0 |
| Texas | TX | none | 0 | 0 |
| Utah | UT | flat | 4.55 | 4.55 |
| Vermont | VT | progressive | 8.75 | 6.6 |
| Virginia | VA | progressive | 5.75 | 5.6 |
| Washington | WA | none | 0 | 0 |
| West Virginia | WV | progressive | 4.82 | 4.4 |
| Wisconsin | WI | progressive | 7.65 | 5.3 |
| Wyoming | WY | none | 0 | 0 |
| Washington, D.C. | DC | progressive | 10.75 | 8.5 |

**۹ ایالت بدون مالیات:** Alaska, Florida, Nevada, New Hampshire, South Dakota, Tennessee, Texas, Washington, Wyoming

### توابع کمکی
- `getState(slug)`, `NO_TAX_STATES`, `getSimilarStates(slug, limit=6)`

---

## بخش F — دیتاست شهرهای آمریکا (۲۵ شهر — آماده)

فیلدها (به‌روزشده با فیلدهای جدید): `slug`, `name`, `state`, `stateSlug`, **`countrySlug` (جدید = "united-states")**, `index`, `rent`, `food`, `transport`, `utilities`, `insurance`, `other`, **`currency`/`currencySymbol` (جدید = "USD"/"$")**, `note`

| شهر | state | index | rent | food | transport | utilities | insurance | other | مجموع |
|---|---|---|---|---|---|---|---|---|---|
| New York City | New York | 168 | 3400 | 620 | 132 | 190 | 210 | 520 | 5072 |
| San Francisco | California | 172 | 3200 | 640 | 110 | 175 | 215 | 560 | 4900 |
| Los Angeles | California | 145 | 2450 | 570 | 250 | 180 | 205 | 480 | 4135 |
| Austin | Texas | 118 | 1650 | 480 | 200 | 190 | 200 | 420 | 3140 |
| Dallas | Texas | 105 | 1450 | 450 | 210 | 185 | 195 | 380 | 2870 |
| Houston | Texas | 98 | 1350 | 440 | 215 | 195 | 195 | 360 | 2755 |
| Miami | Florida | 132 | 2600 | 540 | 190 | 200 | 210 | 470 | 4210 |
| Orlando | Florida | 104 | 1700 | 450 | 200 | 190 | 195 | 370 | 3105 |
| Chicago | Illinois | 116 | 1900 | 500 | 105 | 185 | 200 | 430 | 3320 |
| Seattle | Washington | 148 | 2300 | 580 | 120 | 165 | 205 | 490 | 3860 |
| Denver | Colorado | 122 | 1850 | 510 | 180 | 165 | 200 | 440 | 3345 |
| Phoenix | Arizona | 106 | 1550 | 460 | 205 | 210 | 195 | 380 | 3000 |
| Atlanta | Georgia | 107 | 1700 | 470 | 195 | 180 | 195 | 400 | 3140 |
| Boston | Massachusetts | 152 | 2900 | 580 | 115 | 210 | 210 | 500 | 4515 |
| Washington, D.C. | District of Columbia | 146 | 2400 | 560 | 130 | 185 | 205 | 490 | 3970 |
| Philadelphia | Pennsylvania | 108 | 1600 | 480 | 110 | 190 | 200 | 400 | 2980 |
| Portland | Oregon | 126 | 1750 | 520 | 140 | 170 | 200 | 440 | 3220 |
| Nashville | Tennessee | 105 | 1700 | 460 | 200 | 175 | 195 | 400 | 3130 |
| Las Vegas | Nevada | 102 | 1500 | 450 | 200 | 195 | 195 | 380 | 2920 |
| San Diego | California | 143 | 2600 | 560 | 210 | 175 | 205 | 470 | 4220 |
| Minneapolis | Minnesota | 108 | 1450 | 470 | 140 | 190 | 200 | 400 | 2850 |
| Salt Lake City | Utah | 110 | 1550 | 460 | 165 | 175 | 195 | 390 | 2935 |
| Charlotte | North Carolina | 104 | 1600 | 450 | 195 | 180 | 195 | 380 | 3000 |
| Detroit | Michigan | 92 | 1150 | 430 | 200 | 200 | 210 | 340 | 2530 |

### توابع کمکی
- `getCity(slug)`, `cityTotal(c)`, `getSimilarCities(slug, limit=6)`

---

## بخش G — دیتاست بین‌المللی جدید (فاز ۱: ۵۵-۶۰ شهر، ~۲۵ کشور)

**اولویت انتخاب:** قطب‌های remote-work/nomad + مقاصد رایج مهاجرت فریلنسری + کشورهای با حجم جستجوی سطح کشور بالا.

| کشور | شهرها |
|---|---|
| United Kingdom | London, Manchester, Edinburgh, Birmingham |
| Canada | Toronto, Vancouver, Montreal |
| Germany | Berlin, Munich, Hamburg |
| Portugal | Lisbon, Porto |
| Spain | Barcelona, Madrid, Valencia |
| Thailand | Bangkok, Chiang Mai |
| Mexico | Mexico City, Playa del Carmen |
| UAE | Dubai, Abu Dhabi |
| Australia | Sydney, Melbourne, Brisbane |
| Netherlands | Amsterdam, Rotterdam |
| France | Paris, Lyon |
| Italy | Rome, Milan |
| Ireland | Dublin |
| Switzerland | Zurich, Geneva |
| Singapore | Singapore |
| Japan | Tokyo, Osaka |
| South Korea | Seoul |
| Brazil | São Paulo, Rio de Janeiro |
| Argentina | Buenos Aires |
| Colombia | Medellín, Bogotá |
| Indonesia | Bali/Denpasar, Jakarta |
| Vietnam | Ho Chi Minh City, Hanoi |
| Philippines | Manila |
| India | Bangalore, Mumbai |
| Turkey | Istanbul |
| Poland | Warsaw, Krakow |
| Czech Republic | Prague |
| Georgia | Tbilisi |
| Malaysia | Kuala Lumpur |
| New Zealand | Auckland |

**منبع داده‌ی اولیه:** Numbeo برای baseline شاخص/هزینه، سپس اصلاح دستی برای صحت.

**فاز ۲ (ماه ۷ به بعد):** گسترش به ۱۵۰-۲۰۰ شهر بر اساس داده‌ی واقعی Search Console، نه حدس.

### مدل داده‌ی سلسله‌مراتبی کشور

```
Country
  slug, name, region  (مثلاً "Europe", "Asia", "Americas")
  avgIndex            // میانگین وزنی شهرهای زیرمجموعه، یا Numbeo country index
  avgRent, avgFood, avgTransport, avgUtilities, avgInsurance, avgOther
  currency, currencySymbol
  note                // پاراگراف یکتا برای سئو
  cities: [citySlug, ...]

City (به‌روزشده)
  slug, name, countrySlug   ← فیلد جدید، برای آمریکا = "united-states"
  index, rent, food, transport, utilities, insurance, other
  currency, currencySymbol  ← فیلد جدید
  note
```

### توابع کمکی جدید
- `getCountry(slug)`
- `getCitiesByCountry(countrySlug)`
- `getSimilarCountries(slug, limit=6)` — بر اساس avgIndex

---

## بخش H — فرمول‌های محاسباتی

### H-1. فرمول مالیات Freelance (`src/lib/taxMath.js`)

```js
estimateTax({ gross, expenses, federalRate, stateRate }) {
  net         = max(0, gross - expenses)
  seTax       = net * 0.9235 * (15.3 / 100)
  taxableBase = max(0, net - seTax / 2)
  federalTax  = taxableBase * (federalRate / 100)
  stateTax    = taxableBase * (stateRate / 100)
  totalTax    = seTax + federalTax + stateTax
  takeHome    = net - totalTax
  effectiveRate   = (totalTax / gross) * 100
  monthlySetAside = totalTax / 12
  quarterly       = totalTax / 4
}
```

### H-2. Hourly Rate Calculator

پیش‌فرض‌ها: `targetIncome=70000, expenses=6000, taxRate=25%, billableHours=25/week, weeksOff=4`

```js
weeks       = max(0, 52 - weeksOff)
grossNeeded = (targetIncome + expenses) / (1 - taxRate/100)
totalHours  = billableHours * weeks
rate        = grossNeeded / totalHours
dayRate     = rate * 8
```

### H-3. Project Profit Calculator

پیش‌فرض‌ها: `price=2000, platformFee=10%, expenses=150, taxRate=25%, hours=30`

```js
fee    = price * (platformFee/100)
preTax = max(0, price - fee - expenses)
tax    = preTax * (taxRate/100)
profit = preTax - tax
hourly = profit / hours
margin = (profit / price) * 100
```

### H-4. Cost of Living Calculator (مستقل)

پیش‌فرض‌ها: `income=3500, rent=1200, food=500, transport=150, utilities=200, insurance=180, other=300`

```js
total   = rent+food+transport+utilities+insurance+other
surplus = income - total
ratio   = (surplus/income) * 100
yearly  = surplus * 12
status  = ratio>=20 ? "Comfortable" : ratio>=0 ? "Tight" : "Over budget"
```

### H-5. Money Transfer Fee Calculator

پیش‌فرض‌ها: `amount=2000, fixedFee=5, percentFee=1%, rateMarkup=1.5%, midRate=1`

```js
pct           = amount * (percentFee/100)
afterFees     = max(0, amount - fixedFee - pct)
actualRate    = midRate * (1 - rateMarkup/100)
received      = afterFees * actualRate
idealReceived = amount * midRate
totalCost     = idealReceived - received
costPct       = (totalCost / idealReceived) * 100
```

### H-6. Travel Budget Calculator

پیش‌فرض‌ها: `days=14, flights=800, visa=100, insurance=80, accommodation=70/night, dailySpend=60/day, buffer=15%`

```js
fixed       = flights + visa + insurance
daily       = (accommodation + dailySpend) * days
subtotal    = fixed + daily
contingency = subtotal * (buffer/100)
total       = subtotal + contingency
perDay      = total / days
```

### H-7. Salary / Purchasing Power Converter *(جدید)*

```js
convertSalary({ currentSalary, currentLocationIndex, targetLocationIndex }) {
  targetSalary = currentSalary * (targetLocationIndex / currentLocationIndex)
}
```
از دیتاست `index` موجود ساخته می‌شود؛ نیاز به داده‌ی جدید ندارد.

### H-8. Family size multiplier *(جدید)*

```js
FAMILY_MULTIPLIERS = { single: 1, couple: 1.6, family: 2.2 }
adjustedTotal = baseTotal * FAMILY_MULTIPLIERS[selectedSize]
```
ضرایب اولیه‌ی تخمینی — قابل تنظیم دقیق‌تر پس از جمع‌آوری بازخورد.

### H-9. فرمت دلار/ارز

```js
formatCurrency(n, currency) = n.toLocaleString("en-US", {
  style: "currency", currency, maximumFractionDigits: 0
})
```

---

## بخش I — رجیستری Programmatic (`src/lib/programmatic.js`)

### I-1. `freelance-tax-calculator`
بدون تغییر نسبت به نسخه‌ی فعلی — `locations: STATES`, `getSimilar: getSimilarStates`, `Calculator: StateTaxCalculator`, `DataTable: StateIncomeTable`, `buildFaq: buildStateFaq`.

### I-2. `cost-of-living-calculator` (به‌روزشده — سلسله‌مراتبی)
```js
{
  toolSlug: "cost-of-living-calculator",
  locationNoun: "city",
  locations: CITIES,              // اکنون شامل آمریکا + بین‌المللی
  getLocation: getCity,
  getSimilar: getSimilarCities,
  Calculator: CityCostCalculator,
  DataTable: CityCostTable,
  buildFaq: buildCityFaq,
  badge: (c) => `${formatCurrency(cityTotal(c), c.currency)}/mo`,
  crossLinks: (c) => [
    state tax calculator (اگر countrySlug === "united-states"),
    country aggregate page (getCountry(c.countrySlug))
  ]
}
```

### I-3. `cost-of-living-country` *(جدید)*
```js
{
  toolSlug: "cost-of-living-calculator",
  locationNoun: "country",
  locations: COUNTRIES,
  getLocation: getCountry,
  getSimilar: getSimilarCountries,
  Calculator: CountryCostCalculator,   // نسخه‌ی aggregate از CityCostCalculator
  buildFaq: buildCountryFaq,
  crossLinks: (country) => getCitiesByCountry(country.slug)  // لینک به شهرهای زیرمجموعه
}
```

**تعداد صفحات تولیدشده (فاز ۱):** ۵۱ (state) + ۲۵ (شهر آمریکا) + ۵۵-۶۰ (شهر بین‌المللی) + ۲۵ (کشور) ≈ **۱۵۶-۱۶۱ صفحه**

---

## بخش J — فیچرهای جدید (اولویت‌بندی‌شده)

### J-1. مقایسه‌ی دو لوکیشن — اولویت اول
- مسیر: `/compare/:locationA/:locationB`
- دو ستون کنار هم: rent, food, transport, utilities, insurance, other, total, index
- تولید خودکار از ترکیب‌های دوتایی دیتاست موجود — کلمات کلیدی نامحدود بدون کار دستی اضافه
- عنوان صفحه: "{A} vs {B}: Cost of Living Comparison ({year})"
- بیشترین بازده سئو/هزینه چون رقبای بزرگ (Numbeo, Expatistan) دقیقاً همین را ارائه می‌دهند

### J-2. Salary / Purchasing Power Converter — اولویت دوم
فرمول در بخش H-7. کاربرد مستقیم برای فریلنسرهای remote که بین شهرها جابه‌جا می‌شوند.

### J-3. Family size toggle — اولویت سوم
فرمول در بخش H-8. بدون نیاز به دیتاست جدید.

### J-4. Currency selector — اولویت چهارم
نمایش خروجی به ارز محلی کاربر با نرخ تقریبی (API رایگان نرخ ارز مثل exchangerate-api). پیش‌نیازش فیلد `currency` در دیتاست (بخش G) است.

### فیچرهای کنارگذاشته‌شده (بازگشت پایین در بازه‌ی ۶ ماهه)
- نقشه‌ی تعاملی heat map جهانی
- حساب کاربری/ذخیره‌سازی سمت کاربر (نقض معماری static-first)
- داده‌ی real-time به‌جای دیتاست استاتیک

---

## بخش K — سازنده‌های FAQ

### K-1. `buildStateFaq(state)` — ۵ سؤال
۱. مالیات فریلنسری در {state} چطوره؟ (شرطی بر `structure`)
۲. مالیات روی $80,000 چقدره؟ (`estimateTax`)
۳. ماهانه چقدر باید کنار بذاری؟ (`monthlySetAside`, `quarterly`)
۴. پرداخت فصلی لازمه؟ (بله اگر بدهی ≥ $1,000)
۵. نکات دیگه برای فریلنسرهای {state}؟ (`state.note`)

### K-2. `buildCityFaq(city)` — ۵ سؤال
۱. هزینه‌ی زندگی در {city} چقدره؟
۲. برای زندگی راحت چقدر حقوق لازمه؟ (`comfortable = round(total*1.25/50)*50`)
۳. {city} گرونه؟ (مقایسه‌ی `index` با ۱۰۰)
۴. برای شروع چقدر باید کنار گذاشت؟ (`total*2 + rent*2`)
۵. {city} برای کار ریموت چه ویژگی‌ای داره؟ (`city.note`)

### K-3. `buildCountryFaq(country)` — ۵ سؤال *(جدید، الگوی مشابه K-2 در سطح کشور)*
۱. هزینه‌ی زندگی در {country} به‌طور میانگین چقدره؟
۲. کدوم شهرهای {country} ارزون‌تر/گرون‌تر هستن؟ (لینک به `getCitiesByCountry`)
۳. برای زندگی راحت در {country} چقدر حقوق لازمه؟
۴. {country} برای فریلنسر/نومد دیجیتال مناسبه؟ (شامل یک پاراگراف کوتاه ویزا/اقامت — نه یک نیش کامل)
۵. {country.note}

---

## بخش L — الزامات محتوا (مهم‌ترین شکاف نسبت به نسخه‌ی اول)

هر صفحه‌ی location (state/city/country) باید **۸۰۰ تا ۱۲۰۰ کلمه محتوای یکتا** داشته باشد.

**ساختار پیشنهادی هر صفحه:**
1. Intro (۱۰۰-۱۵۰ کلمه)
2. Calculator
3. «Breakdown توضیحی» (۲۰۰-۳۰۰ کلمه) — چرا اجاره/غذا/حمل‌ونقل این‌قدره
4. «Who this fits» (۲۰۰-۳۰۰ کلمه) — این مکان برای چه نوع فریلنسر/مهاجری مناسب است
5. یک پاراگراف کوتاه «Visa/tax context» (بدون ورود کامل به نیش مهاجرت)
6. FAQ (۵ سوال)
7. Disclaimer box (تاریخ به‌روزرسانی داده)

**پیش‌نیاز اپلای AdSense:** حداقل ۳۰-۴۰ صفحه با این سطح محتوا آماده باشد.

---

## بخش M — مسیریابی کامل (`src/App.jsx`)

```
/                                          → Home
/tools                                     → AllTools
/freelancer-tools                          → CategoryPage(freelance)
/immigration-tools                         → CategoryPage(immigration)
/tools/freelance-tax-calculator            → FreelanceTaxCalculator
/tools/hourly-rate-calculator              → HourlyRateCalculator
/tools/project-profit-calculator           → ProjectProfitCalculator
/tools/cost-of-living-calculator           → CostOfLivingCalculator (+ LocationDirectory)
/tools/money-transfer-fee-calculator       → MoneyTransferFeeCalculator
/tools/travel-budget-calculator            → TravelBudgetCalculator
/tools/:toolSlug/:locationSlug              → LocationToolPage (state/city، داینامیک)
/tools/cost-of-living-calculator/country/:countrySlug → CountryCostPage (جدید)
/compare/:locationA/:locationB             → ComparePage (جدید)
/tools/salary-converter                    → SalaryConverterPage (جدید)
/blog                                      → Blog
/blog/:slug                                → BlogPost
*                                          → PageNotFound
```

---

## بخش N — ساختار صفحه‌ی Programmatic (`LocationToolPage`)

۱. Seo (title, description, keywords, canonical, FAQPage JSON-LD)
۲. Breadcrumbs (+ BreadcrumbList schema) — Home → Category → Tool → Country → City (سلسله‌مراتب کامل برای شهرهای بین‌المللی)
۳. H1 + Intro
۴. Calculator
۵. Disclaimer box
۶. AdSlot (banner)
۷. DataTable
۸. Article sections (طبق بخش L، ۳-۴ بخش نه ۲ بخش)
۹. FAQ Accordion
۱۰. LocationLinkGrid ("Compare with similar")
۱۱. "See all" → directory
۱۲. crossLinks (state↔city، city↔country)
۱۳. RelatedTools (۳ ابزار مرتبط)
۱۴. Sidebar AdSlot (sticky rectangle)

---

## بخش O — کامپوننت‌های مشترک

| کامپوننت | نقش |
|---|---|
| `Layout` | Header + Outlet + Footer |
| `Seo` | مدیریت داینامیک head + JSON-LD |
| `Breadcrumbs` | مسیر ناوبری + schema |
| `AdSlot` | جایگاه ادسنس (banner/rectangle/leaderboard) |
| `NumberField` | ورودی عددی با prefix/suffix |
| `ResultCard` | کارت نتیجه با highlight |
| `BreakdownBar` | نمودار میله‌ای انباشته |
| `ToolPageShell` | قالب صفحات ابزار مستقل |
| `RelatedTools` | ۳ ابزار مرتبط |
| `LocationDirectory` | گرید همه‌ی لوکیشن‌ها |
| `LocationLinkGrid` | گرید لوکیشن‌های مشابه |
| `StateFaq` / `CityFaq` / `CountryFaq` | آکاردئون FAQ |
| `CompareTable` *(جدید)* | جدول دو‌ستونه‌ی مقایسه |
| `CurrencySelector` *(جدید)* | انتخاب ارز نمایش |
| `FamilySizeToggle` *(جدید)* | سوییچ single/couple/family |

---

## بخش P — استراتژی سئو

- Long-tail keywords اختصاصی هر صفحه
- FAQPage + BreadcrumbList JSON-LD
- Canonical URL مستقل هر صفحه
- محتوای منحصربه‌فرد (فیلد `note` + FAQ با اعداد محاسبه‌شده)
- Internal linking چهارلایه: state↔city، city↔country، similar locations، related tools
- صفحات مقایسه (J-1) به‌عنوان لایه‌ی چهارم تولید کلمات کلیدی ترکیبی

---

## بخش Q — نکات فنی پیاده‌سازی

1. **Reactivity:** `useEffect` به‌جای `key` prop برای حفظ ورودی کاربر هنگام تغییر لوکیشن. `StateTaxCalculator` فقط `stateRate` را سینک می‌کند؛ `CityCostCalculator` هزینه‌ها را ریست می‌کند ولی درآمد کاربر را حفظ می‌کند.
2. **prop naming:** کامپوننت‌های programmatic با prop یکسان `location` (شامل country) دریافت می‌شوند.
3. **useMemo** برای همه‌ی محاسبات.
4. **ScrollToTop** با هر تغییر مسیر.
5. **منبع واحد حقیقت:** منطق محاسبه فقط در `taxMath.js` و دیتاست‌ها.

---

## بخش R — برنامه‌ی زمانی ۶ ماهه

| ماه | کار |
|---|---|
| ۱ | تکمیل محتوای ۸۰۰-۱۲۰۰ کلمه‌ای برای ۵۱ استیت آمریکا (دیتاست آماده است) |
| ۱-۲ | افزودن دیتاست ۵۵-۶۰ شهر بین‌المللی + ۲۵ کشور، با همان سطح محتوا |
| ۲ | اپلای AdSense (پس از ۳۰-۴۰ صفحه‌ی کامل) |
| ۲-۳ | ساخت فیچر مقایسه (J-1) — بیشترین بازده سئو |
| ۲-۳ | لینک‌سازی داخلی از بلاگ موجود به صفحات ابزار |
| ۳-۴ | لینک‌سازی خارجی سبک (Reddit r/freelance, Indie Hackers, Product Hunt) |
| ۴ | افزودن Salary Converter (J-2) |
| ۴-۶ | بر اساس Search Console، تقویت صفحات پرپتانسیل + شروع فاز ۲ (گسترش شهرها) |

---

## بخش S — چک‌لیست شروع فوری

- [ ] افزودن فیلد `countrySlug` و `currency`/`currencySymbol` به دیتاست شهرهای موجود
- [ ] ساخت دیتاست ۲۵ کشور با فیلدهای aggregate (بخش G)
- [ ] ساخت `CountryCostPage` و `CountryCostCalculator`
- [ ] بازنویسی محتوای هر صفحه‌ی موجود به ۸۰۰+ کلمه طبق ساختار بخش L
- [ ] ساخت مسیر و کامپوننت `/compare/:a/:b` + `CompareTable`
- [ ] ساخت `SalaryConverterPage`
- [ ] افزودن `FamilySizeToggle` به `CityCostCalculator` و `CountryCostCalculator`
- [ ] افزودن `CurrencySelector` + اتصال به API نرخ ارز
- [ ] برنامه‌ریزی تقویم انتشار بلاگ هم‌زمان با انتشار صفحات جدید
- [ ] آماده‌سازی حداقل ۳۰-۴۰ صفحه قبل از اپلای AdSense
