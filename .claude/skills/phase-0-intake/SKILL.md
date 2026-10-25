---
name: phase-0-intake
description: Phase 0 - audit the PO's rough app idea through structured interview rounds with the business-analyst, then produce and confirm the product brief and constitution (gate G0). Use when a new app idea arrives or the brief must be redone.
argument-hint: "[ý tưởng app của PO]"
---

# Phase 0 — Intake & audit

Goal: a confirmed `docs/00-intake/brief.md` and `docs/00-intake/constitution.md` with no critical unknowns.

## Steps
1. **Capture the idea.** Save the PO's words verbatim (and `$ARGUMENTS` if given) to `docs/00-intake/answers.md` under "Round 0 — Original idea". Set `state/project.json`: `idea`, `phase: "0-intake"`, `phase_status: "in-progress"`.
2. **Interview rounds** (repeat 3–5 times):
   a. Delegate to `business-analyst`: "Read `docs/00-intake/answers.md` and `.claude/skills/phase-0-intake/question-bank.md`. Write the next round (≤4 questions, 2–4 options each, recommended option first, why it matters) to `docs/00-intake/question-rounds.md`. If no critical unknowns remain, answer `READY_FOR_BRIEF`." For later rounds start a fresh `business-analyst` with the same brief (the PO's answers usually take longer than the 4-minute resume window; the files carry the history).
   b. Ask the PO with **AskUserQuestion** exactly those questions (Vietnamese). Allow free-text "Other".
   c. Append answers to `docs/00-intake/answers.md` (round number, question, answer).
3. **Brief + constitution.** Delegate to `business-analyst`: write `docs/00-intake/brief.md` and `docs/00-intake/constitution.md` from the templates, plus the PO-only task list.
4. **Quick challenge.** Delegate to `devils-advocate` (short mode): "Read the brief. List the top 5 risks or contradictions and 'assumptions to validate' for R&D. ≤300 words." Feed blocking points back to the BA or as a final question round.
5. **Gate G0.** Summarize the brief to the PO in Vietnamese (≤15 lines): idea, users, core problems, platforms, monetization intent, must-haves, out-of-scope, constraints, the PO's own to-dos (Apple/Google personal accounts, recruit ≥12 Android testers early, budget for paid services). Ask via AskUserQuestion: Confirm / Adjust (what) / Restart.
6. On confirm: set `gates.G0_brief: "approved"`, `app_name` (working name), `phase: "1-research"`, `phase_status: "not-started"`; append to `state/progress.md`; commit if git exists. Recommend running `phase-1-research`.
