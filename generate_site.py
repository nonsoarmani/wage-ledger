import csv
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(ROOT, "template", "page.html")
CSV_PATH = os.path.join(ROOT, "keywords.csv")
DIST = os.path.join(ROOT, "dist")

# ---- EDIT THESE two lines for your site ----
DOMAIN = "https://hourlybreakdown.com"
SITE_NAME = "Hourly Breakdown"

with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    TEMPLATE = f.read()


def money(n):
    return "${:,.2f}".format(n)


def money0(n):
    return "${:,.0f}".format(n)


rows = []
with open(CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

os.makedirs(os.path.join(DIST, "salary"), exist_ok=True)

sitemap_urls = []
hub_links = []

for r in rows:
    salary = float(r["salary"])
    hours = float(r.get("hours_per_week") or 40)
    weeks = float(r.get("weeks_per_year") or 52)

    total_hours = hours * weeks
    hourly = salary / total_hours if total_hours else 0
    daily = hourly * (hours / 5 if hours else 8)
    weekly = hourly * hours
    biweekly = weekly * 2
    monthly = salary / 12
    semi = salary / 24

    slug = "{}-a-year-is-how-much-an-hour".format(int(salary))
    page_dir = os.path.join(DIST, "salary", slug)
    os.makedirs(page_dir, exist_ok=True)

    html = TEMPLATE
    html = html.replace("__SITE_NAME__", SITE_NAME)
    html = html.replace("__SALARY_FULL__", money0(salary))
    html = html.replace("__SALARY_NUM__", str(int(salary)))
    html = html.replace("__HOURLY__", money(hourly))
    html = html.replace("__DAILY__", money(daily))
    html = html.replace("__WEEKLY__", money(weekly))
    html = html.replace("__BIWEEKLY__", money(biweekly))
    html = html.replace("__SEMI__", money(semi))
    html = html.replace("__MONTHLY__", money(monthly))
    html = html.replace("__ANNUAL__", money0(salary))
    html = html.replace("__HOURS_PER_WEEK__", str(int(hours)))
    html = html.replace("__WEEKS_PER_YEAR__", str(int(weeks)))
    html = html.replace("__TOTAL_HOURS__", "{:,.0f}".format(total_hours))
    html = html.replace("__SLUG__", slug)

    with open(os.path.join(page_dir, "index.html"), "w", encoding="utf-8") as out:
        out.write(html)

    sitemap_urls.append("/salary/{}/".format(slug))
    hub_links.append((salary, slug))

# ---- Hub / homepage, grouped into readable salary bands ----
hub_links.sort(key=lambda x: x[0])

bands = [
    ("Under $30,000", 0, 30000),
    ("$30,000 - $50,000", 30000, 50000),
    ("$50,000 - $75,000", 50000, 75000),
    ("$75,000 - $100,000", 75000, 100000),
    ("$100,000 and up", 100000, float("inf")),
]

band_html_parts = []
for label, low, high in bands:
    items_in_band = [(sal, slug) for sal, slug in hub_links if low <= sal < high]
    if not items_in_band:
        continue
    link_parts = []
    for sal, slug in items_in_band:
        link_parts.append(
            '<a class="chip" href="/salary/{}/">{}</a>'.format(slug, money0(sal))
        )
    band_html_parts.append(
        '<section class="band">'
        '<h2>{}</h2>'
        '<div class="chips">{}</div>'
        '</section>'.format(label, "".join(link_parts))
    )
bands_html = "\n".join(band_html_parts)

hub_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{site_name} - Salary to Hourly Wage Converter</title>
<meta name="description" content="Convert any yearly salary to an hourly, daily, weekly, or monthly rate. Pick your salary below for the full breakdown.">
<style>
  :root {{
    --ink: #16241C;
    --paper: #ffffff;
    --panel: #EFE9DA;
    --gold: #A9603F;
    --line: #e3ddc9;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, 'Segoe UI', sans-serif;
    max-width: 860px;
    margin: 0 auto;
    padding: 0 20px 60px;
    color: var(--ink);
    background: var(--paper);
    line-height: 1.5;
  }}
  header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 26px 0;
    border-bottom: 1px solid var(--line);
    margin-bottom: 34px;
  }}
  header .logo {{
    font-weight: 700;
    font-size: 19px;
    color: var(--ink);
    text-decoration: none;
  }}
  header nav a {{
    color: var(--ink);
    text-decoration: none;
    font-size: 14px;
    margin-left: 22px;
    opacity: 0.75;
  }}
  header nav a:hover {{ opacity: 1; }}

  .hero {{
    background: var(--panel);
    border-radius: 10px;
    padding: 36px 32px;
    margin-bottom: 40px;
  }}
  .hero h1 {{
    font-size: 30px;
    margin: 0 0 10px;
    line-height: 1.2;
  }}
  .hero p {{
    margin: 0;
    font-size: 15px;
    color: #4a463d;
    max-width: 50ch;
  }}

  .band {{ margin-bottom: 30px; }}
  .band h2 {{
    font-size: 15px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--gold);
    margin: 0 0 12px;
  }}
  .chips {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }}
  .chip {{
    display: inline-block;
    padding: 8px 14px;
    border: 1px solid var(--line);
    border-radius: 20px;
    font-size: 14px;
    color: var(--ink);
    text-decoration: none;
    background: var(--paper);
  }}
  .chip:hover {{
    border-color: var(--gold);
    color: var(--gold);
  }}

  footer {{
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px solid var(--line);
    font-size: 13px;
    color: #8a8578;
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
  }}
  footer a {{ color: #8a8578; }}
</style>
</head>
<body>

<header>
  <a class="logo" href="/">{site_name}</a>
  <nav>
    <a href="/about/">About</a>
    <a href="/contact/">Contact</a>
  </nav>
</header>

<div class="hero">
  <h1>What does your salary work out to per hour?</h1>
  <p>Pick your yearly salary below for the full hourly, daily, weekly, and monthly breakdown.</p>
</div>

{bands}

<footer>
  <span>&copy; {site_name}</span>
  <span><a href="/privacy/">Privacy Policy</a></span>
</footer>

</body>
</html>""".format(site_name=SITE_NAME, bands=bands_html)

with open(os.path.join(DIST, "index.html"), "w", encoding="utf-8") as f:
    f.write(hub_html)

# ---- sitemap.xml ----
url_parts = []
for u in sitemap_urls:
    url_parts.append("  <url><loc>{}{}</loc></url>".format(DOMAIN, u))
urls_xml = "\n".join(url_parts)

sitemap = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + urls_xml +
    "\n</urlset>"
)

with open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write(sitemap)

# ---- robots.txt ----
robots = "User-agent: *\nAllow: /\nSitemap: {}/sitemap.xml\n".format(DOMAIN)
with open(os.path.join(DIST, "robots.txt"), "w", encoding="utf-8") as f:
    f.write(robots)

print("Generated {} pages.".format(len(rows)))
