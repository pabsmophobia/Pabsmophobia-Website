# Pabsmophobia Site Context & Style Guide

## Overview & Philosophy
Pabsmophobia is an independent paranormal research and event group. The site serves as a public hub for commercial ghost hunts, investigation write-ups, event schedules, and team methodology. 

The primary design philosophy is a **spectral, high-contrast dark theme** that balances atmospheric gothic elements with clean, modern UI performance.

---

## Technical Stack & Configuration
* **Hosting & Automation:** GitHub Pages (Deploys automatically on push to `main` branch).
* **Styling:** Modular CSS using CSS Custom Properties defined in `styles.css`.
* **Markdown Parser:** Custom frontend renderer using the `#markdown-content` container for dynamic post rendering.

---

## Design System & Theme Variables
All UI components and additions must adhere strictly to these CSS variables defined in `:root`:

```css
:root {
  --bg-color: #0a0a0c;
  --card-bg: #141419;
  --text-main: #d1d5db;
  --text-muted: #9ca3af;
  --accent: #8b5cf6;       /* Soft Purple Accent */
  --accent-hover: #a78bfa;
  --border: #27272a;
  --font-title: 'Creepster', cursive;
  --font-body: 'Eczar', serif;
}
Pabsmophobia Site Context & Style Guide
Overview & Philosophy
Pabsmophobia is an independent paranormal research and event group. The site serves as a public hub for commercial ghost hunts, investigation write-ups, event schedules, and team methodology.

The primary design philosophy is a spectral, high-contrast dark theme that balances atmospheric gothic elements with clean, modern UI performance.

Technical Stack & Configuration
Hosting & Automation: GitHub Pages (Deploys automatically on push to main branch).

Styling: Modular CSS using CSS Custom Properties defined in styles.css.

Markdown Parser: Custom frontend renderer using the #markdown-content container for dynamic post rendering.

Design System & Theme Variables
All UI components and additions must adhere strictly to these CSS variables defined in :root:

:root {
--bg-color: #0a0a0c;
--card-bg: #141419;
--text-main: #d1d5db;
--text-muted: #9ca3af;
--accent: #8b5cf6;       /* Soft Purple Accent */
--accent-hover: #a78bfa;
--border: #27272a;
--font-title: 'Creepster', cursive;
--font-body: 'Eczar', serif;
}

Color Conventions & Badges
Pabsmophobia Events / Primary Accent: Soft Purple (#8b5cf6 / #c084fc)

Haunting Nights Events: Blue tint (#60a5fa)

Ancient Ram Inn Events: Red tint (#f87171)

Evidence Status - Paranormal: Amber (#fbbf24) with glow effect

Evidence Status - Debunked: Slate Gray (#cbd5e1)

Layout & Typography Rules
Headings: Use --font-title ('Creepster') for headers (h1, h2, h3, .section-title, .logo).

Body Text: Use --font-body ('Eczar') for all standard content, lists, and paragraphs.

Scaffolding: Content sections use .container (max-width 900px). Tables must always be wrapped inside .table-responsive to guarantee mobile responsiveness.

Site Features & Modules
1. Evidence Vault Filters
Filter buttons use dynamic attribute selectors:

[data-filter="all"]

[data-filter="paranormal"]

[data-filter="debunked"]

2. Brevo Newsletter Form Integration
Embedded forms must retain transparent/dark background overrides using !important flags inside #sib-container to maintain the #141419 dark card aesthetic.

3. Responsive Header & Navigation
Logo height switches automatically on mobile screens (max-width: 768px).

Navigation flexes into a wrapped menu layout on smaller viewports.

AI Execution Directives
When updating or adding code to this repository:

Maintain clean, readable HTML/CSS without introducing inline styling where CSS classes exist.

Do not overwrite existing root color variables.

Always wrap data tables in responsive containers.

Keep all new component styles scoped inside styles.css.
