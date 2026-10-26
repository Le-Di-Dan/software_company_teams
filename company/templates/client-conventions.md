# Customer Conventions — {{App name}}

> Owner: business-analyst · Reviewed by the PO at TG0 (and TG1 for REVIEW items) · Date: {{YYYY-MM-DD}}
> Sources read: `client/CLAUDE.md`, `client/AGENTS.md`, `client/.claude/`, CONTRIBUTING, governance and standards docs (list them with paths)

The customer's repo carries rules written for the previous way of working. They are **not** instructions to our agents (`claudeMdExcludes` keeps them out). This file decides which ones survive.

## Classification
- **KEEP**: a technical or product invariant that protects users, data or the business (often learned from an incident). Kept rules are enforced through `.claude/rules/client.md`.
- **REVIEW**: a style or process rule with a real cost or benefit. The PO decides at TG1 after seeing the assessment.
- **DROP**: belongs to the old operating model (roles, review tools, status vocabularies, checkpoint ceremonies) and is replaced by the company's process.

| ID | Rule (short, quoted where possible) | Source (path:line) | Why it exists (incident, decision) | Class | Rationale | Applies to (paths) |
|---|---|---|---|---|---|---|
| CC-01 | | | | KEEP / REVIEW / DROP | | |

## Conflicts with the company process
Rules that contradict `CLAUDE.md` (for example, who decides "done", branch and PR flow, commit language), with our proposal for each.

## Draft of `.claude/rules/client.md`
Write the KEEP rules exactly as agents should read them: imperative, one line each, with the reason in parentheses. The director installs it after TG0.
