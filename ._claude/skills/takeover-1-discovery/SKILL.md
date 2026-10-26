---
name: takeover-1-discovery
description: Takeover T1 - due-diligence audit of the existing app by parallel tracks (walkthrough, product and business logic, domain and content, UX, UI, architecture, code, performance, security, legal, store, operations, analytics, delivery, AI) into state/findings.json and per-track reports, then a consolidated discovery summary. Use after gate TG0.
---

# Takeover T1 — Discovery

Precondition: `gates.TG0_engagement == "approved"`. Inputs for every brief: `docs/t0-engagement/engagement-brief.md`, `docs/t0-engagement/inventory.md`, `.claude/skills/kb-legacy-audit/SKILL.md`, and the baseline SHA. Run only the tracks marked in scope in the brief.

## Common brief (add it to every track's delegation)
- Read-only audit of `client/` at the baseline, following `kb-legacy-audit`: evidence standards, finding format, severity by business impact, the scorecard.
- Output `docs/t1-discovery/<track>.md` from `company/templates/discovery-report.md`; findings appended to `state/findings.json` (create it from `company/templates/findings.example.json` with an empty `findings` list if missing).
- Test the brief's hypotheses that name your track.
- Screenshots and kept logs go under `docs/t1-discovery/evidence/<track>/`.
- Return ≤200 words: score, top 3 findings, hypotheses verdicts, `needs:` items, questions for the PO.

## Wave 0: the shared walkthrough (one agent, first)
`qa-engineer` → `docs/t1-discovery/walkthrough.md` + `docs/t1-discovery/evidence/walkthrough/`. Cover:
- a fresh install on this machine's platform (profile or release build if possible);
- every reachable screen, with a screenshot, in the order a new user meets it; the time and number of taps from launch to the first moment of value; each main flow end to end;
- crashes, errors, empty screens and dead ends;
- a screen map: route or screen name, how it is reached, the screenshot path.

Use Maestro flows where possible and save them under `docs/t1-discovery/evidence/walkthrough/flows/`, not in `client/`. Other platforms are marked `needs:`. Every other track starts from this walkthrough instead of driving the app again.

## Waves 1–4 (≤3 agents at a time, the order below)
| Wave | Track | Agent | Output |
|---|---|---|---|
| 1 | Product & business logic | business-analyst | `product.md` |
| 1 | UX | ux-designer | `ux.md` |
| 1 | Architecture | solution-architect | `architecture.md` |
| 2 | Code health | code-reviewer | `code.md` |
| 2 | Performance | performance-engineer | `performance.md` |
| 2 | UI & visual quality | uiux-rnd-researcher | `ui.md` |
| 3 | Domain & content | business-rnd-researcher | `domain-content.md` |
| 3 | Security (read-only scans: SAST, secrets, dependencies; pentest only if the brief scoped it) | appsec-code-auditor | `docs/07-qa/appsec-audit-<date>.md` + `state/security-findings.json`, plus a one-page `security.md` summary |
| 3 | Privacy, legal & content licences | privacy-legal-counsel | `legal.md` |
| 4 | Store readiness | store-compliance-officer | `store.md` |
| 4 | Operations, CI & running cost | devops-engineer | `ops.md` |
| 4 | Analytics, then delivery forensics (two runs) | data-analyst | `analytics.md`, `delivery.md` |
| 4 | AI features (if any) | ai-rnd-researcher | `ai.md` |

Track-specific points to put in the brief:
- **Architecture**: write `docs/t1-discovery/module-map.md` as well: every module or package with its purpose, size, dependencies and owner stack. The other tracks and T3 use it as the list of modules.
- **Code health**: churn × complexity hotspots from git forensics; test quality by sampling (does a test fail if the behavior breaks?).
- **Delivery forensics**: effort by area and by commit type, the docs:code ratio, rework, long-blocked decisions. The question to answer is what in the old way of working to keep and what to drop.
- **Security**: tools run via Docker only with the PO's OK (ask once). Targets are local builds only.

If a track's work depends on a machine this session isn't on, run what is possible and list the rest under `needs:` for the PO.

## Consolidation
1. Start a fresh `product-manager` with the paths of all track reports, `state/findings.json` and `state/security-findings.json`. Write `docs/t1-discovery/summary.md`:
   - **De-duplicate.** For each duplicate, keep the clearest entry, move the extra evidence into its `notes`, and mark the duplicate's `notes` with `duplicate of TKO-…`. Never delete a finding.
   - Draft scorecard (10 dimensions).
   - Top 10 findings by business impact.
   - Hypotheses table (confirmed / refuted / inconclusive).
   - Where the PO's symptoms come from.
   - What is worth keeping.
   - Contradictions between tracks.
2. Verify against the definition of done: each in-scope track has a report, a score and findings with evidence; `Grep -n` the register for findings without `evidence` or `business_impact` and send them back to their track.
3. Check that `git -C client status --porcelain` is empty (explain any change).

## Report to the PO
Vietnamese, ≤20 lines:
- the draft scorecard;
- the 5 biggest problems, in plain language;
- which hypotheses held;
- where the symptoms come from;
- what is good and must be kept;
- anything that needs the PO (a physical-device run, the other machine).

No decisions yet: options come in T3.

Set `phase: "t2-market"`; log; commit the workspace.
