import csv
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(ROOT, "template", "page.html")
CSV_PATH = os.path.join(ROOT, "keywords.csv")
DIST = os.path.join(ROOT, "dist")

# ---- EDIT THIS to your real domain before you deploy ----
DOMAIN = "https://hourlybreakdown.com/"

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

# ---- Hub / index page ----
hub_links.sort(key=lambda x: x[0])

list_item_parts = []
for sal, slug in hub_links:
    link = '<li><a href="/salary/{}/">{} a year</a></li>'.format(slug, money0(sal))
    list_item_parts.append(link)
list_items = "\n".join(list_item_parts)

hub_html = (
    "<!DOCTYPE html>\n"
    '<html lang="en"><head><meta charset="UTF-8">\n'
    "<title>Every Salary Conversion - Wage Ledger</title>\n"
       '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<meta name="google-site-verification" content="0idnCI29MrBX-7pPztPKwXOE-f60yuqi5Pskgiza4Tk" />\n'
    "</head><body>\n"
    "</head><body>\n"
    "<h1>Browse every salary conversion</h1>\n"
    "<ul>\n"
    + list_items +
    "\n</ul>\n"
    "</body></html>"
)

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
