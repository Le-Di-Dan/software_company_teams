---
name: company-status
description: Show the company's current state to the PO in Vietnamese (phase, gates, stack, squad, feature progress, open questions, machine capabilities, PO to-dos) and recommend the next step. Use at session start, when the PO asks "đang ở đâu / tiếp theo là gì", or after resuming.
---

# Company status

1. Read `state/project.json`, `state/progress.md` (last ~15 lines), `state/open-questions.md`, `state/feature_list.json` (if present), `state/environment.md`.
   - If `state/project.json` is missing or invalid, recreate it from the structure in this skill's step 4 with `phase: "0-intake"` and tell the PO.
   - If `state/environment.md` is missing or its hostname differs from this machine (`hostname`), run `bash scripts/env-doctor.sh`.
2. Report to the PO in Vietnamese, compact:
   - Loại dự án: app mới hay **tiếp nhận app có sẵn** (`engagement`). Với tiếp nhận: repo của khách, commit gốc đã audit, `client/` đang chỉ đọc (trước TG1) hay đã được sửa trên `company/*`, và số phát hiện theo trạng thái trong `state/findings.json`
   - Tên app / ý tưởng · Pha hiện tại và trạng thái · Các gate (G0–G3, hoặc TG0/TG1/G2/G3 khi tiếp nhận) · Stack & squad (nếu đã chọn)
   - Tiến độ feature: x/y passes (nếu ở pha build), số bug mở (`docs/07-qa/bugs.md`)
   - Bảo mật: số lỗ hổng Critical/High còn mở trong `state/security-findings.json` (nếu có) — cảnh báo đây là thứ chặn G3
   - Gói tài khoản Claude và ngưỡng cầu dao usage (dòng `Account:` của SessionStart; API mà chưa đặt `budget_usd` thì nhắc PO là không có giới hạn)
   - Máy hiện tại làm được gì (iOS? Android?) và việc nào đang chờ máy kia (`needs:`)
   - Câu hỏi đang chờ PO trả lời
   - Việc PO cần tự làm (tài khoản developer, tuyển 12 tester Google Play, API keys, phê duyệt chi phí)
3. Recommend the next step and the skill that runs it (e.g. `phase-1-research`, or `takeover-1-discovery` in a takeover). If the project hasn't started, ask whether the PO brings a new idea or an existing app to take over. A new idea: invite them to describe it in their own words, then run `phase-0-intake`. An existing app: explain the setup (README, "Tiếp nhận app có sẵn": a new workspace from the template, then `bash scripts/setup.sh --takeover <git-url>`). This workspace can only become a takeover while nothing has started; then run `takeover-0-engagement`. If the PO wants a visual overview, offer `/company-dashboard` (the isometric HQ map).
4. `state/project.json` reference structure:
```json
{"app_name": null, "idea": null, "engagement": "new", "doc_language": "en", "phase": "0-intake", "phase_status": "not-started",
 "gates": {"G0_brief": "pending", "G1_mvp_scope": "pending", "G2_stack": "pending", "G3_release": "pending"},
 "stack": {"mobile": null, "backend": null, "baas": null, "web": {}}, "squad": [], "po_release_approval": false,
 "figma": {"enabled": false, "file_key": null, "file_url": null, "library_file_key": null, "plan": null},
 "usage_policy": {"plan": "auto", "budget_usd": null, "plans": {}},
 "cost_policy": {"profile": "economy", "model_overrides": {}, "max_parallel": 3, "resume_idle_min": 4, "read_max_kb": 30, "read_max_lines": 200},
 "updated_at": null}
```
   A takeover project (written by `scripts/takeover_setup.py`) has `"engagement": "takeover"`, phase `t0-engagement`…`t4-transition` then `2-product`…, gates `{"TG0_engagement", "TG1_direction", "G2_stack", "G3_release"}` and `"takeover": {"source_repo", "ref", "baseline_sha", "baseline_date", "owners": {}, "direction"}`. Never recreate it as a new-app project.
