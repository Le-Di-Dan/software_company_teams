---
name: change-request
description: Handle any scope change after the MVP scope gate - impact analysis by affected teams, devil's advocate challenge, PO decision, then controlled updates to stories, design, architecture and the locked feature_list.json. Use when the PO or a team wants to add, change or drop a feature.
argument-hint: "[mô tả thay đổi]"
---

# Change request

1. `product-manager` drafts `docs/change-requests/CR-nnn.md` from `company/templates/change-request.md` (`Status: proposed`) describing `$ARGUMENTS`, affected features/stories.
2. Impact analysis in parallel, ≤3 agents at a time (only affected teams): ui-designer, solution-architect, store-compliance-officer, test-automation-engineer, owning engineers — each returns its impact row/notes (they can't edit `docs/change-requests/`; the hook allows only product-manager and you). Give all notes to a fresh `product-manager` to merge into the CR.
3. `devils-advocate`: short challenge (is it worth it now? cheaper alternative?) returned to you; product-manager adds it to the CR.
4. PO decision via AskUserQuestion (approve / modify / reject / defer to next version) with cost/time impact in Vietnamese.
5. If approved: **you** change the CR line to `Status: approved` (only the main session may; the hook blocks subagents) and record the decision.
6. Apply in order: product-manager updates stories/PRD → designers update specs (if UI) → solution-architect updates `state/feature_list.json`: new features carry `"cr": "CR-nnn"`; changed or dropped features get `"cr": "CR-nnn"` and the new contract or `"status": "dropped"` (the hook validates the CR is approved).
7. Log in `state/progress.md`; continue the build loop.
