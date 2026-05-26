# Pacific Supply Resources — static site concepts

Three standalone **HTML + CSS** versions for **Pacific Supply Resources (PSR Guam)**, built with **[Bulma](https://bulma.io/)** (v1.0.4 via jsDelivr) and small per-version `css/custom.css` files.

## Pages (each version)

| Page | Purpose |
|------|--------|
| `index.html` | Home / positioning |
| `about.html` | Company story, how you work together |
| `products.html` | Product category hub (links to all six categories) |
| `machinery.html` | Heavy Machinery & Spare Parts |
| `safety.html` | Safety & PPE |
| `site-equipment.html` | Site Equipment |
| `medical.html` | Medical Supplies & Parts |
| `janitorial.html` | Janitorial & Cleaning |
| `industrial-tools.html` | Industrial Tools & Equipment |
| `industries.html` | Sectors served |
| `contact.html` | Address, hours, phones, emails, quote form (static demo) |

All sites use a **fixed light theme** (`color-scheme: light` in CSS and HTML meta) so OS/browser dark mode does not change appearance.

## Versions

| Folder | Direction |
|--------|-----------|
| **`site-v1/`** | Classic corporate: navy gradient hero, light sections, cards, `Source Sans 3` |
| **`site-v2/`** | Editorial minimal: warm paper background, serif display + `DM Sans`, bordered panels, product table |
| **`site-v3/`** | Light industrial: white/amber accents, `Barlow`, high-contrast CTAs |

## How to preview

Open any version’s `index.html` in a browser (double-click or use a static server):

```bash
# optional: from repo root
npx --yes serve .
```

Then open `http://localhost:3000/site-v1/` (or v2 / v3).

## Logos & company relationship

Shared image files live in **`assets/`** at the repo root (sibling to `site-v1/`, `site-v2/`, `site-v3/`):

- `psr guam logo.jpg` — trade identity (**PSR Guam** is the DBA / public name for Pacific Supply Resources Guam)
- `yanco logo.png` — **Yanco Corporation** (parent company)

Each site references them as `../assets/...` (URL-encoded spaces). The **navbar** shows the PSR Guam logo as the home link, with a compact **“A division of”** + Yanco logo on tablet/desktop. The **footer** repeats both logos and a one-line DBA / parent-company note.

If you deploy a single site folder to the web root, **copy `assets/` alongside it** (or adjust image paths) so logos resolve.

**Note:** Quote forms use `action="#"` and do not submit until you wire them (e.g. Formspree, Netlify Forms, or your backend). Fonts and Bulma load from CDNs; an internet connection is required for first paint as written.

## Business copy

Contact details match the public listing for PSR Guam (Harmon Industrial Park, `671-787-4007`, `sales@psrguam.com` / `admin@psrguam.com`). Typos from the old site (e.g. “RESORUCES”, “Saftey”) are corrected in this content.

## Next steps (when you deploy)

- Add real form handling, analytics, and `favicon.ico`
- Add Privacy Policy if you collect personal data
- Optimize images if you add photography (not included here)
