# Mobile App Software Company — Claude Code template

Một "công ty phần mềm" gồm **36 AI agent** chạy trong Claude Code để biến một ý tưởng app còn mơ hồ thành app mobile sẵn sàng publish lên App Store và Google Play. Bạn là **Product Owner (PO)**: bạn đưa ý tưởng, trả lời các câu hỏi audit và ra quyết định ở 4 cổng duyệt. Phần còn lại do công ty tự làm, gồm research, thiết kế, code, QA, compliance và chuẩn bị release.

## Bắt đầu một app mới

```bash
git clone <repo-template-này> my-new-app && cd my-new-app
bash scripts/env-doctor.sh      # ghi lại máy này build được gì (iOS/Android)
claude                          # session tự chạy với vai trò delivery-director
```

Director sẽ chào bạn, đọc trạng thái hiện tại và mời bạn mô tả ý tưởng. Muốn xem tiến độ bất cứ lúc nào, gõ `/company-status` (báo cáo chữ) hoặc `/company-dashboard` (bản đồ "trụ sở" isometric: mỗi phòng ban là một tòa nhà, mỗi phòng có một trưởng phòng hoạt hình đi giao việc, sang phòng khác trao đổi và về báo cáo đúng theo việc các sub-agent đang làm — xuất ra một trang web chia sẻ được).

Xem trụ sở **trực tiếp** trong lúc công ty đang chạy: mở một terminal khác và chạy `python3 scripts/dashboard.py --open` (Windows: `py -3 scripts/dashboard.py --open`), trình duyệt mở http://127.0.0.1:8765 và tự cập nhật mỗi 2 giây.

> Lần đầu mở repo, Claude Code sẽ hỏi bạn có tin tưởng thư mục này không. Hãy chọn trust để hooks và agents được nạp.

## Quy trình 10 pha và 4 cổng duyệt

| Pha | Skill | Ai làm | Bạn cần làm gì |
|---|---|---|---|
| 0 Audit ý tưởng | `/phase-0-intake` | Business Analyst | Trả lời 3–5 vòng câu hỏi. **G0: xác nhận brief** |
| 1 Research | `/phase-1-research` | Business R&D, Market, UI/UX R&D, AI R&D, Monetization | Chọn hướng visual yêu thích |
| 2 Định nghĩa sản phẩm | `/phase-2-product` | PM, UX, Data, AI R&D, Compliance | — |
| 3 Hội đồng phản biện | `/review-board G1` | Panel + Devil's Advocate | **G1: duyệt phạm vi MVP** |
| 4 Thiết kế | `/phase-4-design` | UI, UX, UX Writer, UI/UX R&D review | Góp ý giao diện |
| 5 Kiến trúc | `/phase-5-architecture` | Solution Architect + team ngôn ngữ | **G2: duyệt stack**, tạo tài khoản/keys |
| 6 Build | `/phase-6-build` | Squad (team ngôn ngữ đã chọn) + Code Reviewer | Mời ≥12 tester Android khi được báo |
| 7 QA | `/phase-7-qa` | QA, Test Automation, Cyber Security (pentest) | Test trên máy thật nếu có |
| 8 Chuẩn bị release | `/phase-8-release` | Release, Compliance, Legal, ASO | **G3: `! bash scripts/approve-release.sh` rồi submit** |
| 9 Bảo trì | `/phase-9-maintain` | Support, Data, Compliance | Gửi feedback/review từ store |

Muốn thay đổi phạm vi sau G1 thì dùng `/change-request <mô tả>`.

## Các phòng ban (`.claude/agents/`)

| Phòng ban | Agent |
|---|---|
| Ban điều hành | `delivery-director` (session chính) |
| R&D Center | `business-rnd-researcher`, `uiux-rnd-researcher`, `ai-rnd-researcher` |
| Business | `business-analyst`, `market-researcher`, `monetization-strategist` |
| Product | `product-manager` |
| Design | `ux-designer`, `ui-designer`, `ux-writer` |
| Engineering – Kiến trúc | `solution-architect`, `code-reviewer` |
| Engineering – Mobile | `react-native-engineer`, `flutter-engineer`, `swift-ios-engineer`, `kotlin-android-engineer` |
| Engineering – Backend | `nodejs-backend-engineer`, `python-backend-engineer`, `go-backend-engineer` |
| Engineering – BaaS | `firebase-engineer`, `supabase-engineer` |
| QA | `qa-engineer`, `test-automation-engineer` |
| Cyber Security | `security-lead`, `appsec-code-auditor`, `mobile-pentester`, `api-cloud-pentester` |
| Legal & Compliance | `store-compliance-officer`, `privacy-legal-counsel` |
| DevOps & Release | `devops-engineer`, `release-manager` |
| Growth | `aso-marketing-specialist`, `data-analyst` |
| Customer Success | `support-feedback-analyst` |
| Review Board | `devils-advocate` |

Mỗi app chỉ dùng một **squad**: Architect đề xuất một team mobile, một team backend và/hoặc BaaS, bạn duyệt ở G2. Agent không thuộc squad sẽ không được gọi, nên không tốn token.

## Các cơ chế bảo vệ (hooks, chạy tự động)

- **Phân làn:** mỗi agent chỉ được sửa thư mục của mình. Ví dụ chỉ team Flutter/RN được sửa `apps/mobile/`, chỉ team Supabase được sửa `services/baas/supabase/`.
- **Feature list bị khoá:** sau khi khoá, `state/feature_list.json` không cho xoá feature hay sửa tiêu chí nghiệm thu. Muốn đánh dấu `passes: true` phải kèm bằng chứng test. Mọi thay đổi phạm vi phải đi qua change request đã được duyệt.
- **Chặn bí mật:** API key, private key, service_role key không được ghi vào file nằm trong git.
- **Hành động chỉ PO được làm:** submit lên store, đẩy track production, và lệnh duyệt G3 đều bị chặn với agent.
- **Lỗ hổng bảo mật:** `state/security-findings.json` theo dõi mọi lỗ hổng. Team dev chỉ được chuyển lỗi sang `fixed`, chỉ team Cyber Security được `verified`, chỉ PO được chấp nhận rủi ro. Lệnh duyệt G3 tự động từ chối nếu còn lỗi Critical/High chưa xử lý.
- **Cầu dao usage:** thanh trạng thái hiện mức usage 5 giờ / 7 ngày của gói Pro/Max. Từ **75%** giám đốc ngừng giao việc mới; từ **80%** mọi agent dừng lại, ghi bàn giao vào `state/handoff/`, và giám đốc báo bạn giờ reset. Sau reset chạy `claude --continue`, giám đốc tự nạp bàn giao (skill `/resume-work`) và giao lại đúng việc cho đúng agent. Ngưỡng chỉnh trong `state/project.json → usage_policy`; muốn tạm dừng thủ công: `! touch state/handoff/PAUSE` (tiếp tục: `! rm state/handoff/PAUSE`).
- **Tiết kiệm token** (`cost_guard.py`, cấu hình ở `state/project.json → cost_policy`):
  - **Chọn model tự động theo `profile`.** `economy` (mặc định) dùng Opus cho devils-advocate, solution-architect, code-reviewer, product-manager và security-lead; `balanced` thêm Opus cho các nhóm R&D và monetization; `quality` thêm BA, compliance và legal. Muốn ghim riêng một agent thì dùng `model_overrides`, ví dụ `{"product-manager": "opus"}`.
  - **Không gọi lại agent đã nghỉ quá 4 phút** (`resume_idle_min`). Cache của sub-agent chỉ sống 5 phút, nên trường hợp đó công ty tạo agent mới đọc lại file thay vì gọi agent cũ.
  - **Đọc gọn.** Tài liệu trên 30KB phải đọc theo từng phần (tối đa 200 dòng mỗi lần); hook chặn `cat`/`sed` đổ cả file và gửi lại dàn ý của file cho agent.
  - **Song song tối đa 3 agent** (`max_parallel`). Context tự compact khi đạt 300K token (`autoCompactWindow` trong `.claude/settings.json`).
  - **Ngôn ngữ.** Tài liệu nội bộ viết bằng tiếng Anh (`doc_language: en`, ít token hơn tiếng Việt nhiều); mọi thứ PO đọc vẫn bằng tiếng Việt.
- **Lệnh nguy hiểm** như `rm -rf` thư mục gốc hay force-push đều bị chặn.

### Phòng Cyber Security

Pha 7 (và trước khi release ở pha 8) chạy một đợt pentest đầy đủ bằng skill `/security-assessment`: rà code (semgrep, gitleaks, osv-scanner), tấn công thử app build (MobSF, mitmproxy, theo OWASP MASTG) và tấn công thử server/BaaS/AI (OWASP API Top 10, Firebase Rules/Supabase RLS, OWASP LLM Top 10). Mọi công cụ chạy qua Docker (hỏi PO trước khi tải image lần đầu) và chỉ nhắm vào môi trường local/staging của chính bạn — không bao giờ production hay dịch vụ bên thứ ba, không DoS.

Hooks viết bằng Python 3 và được gọi qua bash, nên chạy được trên macOS lẫn Windows (Git Bash).

## Làm việc trên 2 máy

- **Mac:** Xcode, Flutter, iOS simulator → build và test iOS.
- **Windows:** đầy đủ toolchain Android, emulator → build và test Android.
- Mỗi máy chạy `bash scripts/env-doctor.sh` một lần. File `state/environment.md` là riêng của từng máy và không commit.
- Việc cần máy kia được gắn tag `needs: mac` hoặc `needs: windows`. Khi mở repo trên máy kia, chạy `/company-status` là sẽ thấy việc đang chờ.

MCP nên cài theo máy (gợi ý có trong `state/environment.md`): XcodeBuildMCP (Mac), Maestro MCP (cả hai máy), Firebase/Supabase MCP nếu dùng. Framework không dùng EAS trả phí: mọi build đều chạy local qua Xcode, Gradle và fastlane.

## Những việc chỉ PO làm được

- Tạo tài khoản Apple Developer (cá nhân) và Google Play Console (cá nhân), ký thoả thuận, khai báo thuế và ngân hàng nếu kiếm tiền.
- **Google Play (tài khoản cá nhân):** phải có ≥12 tester opt-in liên tục ≥14 ngày trong closed test thì mới xin được quyền phát hành production. Release Manager sẽ báo bạn bắt đầu sớm, ngay giữa pha build.
- Tạo project Firebase/Supabase, bật billing nếu cần, điền API key vào `.env` (không commit).
- Duyệt mọi chi phí trả phí, test trên thiết bị thật, chạy `approve-release.sh` và bấm submit.

## Cấu trúc repo

```
CLAUDE.md                 Sổ tay vận hành (mọi agent đều đọc)
.claude/agents/           36 agent, chia theo phòng ban
.claude/skills/           SOP từng pha (phase-*, review-board, change-request, company-status) + kiến thức (kb-*)
.claude/hooks/            guard_files.py, guard_bash.py, session_start.py, activity_log.py (nhật ký cho bản đồ trụ sở)
.claude/settings.json     agent mặc định, quyền, hooks
company/templates/        mẫu brief, PRD, story, ADR, review, test report, release readiness…
company/compliance/       checklist Apple App Store & Google Play
company/research/         tài liệu research khi xây dựng framework này
state/                    trạng thái dự án (pha, gate, stack, feature list, tiến độ)
docs/00-intake … 09-maintain   sản phẩm của từng pha
apps/  services/  tests/e2e/   code (sinh ra từ pha 5)
scripts/                  env-doctor.sh, approve-release.sh (+ smoke.sh do DevOps tạo)
```

## Tuỳ chỉnh

- **Thêm team** (ví dụ `unity-game-engineer`): tạo file trong `.claude/agents/<phòng ban>/`, thêm skill `kb-<stack>`, cập nhật `OWNERS` trong `.claude/hooks/guard_files.py` và bảng stack trong `company/templates/stack-selection.md`.
- **Agent teams** (tính năng thử nghiệm, cho phép teammate nhắn tin trực tiếp với nhau): đặt `"env": {"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"}` trong `.claude/settings.local.json` nếu muốn hội đồng phản biện chạy theo dạng team. Mặc định framework dùng subagent vì ổn định và rẻ hơn.
- **Chi phí:** agent ra quyết định dùng Opus, agent thực thi dùng Sonnet. Đổi model trong frontmatter của từng agent nếu cần.
