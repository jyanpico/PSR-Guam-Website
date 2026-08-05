#!/usr/bin/env python3
"""
PSR Guam website — product catalog builder.

Site structure this generates:
    products.html            8 category tiles                  (hand-written, unchanged)
    <category>.html          subcategory tiles for that category (marker-patched, e.g. machinery.html)
    products/<subcat>.html   the specific products within one subcategory ("choose from a variety")
    products/items/<id>.html a single product's full detail page

Two data sources, because they change at very different rates:
  - data/subcategories.csv  the structural grouping (Bearings & Seals, Filters, ...).
    Rarely changes - edit the file directly (or ask a developer to).
  - data/products.csv       the actual specific items (a SKF bearing, a Makita drill, ...).
    Changes constantly - this is the one meant to be replaced by a live Google
    Sheet via the PRODUCTS_CSV_URL env var (see docs/adding-products.md).
    A subcategory with zero products yet is completely normal and renders a
    "tell us what you need" page instead of an empty grid.

Also writes assets/data/products.json, which powers the on-site search box
(it indexes both subcategories and individual products).

Run locally:
    python3 scripts/build_catalog.py
On Netlify this is the build command (see netlify.toml) so it re-runs on
every deploy.
"""
import csv
import html
import io
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCAL_PRODUCTS_CSV = ROOT / "data" / "products.csv"
LOCAL_SUBCATEGORIES_CSV = ROOT / "data" / "subcategories.csv"
PRODUCTS_JSON = ROOT / "assets" / "data" / "products.json"
PRODUCTS_DIR = ROOT / "products"
ITEMS_DIR = PRODUCTS_DIR / "items"
SUBCATEGORY_TEMPLATE_PATH = ROOT / "templates" / "subcategory.html"
PRODUCT_TEMPLATE_PATH = ROOT / "templates" / "product.html"

SITE_PHONE = "671-787-4007"
SITE_PHONE_TEL = "6717874007"

# Category slugs must match one of these keys exactly in the "category"
# column of both CSVs. Adding a brand-new top-level category later means
# adding an entry here + a matching <slug>.html page + a tile on products.html.
CATEGORIES = {
    "machinery": {"file": "machinery.html", "name": "Heavy Machinery & Spare Parts", "email": "sales@yancocorp.com"},
    "safety": {"file": "safety.html", "name": "Safety & PPE", "email": "sales@yancocorp.com"},
    "site-equipment": {"file": "site-equipment.html", "name": "Site Equipment", "email": "sales@yancocorp.com"},
    "medical": {"file": "medical.html", "name": "Medical Supplies & Parts", "email": "sales@psrguam.com"},
    "janitorial": {"file": "janitorial.html", "name": "Janitorial & Cleaning", "email": "sales@psrguam.com"},
    "hotel-supplies": {"file": "hotel-supplies.html", "name": "Hotel Supplies", "email": "sales@psrguam.com"},
    "lubricants-coolants": {"file": "lubricants-coolants.html", "name": "Lubricants & Coolants", "email": "sales@yancocorp.com"},
    "office-supplies": {"file": "office-supplies.html", "name": "Office Supplies", "email": "sales@psrguam.com"},
}

MARKER_START = "<!-- psr:products:start -->"
MARKER_END = "<!-- psr:products:end -->"


def slugify(text):
    text = text.lower().strip().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def read_csv_rows(local_path, url_env_var):
    csv_url = os.environ.get(url_env_var)
    if csv_url:
        print(f"Fetching {local_path.stem} from {url_env_var}")
        with urllib.request.urlopen(csv_url) as resp:
            raw = resp.read().decode("utf-8-sig")
    else:
        print(f"No {url_env_var} set - using local {local_path.relative_to(ROOT)}")
        raw = local_path.read_text(encoding="utf-8-sig")
    reader = csv.DictReader(io.StringIO(raw))
    return [{(k or "").strip(): (v or "").strip() for k, v in row.items()} for row in reader]


def image_src(filename):
    if not filename:
        return "/assets/products/placeholder.svg"
    if filename.startswith("http://") or filename.startswith("https://"):
        return filename
    return "/assets/products/" + urllib.parse.quote(filename)


def unique_id(base, seen):
    pid, n = base, 2
    while pid in seen:
        pid = f"{base}-{n}"
        n += 1
    seen.add(pid)
    return pid


def build_subcategories(rows):
    subcats = []
    seen_ids = set()
    for i, row in enumerate(rows, start=2):
        if not row.get("name") or not row.get("category"):
            continue
        cat = row["category"]
        if cat not in CATEGORIES:
            print(f"  ! subcategories row {i}: skipping '{row['name']}' - unknown category '{cat}'")
            continue
        sid = unique_id(slugify(f"{cat}-{row['name']}"), seen_ids)
        subcats.append({
            "id": sid,
            "category": cat,
            "categoryName": CATEGORIES[cat]["name"],
            "categoryUrl": f"/{CATEGORIES[cat]['file']}",
            "name": row["name"],
            "description": row.get("description", ""),
            "image": row.get("image", ""),
            "url": f"/products/{sid}.html",
        })
    return subcats


def build_products(rows, subcats):
    # match a product's free-text "subcategory" column to a real subcategory
    # record, scoped within its own category
    by_key = {(sc["category"], sc["name"].strip().lower()): sc for sc in subcats}

    products = []
    seen_ids = set()
    for i, row in enumerate(rows, start=2):
        if not row.get("name") or not row.get("category"):
            continue
        cat = row["category"]
        if cat not in CATEGORIES:
            print(f"  ! products row {i}: skipping '{row['name']}' - unknown category '{cat}'")
            continue

        sub_name = row.get("subcategory", "").strip()
        sc = by_key.get((cat, sub_name.lower())) if sub_name else None
        if sub_name and not sc:
            print(f"  ! products row {i}: '{row['name']}' has subcategory '{sub_name}' "
                  f"which doesn't match any row in subcategories.csv for '{cat}' - listing without one")

        pid = unique_id(slugify(row.get("id") or f"{cat}-{row['name']}"), seen_ids)

        specs = {}
        for part in row.get("specs", "").split(";"):
            part = part.strip()
            if part and ":" in part:
                k, v = part.split(":", 1)
                specs[k.strip()] = v.strip()

        keywords = [k.strip() for k in row.get("keywords", "").split(",") if k.strip()]

        products.append({
            "id": pid,
            "name": row["name"],
            "brand": row.get("brand", ""),
            "category": cat,
            "categoryName": CATEGORIES[cat]["name"],
            "categoryUrl": f"/{CATEGORIES[cat]['file']}",
            "subcategoryId": sc["id"] if sc else None,
            "subcategoryName": sc["name"] if sc else None,
            "subcategoryUrl": sc["url"] if sc else None,
            "description": row.get("description", ""),
            "specs": specs,
            "image": row.get("image", ""),
            "keywords": keywords,
            "url": f"/products/items/{pid}.html",
        })
    return products


def render_subcategory_card(sc):
    return f'''            <div class="column is-4">
              <div class="card category-card">
                <a class="category-card-media" href="{sc['url']}"><img src="{image_src(sc['image'])}" alt="{html.escape(sc['name'])}" loading="lazy"></a>
                <div class="card-content"><p class="card-header-title" style="padding:0"><a href="{sc['url']}">{html.escape(sc['name'])}</a></p><p>{html.escape(sc['description'])}</p></div>
                <footer class="card-footer"><a class="card-footer-item" href="{sc['url']}">View products</a></footer>
              </div>
            </div>'''


def render_product_card(p):
    return f'''            <div class="column is-6-tablet is-4-desktop">
              <a class="product-card-link" href="{p['url']}">
                <article class="product-card">
                  <div class="product-card-media"><img src="{image_src(p['image'])}" alt="{html.escape(p['name'])}" loading="lazy"></div>
                  <div class="product-card-body">
                    <h3 class="product-card-title">{html.escape(p['name'])}</h3>
                    <p class="product-card-desc">{html.escape(p['description'])}</p>
                    <span class="product-card-tag">View details &rarr;</span>
                  </div>
                </article>
              </a>
            </div>'''


def patch_category_pages(subcats_by_category):
    for cat, meta in CATEGORIES.items():
        path = ROOT / meta["file"]
        page = path.read_text(encoding="utf-8")
        items = subcats_by_category.get(cat, [])
        cards = "\n".join(render_subcategory_card(sc) for sc in items) if items else (
            '            <p class="has-text-grey">No subcategories listed yet.</p>'
        )
        block = f"{MARKER_START}\n{cards}\n          {MARKER_END}"

        if MARKER_START in page and MARKER_END in page:
            pre = page.split(MARKER_START)[0]
            post = page.split(MARKER_END)[1]
            new_page = pre + block + post
        else:
            start_tag = '<div class="product-showcase columns is-multiline">'
            end_anchor = '\n          </div>\n\n          <h2 class="title is-4 mt-6">'
            start_idx = page.index(start_tag) + len(start_tag)
            end_idx = page.index(end_anchor, start_idx)
            new_page = page[:start_idx] + "\n" + block + page[end_idx:]

        path.write_text(new_page, encoding="utf-8")
        print(f"  updated {meta['file']} ({len(items)} subcategories)")


def render_subcategory_page(sc, products, template):
    if products:
        grid = "\n".join(render_product_card(p) for p in products)
        products_block = f'''          <h2 class="title is-4 mt-5">Choose from this range</h2>
          <div class="product-showcase columns is-multiline">
{grid}
          </div>'''
    else:
        products_block = '''          <div class="message is-info">
            <div class="message-body">
              We stock a wide variety in this category - specific brands, sizes, and part
              numbers vary by job. Tell us what you need and we'll quote exact matches.
            </div>
          </div>'''

    page = template
    replacements = {
        "%%PAGE_TITLE%%": f"{html.escape(sc['name'])} | Pacific Supply Resources",
        "%%META_DESCRIPTION%%": html.escape(sc["description"] or sc["name"]),
        "%%CATEGORY_NAME%%": html.escape(sc["categoryName"]),
        "%%CATEGORY_URL%%": sc["categoryUrl"],
        "%%SUBCATEGORY_NAME%%": html.escape(sc["name"]),
        "%%DESCRIPTION%%": html.escape(sc["description"]),
        "%%IMAGE_SRC%%": image_src(sc["image"]),
        "%%IMAGE_ALT%%": html.escape(sc["name"]),
        "%%PRODUCTS_BLOCK%%": products_block,
        "%%QUOTE_EMAIL%%": CATEGORIES[sc["category"]]["email"],
        "%%QUOTE_PHONE%%": SITE_PHONE,
        "%%QUOTE_PHONE_TEL%%": SITE_PHONE_TEL,
    }
    for token, value in replacements.items():
        page = page.replace(token, value)
    return page


def render_product_page(p, template):
    if p["brand"]:
        brand_block = f'''
                <p class="heading">Brand</p>
                <p class="mb-4"><strong>{html.escape(p["brand"])}</strong></p>'''
    else:
        brand_block = ""

    if p["specs"]:
        rows = "\n".join(
            f'                    <tr><th>{html.escape(k)}</th><td>{html.escape(v)}</td></tr>'
            for k, v in p["specs"].items()
        )
        specs_block = f'''
                <h2 class="title is-4 mt-5">Specifications</h2>
                <table class="table is-fullwidth is-bordered">
                  <tbody>
{rows}
                  </tbody>
                </table>'''
    else:
        specs_block = ""

    back_url = p["subcategoryUrl"] or p["categoryUrl"]
    back_name = p["subcategoryName"] or p["categoryName"]
    subcat_crumb = (
        f'<li><a href="{p["subcategoryUrl"]}" class="has-text-white-ter">{html.escape(p["subcategoryName"])}</a></li>'
        if p["subcategoryUrl"] else ""
    )

    page = template
    replacements = {
        "%%PAGE_TITLE%%": f"{html.escape(p['name'])} | Pacific Supply Resources",
        "%%META_DESCRIPTION%%": html.escape(p["description"] or p["name"]),
        "%%CATEGORY_NAME%%": html.escape(p["categoryName"]),
        "%%CATEGORY_URL%%": p["categoryUrl"],
        "%%SUBCATEGORY_CRUMB%%": subcat_crumb,
        "%%PRODUCT_NAME%%": html.escape(p["name"]),
        "%%IMAGE_SRC%%": image_src(p["image"]),
        "%%IMAGE_ALT%%": html.escape(p["name"]),
        "%%BRAND_BLOCK%%": brand_block,
        "%%DESCRIPTION%%": html.escape(p["description"]),
        "%%SPECS_BLOCK%%": specs_block,
        "%%BACK_URL%%": back_url,
        "%%BACK_NAME%%": html.escape(back_name),
        "%%QUOTE_EMAIL%%": CATEGORIES[p["category"]]["email"],
        "%%QUOTE_PHONE%%": SITE_PHONE,
        "%%QUOTE_PHONE_TEL%%": SITE_PHONE_TEL,
    }
    for token, value in replacements.items():
        page = page.replace(token, value)
    return page


def write_tree(directory, filenames_to_content):
    directory.mkdir(parents=True, exist_ok=True)
    existing = {f.name for f in directory.glob("*.html")}
    for name, content in filenames_to_content.items():
        (directory / name).write_text(content, encoding="utf-8")
    stale = existing - set(filenames_to_content)
    for name in stale:
        (directory / name).unlink()
    return len(filenames_to_content), len(stale)


def main():
    subcat_rows = read_csv_rows(LOCAL_SUBCATEGORIES_CSV, "SUBCATEGORIES_CSV_URL")
    product_rows = read_csv_rows(LOCAL_PRODUCTS_CSV, "PRODUCTS_CSV_URL")

    subcats = build_subcategories(subcat_rows)
    products = build_products(product_rows, subcats)
    print(f"Loaded {len(subcats)} subcategories and {len(products)} products across {len(CATEGORIES)} categories")

    # 1. search index - subcategories AND products, so "filters" finds the
    #    subcategory tile even before any specific filter SKU is listed.
    search_entries = []
    for sc in subcats:
        search_entries.append({
            "type": "subcategory",
            "name": sc["name"],
            "brand": "",
            "category": sc["category"],
            "categoryName": sc["categoryName"],
            "description": sc["description"],
            "image": sc["image"],
            "keywords": [],
            "url": sc["url"],
        })
    for p in products:
        search_entries.append({
            "type": "product",
            "name": p["name"],
            "brand": p["brand"],
            "category": p["category"],
            "categoryName": p["categoryName"],
            "description": p["description"],
            "image": p["image"],
            "keywords": p["keywords"],
            "url": p["url"],
        })
    PRODUCTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    PRODUCTS_JSON.write_text(json.dumps(search_entries, indent=2), encoding="utf-8")
    print(f"  wrote {PRODUCTS_JSON.relative_to(ROOT)} ({len(search_entries)} searchable entries)")

    # 2. subcategory tiles on each category page
    subcats_by_category = {}
    for sc in subcats:
        subcats_by_category.setdefault(sc["category"], []).append(sc)
    patch_category_pages(subcats_by_category)

    # 3. one page per subcategory, listing whatever products are in it
    products_by_subcat = {}
    for p in products:
        if p["subcategoryId"]:
            products_by_subcat.setdefault(p["subcategoryId"], []).append(p)

    subcat_template = SUBCATEGORY_TEMPLATE_PATH.read_text(encoding="utf-8")
    subcat_pages = {
        f"{sc['id']}.html": render_subcategory_page(sc, products_by_subcat.get(sc["id"], []), subcat_template)
        for sc in subcats
    }
    written, stale = write_tree(PRODUCTS_DIR, subcat_pages)
    # don't let the stale-file sweep touch products/items/
    print(f"  wrote {written} subcategory pages to products/ ({stale} stale pages removed)")

    # 4. one page per product
    product_template = PRODUCT_TEMPLATE_PATH.read_text(encoding="utf-8")
    product_pages = {f"{p['id']}.html": render_product_page(p, product_template) for p in products}
    written, stale = write_tree(ITEMS_DIR, product_pages)
    print(f"  wrote {written} product pages to products/items/ ({stale} stale pages removed)")

    print("Done.")


if __name__ == "__main__":
    main()
