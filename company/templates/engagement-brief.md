# Engagement Brief — {{App name}} (takeover)

> Owner: business-analyst · Gate TG0 (PO confirms) · Date: {{YYYY-MM-DD}}
> Customer repo: {{source_repo}} · Audited baseline: {{baseline_sha}} ({{ref}})

## 1. Why the PO hands the app over
The PO's own words (verbatim, from `answers.md`), then a one-paragraph restatement.

## 2. Business goal
- Target outcome (for example: first paying users, X subscribers or revenue by a date) and the time horizon
- Markets, languages and platforms in scope
- What the PO is willing to cut, and what they are attached to (they must justify keeping it, or we will challenge it)

## 3. Symptoms the PO feels
| # | Symptom (PO's words) | Where / when it shows | Our first reading |
|---|---|---|---|

## 4. What the app is today (from `inventory.md`)
Stack, size, age and commit pace, platforms built, distribution status (store / TestFlight / none), users, revenue, the state of CI, the main modules.

## 5. Hypotheses to test in discovery
| # | Hypothesis | Track(s) that test it | What would prove it wrong |
|---|---|---|---|

## 6. Discovery scope
| Track | In scope? | Agent | Notes (for example: needs a running build, needs the Mac) |
|---|---|---|---|
| Walkthrough (shared screenshots) | yes | qa-engineer | |
| Product & business logic | | business-analyst | |
| Domain & content | | business-rnd-researcher | |
| UX | | ux-designer | |
| UI | | uiux-rnd-researcher | |
| Architecture | | solution-architect | |
| Code health | | code-reviewer | |
| Performance | | performance-engineer | |
| Security (read-only scans) | | appsec-code-auditor | |
| Privacy, legal & content licences | | privacy-legal-counsel | |
| Store readiness | | store-compliance-officer | |
| Operations & CI | | devops-engineer | |
| Analytics | | data-analyst | |
| Delivery forensics | | data-analyst | |
| AI features | | ai-rnd-researcher | |
| Market & monetization (T2) | | market-researcher, monetization-strategist, aso-marketing-specialist | |

## 7. Constraints
Budget (Claude plan or API, paid services), deadline, machines available, accounts the PO already has (Apple, Google, backend), data or users that must not be lost.

## 8. The customer's conventions
Summary of `client-conventions.md`: KEEP / REVIEW / DROP counts and the rules the PO wants enforced.

## 9. PO-only tasks
Copy `.env` values, give repo or store access, test on a physical device, decisions due at TG1.

## 10. PO decision (TG0)
Confirmed scope, date, changes requested.
