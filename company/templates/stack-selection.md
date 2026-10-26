# Stack Selection — {{App name}}

> Owner: solution-architect · Gate G2 · Score 1–5 per criterion; weights sum to 100 in each table.

## Mobile stack
| Criterion | Weight | React Native | Flutter | Swift + Kotlin (native) |
|---|---|---|---|---|
| Fit to required native capabilities (camera, audio, widgets, background, AR, health…) | 20 | | | |
| UI richness & motion needed by the design | 15 | | | |
| Both platforms needed? time-to-market | 15 | | | |
| Performance needs (audio latency, heavy animation, on-device ML) | 15 | | | |
| Library ecosystem for required features (IAP, ads, AI SDKs, maps…) | 10 | | | |
| Build/test feasibility on our machines (Mac: Xcode+Flutter; Windows: Android toolchain) without paid EAS | 10 | | | |
| Long-term maintenance by AI agents | 10 | | | |
| Store-compliance risk (privacy manifests, SDK support) | 5 | | | |
| **Weighted total** | 100 | | | |

## Backend
| Option | When it fits | Score / notes |
|---|---|---|
| None (local-only) | no sync, no accounts | |
| Firebase | realtime, auth, push, analytics, fast MVP | |
| Supabase | relational data, SQL, row-level security, open-source | |
| Custom server — Node.js / Python / Go | complex domain logic, AI orchestration, data pipelines, 3rd-party integrations | |
| BaaS + custom server (hybrid) | BaaS for auth/data + server for AI/LLM proxy or heavy logic | |

## Web surfaces (from the PRD's "Web surfaces" section; rules in `kb-web-frontend`)
| Surface | Needed for MVP? (or covered by a hosted tool / console) | Rendering (SSG / SSR / SPA) | Framework + meta-framework | Owner | Folder |
|---|---|---|---|---|---|
| site | | | | | `apps/web/site/` |
| app | | | | | `apps/web/app/` |
| portal | | | | | `apps/web/portal/` |
| dashboard | | | | | `apps/web/dashboard/` |
| admin | | | | | `apps/web/admin/` |

Framework scores (one table for all surfaces; score a surface separately only if it would pick a different framework):

| Criterion | Weight | React (Vite / Next.js) | Vue (Vite / Nuxt) | Angular (SPA / SSR) |
|---|---|---|---|---|
| Fits the surfaces' rendering needs (SEO and first paint for public pages, rich interactivity for apps) | 20 | | | |
| Shared code with the mobile app (types, schemas, tokens, API client; React pairs with React Native) | 15 | | | |
| Ecosystem for the needed features (data grids, forms, charts, i18n, PWA, CMS/MDX) | 15 | | | |
| Security model fits (no secrets in bundles, server-side authorization, SSR attack surface) | 10 | | | |
| Long-term maintenance by AI agents and the PO's future team | 15 | | | |
| Customer or team convention (takeover: the existing web code's framework) | 15 | | | |
| Hosting cost and build time (static vs SSR runtime) | 10 | | | |
| **Weighted total** | 100 | | | |

Owners: `frontend-react-engineer` / `frontend-vue-engineer` / `frontend-angular-engineer`, recorded in `state/project.json → stack.web` as `{"<surface>": "<framework>/<meta-framework or vite>"}`.

## Recommendation & rationale
## Rejected options and why
## Environment impact (what runs on Mac vs Windows)
