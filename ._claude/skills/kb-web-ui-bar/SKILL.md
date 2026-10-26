---
name: kb-web-ui-bar
description: The production UI quality bar for web frontends - pass/fail checks for identity, responsive layout, states, motion, accessibility and perceived speed, plus surface-specific checks for marketing sites, web apps and portals. Used by the frontend teams, UI designer, UI/UX R&D and QA.
user-invocable: false
---

# Web production UI bar

Generic AI-built web UIs fail the same way as mobile ones: default fonts and blue buttons, centered card grids, a hero that says nothing, no states, no brand. Each item is **pass/fail**; a FAIL on a key page (home/landing, sign-in, the core flow, pricing/checkout) is a major defect. The brand comes from `docs/04-design/design-system.md`, shared with the mobile app.

## 1. Identity
- [ ] Brand palette, type scale and visual motif from the design system, light and dark; not framework defaults.
- [ ] Favicon set, social share image, page titles consistent with the brand.

## 2. Layout and responsiveness
- [ ] Works from 360 px to 1920 px with deliberate breakpoints (e.g. 640 / 768 / 1024 / 1280 / 1536); no horizontal scroll, no clipped text, readable line length (≤ 75 characters for body text).
- [ ] One obvious primary action per page; consistent spacing scale and grid.
- [ ] Touch targets ≥ 44 px on touch screens; hover-only affordances have a touch alternative.

## 3. Components and states
- [ ] Interactive elements have hover, focus-visible, active, disabled and loading states.
- [ ] Every data view has loading (skeletons), empty (explanation + action), error (cause + retry) and success states; no raw error codes.
- [ ] Forms: labels, inline validation, preserved input on error, clear submit feedback.
- [ ] One icon family, consistently sized.

## 4. Motion
- [ ] Purposeful transitions with durations/easing from motion tokens; no animation blocks input.
- [ ] `prefers-reduced-motion` respected.

## 5. Accessibility
- [ ] WCAG 2.2 AA contrast in both themes; keyboard-only use of every flow; focus visible and managed in dialogs and on route change; landmarks and headings in order; text scales to 200% without loss.
- [ ] axe scan of key pages: no serious or critical violations.

## 6. Perceived speed
- [ ] Core Web Vitals budget from `kb-web-frontend` met on key pages; no layout shift on load; instant feedback on clicks; cached navigation.

## 7. Content
- [ ] Real copy from `docs/04-design/copy.md` in every language; no lorem ipsum or "Item 1"; dates, numbers and currency localized.

## Surface checks
- **site (marketing/landing)**: the hero states the value in one sentence with a primary CTA (store badges or sign-up) above the fold at 390 px and 1280 px; real product screenshots; social proof only if real; pricing clear; legal, privacy and support links in the footer; share previews render.
- **app / portal / dashboard**: persistent navigation showing where you are; deep-linkable URLs (filters, tabs, selected item); unsaved-changes guard; session expiry handled without losing work; PWA (if in scope): installable, offline page, update prompt.
- **admin**: the Admin UI bar in `kb-web-admin`.

## Review output format
`| # | Item | PASS/FAIL | Page(s) / viewport | Evidence (screenshot path / spec ref) | Fix |`
