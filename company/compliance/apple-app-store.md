# Apple App Store — Compliance Checklist

> Used by `store-compliance-officer` at three checkpoints: **P2** (after PRD), **P5** (architecture), **P8** (release).
> Policies change. Before every audit, fetch the live sources and note the fetch date in the audit report:
> - Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
> - Upcoming requirements: https://developer.apple.com/news/upcoming-requirements/
> - Privacy manifest / required reason APIs: https://developer.apple.com/documentation/bundleresources/privacy-manifest-files
> - App Store Connect help (metadata limits, age ratings): https://developer.apple.com/help/app-store-connect/
> Items marked *(verify)* were current at framework creation (2026-10) but must be re-checked.
>
> Severity: **B** = blocker (likely rejection) · **H** = high · **M** = medium. Check = how to verify with evidence.

## Build & technical
| ID | Rule | Sev | Check | When |
|---|---|---|---|---|
| A-T1 | Built with Xcode 26+ against the iOS 26 SDK (required for uploads since 2026-04-28) *(verify for newer minimum)* | B | `xcodebuild -version`; archive build settings | P5, P8 |
| A-T2 | `PrivacyInfo.xcprivacy` present; every Required Reason API used by the app and each third-party SDK is declared with an approved reason; listed SDKs ship their own manifest/signature | B | inspect manifest; grep for UserDefaults, file timestamp, disk space, boot time, keyboard APIs; SDK list | P5, P8 |
| A-T3 | No crashes / hangs on launch and core flows on current iOS + one older supported version | B | QA report, TestFlight crash logs | P8 |
| A-T4 | Works on IPv6-only networks; graceful offline / server-down handling | H | QA network test | P7 |
| A-T5 | Export compliance: `ITSAppUsesNonExemptEncryption` set correctly | M | Info.plist | P8 |
| A-T6 | No downloading/executing code that changes features (2.5.2); OTA JS updates only for bug fixes | B | architecture review | P5 |
| A-T7 | Only public APIs (2.5.1); background modes used only for their declared purpose (2.5.4) | H | code review, Info.plist `UIBackgroundModes` | P6, P8 |

## Completeness & metadata (2.1, 2.3)
| ID | Rule | Sev | Check | When |
|---|---|---|---|---|
| A-C1 | No placeholder text/images, "beta", "test", lorem ipsum, broken links, dead buttons | B | QA exploratory + grep | P8 |
| A-C2 | Reviewer can access everything: demo account (+ data) in App Review notes; backend live during review | B | `docs/08-release/review-notes.md` | P8 |
| A-C3 | IAP products created, submitted with the binary, purchasable in sandbox | B | sandbox test evidence | P8 |
| A-C4 | Screenshots show the real app UI on required device sizes; no other platform names/logos | B | listing review | P8 |
| A-C5 | Name ≤30 chars, subtitle ≤30, keywords ≤100 bytes; no competitor names/trademarks or pricing claims in metadata *(verify limits)* | H | listing lint | P8 |
| A-C6 | Age rating questionnaire (new 4+/9+/13+/16+/18+ system) answered truthfully, incl. UGC/social and AI content questions *(verify current questions)* | H | answers drafted in `docs/08-release/` | P8 |
| A-C7 | Support URL and Privacy Policy URL live and correct | B | open URLs | P8 |

## Design & business (3.x, 4.x)
| ID | Rule | Sev | Check | When |
|---|---|---|---|---|
| A-D1 | Minimum functionality (4.2): genuine native value, not a repackaged website or thin template | B | review board evidence of differentiation | P3, P8 |
| A-D2 | Not spam / duplicate (4.3): differentiated from existing apps, not one of many near-identical apps from this developer | B | market research + R&D differentiation | P3 |
| A-D3 | Digital goods/features unlocked only via Apple IAP (3.1.1); no steering to external payment unless current rules allow for the storefront *(verify)* | B | paywall review | P2, P8 |
| A-D4 | Subscriptions (3.1.2): clear price/period/trial before purchase, ongoing value, Restore Purchases, links to Terms (EULA) & Privacy in app and metadata | B | paywall screenshot | P4, P8 |
| A-D5 | Login services (4.8): if third-party/social login is offered, also offer an equivalent privacy-preserving option (e.g. Sign in with Apple) | B | auth design | P5 |
| A-D6 | Push notifications not required to use the app; no marketing pushes without explicit opt-in (4.5.4) | H | permission flow | P4 |
| A-D7 | Follows HIG: standard gestures/navigation behave as expected, supports Dynamic Type and Dark Mode where applicable | M | design review | P4 |

## Privacy & safety (5.1, 1.x)
| ID | Rule | Sev | Check | When |
|---|---|---|---|---|
| A-P1 | Privacy policy in App Store Connect and inside the app; describes all data collected, uses, third parties, retention, deletion | B | legal doc vs data map | P8 |
| A-P2 | App Privacy labels match actual collection including SDKs (analytics, crash, ads, AI providers) | B | data map vs SDK list | P8 |
| A-P3 | Account deletion inside the app if account creation exists (5.1.1(v)) — deletes account and associated data, not just deactivation | B | E2E flow | P2, P8 |
| A-P4 | Permission prompts only when needed, with specific `NS*UsageDescription` strings; app still works if denied where feasible | B | Info.plist + flow | P4, P8 |
| A-P5 | No forced login for features that don't need an account | H | flow review | P2 |
| A-P6 | App Tracking Transparency prompt before any cross-app tracking / IDFA (5.1.2) | B | ads/analytics config | P5, P8 |
| A-P7 | Personal data sent to third-party AI services is disclosed and the user gives explicit permission first (5.1.2(i)) *(verify)* | B | AI feature flow + privacy policy | P2, P8 |
| A-P8 | User-generated content (1.2): filtering, report, block, published contact info, timely moderation | B | feature design | P2, P8 |
| A-P9 | Health, medical, finance, kids (5.1.4 / Kids category) special rules applied if relevant; no unverified medical claims | B | domain review | P2 |
| A-P10 | AI-generated content: safeguards against harmful output, reporting path, no impersonation | H | AI R&D design | P2, P7 |

## Account (individual developer)
| ID | Rule | Sev | Check | When |
|---|---|---|---|---|
| A-A1 | Individual account: seller name shown on the store is the PO's legal name — PO confirmed this is acceptable | M | PO question at G0 | P0 |
| A-A2 | Paid Apps agreement, tax and banking completed by PO before monetized release | B | PO checklist | P8 |
