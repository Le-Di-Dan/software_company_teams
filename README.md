# Mobile App Software Company — Claude Code template

Một "công ty phần mềm" gồm **36 AI agent** chạy trong Claude Code để biến một ý tưởng app còn mơ hồ thành app mobile sẵn sàng publish lên App Store và Google Play. Bạn là **Product Owner (PO)**: bạn đưa ý tưởng, trả lời các câu hỏi audit và ra quyết định ở 4 cổng duyệt. Phần còn lại do công ty tự làm, gồm research, thiết kế, code, QA, compliance và chuẩn bị release.

## Bắt đầu một app mới

```bash
git clone <repo-template-này> my-new-app && cd my-new-app
bash scripts/setup.sh           # đổi ._claude → .claude, _CLAUDE.md → CLAUDE.md, rồi ghi lại máy này build được gì
git add -A && git commit -m "Set up company project"
claude                          # session tự chạy với vai trò delivery-director
```

Trong repo template, framework được cất dưới tên `._claude/` và `_CLAUDE.md` để khi phát triển chính framework, Claude Code không nạp agent, hook và sổ tay của công ty (không bị nhầm repo template là dự án app). Git không cho chạy script tự động khi clone, nên `scripts/setup.sh` là bước bắt buộc ngay sau khi clone. Script chạy lại an toàn (ví dụ trên máy thứ hai: không còn gì để đổi tên, chỉ chạy `env-doctor.sh`).

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
- **Cầu dao usage:** thanh trạng thái hiện gói tài khoản và mức usage 5 giờ / 7 ngày. Mỗi đầu phiên, hook tự nhận diện gói qua `claude auth status` và `~/.claude.json` (chỉ đọc thông tin hồ sơ, không đọc token) rồi lưu vào `state/account.json` (riêng từng máy). Ngưỡng phụ thuộc gói, vì phần việc còn chạy sau khi cầu dao nhảy (agent làm nốt việc, ghi bàn giao) tốn số token gần như nhau ở mọi gói, nên gói lớn chỉ cần chừa ít phần trăm hơn:

  | Gói | 5 giờ: ngừng giao việc / dừng hẳn | 7 ngày: ngừng giao việc / dừng hẳn |
  |---|---|---|
  | Pro | 75% / 80% | 95% / 98% |
  | Max 5x | 82% / 88% | 96% / 98% |
  | Max 20x | 88% / 93% | 97% / 99% |
  | API (trả theo token) | 85% / 95% của `budget_usd` | — |

  Cửa sổ 7 ngày chỉ nhảy khi rất gần giới hạn, vì 75% của tuần vẫn còn tương đương nhiều phiên 5 giờ, còn dừng theo tuần thì phải chờ nhiều ngày. Với API key không có cửa sổ giới hạn: nếu không đặt `budget_usd`, cầu dao không bao giờ nhảy và giám đốc sẽ nhắc bạn điều đó. Khi dừng, mọi agent ghi bàn giao vào `state/handoff/`, và giám đốc báo bạn giờ reset. Sau reset chạy `claude --continue`, giám đốc tự nạp bàn giao (skill `/resume-work`) và giao lại đúng việc cho đúng agent. Chỉnh trong `state/project.json → usage_policy`: `plan` (`auto` hoặc ghim `api`/`pro`/`max5x`/`max20x` nếu nhận diện sai), `budget_usd` cho API, `plans` để đổi ngưỡng một gói (ví dụ `{"max5x": {"soft_pct": 85}}`; các khoá `soft_pct`/`hard_pct` cho 5 giờ, `seven_day_soft_pct`/`seven_day_hard_pct` cho 7 ngày; đặt các khoá đó thẳng trong `usage_policy` thì áp cho mọi gói); muốn tạm dừng thủ công: `! touch state/handoff/PAUSE` (tiếp tục: `! rm state/handoff/PAUSE`).
- **Tiết kiệm token** (`cost_guard.py`, cấu hình ở `state/project.json → cost_policy`):
  - **Chọn model tự động theo `profile`.** `economy` (mặc định) dùng Opus cho devils-advocate, solution-architect, code-reviewer, product-manager và security-lead; `balanced` thêm Opus cho các nhóm R&D và monetization; `quality` thêm BA, compliance và legal. Muốn ghim riêng một agent thì dùng `model_overrides`, ví dụ `{"product-manager": "opus"}`.
  - **Không gọi lại agent đã nghỉ quá 4 phút** (`resume_idle_min`). Cache của sub-agent chỉ sống 5 phút, nên trường hợp đó công ty tạo agent mới đọc lại file thay vì gọi agent cũ.
  - **Đọc gọn.** Tài liệu trên 30KB phải đọc theo từng phần (tối đa 200 dòng mỗi lần); hook chặn `cat`/`sed` đổ cả file và gửi lại dàn ý của file cho agent.
  - **Chạy build/test một lần, đọc đúng chỗ lỗi** (`scripts/check.sh`, skill `kb-run-checks`). Mọi lệnh build/test/lint/typecheck (`flutter test`, `npx tsc`, `jest`, `pytest`, `./gradlew`, `xcodebuild`…) được hook tự chạy qua `check.sh`: log đầy đủ lưu ở `state/runs/`, agent chỉ nhận một dòng khi pass, còn khi fail thì nhận danh sách test lỗi kèm số dòng trong log và lệnh chạy lại riêng phần lỗi. Nhờ vậy không còn cảnh chạy lại một lệnh 10–15 phút chỉ để xem output. Lệnh build/test bị pipe sang `tail`/`grep` hoặc redirect ra file sẽ bị chặn. Code không đổi (HEAD + thay đổi chưa commit + file mới) thì trả kết quả lần trước ngay lập tức (`--fresh` để ép chạy; e2e/integration và build không bao giờ dùng cache). Log tự dọn: pass thì xoá log fail cũ của check đó, ngoài ra giới hạn 3 ngày, 3 log fail mỗi check, tổng 200 MB, mỗi log 20 MB (`cost_policy`: `runs_max_age_days`, `runs_keep_failed`, `runs_max_mb`, `runs_max_log_mb`). Cần giữ log làm bằng chứng thì thêm `--keep <feature-id>` (copy sang `docs/07-qa/evidence/`), muốn xoá sạch thì chạy `bash scripts/check.sh --clean`.
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

Sau khi chạy `scripts/setup.sh` (trong repo template là `_CLAUDE.md` và `._claude/`):

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
scripts/                  setup.sh, env-doctor.sh, check.sh, approve-release.sh, dashboard.py (+ smoke.sh do DevOps tạo)
```

## Tuỳ chỉnh

- **Thêm team** (ví dụ `unity-game-engineer`): tạo file trong `.claude/agents/<phòng ban>/`, thêm skill `kb-<stack>`, cập nhật `OWNERS` trong `.claude/hooks/guard_files.py` và bảng stack trong `company/templates/stack-selection.md`.
- **Agent teams** (tính năng thử nghiệm, cho phép teammate nhắn tin trực tiếp với nhau): đặt `"env": {"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"}` trong `.claude/settings.local.json` nếu muốn hội đồng phản biện chạy theo dạng team. Mặc định framework dùng subagent vì ổn định và rẻ hơn.
- **Chi phí:** agent ra quyết định dùng Opus, agent thực thi dùng Sonnet. Đổi model trong frontmatter của từng agent nếu cần.
