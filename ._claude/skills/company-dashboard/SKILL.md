---
name: company-dashboard
description: Build or refresh the visual "HQ map" — an isometric, game-style dashboard where departments are buildings and cartoon department leaders walk between them according to what the subagents are really doing (assign, consult another team's files, report back). Shows phase pipeline, gates, running agents, task board and activity log. Use when the PO asks to see the dashboard / trụ sở / bản đồ công ty, or after a phase changes.
argument-hint: "[live | refresh]"
---

# Company dashboard (HQ map)

One page, two ways to view it. Both come from the same template `company/templates/dashboard.html`, filled by `scripts/dashboard.py` (Python 3 stdlib, works on the Mac and the Windows PC).

| Mode | How | What the PO sees |
|---|---|---|
| **Live** (on this machine) | PO runs `! python3 scripts/dashboard.py --open` (Windows: `py -3 scripts/dashboard.py --open`) | http://127.0.0.1:8765, refreshed every 2 s from `state/` and the activity log; leaders walk in real time |
| **Snapshot** (shareable Artifact) | this skill publishes it | the state at publish time, plus "Phát lại hoạt động" (replays the last 60 events) and "Mô phỏng pha Research" (clearly labelled example data) |

## Where the movement comes from
`.claude/hooks/activity_log.py` appends one line per event to `state/activity.jsonl` (gitignored, machine-local):
`assign` (director launches an agent, with its description) → the director's mascot walks to that building · `start` · `tool` (a subagent reads/writes/searches; reading a file owned by another department makes that department's leader walk over to "trao đổi") · `stop` → the leader walks to Nhà Trắng to report · `po` / `idle`. The page maps agents to departments with its `DEPTS` list and file paths to owners with its `OWNER` rules — update both if the org chart or folder layout changes.

## Steps
1. Live mode wanted (argument `live`, or the PO says "xem trực tiếp")? The server is long-running, so don't start it yourself: tell the PO to run `! python3 scripts/dashboard.py --open` in their terminal, and stop.
2. Otherwise build the snapshot: `python3 scripts/dashboard.py --snapshot <scratchpad>/tru-so.html`. It reads `state/project.json`, `feature_list.json`, `security-findings.json`, `open-questions.md` and `activity.jsonl` itself — never hand-edit numbers into the page.
3. Publish the file with the Artifact tool (icon `map`). If `state/project.json` holds `dashboard_url`, publish to that URL to keep one page; otherwise publish fresh and save the returned URL as `dashboard_url` in `state/project.json`.
4. Tell the PO in one Vietnamese line: what the map shows, that tapping a building or a leader opens that department, and the live command above.

## Notes
- Keep it honest: every number and every walk comes from `state/` or the activity log. The demo button is the only scripted motion and the page labels it "Mô phỏng · dữ liệu minh họa".
- The activity log stores agent types, task descriptions, file paths, web hosts and the first two words of shell commands — never PO messages or command arguments. `COMPANY_ACTIVITY=0` turns it off.
- The artifact is private to the PO's account; they share it from the page's Share menu.
