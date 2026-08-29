# چک‌لیست راستی‌آزمایی داده‌ی مالیاتی — سال ۲۰۲۶

> این سند خروجی بخش ۱۳ سند اصلی است.

> **داده تولید شد، ولی هنوز تأییدشده نیست.** هیچ صفحه‌ای منتشر نمی‌شود تا ردیف مربوطه‌اش اینجا تیک بخورد.


---

## ۱. وضعیت فعلی

| مورد | مقدار |
|---|---|
| حوزه‌های استخراج‌شده | **51** (۵۰ ایالت + واشنگتن دی‌سی) |
| ساختار | 9 بدون مالیات · 15 تخت · 27 پلکانی |
| خطای ساختاری | **۰** (`scripts/validate_tax_data.py`) |
| کلاس منبع | **ثانویه** — نیازمند تأیید |
| بسته‌ی مبدأ | `policyengine-us` نسخه‌ی `1.821.4` |
| تاریخ تولید | 2026-08-29T16:05:23Z |

### چرا «ثانویه»

شبکه‌ی محیط توسعه به `irs.gov` و سایت دپارتمان‌های درآمد ایالتی دسترسی ندارد. داده از درخت پارامتر یک مدل متن‌باز نگهداری‌شده استخراج شد که هر پارامترش ارجاع به منبع اولیه (قانون، Revenue Procedure، فرم ایالتی) دارد؛ آن ارجاع‌ها در فیلد `provenance.sources` هر فایل کپی شده‌اند.

**جایگزین جستجوی وب عمداً رد شد:** دو جستجوی متوالی برای همان کیورد، براکت‌های فدرال متناقض برگرداندند (۱۰۵٬۷۰۰ در برابر ۱۰۷٬۴۷۵). داده‌ی فعلی با منبع اول همخوان است و با دومی نیست — یعنی خلاصه‌های جستجو برای این کار قابل اعتماد نیستند.


---

## ۲. فدرال — بالاترین اولویت

اشتباه اینجا هم‌زمان **همه‌ی** صفحات را غلط می‌کند.


| # | قلم | مقدار استخراج‌شده | تأیید |
|---|---|---|---|
| ۱ | براکت‌های فدرال (single) | 10% · 12% · 22% · 24% · 32% · 35% · 37% | ⬜ |
| ۲ | آستانه‌های single | 12,400 · 50,400 · 105,700 · 201,775 · 256,225 · 640,600 | ⬜ |
| ۳ | آستانه‌های marriedJointly | 24,800 · 100,800 · 211,400 · 403,550 · 512,450 · 768,700 | ⬜ |
| ۴ | آستانه‌های marriedSeparately | 12,400 · 50,400 · 105,700 · 201,775 · 256,225 · 384,350 | ⬜ |
| ۵ | آستانه‌های headOfHousehold | 17,700 · 67,450 · 105,700 · 201,750 · 256,200 · 640,600 | ⬜ |
| ۶ | کسر استاندارد | single 16,100 · MFJ 32,200 · HoH 24,150 | ⬜ |
| ۷ | نرخ‌های SE tax | 12.4% + 2.9% = 15.3% | ⬜ |
| ۸ | ضریب NESE | 0.9235 (مشتق از `1 - (socialSecurityRate + medicareRate) / 2`) | ⬜ |
| ۹ | سقف Social Security | 184,500 | ⬜ |
| ۱۰ | آستانه‌ی حداقل SE tax | 400 | ⬜ |
| ۱۱ | Additional Medicare | 0.9% بالای 200,000/250,000/125,000 (تعدیل‌نشونده) | ⬜ |
| ۱۲ | QBI | نرخ 20.0% · شروع phase-out: single 201,750 · MFJ 403,500 | ⬜ |
| ۱۳ | تاریخ‌های سررسید فصلی | Q1 2026-04-15 · Q2 2026-06-15 · Q3 2026-09-15 · Q4 2027-01-15 | ⬜ |
| ۱۴ | درصدهای safe harbor | 90% سال جاری · 100% سال قبل · 110% اگر AGI سال قبل > $150,000 (MFS: $75,000) | ⬜ |
| ۱۵ | حداقل بدهی مشمول جریمه | $1,000 | ⬜ |

**منبع اولیه‌ی موارد ۱ تا ۶:** Rev. Proc. 2025-32 — https://www.irs.gov/pub/irs-drop/rp-25-32.pdf


**موارد ۱۳ تا ۱۵ منبع متفاوتی دارند.** این‌ها در درخت پارامتر مبدأ نبودند، ولی برخلاف براکت‌ها ثابت‌های قانونی‌اند نه ارقام تورمی. به‌جای کپی از یک جدول، `scripts/estimated_tax.py` آن‌ها را از الگوی ۲۶ U.S.C. ۶۶۵۴(c)(2) و قاعده‌ی تعطیلات ۷۵۰۳ محاسبه می‌کند.

> ✅ **این کار یک تناقض واقعی را حل کرد:** دو منبع وب برای سررسید دوم ۲۰۲۶ دو تاریخ متفاوت دادند (۱۵ و ۱۶ ژوئن). محاسبه نشان داد ۱۵ ژوئن ۲۰۲۶ دوشنبه است، پس هیچ جابه‌جایی لازم نیست. اشتقاق الگوریتمی ضمناً سال‌های واقعاً جابه‌جاشونده را هم درست می‌دهد — مثلاً سررسید اول ۲۰۲۸ به ۱۸ آوریل می‌رود چون ۱۵ آوریل شنبه است و ۱۷ آوریل روز رهایی دی‌سی.

**راستی‌آزمایی این سه ردیف** با فرم ۱۰۴۰-ES همان سال انجام شود: https://www.irs.gov/pub/irs-pdf/f1040es.pdf


---

## ۳. ایالت‌های اولویت‌دار (۸ صفحه‌ی اول)

| ایالت | ساختار | نرخ | کهنه؟ | منبع اولیه | تأیید |
|---|---|---|---|---|---|
| California | progressive | 9 پله، سقف 12.3% | ⚠️ بله | [2021 Form 540 California Resident Income Tax](https://www.ftb.ca.gov/forms/2021/2021-540.pdf) | ⬜ |
| New York | progressive | 9 پله، سقف 10.9% | نه | [2021 NY Form IT-201 Instructions](https://www.tax.ny.gov/pdf/2021/inc/it201i_2021.pdf#page=51) | ⬜ |
| Texas | none | — | نه | — | ⬜ |
| Florida | none | — | نه | — | ⬜ |
| Illinois | flat | 4.95% | نه | [Income Tax Rates](https://www2.illinois.gov/rev/research/taxrates/Pages/income.aspx) | ⬜ |
| Pennsylvania | flat | 3.07% | نه | [PA Form PA-40 Instructions, page 1](https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=1) | ⬜ |
| Washington | none | — | نه | — | ⬜ |
| Ohio | progressive | 2 پله، سقف 2.75% | نه | [Section 5747.02 | Tax rates.](https://codes.ohio.gov/ohio-revised-code/section-5747.02) | ⬜ |

---

## ۴. بقیه‌ی ایالت‌ها

| ایالت | ساختار | نرخ | کهنه؟ | منبع اولیه | تأیید |
|---|---|---|---|---|---|
| Alabama | progressive | 3 پله، سقف 5% | نه | [2024 Alabama Income Tax Instructions](https://www.revenue.alabama.gov/wp-content/uploads/2025/01/24f40bk.pdf#page=25) | ⬜ |
| Alaska | none | — | نه | — | ⬜ |
| Arizona | flat | 2.5% | نه | [Arizona State Legislature Title 43 - Taxatio](https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01011.htm) | ⬜ |
| Arkansas | progressive | 5 پله، سقف 3.7% | نه | [2014 Indexed Tax Brackets](https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/TaxBrackets_2014.pdf#page=1) | ⬜ |
| Colorado | flat | 4.4% | نه | [Colorado Proposition 121, passed by the elec](https://leg.colorado.gov/sites/default/files/initiative%2520referendum_proposition%20121%20final%20lc%20packet.pdf#page=1) | ⬜ |
| Connecticut | progressive | 7 پله، سقف 6.99% | نه | [Connecticut General Statutes, Chapter 229, S](https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-700) | ⬜ |
| Delaware | progressive | 7 پله، سقف 6.6% | نه | [Government of Delaware - Tax Rate Changes](https://revenue.delaware.gov/software-developer/tax-rate-changes/) | ⬜ |
| Georgia | flat | 4.99% | نه | [Georgia HB1015 (2023-2024), Section 1 - flat](https://www.legis.ga.gov/legislation/66260) | ⬜ |
| Hawaii | progressive | 12 پله، سقف 11% | نه | [Tax Rate Schedules For Taxable Years Beginni](https://tax.hawaii.gov/forms/d_18table-on/d_18table-on_p13/) | ⬜ |
| Idaho | flat | 5.3% | ⚠️ بله | [Idaho State Tax Comission - Individual Incom](https://tax.idaho.gov/taxes/income-tax/individual-income/individual-income-tax-rate-schedule/) | ⬜ |
| Indiana | flat | 2.95% | نه | [IC 6-3-2-1 Tax rate (a)(3)](https://iga.in.gov/laws/2024/ic/titles/6#6-3-2-1) | ⬜ |
| Iowa | flat | 3.8% | نه | [IDR Announces 2023 Interest Rates, Deduction](https://revenue.iowa.gov/taxes/tax-guidance/individual-income-tax/2023-changes-iowa-individual-income-tax) | ⬜ |
| Kansas | progressive | — | نه | [2022 Form K-40 instructions](https://www.ksrevenue.gov/pdf/ip22.pdf) | ⬜ |
| Kentucky | flat | 3.5% | نه | [2021 Kentucky Individual Income Tax Return R](https://revenue.ky.gov/Forms/Form%20740-2021.pdf#page=1) | ⬜ |
| Louisiana | flat | 3% | نه | [Louisiana Revised Statutes, RS 47:32 - Tax o](https://www.legis.la.gov/legis/Law.aspx?d=101946) | ⬜ |
| Maine | progressive | 3 پله، سقف 7.15% | نه | [§5403. Annual adjustments for inflation 1(A)](https://legislature.maine.gov/statutes/36/title36sec5403.html) | ⬜ |
| Maryland | progressive | 10 پله، سقف 6.5% | نه | [Maryland 2025 Resident Tax Forms and Instruc](https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=22) | ⬜ |
| Massachusetts | flat | 5% | نه | [Section 4: Rates of tax for residents, non-r](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section4) | ⬜ |
| Michigan | flat | 4.25% | نه | [Michigan INCOME TAX ACT OF 1967 Chapter 2, 2](http://www.legislature.mi.gov/documents/mcl/pdf/mcl-act-281-of-1967.pdf#page=60) | ⬜ |
| Minnesota | progressive | 4 پله، سقف 9.85% | ⚠️ بله | [2023 Minnesota Statutes, 290.06 RATES OF TAX](https://www.revisor.mn.gov/statutes/cite/290.06#stat.290.06.2c) | ⬜ |
| Mississippi | flat | 4% | نه | [Mississippi Income Tax Instructions 2022](https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=20) | ⬜ |
| Missouri | progressive | 8 پله، سقف 4.7% | ⚠️ بله | [2019 Missouri Income Tax Chart Form MO-1040 ](https://dor.mo.gov/forms/MO-1040%20Instructions_2019.pdf#page=22) | ⬜ |
| Montana | progressive | 2 پله، سقف 5.65% | نه | [Montana Code Annotated 2021 Title 15, Chapte](https://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0030/0150-0300-0210-0030.html) | ⬜ |
| Nebraska | progressive | 4 پله، سقف 4.55% | نه | [Legislative Bill 754 (Bill Text)](https://www.nebraskalegislature.gov/FloorDocs/108/PDF/Slip/LB754.pdf#page=3) | ⬜ |
| Nevada | none | — | نه | — | ⬜ |
| New Hampshire | none | — | نه | — | ⬜ |
| New Jersey | progressive | 7 پله، سقف 10.75% | نه | [2025 NJ-1040 Instructions - Tax Rate Schedul](https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf#page=65) | ⬜ |
| New Mexico | progressive | 6 پله، سقف 5.9% | نه | [New Mexico Income Tax, Title 3, Chapter 3, P](https://www.srca.nm.gov/parts/title03/03.003.0007.html) | ⬜ |
| North Carolina | flat | 3.99% | نه | [North Carolina Department of Revenue - Tax R](https://www.ncdor.gov/taxes-forms/tax-rate-schedules) | ⬜ |
| North Dakota | progressive | 3 پله، سقف 2.5% | نه | [2021 North Dakota income tax instructions](https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdf#page=34) | ⬜ |
| Oklahoma | progressive | 4 پله، سقف 4.5% | نه | [2021 Form 511 instructions](https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf) | ⬜ |
| Oregon | progressive | 4 پله، سقف 9.9% | ⚠️ بله | [Chapter 316 - Personal Income Tax](https://www.oregonlegislature.gov/bills_laws/ors/ors316.html) | ⬜ |
| Rhode Island | progressive | 3 پله، سقف 5.99% | نه | [Rhode Island Division of Taxation Advisory A](https://tax.ri.gov/sites/g/files/xkgbur541/files/2025-11/ADV_2025_22_Inflation_Adjustments.pdf#page=2) | ⬜ |
| South Carolina | progressive | 2 پله، سقف 5.21% | نه | [SC H.4216 Section 1 - Section 12-6-510(C) (2](https://www.scstatehouse.gov/sess126_2025-2026/bills/4216.htm) | ⬜ |
| South Dakota | none | — | نه | — | ⬜ |
| Tennessee | none | — | نه | — | ⬜ |
| Utah | flat | 4.45% | نه | [Utah Code 59-10-104 (2) (b)](https://le.utah.gov/xcode/historical.html?date=1/1/2014&oc=/xcode/Title59/Chapter10/C59-10-S104_1800010118000101.html) | ⬜ |
| Vermont | progressive | 4 پله، سقف 8.75% | ⚠️ بله | [Vermont §5822. Tax on income of individuals,](https://legislature.vermont.gov/statutes/section/32/151/05822) | ⬜ |
| Virginia | progressive | 4 پله، سقف 5.75% | نه | [Code of Virginia § 58.1-320.](https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/) | ⬜ |
| Washington, D.C. | progressive | 7 پله، سقف 10.75% | نه | [2021 Form D-40 Booklet](https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=19) | ⬜ |
| West Virginia | progressive | 5 پله، سقف 4.58% | نه | [West Virginia Senate Bill 392 (2026), §11-21](https://www.wvlegislature.gov/Bill_Text_HTML/2026_SESSIONS/RS/bills/sb392%20sub1%20enr.pdf#page=6) | ⬜ |
| Wisconsin | progressive | 4 پله، سقف 7.65% | ⚠️ بله | [State of Wisconsin Department of Revenue](https://www.revenue.wi.gov/Pages/FAQS/pcs-taxrates.aspx) | ⬜ |
| Wyoming | none | — | نه | — | ⬜ |

---

## ۵. هفت ایالتی که ارقام ۲۰۲۶ ندارند

براکت این‌ها تورمی است و ایالت هنوز ارقام ۲۰۲۶ را منتشر نکرده. مقادیر فعلی **۲۰۲۵** هستند.

- **California** — آخرین مقدار مؤثر از 2025-01-01
- **Idaho** — آخرین مقدار مؤثر از 2025-01-01
- **Minnesota** — آخرین مقدار مؤثر از 2025-01-01
- **Missouri** — آخرین مقدار مؤثر از 2025-01-01
- **Oregon** — آخرین مقدار مؤثر از 2025-01-01
- **Vermont** — آخرین مقدار مؤثر از 2025-01-01
- **Wisconsin** — آخرین مقدار مؤثر از 2025-01-01

**قاعده:** تا انتشار ارقام ۲۰۲۶، این صفحات یا ساخته نمی‌شوند یا صریحاً «بر اساس ارقام ۲۰۲۵» برچسب می‌خورند. نمایش عدد ۲۰۲۵ زیر عنوان ۲۰۲۶ همان اشتباهی است که کل پروژه برای پرهیز از آن ساخته می‌شود.


---

## ۶. روش تأیید هر ردیف

1. لینک منبع اولیه‌ی همان ردیف را باز کن (از `provenance.sources` فایل JSON).

2. عدد را با فایل JSON مقایسه کن.

3. اگر خواند: `verification` را در فایل به `"verified"` تغییر بده و `verifiedAt` و `verifiedBy` اضافه کن.

4. اگر نخواند: **عدد فایل را اصلاح کن**، نه منبع را. سپس یک ردیف در `changelog` فایل `meta.json` اضافه کن.

5. بعد از اتمام یک دسته: `python3 scripts/validate_tax_data.py --year 2026 --strict`


## ۷. بازتولید داده

```bash
python3 scripts/extract_tax_data.py --year 2026   # بازسازی از بسته‌ی مبدأ
python3 scripts/validate_tax_data.py --year 2026  # بررسی ساختاری
```


> بازاجرای استخراج، `verification` را به `pending` برمی‌گرداند. تأییدهای انجام‌شده را قبل از بازاجرا در گیت کامیت کن.

