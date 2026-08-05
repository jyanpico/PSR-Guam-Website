# Adding products — how it works

Products live in a Google Sheet, not in the website's code. Anyone with
edit access to that sheet can add a product; no coding, no logins to
GitHub or Netlify required for that part.

Every product also needs a **category** and a **subcategory** ("Bearings
& Seals", "Filters", ...). Subcategories are the more permanent, rarely-
changing structure of the site and live in `data/subcategories.csv` —
ask a developer to add a new one, or edit that file directly. Products
are the fast-changing part and are what the Sheet below is for. A
subcategory with no products in it yet just shows a "tell us what you
need" message instead of an empty page, so it's fine to leave most of
them empty for now.

## One-time setup (you or a developer does this once)

1. **Create the Google Sheet.** Import `data/products.csv` into a new
   Google Sheet (Google Sheets → File → Import → Upload → pick the
   file) so the column headers match exactly:

   | id | name | brand | category | subcategory | description | specs | image | keywords |
   |----|------|-------|----------|--------------|--------------|-------|-------|----------|

   The file already has one "Sample Product (replace this row)" example
   per category — delete each once you add a real product in that spot.

   - `id` — leave blank; the site generates one automatically.
   - `category` — must be exactly one of: `machinery`, `safety`,
     `site-equipment`, `medical`, `janitorial`, `hotel-supplies`,
     `lubricants-coolants`, `office-supplies`.
   - `subcategory` — must match the name of one of the tiles on that
     category's page exactly (e.g. `Bearings & Seals`, `Filters`). If it
     doesn't match anything, the build log will flag it and the product
     just won't have a subcategory link, so this is safe to get wrong.
   - `specs` — optional. `Key: Value` pairs separated by semicolons,
     e.g. `Bore: 25mm; OD: 52mm; Width: 15mm`.
   - `image` — see **Adding images** below. Leave blank to use a
     "photo coming soon" placeholder.
   - `keywords` — optional search aliases, comma-separated, e.g.
     `bearing, 6205, skf, sealed bearing`. This is what makes brand and
     part-number search work well.

2. **Publish the sheet as CSV**: File → Share → Publish to web → choose
   the products tab → format **CSV** → Publish → copy the URL.

3. **Connect it to the site**: in Netlify, Site settings → Environment
   variables → add `PRODUCTS_CSV_URL` = that URL. (One-time; already
   wired into `netlify.toml` as the build command.)

4. **Create a "Publish" button**: Netlify → Site settings → Build &
   deploy → Build hooks → Add build hook → name it "Publish products" →
   copy the URL it gives you. Bookmark that URL somewhere handy (or set
   it up as a custom menu item in the Sheet — see below).

## Every time someone wants to add or edit a product

1. Open the Google Sheet, add a new row (or edit an existing one).
2. Click the bookmarked **"Publish products"** link (the build hook
   URL from step 4 above).
3. Wait about a minute — Netlify rebuilds the site: pulls every row
   from the sheet, generates a real static page for each product,
   updates the matching subcategory page, and refreshes the search
   index. The new product is now live, browsable, and searchable.

That's the whole workflow — no code, no git, no CMS login. Bad or
incomplete rows are skipped automatically (with a note in the Netlify
build log) instead of breaking the site, so a typo in one row is safe.

## Adding images

Two options, from easiest to most "official":

**Option A — paste a link, no repo access needed (recommended).**
Upload the photo somewhere that gives you a direct public link, then
paste that full link into the sheet's `image` column instead of a
filename.
- **Imgur** (imgur.com) — no account needed, drag-and-drop the photo,
  copy the "Direct Link" it gives you (ends in `.jpg`/`.png`). This is
  the simplest option.
- **Google Drive** — upload the photo, right-click → Share → "Anyone
  with the link", then rewrite the link it gives you: take the file ID
  out of `https://drive.google.com/file/d/FILE_ID/view` and use
  `https://drive.google.com/uc?export=view&id=FILE_ID` instead — the
  plain share link won't work, it opens a preview page, not the image.

**Option B — upload straight into the repo.**
On github.com, open the repo → `assets/products/` folder → "Add file" →
"Upload files" → drag the photo → commit. Then just type that exact
filename (e.g. `bearings-6205.jpg`) into the sheet's `image` column,
same as the 56 sample photos already there. No coding, but does need a
GitHub login.

Leave the column blank to show a neutral "photo coming soon" graphic
instead — better than a broken image link.

## Optional: one-click publish from inside the Sheet

Instead of a bookmark, you can add a menu button inside the spreadsheet
itself. In the Sheet: Extensions → Apps Script, paste this, replace the
URL, and save:

```javascript
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('PSR Website')
    .addItem('Publish changes', 'publishSite')
    .addToUi();
}

function publishSite() {
  UrlFetchApp.fetch('PASTE_YOUR_BUILD_HOOK_URL_HERE', { method: 'post' });
  SpreadsheetApp.getUi().alert('Publishing... the site will update in about a minute.');
}
```

Reload the Sheet and a **PSR Website → Publish changes** menu appears —
so editors never have to leave the spreadsheet tab.

## Local preview (for developers)

```bash
python3 scripts/build_catalog.py   # regenerates everything from the two CSVs in data/
python3 -m http.server 8000        # serve the site locally
```

Then open `http://localhost:8000`. (Search and product pages need a
real HTTP server — they won't work if you just double-click an HTML
file, because of the absolute `/assets/...` paths.)
