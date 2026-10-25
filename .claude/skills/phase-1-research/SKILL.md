---
name: phase-1-research
description: Phase 1 - run the R&D center in parallel (Business R&D, Market, UI/UX R&D, AI R&D, Monetization), cross-check findings, and synthesize research into opportunities, risks and differentiation. Use after gate G0.
---

# Phase 1 — Research (R&D center)

Precondition: `gates.G0_brief == "approved"`.

## Step 1 — Parallel research (two waves, ≤3 agents at a time)
Wave A: business-rnd-researcher, market-researcher, uiux-rnd-researcher. Wave B: ai-rnd-researcher, monetization-strategist (after `market.md` exists, so pricing data is available).
Common brief for all: inputs `docs/00-intake/brief.md`, `docs/00-intake/constitution.md`, the "Assumptions to validate" list; output to their file in `docs/01-research/`; sources with URLs and dates; end with "Challenges", "Questions for PO" and "Working notes (for cross-check)" (template `company/templates/research-report.md`), so the fresh cross-check agent loses nothing.

| Agent | Output | Focus to state in the brief |
|---|---|---|
| business-rnd-researcher | `business-rnd.md` | domain science & expert practice, ranked user problems, effectiveness metrics |
| market-researcher | `market.md` | competitors, review mining, differentiation gap, ASO landscape |
| uiux-rnd-researcher | `uiux-rnd.md` | current Apple/Android design language, competitor UI teardown, patterns, 2–3 visual directions, motion/haptics/sound, assets strategy |
| ai-rnd-researcher | `ai-rnd.md` | AI opportunity map for the ranked problems, models/cost/latency, AI UX, competitor AI |
| monetization-strategist | `monetization.md` | pricing models, competitor pricing from `market.md`, store fees, AI cost per user |

## Step 2 — Cross-examination (one round)
Start a fresh agent of each research type (≤3 at a time; the originals' caches have expired by now) with its own report path and the paths of the other reports: "Read the other R&D reports. Append a `## Cross-check` section to your file: contradictions with your findings (with evidence), points you now revise, and opportunities that combine findings." Keep it ≤300 words each.

## Step 3 — Synthesis
Delegate to `product-manager`: write `docs/01-research/synthesis.md`:
- Top user problems (ranked, evidence-linked) and the core outcome the app must deliver.
- Differentiation thesis (why us vs competitors; defense against Apple 4.2/4.3).
- Opportunity list: feature ideas from all teams with source report, value, effort, risk.
- Visual direction options (from UI/UX R&D) and AI opportunities worth pursuing.
- Monetization recommendation and AI cost implications.
- Unresolved disagreements between teams.

## Step 4 — Report to PO
Vietnamese summary (≤20 lines): what we learned, differentiation thesis, 2–3 visual directions (let the PO pick a favorite now via AskUserQuestion — it guides phase 4), monetization direction, top risks. Batch any open questions from the reports.

Update state: `phase: "2-product"`; log in `state/progress.md`; commit.
