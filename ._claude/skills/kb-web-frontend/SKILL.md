---
name: kb-web-frontend
description: Shared rules for every web frontend the company builds - surface types (marketing site, web app / PWA, customer portal, dashboard, admin console) and their rendering mode, apps/web/<surface>/ layout, data access from the API contract, security, Core Web Vitals budget, SEO, accessibility, i18n, consent, links with the mobile app, testing with Playwright and hosting. Used by the frontend teams (React, Vue, Angular), the architect, QA and Cyber Security.
user-invocable: false
---

# Web frontend engineering

## Surfaces and rendering
Each web frontend is a **surface** with its own folder `apps/web/<surface>/` (owned by the frontend team the architect assigns; in a takeover, the path in `takeover.owners`). Pick the rendering mode per surface and record it in an ADR:

| Surface | Typical content | Default rendering |
|---|---|---|
| `site` | landing / marketing site, blog, docs, legal and support pages, store badges | static generation (SSG), SSR only for dynamic pages |
| `app` | web version of the product, PWA, companion app | SPA behind login; SSR when public pages need SEO or fast first paint |
| `portal` | customer account: profile, subscription, data export, account deletion web link | SPA or SSR |
| `dashboard` | analytics, partner or creator dashboards | SPA |
| `admin` | back office for operators (also read `.claude/skills/kb-web-admin/SKILL.md`) | SPA, `noindex` |

- Meta-frameworks: React → Next.js, Vue → Nuxt, Angular → `@angular/ssr`. Plain Vite / Angular CLI SPA when no server rendering is needed. A static site generator (e.g. Astro) only with an ADR.
- A meta-framework's server (route handlers, server actions, Nitro routes) is a thin backend-for-frontend at most: business logic, data rules and privileged keys stay in `services/`.
- Stories for a surface carry `surface: <name>` in `docs/02-product/user-stories.md`; features carry `"platforms": ["web:<surface>"]` in `state/feature_list.json`.
- Several surfaces may share a design-system package and generated API types (`packages/` per `repo-layout.md`).

## Layout (inside each surface; the framework skill adds details)
`src/app` or the framework's routing folder (routes, layouts, providers), `src/features/<area>/` (pages, components, data hooks/services, model), `src/design-system/` (tokens, wrapped components), `src/lib/` (api client, auth, i18n, formatting, analytics), `src/test/` (fixtures, MSW handlers). E2E specs live in `tests/web-e2e/<surface>/` (test-automation-engineer).

## Data access
- Generate clients and types from `docs/05-architecture/api-contract/` (OpenAPI → `openapi-typescript`/`orval`; Supabase → `supabase gen types`; Firebase → shared TS types). Never hand-write request shapes; if the contract lacks something, ask the architect.
- Server state through the framework's query/cache layer; invalidate after writes; optimistic updates only with a defined rollback. Lists paginate, sort and filter on the server.

## Security (Cyber Security tests these)
- Everything shipped to the browser is public: `VITE_*`, `NEXT_PUBLIC_*`, Nuxt `runtimeConfig.public`, Angular `environment.ts`, source maps. No secrets, service-role or admin keys there; keep server-only config on the server side of the meta-framework.
- Authorization is decided by the backend (claims / RLS / Rules). Route guards are UX.
- Sessions: httpOnly, `Secure`, `SameSite` cookies preferred; if an SDK keeps tokens in browser storage, keep CSP strict and sessions short. CSRF protection for cookie sessions.
- No unsanitized HTML sinks (`dangerouslySetInnerHTML`, `v-html`, `bypassSecurityTrust*`) without DOMPurify and an ADR.
- Headers at the host: CSP, `frame-ancestors`, HSTS, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`.

## Performance budget
- Core Web Vitals "good" at the 75th percentile of page loads, mobile and desktop separately: LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1. Source: https://web.dev/articles/vitals, accessed 2026-10-26.
- Route-level code splitting, responsive images (`srcset`, AVIF/WebP, explicit size), self-hosted fonts with `font-display: swap`, no layout shift when data or ads load, bundle size reported per build.
- Lighthouse (CI or `npx lighthouse`) on key pages of public surfaces; budgets in the surface's README.

## SEO (public surfaces only)
Unique `<title>` and meta description per page, canonical URLs, Open Graph / Twitter cards, `sitemap.xml`, `robots.txt`, structured data where it fits (`SoftwareApplication`, `FAQPage`, `Article`), localized pages with `hreflang`. Private surfaces send `noindex`.

## Accessibility and i18n
- WCAG 2.2 AA: semantic HTML first, labels, keyboard access, visible focus, focus management on route change and in dialogs, contrast in light and dark, `prefers-reduced-motion`.
- Languages from the brief; message catalogs, never concatenated strings; locale-aware dates, numbers and currency; RTL if a target language needs it.

## Consent, analytics and the mobile app
- Cookie/analytics consent follows `docs/04-design/consent-requirements.md` (privacy-legal-counsel); no tracking before consent where the law requires it. Events follow `docs/02-product/tracking-plan.md`.
- Deep links: the `site` (or the app domain) serves `/.well-known/apple-app-site-association` and `/.well-known/assetlinks.json` from the architect's values; store badges and smart app banners link to the listings.
- Purchases on the web that the app links to or mentions are subject to App Store / Google Play rules: store-compliance-officer reviews those flows before they ship.

## Testing and evidence
- Unit/component: Vitest (or the framework's runner) + Testing Library, MSW or fakes for the API.
- E2E: Playwright in `tests/web-e2e/<surface>/` against the local backend/emulators with seeded data; selectors by role/label, then `data-testid`; no fixed waits. Accessibility scan with `@axe-core/playwright` on key pages.
- UI evidence: screenshots in `docs/07-qa/evidence/<feature-id>/` at 390 px, 768 px and 1280 px, light and dark.
- Web work builds and tests on both machines (Node only): never tag it `needs: mac|windows`.

## Hosting and environments
- Free-tier hosting the architect picks per surface (Firebase Hosting, Cloudflare Pages, Netlify, Vercel, or the backend's server/CDN); static or SSR runtime as the rendering mode requires. Preview/staging deploys per environment; config from build or runtime env documented in `docs/05-architecture/secrets.md`.
- SPA fallback routing, cache-busted assets, `index.html` and SSR responses not cached at the edge unless designed to be.
- Staging and preview deploys are fine; **production deploys are PO-only** (golden rule 7). devops-engineer owns pipelines and domains.
