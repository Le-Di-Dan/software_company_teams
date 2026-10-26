---
name: kb-react-web
description: React web team conventions - Vite SPA or Next.js (App Router, server components, SSG/SSR), TypeScript, routing, TanStack Query/Table, forms with react-hook-form + zod, styling and component libraries, animation, testing with Vitest, Testing Library, MSW and Playwright, and common pitfalls.
user-invocable: false
---

# React (web) conventions

## Setup
- TypeScript strict. Per the surface's rendering ADR (`kb-web-frontend`):
  - **Next.js (App Router)** for public or SEO-relevant surfaces (`site`, public parts of `app`) and wherever SSR/SSG/ISR helps.
  - **Vite + React SPA** for surfaces behind login (`admin`, `dashboard`, most `portal`/`app`).
- Check the current React, Next.js, Vite and router majors on official docs before init; pin versions, commit the lockfile. Alias `@/` → `src/`.
- When the mobile app is React Native, share types, zod schemas, tokens and the API client through the package in `repo-layout.md`; never import RN modules into web code.

## Patterns
- **Next.js**: Server Components by default; `"use client"` only on interactive leaves. Data fetching in server components or route loaders with explicit caching/revalidation; `generateStaticParams` + `generateMetadata` for static and SEO pages; `next/image`, `next/font`. Server-only modules marked with `server-only`; only `NEXT_PUBLIC_*` reaches the browser. Route handlers / server actions as a thin BFF only.
- **SPA routing**: TanStack Router (type-safe search params) or React Router data routers; route-level `lazy()`; guards in loaders/`beforeLoad`, mirrored by server checks.
- Server state: TanStack Query (keys per resource, invalidate after mutations). Client state: component state, context, or Zustand; Redux only with an ADR.
- Tables: TanStack Table (headless, server-side modes). Forms: react-hook-form + zod resolver with schemas shared with the API types.
- Styling: Tailwind with tokens in the theme, or CSS Modules; one approach per surface. Component library (one per ADR): shadcn/ui on Radix (own the components), MUI, Mantine or Ant Design; wrap in `src/design-system/`.
- Motion: Motion (Framer Motion) or CSS transitions with motion tokens; respect reduced motion. Charts: Recharts or ECharts. Icons: one family (Lucide or Material Symbols).
- i18n: next-intl (Next.js) or react-i18next / FormatJS (SPA).
- PWA (if in scope): `vite-plugin-pwa` or the Next.js manifest + a service worker with an explicit update strategy.

## Quality commands
`npx tsc --noEmit`, `npx eslint .` (typescript-eslint, react-hooks, jsx-a11y; plus `eslint-config-next` on Next.js), `npx vitest run` (Testing Library + MSW), `npx playwright test` (from `tests/web-e2e/`), `npx next build` or `npx vite build`.

## Pitfalls
- `useEffect` for data fetching or derived state → query cache, server components, or compute during render.
- Hydration mismatches from `Date.now()`, `Math.random()`, locale or `window` during render → render on the client after mount or pass the value from the server.
- Importing a server-only module (DB client, secrets) into a client component leaks it into the bundle.
- Unstable query keys or inline objects in deps → refetch loops; large lists without virtualization (TanStack Virtual).
- `dangerouslySetInnerHTML` without DOMPurify → XSS.
- Strict Mode double-invokes effects in dev; effects must be idempotent.
