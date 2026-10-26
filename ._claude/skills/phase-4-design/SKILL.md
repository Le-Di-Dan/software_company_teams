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
   - If the PRD has web surfaces: the `ui-designer` brief also covers them: a "Web" section in `design-system.md` (same brand; web type scale, breakpoints, grid, density per surface, web components) and one responsive spec per page in `docs/04-design/web/<surface>/SCR-W-nnn-<name>.md` (390 / 768 / 1280 px, every state). The bar is `.claude/skills/kb-web-ui-bar/SKILL.md` (plus the Admin UI bar in `kb-web-admin` for `admin`), not mobile platform guidelines. The `site` surface also needs `ux-writer` landing copy and the `aso-marketing-specialist` messaging so site and store listing agree.
3. `ui-designer` integrates copy keys and consent screens into specs (a fresh agent with the spec, copy and consent paths, unless it returned less than 4 minutes ago).
4. **Quality review** (parallel):
   - `uiux-rnd-researcher` → `docs/04-design/uiux-rnd-review.md` against `kb-production-ui-bar` and the direction (web pages: against `kb-web-ui-bar`).
   - `store-compliance-officer` → HIG/Material, paywall disclosures, permission rationale timing (append to `docs/02-product/compliance-precheck.md`).
   - `qa-engineer` → testability notes (missing states, ambiguous behavior) in `docs/07-qa/design-testability.md`.
5. Loop `ui-designer` on all FAIL items until the UI/UX R&D review passes (max 3 loops; then run `review-board Design`).
6. Show the PO the design direction: palette, typography, 3–5 key screen specs (and Figma links if built). Ask for approval or adjustments via AskUserQuestion. (Not a formal gate, but PO taste matters.)

Update state: `phase: "5-architecture"`; log; commit.

## Takeover mode
- The precondition is `gates.TG1_direction == "approved"` (it replaces G1).
- Start from the existing design: the walkthrough screenshots, the T1 UX/UI reports and the existing design system in `client/` (tokens, components). Decide with the PO whether v2 **evolves** the current visual language or **replaces** it (a TG1 decision or an AskUserQuestion here).
- Specify every screen touched by fix, rebuild or add stories, plus the shared components they change. Screens marked keep get a short spec only if the design system change alters them.
- Each spec states "today → v2" with the current screenshot path, so engineers change what is intended and nothing else.
