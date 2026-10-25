---
name: phase-4-design
description: Phase 4 - produce the production design system, wireframes, per-screen specs, motion/haptics/sound, copy, consent UX and assets plan, reviewed by UI/UX R&D against the production UI bar. Use after gate G1.
---

# Phase 4 — Design

Precondition: `gates.G1_mvp_scope == "approved"`. Inputs: PRD, stories, flows, `docs/01-research/uiux-rnd.md` (+ the visual direction the PO preferred), brief (brand & feel).

## Steps
1. `ux-designer` → `docs/04-design/wireframes.md` (every MVP screen, all states).
2. In parallel:
   - `ui-designer` → design system, screen specs, motion/sound/haptics, assets plan (see its agent file). Brief must name the chosen visual direction.
   - `ux-writer` → `voice-and-tone.md`, `copy.md`.
   - `privacy-legal-counsel` → `docs/04-design/consent-requirements.md`.
3. `ui-designer` integrates copy keys and consent screens into specs (a fresh agent with the spec, copy and consent paths, unless it returned less than 4 minutes ago).
4. **Quality review** (parallel):
   - `uiux-rnd-researcher` → `docs/04-design/uiux-rnd-review.md` against `kb-production-ui-bar` and the direction.
   - `store-compliance-officer` → HIG/Material, paywall disclosures, permission rationale timing (append to `docs/02-product/compliance-precheck.md`).
   - `qa-engineer` → testability notes (missing states, ambiguous behavior) in `docs/07-qa/design-testability.md`.
5. Loop `ui-designer` on all FAIL items until the UI/UX R&D review passes (max 3 loops; then run `review-board Design`).
6. Show the PO the design direction: palette, typography, 3–5 key screen specs (and Figma links if built). Ask for approval or adjustments via AskUserQuestion. (Not a formal gate, but PO taste matters.)

Update state: `phase: "5-architecture"`; log; commit.
