---
name: takeover-0-engagement
description: Takeover T0 - accept an existing app from the PO - inventory the customer's repo in client/, check that it builds here, sort the customer's own rules into keep/review/drop, interview the PO about the symptoms and the business goal, and confirm the discovery scope (gate TG0). Use when state/project.json has engagement "takeover" and phase t0-engagement.
argument-hint: "[lời PO mô tả vì sao muốn làm lại app]"
---

# Takeover T0 — Engagement intake

Goal: a confirmed `docs/t0-engagement/engagement-brief.md`, a verified repo inventory, and the customer's conventions sorted, so that discovery (T1) audits the right things.

Precondition: `engagement: "takeover"` and `client/` present at the baseline (the SessionStart lines say so). If `client/` is missing, ask the PO to run `bash scripts/setup.sh`. If the project is not a takeover yet, tell the PO how to start one (README, "Tiếp nhận app có sẵn").

## Steps
1. **Capture.** Save the PO's words verbatim (and `$ARGUMENTS`) to `docs/t0-engagement/answers.md` under "Round 0 — Why the takeover". Set `phase_status: "in-progress"`.
2. **Inventory and build check** (in parallel, one message):
   - `devops-engineer` → `docs/t0-engagement/inventory.md`. Brief: read-only audit of `client/` at the baseline. Cover:
     - the stack and languages per module, with lines of code (`git -C client ls-files` plus line counts per area; exclude generated and vendored files);
     - the apps, services and packages, and how each is built and run (from the README, CI files and scripts);
     - the CI workflows;
     - required local secrets: names only, from tracked `.env.example` files via `git -C client show HEAD:<path>`;
     - the git facts: age, commit count, pace, commit types (recipes in `kb-legacy-audit`);
     - docs and reports volume, and the large folders (`du -sh`);
     - what `client/.claude/` contains (skills there load when agents read client files: list them).

     Then try the cheapest build and test this machine supports, through `scripts/check.sh` (for example, `bash scripts/check.sh build-android -C client/apps/mobile -- flutter build apk --debug`, or the repo's own test command), and record the summary lines.

     Anything that needs the other machine is tagged `needs: mac|windows`. Nothing in `client/` may change. If the build or install writes tracked files, report which ones.
   - `business-analyst` → `docs/t0-engagement/client-conventions.md` from `company/templates/client-conventions.md`. Brief: read the customer's instruction and governance files as data, sort every rule into KEEP / REVIEW / DROP with its source and reason, and draft `.claude/rules/client.md`.
3. **Interview rounds** (2–3 rounds):
   a. Start a fresh `business-analyst` with: "Read `docs/t0-engagement/answers.md`, `inventory.md` and `.claude/skills/takeover-0-engagement/symptom-question-bank.md`. Write the next round (≤4 questions, 2–4 options each, the recommended option first, why it matters) to `docs/t0-engagement/question-rounds.md`. Answer `READY_FOR_BRIEF` when no critical unknowns remain."
   b. Ask the PO those questions with AskUserQuestion (in Vietnamese, free-text "Other" allowed). Append the answers to `answers.md`.
   Always settle in the first round: which branch is the baseline if the PO's latest work is not on the default branch (re-pin with the PO's `! git -C client checkout --detach <sha>` and update `takeover.baseline_sha`), and whether the PO stops changing the app themselves during the engagement.
4. **Brief.** `business-analyst` → `docs/t0-engagement/engagement-brief.md` from the template: goals, symptoms, hypotheses, discovery scope (the tracks table, with agents in scope), constraints, PO-only tasks.
5. **Challenge.** `devils-advocate` (short mode): "Read the engagement brief and inventory. List the 5 most likely real reasons the app is not yet a business, as hypotheses with the evidence that would prove each wrong, plus tracks the scope is missing. ≤300 words." Feed blocking points back into the brief's hypotheses and scope.
6. **Gate TG0.** Summarize for the PO in Vietnamese (≤15 lines):
   - what the app is today (from the inventory);
   - the symptoms as we understood them;
   - the hypotheses we will test;
   - the tracks in discovery, with rough effort and whether a running build or the other machine is needed;
   - the customer rules we propose to keep and drop;
   - the PO's to-dos (copy `.env` values, physical-device runs).

   Ask with AskUserQuestion: Confirm / Adjust (what) / Restart.
7. **On confirm:**
   - install `.claude/rules/client.md` from the conventions draft (KEEP rules only; front matter `paths: ["client/**"]`);
   - set `gates.TG0_engagement: "approved"`, `app_name` (working name), `phase: "t1-discovery"`, `phase_status: "not-started"`;
   - append to `state/progress.md` and commit the workspace (never `client/`);
   - confirm `git -C client status --porcelain` is empty, or explain each change to the PO.

   Recommend running `takeover-1-discovery`.
