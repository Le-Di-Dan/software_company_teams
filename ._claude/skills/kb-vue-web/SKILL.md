---
name: kb-vue-web
description: Vue web team conventions - Vue 3 with script setup and TypeScript, Vite SPA or Nuxt (SSR/SSG), Vue Router, Pinia, TanStack Query for Vue, forms with VeeValidate + zod, styling and component libraries, testing with Vitest, Vue Test Utils, Testing Library and Playwright, and common pitfalls.
user-invocable: false
---

# Vue (web) conventions

## Setup
- Vue 3, TypeScript strict, Composition API with `<script setup lang="ts">` only. Per the surface's rendering ADR (`kb-web-frontend`):
  - **Nuxt** for public or SEO-relevant surfaces and wherever SSR/SSG/hybrid rendering helps (`routeRules` per route: prerender, SSR, SWR, SPA).
  - **Vite + Vue SPA** (`npm create vue@latest` with TypeScript, Router, Pinia, Vitest, Playwright, ESLint) for surfaces behind login.
- Check the current Vue, Nuxt, Vite and Vue Router versions on official docs before init; pin versions. Alias `@/` → `src/` (Nuxt: its own `~`).

## Patterns
- **Nuxt**: file-based routing, layouts and middleware; data with `useFetch`/`useAsyncData` (keyed, SSR-safe) — not `onMounted` fetches; `useHead`/`useSeoMeta` for SEO; `@nuxt/image`, `@nuxt/fonts`; `runtimeConfig` keeps secrets server-side, only `runtimeConfig.public` reaches the browser; `server/api` as a thin BFF only.
- **SPA routing**: Vue Router with lazy routes; guards in `beforeEach` using `meta.roles`, mirrored by server checks; filters in `route.query`.
- Server state: TanStack Query for Vue (`@tanstack/vue-query`) or Pinia Colada; client state: small Pinia setup stores per domain; no server data copied into Pinia.
- Reusable logic in composables (`useXxx`) returning refs; VueUse for browser utilities.
- Forms: VeeValidate + zod (`@vee-validate/zod`), schemas shared with the API types.
- Styling: Tailwind or scoped CSS / CSS modules with token variables. Component library (one per ADR): PrimeVue, Element Plus, Naive UI, Vuetify or Nuxt UI; wrap in `src/design-system/`. Charts: ECharts (`vue-echarts`). Motion: `<Transition>` / `@vueuse/motion` with motion tokens.
- i18n: vue-i18n / `@nuxtjs/i18n` with typed keys. PWA: `vite-plugin-pwa` / `@vite-pwa/nuxt`.

## Quality commands
`npx vue-tsc --noEmit` (or `npx nuxi typecheck`; plain `tsc` does not check `.vue` files), `npx eslint .` (eslint-plugin-vue, typescript-eslint, vuejs-accessibility), `npx vitest run` (Vue Test Utils or `@testing-library/vue` + MSW; `@nuxt/test-utils` on Nuxt), `npx playwright test` (from `tests/web-e2e/`), `npx vite build` or `npx nuxi build`.

## Pitfalls
- Destructuring a reactive object or Pinia store loses reactivity → `toRefs` / `storeToRefs`.
- Hydration mismatches from browser-only APIs or time/locale during SSR → `<ClientOnly>`, `onMounted`, or values from the server.
- Shared state in module scope on the Nuxt server leaks between requests → `useState` or Pinia.
- `v-html` with untrusted data → XSS; sanitize with DOMPurify or don't.
- Deep watchers on large lists → watch a computed key; `shallowRef` for big read-only data. `v-if` with `v-for` on one element; missing `:key`.
- Mutating props → emit an update (`defineModel` for two-way bindings).
