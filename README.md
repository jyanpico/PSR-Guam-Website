# Pacific Supply Resources — PSR Guam website

Static **HTML + CSS** site for **Pacific Supply Resources (PSR Guam)**, built with **[Bulma](https://bulma.io/)** (v1.0.4 via jsDelivr) and `css/custom.css`.

## Pages

| Page | Purpose |
|------|--------|
| `index.html` | Home / positioning |
| `about.html` | Company story, how you work together |
| `products.html` | Product category hub (links to all eight categories) |
| `machinery.html` | Heavy Machinery & Spare Parts |
| `safety.html` | Safety & PPE |
| `site-equipment.html` | Site Equipment |
| `medical.html` | Medical Supplies & Parts |
| `janitorial.html` | Janitorial & Cleaning |
| `industrial-tools.html` | Industrial Tools & Equipment |
| `hotel-supplies.html` | Hotel supplies category |
| `lubricants-coolants.html` | Lubricants & coolants category |
| `industries.html` | Sectors served |
| `contact.html` | Address, hours, phones, emails, quote form (static demo) |

The site uses a **fixed light theme** (`color-scheme: light` in CSS and HTML meta) so OS/browser dark mode does not change appearance.

## How to preview

Open `index.html` in a browser (double-click or use a static server):

```bash
npx --yes serve .
```

Then open `http://localhost:3000/`.

## Logos & company relationship

Image files live in **`assets/`**:

- `psr_guam_logo.jpg` — trade identity (**PSR Guam** is the DBA / public name for Pacific Supply Resources Guam)
- `yanco_logo.png` — **Yanco Corporation** (parent company)

The **navbar** shows the PSR Guam logo as the home link, with a compact **“Yanco Corporation”** text label on tablet/desktop. The **footer** repeats both logos and a one-line DBA / parent-company note.

**Note:** Quote forms use `action="#"` and do not submit until you wire them (e.g. Formspree, Netlify Forms, or your backend). Fonts and Bulma load from CDNs; an internet connection is required for first paint as written.

## Business copy

Contact details match the public listing for PSR Guam (Harmon Industrial Park, `671-787-4007`, sales emails by category). Sales team numbers: `671-687-9394`, `671-688-3288`. Typos from the old site (e.g. “RESORUCES”, “Saftey”) are corrected in this content.

## Next steps (when you deploy)

- Add real form handling, analytics, and `favicon.ico`
- Add Privacy Policy if you collect personal data
- Optimize images if you add photography (not included here)
