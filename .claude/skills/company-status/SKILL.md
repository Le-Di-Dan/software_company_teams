---
name: company-status
description: Show the company's current state to the PO in Vietnamese (phase, gates, stack, squad, feature progress, open questions, machine capabilities, PO to-dos) and recommend the next step. Use at session start, when the PO asks "đang ở đâu / tiếp theo là gì", or after resuming.
---

# Company status

1. Read `state/project.json`, `state/progress.md` (last ~15 lines), `state/open-questions.md`, `state/feature_list.json` (if present), `state/environment.md`.
   - If `state/project.json` is missing or invalid, recreate it from the structure in this skill's step 4 with `phase: "0-intake"` and tell the PO.
   - If `state/environment.md` is missing or its hostname differs from this machine (`hostname`), run `bash scripts/env-doctor.sh`.
2. Report to the PO in Vietnamese, compact:
   - Tên app / ý tưởng · Pha hiện tại và trạng thái · Các gate (G0–G3) · Stack & squad (nếu đã chọn)
   - Tiến độ feature: x/y passes (nếu ở pha build), số bug mở (`docs/07-qa/bugs.md`)
   - Bảo mật: số lỗ hổng Critical/High còn mở trong `state/security-findings.json` (nếu có) — cảnh báo đây là thứ chặn G3
   - Máy hiện tại làm được gì (iOS? Android?) và việc nào đang chờ máy kia (`needs:`)
   - Câu hỏi đang chờ PO trả lời
   - Việc PO cần tự làm (tài khoản developer, tuyển 12 tester Google Play, API keys, phê duyệt chi phí)
3. Recommend the next step and the skill that runs it (e.g. `phase-1-research`). If the project hasn't started, invite the PO to describe the idea in their own words, then run `phase-0-intake`. If the PO wants a visual overview, offer `/company-dashboard` (the isometric HQ map).
4. `state/project.json` reference structure:
```json
{"app_name": null, "idea": null, "doc_language": "en", "phase": "0-intake", "phase_status": "not-started",
 "gates": {"G0_brief": "pending", "G1_mvp_scope": "pending", "G2_stack": "pending", "G3_release": "pending"},
 "stack": {"mobile": null, "backend": null, "baas": null}, "squad": [], "po_release_approval": false,
 "usage_policy": {"soft_pct": 75, "hard_pct": 80, "seven_day_soft_pct": 95, "seven_day_hard_pct": 98, "budget_usd": null},
 "cost_policy": {"profile": "economy", "model_overrides": {}, "max_parallel": 3, "resume_idle_min": 4, "read_max_kb": 30, "read_max_lines": 200},
 "updated_at": null}
```
