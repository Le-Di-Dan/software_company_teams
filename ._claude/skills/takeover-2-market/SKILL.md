---
name: takeover-2-market
description: Takeover T2 - market, competitor and monetization research seen through the existing app - who the app competes with, what their users complain about, where this app can win, how it should be priced and found in the stores. Use after takeover discovery (T1).
---

# Takeover T2 — Market & positioning

Precondition: `docs/t1-discovery/summary.md` exists. The question is not "is there a market for an app like this" in general: it is **can this app, as it is and as it could be, win a paying segment**.

Common brief inputs: the engagement brief, `docs/t1-discovery/summary.md`, `docs/t1-discovery/walkthrough.md` (what the app is), `docs/t1-discovery/product.md`. Template `company/templates/research-report.md`. Sources with URLs and access dates (golden rule 3). Market and monetization findings also go to `state/findings.json` (tracks MKT and MON) per `kb-legacy-audit`.

## Wave A (parallel)
| Agent | Output | Focus |
|---|---|---|
| market-researcher | `docs/t2-market/market.md` | Segment size and growth, with sources. The 5–8 direct competitors (store pages, ratings, installs, last update), what each does best, and **review mining**: the 1–2-star complaints that this app could answer. A feature and quality comparison against the walkthrough. |
| uiux-rnd-researcher | `docs/t2-market/competitor-ux.md` | A teardown of the top 3–4 competitors: first run, core loop, paywall moment, visual quality, compared screen by screen with ours. |
| aso-marketing-specialist | `docs/t2-market/aso.md` | Keyword landscape, store listing benchmarks, and whether the name and brand can be found and are free. |

## Wave B (after `market.md` exists)
| Agent | Output | Focus |
|---|---|---|
| monetization-strategist | `docs/t2-market/monetization.md` | Competitor pricing in the target markets. Willingness to pay in the segment. Model options (subscription, one-time purchase, freemium limits, AI as a paid tier). Store fees. The AI or backend cost per active user from `docs/t1-discovery/ai.md` and `ops.md`. A first revenue scenario. |
| business-rnd-researcher (optional, if the brief scoped it) | `docs/t2-market/segment-needs.md` | What the target segment actually needs to reach its goal, as expert practice and research describe it, set against the app's method. |

## Synthesis
`product-manager` → `docs/t2-market/positioning.md`:
- the target segment (and segments rejected, with the reason);
- the gap we can own, with evidence links;
- a positioning statement;
- the differentiation thesis (and defence against Apple guideline 4.2/4.3 copycat rejection);
- a pricing hypothesis;
- the existing strengths that serve the positioning;
- what the positioning makes irrelevant (candidates for "cut").

Report to the PO in Vietnamese (≤15 lines): who we sell to, against whom, why they would switch, roughly at what price. Batch the open questions.

Set `phase: "t3-assessment"`; log; commit the workspace.
