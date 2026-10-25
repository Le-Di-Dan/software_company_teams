# Handoff templates

Used when the usage circuit breaker (`.claude/hooks/usage_guard.py`) pauses the company. The guard tells each
agent its exact file path; these are the required sections. Write in `state/project.json → doc_language`.

---

## A. Agent handoff: `state/handoff/<agent-type>-<id>.md`

```markdown
# Handoff: <agent-type> - <task title>
Paused: <date time> · Phase: <phase> · Reason: <usage % / manual pause>

## Task
Original objective, input paths, output paths, template, definition of done (copied from the director's brief).

## Done
- <item> → `<path>` (complete)

## In progress
- `<path>`: partial, stopped after <section/line>. Remaining: <what is missing>.

## Next steps
1. <concrete step a fresh agent can execute without this conversation>

## Open questions / risks
- <question for the director or PO>

## How to verify
- <command, check or file to inspect>
```

---

## B. Director handoff: `state/handoff/HANDOFF.md`

```markdown
# Company handoff
Paused: <date time> · Usage: <x% of 5h/7d> · Resets: <time> · Phase: <phase> (<status>)

## Paused agents
| Agent | Task | Handoff file | State |
|---|---|---|---|
| market-researcher | Competitor analysis | state/handoff/market-researcher-ab12cd34.md | partial |

## Interrupted without handoff
Agents in `state/handoff/INTERRUPTED.json`, if any, and what their output files look like.

## Done this phase
- <deliverable> → `<path>`

## Resume plan (in order)
1. Re-dispatch <agent> with <handoff path> (parallel group A)
2. Then <next SOP step>

## Waiting on the PO
- <decision or action>
```
