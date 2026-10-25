# Stack Selection — {{App name}}

> Owner: solution-architect · Gate G2 · Score 1–5 per criterion; weights sum to 100.

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

## Recommendation & rationale
## Rejected options and why
## Environment impact (what runs on Mac vs Windows)
