---
name: review-board
description: Run a structured cross-functional debate (independent positions, rebuttal round, devil's advocate, synthesis) on a proposal, then take the decision to the PO. Use for gate G1 (MVP scope), G2 (stack), design direction disputes, change requests, or any contested decision.
argument-hint: "[G1 | G2 | <topic>]"
---

# Review board

Argument: `$ARGUMENTS` = gate or topic. Folder: `docs/03-review-board/<gate-or-topic>/`.

## Panels
| Gate | Proposal files | Panel (positions) | Synthesizer |
|---|---|---|---|
| G1 MVP scope | `docs/02-product/prd.md`, `scope.md`, `user-stories.md`, `docs/01-research/synthesis.md` | product-manager (defends), business-rnd-researcher, market-researcher, monetization-strategist, store-compliance-officer, solution-architect (feasibility), devils-advocate | product-manager |
| G2 Stack | `docs/05-architecture/stack-selection.md`, `architecture.md`, `ai-architecture.md`, `security-review.md` | solution-architect (defends), the relevant mobile/backend/BaaS team leads (2–4 agents), security-lead, ai-rnd-researcher (if AI), devils-advocate | solution-architect |
| Design | `docs/04-design/*` | ui-designer (defends), uiux-rnd-researcher, ux-designer, qa-engineer, devils-advocate | ui-designer |
| Other / CR | given in the request | owner + affected teams + devils-advocate | owner |

Keep panels ≤6 agents for cost.

## Round 1 — independent positions (parallel, one message)
Brief each member: read the proposal files; write `<folder>/<agent>-round-1.md` using `company/templates/review-position.md`; judge only from your discipline; cite evidence; give a verdict and conditions.

## Round 2 — rebuttal (parallel)
SendMessage to each member: "Read all round-1 files in `<folder>`. Write `<agent>-round-2.md`: respond to the claims that touch your area, say what changed your mind, keep or drop your conditions."

## Round 3 — devil's advocate final challenge
`devils-advocate`: read all files, write `devils-advocate-final.md`: remaining unresolved objections ranked, and the best alternative proposal if any.

## Synthesis
The synthesizer writes `<folder>/decision.md` from `company/templates/review-decision.md`: recommendation, 2–3 options for the PO with pros/cons and board support, consensus, unresolved disagreements (both sides' best argument), conditions.

## PO decision
Present in Vietnamese: recommendation, options, key disagreements, cost/time implications. AskUserQuestion with the options (recommended first). Record the decision in `decision.md` ("PO decision"), `state/project.json` gate (`G1_mvp_scope` / `G2_stack` → `approved` or `changes-requested`), and `state/progress.md`.

If the PO requests changes: route them to the owner, then re-run only Round 1 for affected members (not the whole board).
