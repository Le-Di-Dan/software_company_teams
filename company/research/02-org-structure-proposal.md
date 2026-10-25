# Đề xuất cơ cấu tổ chức "Mobile App Software Company"

> **Bản cuối đã triển khai (2026-10-25): 33 agent.** Thay đổi so với đề xuất bên dưới theo quyết định của PO:
> - Thêm **R&D Center** gồm 3 team: `business-rnd-researcher` (nghiệp vụ và nghiên cứu khoa học), `uiux-rnd-researcher` (xu hướng UI/UX, UI của đối thủ, pattern, âm thanh và hình ảnh), `ai-rnd-researcher` (xu hướng AI, kiến trúc tích hợp AI).
> - Backend tách theo ngôn ngữ: `nodejs-backend-engineer`, `python-backend-engineer`, `go-backend-engineer`, thay cho `backend-server-engineer`.
> - BaaS tách thành `firebase-engineer` và `supabase-engineer`, thay cho `baas-engineer`.
> - Máy Mac hiện có Xcode và Flutter; máy Windows sẽ có đầy đủ toolchain. Repo hỗ trợ làm việc trên 2 máy.
> Danh sách hiện hành nằm trong `README.md` và `.claude/agents/`.
>
> Ngày: 2026-10-25 · Bản đề xuất ban đầu:
> Căn cứ: research cơ cấu team của các công ty phát triển mobile app (mục 1) + quyết định của PO (mục 2) + giới hạn kỹ thuật của Claude Code (docs/research/01-claude-code-multi-agent-company.md).

---

## 1. Thị trường: một công ty mobile app chuẩn có những vai trò nào?

Tổng hợp từ các công ty outsource/agency mobile (Innowise, Decode, Orangesoft, Empat, Andersen…):

| Lớp | Vai trò cốt lõi (team nào cũng có) | Vai trò bổ sung (dự án lớn / theo pha) |
|---|---|---|
| Lãnh đạo & quản lý | Product Manager, Project Manager / Delivery Manager | Tech Lead, Business Analyst |
| Thiết kế | UI/UX (Product) Designer | UX Researcher, Copywriter / UX Writer |
| Kỹ thuật | iOS dev, Android dev hoặc cross-platform dev, Backend dev | DevOps, Full-stack, Data/ML engineer |
| Chất lượng | QA Engineer (manual + automation) | QA automation riêng, Security specialist (pentest, compliance) |
| Sau ra mắt | — | Marketing / ASO, Data analyst, Technical support |

Các nhận xét chung của nguồn:
- Mô hình **hybrid theo pha** là phổ biến nhất: lõi nhỏ lúc build, thêm QA ở pha test, thêm marketing/copywriter trước launch, thêm support sau launch; chuyên gia ngắn hạn (security auditor, data scientist) chỉ gọi khi cần.
- App đơn giản: 4–5 người; trung bình 6–8; phức tạp 8–12+. **Tập trung quan trọng hơn số lượng.**
- Native iOS + Android tách riêng cần kỹ sư riêng cho mỗi nền tảng; cross-platform giảm nhu cầu này.
- Mô hình Spotify (squad / tribe / chapter / guild): kỹ sư cùng chuyên môn gom thành **chapter**, mỗi sản phẩm là một **squad** đa chức năng lấy người từ các chapter.

**Áp dụng**: các team ngôn ngữ (RN, Flutter, Swift, Kotlin) đóng vai **chapter**. Với mỗi app, Delivery Director ráp một **squad** gồm đúng các agent cần dùng. Agent không liên quan sẽ không được gọi, nên không tốn token.

---

## 2. Quyết định của PO và tác động

| Quyết định | Tác động lên thiết kế |
|---|---|
| 4 team ngôn ngữ: React Native, Flutter, Swift, Kotlin | 4 agent engineer riêng, mỗi agent preload skill kiến thức của stack đó. Solution Architect chọn stack theo bộ tiêu chí, **PO duyệt** tại Review Board |
| Backend server và BaaS là 2 team riêng | `backend-server-engineer` (API, DB, auth, deploy server) tách khỏi `baas-engineer` (Firebase/Supabase: schema, security rules/RLS, functions) |
| Không dùng EAS trả phí, có Mac + Xcode | Build và ký **local** (xcodebuild, Gradle, fastlane; RN dùng Expo prebuild/`expo run` hoặc bare RN). Không dùng Expo MCP vì cần gói trả phí. Dùng XcodeBuildMCP, iOS Simulator, Maestro (miễn phí) |
| Tài khoản Apple và Google đều là cá nhân | Release Manager phải lên kế hoạch **closed test 12 tester × 14 ngày** của Google Play từ sớm (song song pha Build). Apple Individual: tên người bán hiển thị là tên cá nhân của PO |

---

## 3. Cơ cấu đề xuất: 10 phòng ban, 27 agent

Ký hiệu model: **O** = opus (quyết định, kiến trúc, phản biện, rủi ro), **S** = sonnet (thực thi). Quyền: **RO** = chỉ đọc/research, **RW** = được sửa file.

### A. Ban điều hành
| # | Agent | Vai trò ngoài đời | Trách nhiệm | Model / quyền |
|---|---|---|---|---|
| 1 | `delivery-director` | CEO + Delivery/Project Manager | Session chính. Điều phối các pha, ráp squad, giữ state (`state/`), mở gate cho PO, gom câu hỏi để hỏi PO một lần | O / RW (chỉ file `state/`, `docs/`) |

### B. Business & Strategy
| # | Agent | Trách nhiệm | Model / quyền |
|---|---|---|---|
| 2 | `business-analyst` | **Audit PO** (phỏng vấn nhiều vòng), làm rõ mục tiêu, ràng buộc, phạm vi "không làm", viết brief + constitution | O / RW docs |
| 3 | `market-researcher` | Thị trường, đối thủ, phân tích review store của đối thủ, xu hướng, cơ hội khác biệt (chống Apple 4.3) | S / RO + web |
| 4 | `monetization-strategist` | Mô hình doanh thu (IAP, subscription, ads, freemium), pricing, paywall, unit economics, tuân thủ Apple 3.1.1 | O / RO + web |

### C. Product
| # | Agent | Trách nhiệm | Model / quyền |
|---|---|---|---|
| 5 | `product-manager` | PRD, user stories (acceptance criteria Given/When/Then), ưu tiên RICE/MoSCoW, roadmap, KPI, phạm vi MVP | O / RW docs |

### D. Design
| # | Agent | Trách nhiệm | Model / quyền |
|---|---|---|---|
| 6 | `ux-designer` | Personas, user flows, kiến trúc thông tin, wireframe (dạng text/Mermaid), heuristic usability | S / RW docs |
| 7 | `ui-designer` | Design system & tokens, spec từng màn hình theo **Apple HIG / Material 3**, dark mode, accessibility, các trạng thái empty/loading/error | S / RW docs |
| 8 | `ux-writer` | Microcopy, onboarding, thông báo lỗi, push notification, chuỗi i18n | S / RW docs |

### E. Engineering
| # | Agent | Trách nhiệm | Model / quyền |
|---|---|---|---|
| 9 | `solution-architect` | Tech Lead. **Chọn stack** (ma trận tiêu chí), kiến trúc, ADR, API contract, data model, khởi tạo dự án, `feature_list.json`, smoke script | O / RW |
| 10 | `react-native-engineer` | Team RN (TypeScript, Expo không trả phí hoặc bare RN) | S / RW |
| 11 | `flutter-engineer` | Team Flutter (Dart, state management, platform channels) | S / RW |
| 12 | `swift-ios-engineer` | Team iOS native (Swift, SwiftUI, XCTest/XCUITest, XcodeBuildMCP) | S / RW |
| 13 | `kotlin-android-engineer` | Team Android native (Kotlin, Jetpack Compose, Espresso, Gradle) | S / RW |
| 14 | `backend-server-engineer` | Server tự dựng: REST/GraphQL, DB, auth, background jobs, tài liệu API (OpenAPI) | S / RW |
| 15 | `baas-engineer` | Firebase/Supabase: schema, Security Rules/RLS, Cloud/Edge Functions, auth, storage, push | S / RW |
| 16 | `code-reviewer` | Review 2 tầng: (1) đúng spec/acceptance criteria, (2) chất lượng code theo stack. Chỉ báo lỗi ảnh hưởng correctness/yêu cầu | O / RO |

### F. Quality Assurance
| # | Agent | Trách nhiệm | Model / quyền |
|---|---|---|---|
| 17 | `qa-engineer` | Test plan, test case từ acceptance criteria, exploratory test trên simulator/emulator (chụp màn hình), báo cáo bug, regression | S / RO + chạy app |
| 18 | `test-automation-engineer` | Unit/widget/UI test theo stack, E2E **Maestro** chạy cả iOS và Android, đưa test vào CI | S / RW (chỉ thư mục test) |

### G. Security, Legal & Compliance
| # | Agent | Trách nhiệm | Model / quyền |
|---|---|---|---|
| 19 | `security-engineer` | OWASP MASVS/MASTG, lưu trữ dữ liệu, secrets, network security, quét dependency, review auth | O / RO |
| 20 | `store-compliance-officer` | App Store Review Guidelines, Google Play policy, privacy manifest, App Privacy labels, Data safety, age rating, xoá tài khoản. Fetch policy mới nhất mỗi lần kiểm tra. **Có quyền chặn release** | O / RO + web |
| 21 | `privacy-legal-counsel` | Privacy Policy, Terms of Use, EULA, consent (GDPR/CCPA/Nghị định 13 VN), đảm bảo tài liệu pháp lý khớp với dữ liệu app thu thập thật | O / RW docs |

### H. DevOps & Release
| # | Agent | Trách nhiệm | Model / quyền |
|---|---|---|---|
| 22 | `devops-engineer` | GitHub Actions CI, môi trường dev/staging/prod, secrets, hạ tầng server (Docker, hosting), crash monitoring (Crashlytics/Sentry), trang web tĩnh cho privacy policy / support URL | S / RW |
| 23 | `release-manager` | Versioning, ký app (certificate, provisioning profile, keystore), build local bằng fastlane/xcodebuild/Gradle, TestFlight, **kế hoạch closed test 12 tester × 14 ngày**, bộ hồ sơ submit, phased rollout | S / RW |

### I. Growth & Data
| # | Agent | Trách nhiệm | Model / quyền |
|---|---|---|---|
| 24 | `aso-marketing-specialist` | Store listing (tên, subtitle, keywords, mô tả), brief screenshot, kế hoạch launch | S / RW docs + web |
| 25 | `data-analyst` | Tracking plan (event analytics), KPI/funnel, sau launch phân tích số liệu đề xuất cải tiến | S / RW docs |

### J. Customer Success (sau launch)
| # | Agent | Trách nhiệm | Model / quyền |
|---|---|---|---|
| 26 | `support-feedback-analyst` | Đọc review store, crash report, phản hồi người dùng, phân loại rồi đưa vào backlog; soạn câu trả lời review | S / RO |

### K. Review Board (hội đồng phản biện, liên phòng ban)
| # | Agent | Trách nhiệm | Model / quyền |
|---|---|---|---|
| 27 | `devils-advocate` | Phản biện mọi quyết định lớn: ý tưởng có đáng làm không, feature thừa, rủi ro bị reject, rủi ro kỹ thuật, chi phí. Bắt buộc đưa phương án thay thế | O / RO |

Thành phần hội đồng tại mỗi gate (chạy bằng agent team hoặc workflow):
- **Gate Scope MVP**: product-manager, devils-advocate, solution-architect, store-compliance-officer, monetization-strategist.
- **Gate Stack**: solution-architect và đại diện các team ngôn ngữ liên quan, cùng devils-advocate.
- **Gate Release**: store-compliance-officer, security-engineer, qa-engineer, privacy-legal-counsel.

---

## 4. Vai trò cố ý KHÔNG tạo (và ai đảm nhận thay)

| Vai trò ngoài đời | Lý do không tạo | Ai đảm nhận |
|---|---|---|
| Sales / Account Manager | PO chính là khách hàng | — |
| Project Manager / Scrum Master riêng | Trùng với điều phối | `delivery-director` |
| Technical Writer | Mỗi agent tự viết tài liệu của mình theo template | architect (kỹ thuật), PM (sản phẩm) |
| Full-stack developer | Đã tách rõ mobile / server / BaaS | — |
| Data scientist / ML engineer | Chỉ cần khi app có AI/ML | Thêm khi có dự án cần |
| Game developer (Unity/Godot) | Ngoài phạm vi 4 stack | Thêm sau nếu cần |
| Web frontend | Chỉ cần trang tĩnh cho policy/support | `devops-engineer` |
| HR, Finance | Không áp dụng | — |

---

## 5. Agent nào được dùng ở pha nào

| Pha | Agent chính | Agent hỗ trợ / phản biện | Cách chạy |
|---|---|---|---|
| 0. Intake / Audit | business-analyst | director | Skill phỏng vấn PO (AskUserQuestion) |
| 1. Discovery | market-researcher, monetization-strategist | aso-marketing-specialist | Workflow fan-out, kiểm chứng chéo nguồn |
| 2. Product definition | product-manager, ux-designer | business-analyst, data-analyst (tracking plan) | Tuần tự |
| 3. Review Board → **Gate PO** | devils-advocate + hội đồng | — | Agent team / workflow |
| 4. Design | ui-designer, ux-writer | ux-designer, store-compliance-officer (HIG) | Tuần tự |
| 5. Architecture & init → **Gate stack** | solution-architect | security-engineer, team ngôn ngữ được chọn | Tuần tự + review |
| 6. Build loop | team ngôn ngữ được chọn, backend-server / baas | code-reviewer, test-automation-engineer | `/goal` + hooks, 1 feature/vòng |
| 7. QA | qa-engineer, test-automation-engineer | security-engineer | Maestro + simulator/emulator |
| 8. Release readiness → **Gate PO submit** | release-manager, store-compliance-officer | privacy-legal-counsel, aso-marketing-specialist, devops-engineer | Workflow audit theo checklist |
| 9. Maintain | support-feedback-analyst, data-analyst | team ngôn ngữ để fix | Routines định kỳ |

Lưu ý kỹ thuật:
- Tổng `description` của 27 agent cần dưới ~15k token. Mỗi description giữ khoảng 1–2 câu.
- Agent được xếp vào thư mục con theo phòng ban (`.claude/agents/engineering/...`). Claude Code quét đệ quy, định danh agent theo `name`.
- Kiến thức theo stack và policy nằm trong **skills** (vd `kb-react-native`, `kb-flutter`, `kb-swift`, `kb-kotlin`, `kb-appstore-guidelines`, `kb-play-policy`, `kb-apple-hig`, `kb-material3`). Engineer preload skill stack của mình; reviewer và QA nạp khi cần.
