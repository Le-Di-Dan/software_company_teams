# Research: Xây dựng "Software Company" tự động hoá bằng Claude Code multi-agent cho phát triển Mobile App

> Ngày research: 2026-10-25 · Claude Code đang dùng: v2.1.310
> Mục tiêu: Product Owner (PO) chỉ đưa ý tưởng mơ hồ + trả lời audit. Một tập agent đóng vai các team của công ty phần mềm tự research → thiết kế → code → QA → chuẩn bị publish lên App Store / Google Play, phản biện lẫn nhau, đóng gói thành repo GitHub để clone dùng lại cho mỗi app mới.

---

## 0. TL;DR — 10 kết luận quan trọng nhất

1. **Claude Code hiện có đủ primitive để dựng "công ty"**: subagents (vai trò), skills (quy trình/SOP), hooks (quality gate cứng), agent teams (team tranh luận), dynamic workflows (fan-out + kiểm chứng chéo), `/goal` (chạy tới khi đạt điều kiện), plugins/marketplace (đóng gói), routines (chạy định kỳ trên cloud). Không cần framework bên ngoài.
2. **Đừng cho mọi agent "chat tự do" với nhau.** Bài học từ MetaGPT và từ Anthropic: giao tiếp qua **artifact có cấu trúc** (PRD, user stories, ADR, `feature_list.json`, test report) ổn định hơn nhiều so với hội thoại. Tranh luận/phản biện chỉ dùng ở các **điểm quyết định** (review board), không dùng cho từng dòng code.
3. **Kiến trúc khuyến nghị: Orchestrator–Workers + Review Board.** Session chính đóng vai "Delivery Director" (chạy bằng `"agent"` trong `.claude/settings.json`), gọi subagent chuyên trách theo pha; tại các gate thì mở **agent team** hoặc **workflow adversarial** để phản biện.
4. **Mọi pha phải có "check chạy được"** (test, build, screenshot, checklist có pass/fail). Anthropic nhấn mạnh: không có verification thì agent dừng khi "trông có vẻ xong" — và PO lại thành người QA.
5. **Chạy dài hạn cần state ngoài context**: `feature_list.json` (chỉ được sửa field `passes`), `progress.md`, git commit mỗi feature, script `init.sh`/smoke test — đúng harness Anthropic công bố cho long-running agents.
6. **Agent teams vẫn là experimental**: không resume được teammate in-process, không nested team, tốn token cao, cần session interactive (không chạy với `-p`). → Dùng cho research/review/debate, **không** dùng làm xương sống cho toàn bộ pipeline.
7. **Chi phí token là ràng buộc thật**: multi-agent ≈ 15× token so với chat (Anthropic). Cần định tuyến model (Opus cho quyết định/kiến trúc/review, Sonnet cho code, Haiku cho việc lặt vặt) và giới hạn số agent.
8. **Mobile stack khuyến nghị cho solo + AI: Expo (React Native + TypeScript) + EAS** — một codebase cho 2 store, build iOS trên cloud (không bắt buộc Mac để build), có **Expo MCP** (build/submit), **Maestro MCP** cho E2E test, **XcodeBuildMCP**/iOS Simulator pane khi cần native.
9. **Compliance phải là một "phòng ban" riêng chạy từ pha thiết kế**, không phải bước cuối. Các lý do reject phổ biến (Apple 2.1, 5.1.1, 4.2/4.3, 3.1.1, 2.3; Google target API 36, closed testing 12 tester/14 ngày, Data safety) phải được biến thành checklist có thể kiểm tra tự động.
10. **Đóng gói: bắt đầu bằng GitHub *template repo***, không phải plugin. Lý do kỹ thuật: subagent trong plugin **không hỗ trợ** `hooks`, `mcpServers`, `permissionMode` — trong khi "công ty" cần các thứ này per-agent. Khi framework ổn định, tách phần skills/workflows dùng chung ra plugin marketplace.

Những điểm PO **vẫn phải tự làm** (không tự động hoá được): tạo/trả phí tài khoản Apple Developer & Google Play, ký hợp đồng thuế/ngân hàng, tuyển 12 tester thật cho Google Play (tài khoản cá nhân), cung cấp secrets/API keys, test trên thiết bị thật, bấm nút submit cuối cùng (khuyến nghị giữ là gate thủ công).

---

## 1. Bản đồ primitive của Claude Code và vai trò trong "công ty"

| Primitive | Là gì (theo docs) | Dùng trong công ty để |
|---|---|---|
| **CLAUDE.md** | Context nạp mỗi session, nên ngắn | "Sổ tay công ty": quy trình pha, quy ước repo, lệnh build/test. Giữ ngắn, chi tiết đưa vào skills |
| **Subagents** (`.claude/agents/*.md`) | Worker có system prompt, tools, model, memory riêng; context riêng, trả về summary | **Mỗi vai trò = 1 subagent**: BA, PM, UX, Architect, Mobile Dev, Backend Dev, QA, DevOps, Compliance, Critic |
| **Skills** (`.claude/skills/<name>/SKILL.md`) | Quy trình/kiến thức nạp theo nhu cầu, có thể gọi `/skill-name`, có thể chạy `context: fork` | **SOP của từng pha** (`/intake`, `/discovery`, `/prd`, `/design`, `/build-feature`, `/release-check`…) + knowledge base (HIG, Material 3, store guidelines) |
| **Hooks** (settings.json / frontmatter) | Script/prompt/agent chạy deterministic ở các event; exit 2 = chặn | **Quality gate cứng**: chặn hoàn thành task khi test fail, chặn sửa `feature_list.json` sai cách, chặn lệnh nguy hiểm, auto-lint sau Edit |
| **Agent teams** (experimental) | Lead + teammates, task list chung, nhắn tin trực tiếp, có thể phản biện nhau | **Review board / debate**: đánh giá ý tưởng, chọn feature, phản biện kiến trúc, điều tra bug nhiều giả thuyết |
| **Dynamic workflows** | Script JS điều phối hàng chục–trăm subagent, có schema output, có thể verify chéo, lưu thành `/command` | **Fan-out có kiểm chứng**: market research cross-check, audit compliance toàn app, review mọi file thay đổi, sửa tới khi typecheck pass |
| **`/goal`** | Stop-hook do model đánh giá; chạy turn liên tục tới khi điều kiện đạt | **Vòng build không giám sát**: "mọi feature trong feature_list.json passes=true và `npm test` exit 0" |
| **Permission modes / auto mode** | Classifier duyệt tool call thay người | Giảm prompt duyệt khi chạy dài; kết hợp allowlist + deny rules |
| **Worktrees / `isolation: worktree`** | Mỗi agent một git checkout riêng | Chạy song song nhiều dev agent không đè file nhau |
| **MCP servers** | Kết nối tool ngoài | Expo MCP, Maestro MCP, XcodeBuildMCP, Figma, GitHub, Supabase… |
| **Agent memory** (`memory: project`) | Thư mục nhớ bền vững per-agent (`.claude/agent-memory/<name>/`) | Mỗi phòng ban tích luỹ "bài học" qua nhiều app (vd QA nhớ lỗi hay gặp, Compliance nhớ lý do bị reject) |
| **Headless `claude -p` / Agent SDK** | Chạy không tương tác, output JSON | CI, script pipeline, GitHub Actions |
| **Routines / scheduled tasks** | Session cloud chạy theo lịch / API / GitHub event | **Giai đoạn maintain**: triage review store hằng tuần, kiểm tra policy mới, dependency update |
| **Plugins + marketplace** | Đóng gói skills/agents/hooks/MCP/workflows, cài qua `/plugin marketplace add owner/repo` | Phân phối framework dùng chung giữa các repo app (giai đoạn sau) |

### Các chi tiết kỹ thuật quan trọng (đã xác minh trong docs hiện hành)

**Subagent frontmatter** (chỉ `name`, `description` bắt buộc): `tools`, `disallowedTools`, `model` (`sonnet|opus|haiku|fable|inherit|<id>`), `permissionMode`, `maxTurns`, `skills` (preload), `mcpServers`, `hooks` (PreToolUse/PostToolUse/Stop), `memory` (`user|project|local`), `background`, `effort`, `isolation: worktree`, `color`, `initialPrompt`, `omitClaudeMd`, `autoCompactWindow`.
- Subagent **có thể spawn subagent lồng nhau** tới 3 tầng (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`), tối đa 20 chạy đồng thời (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`).
- Giới hạn agent được spawn: `tools: Agent(ba, pm), Read` — rất hữu ích để "trưởng phòng" chỉ gọi được nhân viên phòng mình.
- Subagent **không thấy lịch sử hội thoại** và có thể không nạp CLAUDE.md → prompt giao việc phải tự đủ (đường dẫn artifact, tiêu chí xong).
- Subagent được đặt tên có thể **nhắn nhau qua `SendMessage`** và được resume với đầy đủ lịch sử.
- Chạy cả session như một agent: `claude --agent delivery-director` hoặc `"agent": "delivery-director"` trong `.claude/settings.json`; `initialPrompt` tự gửi turn đầu → đúng nhu cầu "clone về và khởi chạy".
- Tổng description của tất cả agents > 15.000 token sẽ cảnh báo → mô tả phải ngắn, phân biệt rõ.

**Agent teams**: bật bằng `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. Teammate dùng lại định nghĩa subagent (`tools`, `model`, body), nhưng **không áp dụng `skills`** của định nghĩa. Hooks riêng: `TeammateIdle`, `TaskCreated`, `TaskCompleted` (exit 2 để chặn/ép làm tiếp). Khuyến nghị 3–5 teammate, 5–6 task/teammate. Hạn chế: 1 team/session, không nested team, lead cố định, `/resume` không khôi phục teammate in-process, task status có thể lag, chỉ chạy ở session interactive.

**Hooks** có 5 loại handler: `command`, `http`, `prompt` (model đánh giá 1 lượt), `agent` (subagent kiểm tra điều kiện rồi quyết định), `mcp_tool`. Event quan trọng cho công ty: `SessionStart` (nạp state dự án), `PreToolUse` (chặn hành vi), `PostToolUse` (lint/format), `SubagentStop` & `TaskCompleted` (gate "Definition of Done"), `Stop` (không cho dừng khi chưa đạt), `PreCompact` (lưu state trước khi nén context).

**Dynamic workflows**: script JS với `agent()`, `pipeline()`, `parallel()`, `phase()`, `schema` cho output JSON; tối đa 16 agent đồng thời, 1000 agent/run; resume được; **không nhận input người dùng giữa run** → mỗi gate cần PO duyệt phải tách thành workflow riêng. Lưu ở `.claude/workflows/` → thành `/command`. Kích hoạt bằng từ khoá `ultracode` hoặc "use a workflow".

**`/goal`**: evaluator (model nhỏ) chỉ đọc transcript, **không tự chạy lệnh** → điều kiện phải là thứ agent in ra được (vd "`npm test` exit 0"). Hỗ trợ cả `claude -p "/goal ..."`.

---

## 2. Bài học từ Anthropic (engineering blog + docs best practices)

### 2.1 "How we built our multi-agent research system"
- Orchestrator–worker: lead lập kế hoạch, **lưu plan ra memory/file**, spawn 3–5 subagent song song; subagent trả kết quả cô đọng.
- Multi-agent (Opus lead + Sonnet workers) hơn single-agent **90,2%** trên eval research nội bộ, nhưng tốn **~15× token** so với chat. Hợp với việc **breadth-first, song song hoá được**; **kém** với việc cần chia sẻ context chặt như phần lớn coding.
- Giao việc phải có: mục tiêu, format output, tool/nguồn nên dùng, ranh giới rõ — giao việc mơ hồ gây trùng lặp và bỏ sót.
- Quy tắc scale nỗ lực: việc đơn giản 1 agent; so sánh 2–4 agent; phức tạp >10 agent. Lỗi sớm: spawn 50 agent cho câu hỏi đơn giản.
- Đánh giá theo **kết quả cuối**, dùng LLM-as-judge với rubric; bắt đầu với ~20 case thật.
- Lưu kết quả ra storage ngoài, truyền **tham chiếu** (đường dẫn file) thay vì nhồi toàn bộ qua lead.

→ **Áp dụng**: Pha research/discovery và audit = multi-agent song song. Pha code = ít agent, tuần tự theo feature, chia sẻ context qua file.

### 2.2 "Effective harnesses for long-running agents"
- **Initializer agent** (chạy 1 lần): tạo `init.sh`, `claude-progress.txt`, git commit đầu, **feature list JSON** (ví dụ >200 feature, tất cả `passes: false`).
- **Coding agent** (mỗi session): `pwd` → đọc git log + progress → chọn feature ưu tiên cao nhất chưa pass → chạy `init.sh` + smoke test → làm **1 feature** → test E2E như người dùng → commit + cập nhật progress.
- Chỉ được sửa field `passes`; cấm xoá/sửa test. Dùng JSON vì model ít "tự tiện" sửa JSON hơn Markdown.
- Không nhắc thì Claude chỉ unit test/curl và bỏ sót lỗi E2E → phải ép test bằng automation thật (với mobile: Maestro / simulator screenshot).

→ **Áp dụng trực tiếp** cho pha Build: Architect = initializer; Mobile/Backend Dev = coding agent.

### 2.3 "Building effective agents" — 5 pattern
Prompt chaining · Routing · Parallelization (sectioning / voting) · Orchestrator-workers · Evaluator-optimizer. Nguyên tắc: **đơn giản nhất có thể**, minh bạch kế hoạch, đầu tư vào mô tả tool.
→ Pipeline pha = prompt chaining có gate; chọn agent theo loại việc = routing; review board = voting; dev↔reviewer = evaluator-optimizer.

### 2.4 "Effective context engineering"
Context là tài nguyên hữu hạn; system prompt "đúng độ cao" (không if-else cứng, không mơ hồ); ví dụ canonical tốt hơn danh sách luật; retrieval just-in-time; **structured note-taking** ra file; subagent trả summary 1–2k token.

### 2.5 Claude Code best practices (docs)
- **Cho Claude cách tự verify** — quan trọng nhất. Mức độ gate: prompt → `/goal` → Stop hook → subagent/workflow reviewer độc lập.
- **Explore → Plan → Code → Commit**.
- **"Let Claude interview you"** bằng `AskUserQuestion`, rồi viết `SPEC.md`, sau đó **mở session mới** để thực thi → chính là pha Audit của công ty.
- **Writer/Reviewer** ở context riêng (reviewer không bị thiên vị code mình viết).
- **Cảnh báo over-engineering**: reviewer được bảo "tìm lỗi" sẽ luôn tìm ra lỗi → phải dặn chỉ báo lỗi ảnh hưởng correctness/yêu cầu.
- CLAUDE.md ngắn; cái gì cần đúng 100% thì chuyển thành hook.

---

## 3. Prior art từ cộng đồng — học gì, tránh gì

| Dự án | Ý tưởng chính | Nên mượn | Lưu ý |
|---|---|---|---|
| **BMAD-METHOD** (bmad-code-org, MIT) | Agile AI-driven: Analyst → PM (PRD) → Architect → Scrum Master (story siêu chi tiết) → Dev (1 story/lần) → QA. V6 có 12+ persona (UX, security, DevOps…) | Chuỗi persona + **story file tự chứa đủ context** cho dev agent; tách pha Planning và Implementation | Khá nặng tài liệu; dễ phình prompt. Lấy cấu trúc, không cần copy nguyên |
| **GitHub Spec Kit** (MIT) | Spec-driven: `/speckit.constitution` → `specify` → `plan` → `tasks` → `implement` | Khái niệm **constitution** (nguyên tắc bất biến của dự án: platform, a11y, privacy, store compliance) mà mọi agent phải tuân theo | Không có khái niệm team/phản biện; cần bổ sung |
| **Superpowers** (obra) | Skills: brainstorming → git worktree → writing-plans (task 2–5 phút, đường dẫn file chính xác, bước verify) → subagent-driven-development (subagent mới mỗi task, **review 2 tầng: đúng spec rồi mới tới chất lượng code**) + TDD | Pattern **review 2 tầng** và **task granularity** rất hợp cho Build | Thiên về coding; không có business/compliance |
| **Contains Studio agents / wshobson / VoltAgent collections** | Thư viện 50–100+ subagent theo phòng ban (engineering, design, marketing: `app-store-optimizer`, `mobile-app-builder`, `rapid-prototyper`, `studio-coach`…) | Tham khảo **nội dung prompt** cho từng vai trò mobile/ASO | Nhiều fork, chất lượng không đồng đều, không có quy trình gate; đừng cài nguyên bộ (vượt budget description 15k token, routing loạn) |
| **MetaGPT / ChatDev** (nghiên cứu) | Mô phỏng công ty phần mềm: PM→Architect→PM→Engineer→QA theo SOP; ChatDev theo waterfall chat-chain | **Giao tiếp qua artifact chuẩn hoá** (PRD, design doc, task list) thay vì chat tự do → giảm trôi chủ đề, trùng việc | Waterfall cứng; thiếu vòng feedback thực tế (chạy test thật) |

**Tổng hợp**: Framework của bạn nên = *Spec Kit constitution* + *BMAD role chain & story files* + *Anthropic long-running harness (feature_list.json)* + *Superpowers 2-stage review* + *Agent teams/workflows cho debate* + *Compliance department riêng cho mobile store*.

---

## 4. Tooling riêng cho Mobile

| Nhu cầu | Công cụ | Ghi chú |
|---|---|---|
| Framework app | **Expo / React Native + TypeScript** (khuyến nghị mặc định) | 1 codebase 2 nền tảng; Claude rất mạnh với TS; ít phụ thuộc Xcode cho phần lớn công việc |
| Build & submit | **EAS Build / EAS Submit** + **Expo MCP** (`claude mcp add --transport http expo-mcp https://mcp.expo.dev/mcp`) | Expo MCP có tool trigger build và submit store (từ 02/2026); **cần EAS paid plan**; local capabilities cần SDK 54+ |
| Native iOS | **XcodeBuildMCP** (Sentry) | Build, simulator, log, UI automation cho Swift/SwiftUI |
| Xem & thao tác simulator | **Claude Code Desktop – iOS Simulator pane** (beta, macOS, local session); CLI dùng computer use | Agent tự build, mở app, tap, chụp màn hình để verify UI. Không chạy trong cloud session |
| E2E test đa nền tảng | **Maestro + Maestro MCP** | Agent đọc màn hình, viết flow YAML, chạy trên emulator/simulator, tự sửa tới khi pass; flow chạy được trong CI |
| Android | Android Emulator + `adb` + Gradle | Bắt buộc `targetSdk = 36` cho app mới/update từ 31/08/2026 |
| Design | Figma MCP (tùy chọn); token hoá design system theo Apple HIG / Material 3 | Agent UX có thể xuất spec màn hình + design tokens thay vì Figma nếu PO không cần |
| Backend tối thiểu | BaaS (Supabase/Firebase) trước, custom server khi thật sự cần | Giảm gánh nặng infra cho solo dev |
| Kiếm tiền | RevenueCat (IAP/subscription), AdMob | Phải tuân thủ Apple 3.1.1 (digital goods qua IAP) |
| CI | GitHub Actions + `claude -p` / claude-code-action; EAS Workflows | QA gate tự động trên mỗi PR |

**Ràng buộc nền tảng**: build iOS native local cần macOS + Xcode 26+ (Apple yêu cầu upload build bằng Xcode 26 / SDK 26 từ 28/04/2026). Cloud session của Claude (Projects, routines) chạy Linux → không có simulator iOS; dùng EAS cloud build cho iOS khi chạy trên cloud.

---

## 5. Kiến thức Store Compliance phải đưa vào knowledge base

> Nguồn phần này phần lớn là blog bên thứ 3 + trang Apple/Google; agent Compliance **phải fetch lại trang chính thức mỗi lần chạy release-check** vì policy thay đổi liên tục.

### Apple App Store — nhóm lý do reject phổ biến
- **2.1 App Completeness** (nhóm lớn nhất): crash, placeholder, link chết, reviewer không đăng nhập được → luôn cung cấp **demo account** + review notes.
- **5.1.1 Privacy**: privacy policy, xin quyền có lý do rõ (purpose strings), **5.1.1(v) có tạo tài khoản thì phải xoá tài khoản được trong app**, App Privacy labels khớp thực tế.
- **Privacy manifest** (`PrivacyInfo.xcprivacy`): khai báo Required Reason APIs; SDK bên thứ ba cần manifest riêng.
- **4.2 Minimum functionality** (web wrapper, app quá mỏng) và **4.3 Spam** (app trùng lặp/template) — **rủi ro đặc biệt cao với app do AI sinh hàng loạt**. Pha Discovery phải chứng minh điểm khác biệt.
- **3.1.1 IAP**: nội dung số phải mua qua IAP.
- **2.3 Metadata**: screenshot/mô tả phải khớp app thật.
- **Age rating**: hệ thống mới 4+/9+/13+/16+/18+, bắt buộc trả lời bộ câu hỏi mới (hạn 31/01/2026); có báo cáo về câu hỏi bổ sung cho social feed năm 2026 — cần xác minh.
- **Build**: Xcode 26+ / SDK 26 từ 28/04/2026.

### Google Play
- **Target API**: từ **31/08/2026**, app mới & update phải target **Android 16 (API 36)** (gia hạn tới 01/11/2026 nếu xin).
- **Tài khoản cá nhân tạo sau 13/11/2023**: phải **closed test với ≥12 tester opt-in liên tục 14 ngày** trước khi mở Production; tài khoản tổ chức (D-U-N-S) được miễn. → Đây là việc PO phải lên kế hoạch sớm, agent không làm thay được.
- **Data safety form**, privacy policy, xoá tài khoản (cả trong app và qua web link), quyền nhạy cảm cần khai báo.

→ **Thiết kế**: biến các mục trên thành `compliance/checklist-ios.yaml` & `checklist-android.yaml` với từng mục có *cách kiểm tra* (grep code, kiểm tra file, screenshot, câu hỏi cho PO). Compliance agent chạy checklist ở **3 thời điểm**: sau PRD (chặn feature rủi ro), trước code freeze, trước submit.

---

## 6. Kiến trúc đề xuất cho "Mobile App Software Company"

### 6.1 Sơ đồ tổ chức (subagents)

```
                         Product Owner (bạn) — chỉ ở các GATE
                                      │
                   ┌──────────────────┴──────────────────┐
                   │  delivery-director (session chính)   │  ← "agent" trong settings.json
                   │  điều phối pha, quản lý state, gate  │     model: opus
                   └──────────────────┬──────────────────┘
   ┌───────────┬───────────┬──────────┼───────────┬────────────┬─────────────┐
 Business    Product     Design    Engineering    Quality     Release &    Review
 ─────────   ───────     ──────    ───────────    ───────     Ops          Board
 market-     product-    ux-       solution-      qa-         devops-      critic /
 researcher  manager     designer  architect      engineer    engineer     devil's-advocate
 business-   (PRD,       ui-       mobile-        (Maestro,   (EAS, CI,    (phản biện mọi
 analyst     stories,    designer  engineer       simulator,  envs,        quyết định lớn)
 monetiza-   flows,      (HIG/M3)  backend-       test plan)  secrets)
 tion/ASO    priority)             engineer                   store-
                                   code-reviewer              compliance-
                                                              officer
```

Gợi ý model/effort: Opus cho director, architect, critic, compliance; Sonnet cho dev/QA/designer; Haiku cho tác vụ đọc/tóm tắt. Giới hạn tool theo vai trò (researcher/critic/compliance **read-only**; chỉ dev được Edit code; chỉ devops chạm EAS/CI).

### 6.2 Pipeline pha + gate

| Pha | Người làm | Cơ chế Claude Code | Artifact đầu ra | Gate |
|---|---|---|---|---|
| **0. Intake / Audit** | director + business-analyst | Skill `/intake`: phỏng vấn PO bằng `AskUserQuestion` theo vòng (mục tiêu, người dùng, nền tảng, kiếm tiền, ràng buộc, "không làm gì") | `docs/00-brief.md`, `constitution.md` | **PO xác nhận brief** |
| **1. Discovery** | market-researcher, monetization | **Workflow** fan-out: đối thủ, review store của đối thủ, ASO keywords, mô hình kiếm tiền; cross-check nguồn | `docs/01-market.md` (có nguồn) | — |
| **2. Product definition** | product-manager, ux-designer | Skill `/prd` | PRD, personas, user stories (INVEST + acceptance criteria Given/When/Then), user flows (Mermaid), MoSCoW | — |
| **3. Review board** | critic + architect + compliance + PM | **Agent team** (debate) hoặc workflow "draft from several angles" | `docs/03-decision.md`: feature nào đáng làm (điểm RICE/value-effort), rủi ro 4.2/4.3, rủi ro kỹ thuật, MVP scope | **PO duyệt scope MVP** |
| **4. Design** | ui-designer | Skill `/design` + HIG/Material 3 knowledge | design tokens, danh sách màn hình, spec component, trạng thái empty/error/loading, a11y | (tùy chọn) PO xem mockup |
| **5. Architecture & init** | solution-architect (= initializer) | Skill `/init-project` | ADRs, scaffold Expo, `feature_list.json`, `progress.md`, `scripts/smoke.sh`, CI, Maestro skeleton | Build + smoke pass |
| **6. Build loop** | mobile-engineer / backend-engineer | `/goal` hoặc Stop hook; 1 feature/vòng; `isolation: worktree` khi song song; review 2 tầng (spec → code quality) bởi code-reviewer | code + test + commit mỗi feature | Hook `SubagentStop`/`TaskCompleted`: test pass mới được đánh `passes: true` |
| **7. QA** | qa-engineer | Maestro MCP + simulator/emulator screenshot; workflow review toàn bộ flow | test report, bug list → quay lại pha 6 | Tất cả E2E pass |
| **8. Release readiness** | compliance-officer, monetization/ASO, devops | **Workflow** audit theo checklist iOS/Android (fetch guideline mới nhất) | store listing, screenshots, privacy labels, data safety, review notes, demo account | **PO duyệt & bấm submit** |
| **9. Maintain** | routines | Scheduled tasks: đọc review/crash, kiểm tra policy & SDK deadline, dependency update | issue/PR định kỳ | PO duyệt PR |

### 6.3 Cơ chế giao tiếp & phản biện (trả lời câu hỏi "agents giao tiếp và phản biện nhau")

1. **Kênh mặc định — artifact trên đĩa** (`docs/`, `state/`): mỗi agent đọc input từ file của pha trước, ghi output theo template. Director truyền **đường dẫn**, không truyền nội dung.
2. **Phản biện có cấu trúc tại gate**: dùng agent team (3–5 teammate: PM bảo vệ, Critic tấn công, Architect/Compliance đánh giá khả thi) với lệnh rõ "cố bác bỏ đề xuất của nhau, chỉ giữ cái còn đứng vững"; hoặc workflow với các agent độc lập chấm điểm rồi tổng hợp (voting).
3. **Evaluator–optimizer trong build**: dev viết → code-reviewer (context mới) kiểm tra theo spec trước, chất lượng sau → dev sửa. Reviewer chỉ báo lỗi ảnh hưởng correctness/yêu cầu.
4. **Hỏi chéo khi cần**: subagent được đặt tên có thể `SendMessage` cho nhau; ghi các câu hỏi chưa giải quyết vào `state/open-questions.md` để director gom hỏi PO một lần.
5. **Decision log**: mọi quyết định lớn ghi ADR (bối cảnh, lựa chọn, lý do, phương án bị loại) → agent sau không tranh luận lại.

### 6.4 Bố cục repo template đề xuất

```
mobile-company-template/
├── CLAUDE.md                     # ngắn: quy trình pha, lệnh, quy ước
├── .claude/
│   ├── settings.json             # "agent": "delivery-director", permissions, hooks, env
│   ├── agents/                   # 1 file / vai trò (ở mục 6.1)
│   ├── skills/
│   │   ├── intake/               # SKILL.md + question-bank.md
│   │   ├── prd/  design/  init-project/  build-feature/  qa/  release-check/
│   │   └── kb-apple-hig/  kb-material3/  kb-appstore-guidelines/  kb-play-policy/
│   ├── workflows/                # market-research.js, compliance-audit.js, review-board.js
│   └── hooks/                    # guard-feature-list.sh, require-tests.sh, block-secrets.sh
├── company/
│   ├── constitution.template.md
│   ├── templates/                # brief, PRD, story, ADR, test-report, store-listing
│   └── compliance/               # checklist-ios.yaml, checklist-android.yaml
├── docs/                         # artifact của app hiện tại (sinh ra khi chạy)
├── state/                        # phase.json, feature_list.json, progress.md, open-questions.md
└── app/                          # code Expo (sinh ra ở pha 5)
```

Khởi chạy: clone → `claude` → director tự chạy `initialPrompt` → hỏi ý tưởng → bắt đầu pha 0. `state/phase.json` + hook `SessionStart` giúp mở lại session là biết đang ở pha nào.

### 6.5 Đóng gói & phân phối

- **Giai đoạn 1 — GitHub Template Repo** (khuyến nghị): đúng workflow "clone về chạy"; agent trong `.claude/agents/` hỗ trợ đủ `hooks`, `mcpServers`, `permissionMode`.
- **Giai đoạn 2 — Plugin marketplace**: tách phần dùng chung (skills KB, workflows, agents không cần hooks) thành plugin `mobile-company@your-marketplace`; template repo khai báo `extraKnownMarketplaces` + `enabledPlugins` trong `.claude/settings.json` để tự cài. Lợi ích: cập nhật framework một chỗ, mọi repo app nhận bản mới.
- Kiểm thử framework: `claude plugin validate`, `claude plugin eval` (evals cho plugin) — chạy thử với 3–5 ý tưởng app mẫu và chấm kết quả.

---

## 7. Rủi ro & hạn chế cần chấp nhận

| Rủi ro | Giảm thiểu |
|---|---|
| Chi phí token cao (multi-agent ~15×) | Chỉ dùng team/workflow ở pha research & gate; model routing; `workflowSizeGuideline: small/medium`; đo bằng `/cost`, `/workflows` |
| Agent teams experimental (không resume, lag task status) | Không phụ thuộc team cho state; state luôn nằm ở `state/` + git |
| Agent tuyên bố "xong" sớm | `feature_list.json` + hook chặn + `/goal` với điều kiện kiểm chứng được |
| Reviewer gây over-engineering | Rubric: chỉ lỗi correctness/yêu cầu; phần còn lại là "optional" |
| Context phình / quên luật | CLAUDE.md ngắn, SOP ở skills, luật quan trọng thành hook |
| App AI-generated bị Apple 4.2/4.3 | Gate ở Review board: bắt buộc có "điểm khác biệt" và chức năng native thực chất |
| Policy store thay đổi | Compliance fetch nguồn chính thức mỗi lần; routine kiểm tra hàng tháng |
| Bảo mật (secrets, lệnh nguy hiểm) | deny rules, hook block secrets, sandbox, auto mode; không đưa secrets vào repo |
| Không test được thiết bị thật | PO test thủ công trước submit; TestFlight / internal testing track |
| iOS cần macOS cho native/simulator | Dùng EAS cloud build; simulator pane trên Desktop Mac khi có |

---

## 8. Lộ trình xây framework đề xuất

1. **MVP (1 app thử nghiệm)**: director + 6 agent cốt lõi (business-analyst, product-manager, ux-designer, solution-architect, mobile-engineer, qa-engineer) + compliance-officer; skills `/intake`, `/prd`, `/init-project`, `/build-feature`, `/release-check`; hook bảo vệ `feature_list.json` và require-tests. Chưa bật agent teams.
2. **v1**: thêm critic + review board (agent team), workflows market-research & compliance-audit, Maestro MCP, Expo MCP, agent memory `project`.
3. **v2**: backend-engineer + devops, CI GitHub Actions, routines cho maintain, tách plugin marketplace, eval suite cho framework.

---

## 9. Nguồn

**Anthropic / Claude Code docs**
- Subagents: https://code.claude.com/docs/en/sub-agents
- Agent teams: https://code.claude.com/docs/en/agent-teams
- So sánh cách chạy song song: https://code.claude.com/docs/en/agents
- Dynamic workflows: https://code.claude.com/docs/en/workflows
- Skills: https://code.claude.com/docs/en/skills
- Hooks: https://code.claude.com/docs/en/hooks
- `/goal`: https://code.claude.com/docs/en/goal
- Best practices: https://code.claude.com/docs/en/best-practices
- Plugin marketplace: https://code.claude.com/docs/en/plugins/create-marketplace
- Scheduled tasks (routines): https://code.claude.com/docs/en/routines
- Projects: https://code.claude.com/docs/en/claude-projects
- iOS Simulator pane: https://code.claude.com/docs/en/desktop-ios-simulator
- Docs index: https://code.claude.com/docs/llms.txt

**Anthropic engineering**
- Multi-agent research system: https://www.anthropic.com/engineering/multi-agent-research-system
- Effective harnesses for long-running agents: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- Building effective agents: https://www.anthropic.com/engineering/building-effective-agents
- Effective context engineering: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

**Cộng đồng / prior art**
- BMAD method: https://codemyspec.com/blog/bmad-method-explained · https://medium.com/@visrow/a-tale-of-two-frameworks-bmad-method-vs-github-spec-kit-c021ab0ad037
- GitHub Spec Kit: https://visualstudiomagazine.com/articles/2025/09/03/github-open-sources-kit-for-spec-driven-ai-development.aspx
- Superpowers: https://github.com/obra/superpowers
- Contains Studio agents (fork): https://github.com/LeanAgents/agents · VoltAgent collection: https://dev.to/voltagent/100-claude-code-subagent-collection-1eb0
- MetaGPT: https://www.noze.it/en/insights/metagpt-open-source/

**Mobile tooling**
- Expo MCP: https://docs.expo.dev/eas/ai/mcp · https://expo.dev/changelog/mcp-build-and-workflows
- Maestro MCP: https://maestro.dev/mcp · https://verygood.ventures/blog/maestro-mcp-claude-mobile-ui-test-automation/
- XcodeBuildMCP: https://sentry.io/resources/xcodebuildmcp-workshop/

**Store policy**
- Google Play target API: https://developer.android.com/google/play/requirements/target-sdk
- Google Play 12 testers: https://www.testerscommunity.com/blog/google-play-closed-testing-requirements-2026 (bên thứ 3 — cần đối chiếu Play Console Help)
- Apple SDK minimum: https://developer.apple.com/news/upcoming-requirements/ · https://expo.dev/blog/app-store-connect-minimum-sdk-26
- Apple Required Reason API: https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api
- Lý do reject phổ biến: https://expo.dev/articles/shipping-to-the-app-stores/app-store-rejection-reasons · https://qawerk.com/blog/app-store-rejection-reasons/
- Apple age rating: https://www.igeeksblog.com/apple-app-store-age-ratings/
