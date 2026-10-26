---
name: kb-angular-web
description: Angular team conventions - Angular CLI workspace, SPA or @angular/ssr (SSR, prerendering, hydration), standalone components, signals, typed reactive forms, HttpClient interceptors and functional guards, Angular Material/CDK or PrimeNG, testing with ng test, Testing Library and Playwright, and common pitfalls.
user-invocable: false
---

# Angular conventions

## Setup
- Current Angular major from angular.dev (check the release and support schedule; pin versions, commit the lockfile). Strict mode, standalone components only, no NgModules in new code.
- Per the surface's rendering ADR (`kb-web-frontend`): SPA for surfaces behind login; `@angular/ssr` with prerendering and/or SSR, incremental hydration where available, for public or SEO-relevant surfaces. Several surfaces may share one Angular workspace (`projects/`) when `repo-layout.md` says so.
- Use the new-project defaults of that version for change detection (zoneless where it is the default) and the test runner (Vitest in recent versions; existing projects may use Karma/Jasmine — keep theirs). Verify on angular.dev rather than assuming.
- Layout: `src/app/{core (auth, http, guards, layout), shared (design-system components, pipes), features/<area>/{pages,components,data-access,model}}`, `src/environments/`, `src/styles/` (tokens).

## Patterns
- State: signals (`signal`, `computed`, `linkedSignal`; `effect` sparingly) for component and feature state; `resource`/`httpResource` or RxJS services for server data; `toSignal` at the edge. NgRx SignalStore only for shared complex state (ADR).
- Templates: built-in control flow (`@if`, `@for` with `track`, `@defer` for heavy or below-the-fold widgets), `OnPush` everywhere, `inject()` over constructor injection, `NgOptimizedImage` for images.
- Routing: lazy `loadComponent`/`loadChildren`; functional `CanActivateFn` guards mirrored by server checks; component input binding for route params; filters in query params. SSR: per-route render mode (prerender / server / client) in the server routes config.
- SEO: `Title` and `Meta` services per route, canonical links; `TransferState`/HTTP transfer cache to avoid double fetching after hydration.
- HTTP: functional interceptors for auth, error mapping and a request id; typed client generated from the OpenAPI contract (`openapi-typescript` or `ng-openapi-gen`).
- Forms: typed reactive forms (`nonNullable`), validators mirroring the API schema, server errors mapped to controls.
- UI library (one per ADR): Angular Material + CDK or PrimeNG, themed from the design tokens; Tailwind allowed alongside. Charts: ECharts (`ngx-echarts`). Animations: CSS / Angular animations with motion tokens. i18n: Angular i18n (build-time) or Transloco (runtime) per ADR. PWA: `@angular/pwa`.

## Quality commands
`npx ng lint` (angular-eslint), `npx ng test` (add `--watch=false` where the runner needs it), `npx playwright test` (from `tests/web-e2e/`), `npx ng build`. Type errors surface in `ng build`/`ng test`; `npx tsc -p tsconfig.app.json --noEmit` for a quick typecheck.

## Pitfalls
- Manual `subscribe` without teardown → leaks; use `takeUntilDestroyed`, the `async` pipe or signals.
- Browser globals (`window`, `localStorage`) during SSR → `afterNextRender`, `isPlatformBrowser`, or inject tokens; hydration errors from DOM manipulation outside Angular.
- `bypassSecurityTrustHtml` / `[innerHTML]` with untrusted data defeats the sanitizer → XSS.
- Writing signals inside `computed`/`effect` → loops; derive with `computed`.
- Default change detection and untracked `@for` on big lists → OnPush, `track` by id, CDK virtual scroll.
- `environment.ts` is bundled and public: no secrets there.
