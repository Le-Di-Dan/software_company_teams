---
name: takeover-3-assessment
description: Takeover T3 - turn discovery and market research into the assessment report (health scorecard, what is missing, Keep/Fix/Cut/Rebuild per module, 2-3 strategic options, release and go-to-market strategy), challenge it with the review board, present it to the PO in Vietnamese and record the chosen direction and finding verdicts (gate TG1). Use after takeover T2.
---

# Takeover T3 — Assessment & proposal (gate TG1)

Precondition: `docs/t1-discovery/summary.md` and `docs/t2-market/positioning.md` exist.

## Steps
1. **Draft.** Run `product-manager` with `solution-architect` input. If the director runs them as two agents, first `solution-architect` → `docs/t3-assessment/architecture-options.md` (for each candidate scope: refactor in place vs rebuild per module, migration risk, effort ranges, the data and users to preserve). Then `product-manager` writes `docs/t3-assessment/assessment.md` from `company/templates/assessment-report.md`. Inputs: everything in `docs/t0-engagement/`, `docs/t1-discovery/`, `docs/t2-market/`, `state/findings.json`, `state/security-findings.json`, `architecture-options.md`.

   Rules for the draft:
   - every score, verdict and option cites finding IDs or sources;
   - options differ in substance (not three sizes of the same plan);
   - each option says what we stop doing;
   - effort is given in build-loop features and a calendar range on the PO's Claude plan, plus paid services;
   - the release strategy follows the store rules (Google Play's 12 testers for 14 days, identity changes).
2. **Board.** Run `review-board TG1` (panel in that skill). The synthesizer updates `assessment.md` (recommendation, board support per option, unresolved disagreements) and writes `docs/03-review-board/TG1/decision.md`.
3. **PO version.** Start a fresh `product-manager` with the paths of `assessment.md` and `decision.md`. Write `docs/t3-assessment/assessment-vi.md`: the Vietnamese report for the PO, readable without the other files (≤6 pages):
   1. one-page summary;
   2. scorecard;
   3. what is missing or wrong, area by area (business logic, UI/UX, content, performance, code, security and legal, operations, monetization, release);
   4. why the PO felt "it is not right yet";
   5. market position;
   6. the options table and our recommendation;
   7. release and go-to-market plan;
   8. the decisions needed.

   Plain language, no internal IDs except in an appendix.
4. **Verify** (you): every finding with severity `critical` or `high` appears in the assessment, either in an option's scope or explicitly deferred with a reason; option effort adds up from the module verdicts; the Vietnamese version matches the English one.
5. **Gate TG1.** Give the PO the path to `assessment-vi.md` (offer to publish it as a shareable page if they want to forward it), then present in Vietnamese (≤20 lines):
   - the scorecard;
   - the top problems;
   - the options with time, cost, revenue path and risk;
   - our recommendation;
   - the disagreements.

   AskUserQuestion:
   - (1) the option, recommended first;
   - (2) the REVIEW items from `client-conventions.md` (keep or drop);
   - (3) any finding verdicts where the PO disagrees with the option's default (ask only about critical or high ones in a batch).
6. **Record:**
   - in `assessment.md` ("PO decision"), `decision.md` and `state/progress.md`;
   - `state/project.json`: `gates.TG1_direction: "approved"`, `takeover.direction` (the option and a one-line scope);
   - `state/findings.json`: each finding becomes `accepted` (in the chosen scope), `rejected` or `deferred`, with the PO's words in `po_note` where they gave any;
   - `.claude/rules/client.md`: update it with the REVIEW decisions.

   Commit the workspace.

   Tell the PO: from now on the company may change `client/`, only on `company/*` branches; the PO merges our pull requests on GitHub. Recommend `takeover-4-transition`.

If the PO asks for changes: route them to the owner (`product-manager` or `solution-architect`), then re-run only the affected board members' Round 1. If the PO decides to stop the engagement, record it, hand over the reports, and set `phase_status: "closed"`.
