# Google Play — Compliance Checklist

> Used by `store-compliance-officer` at **P2**, **P5**, **P8**. Fetch live sources before each audit and record the date:
> - Developer Policy Center: https://play.google/developer-content-policy/
> - Target API requirements: https://developer.android.com/google/play/requirements/target-sdk
> - Testing requirements for new personal accounts: https://support.google.com/googleplay/android-developer/answer/14151465
> - Data safety: https://support.google.com/googleplay/android-developer/answer/10787469
> - Account deletion: https://support.google.com/googleplay/android-developer/answer/13327111
> Items marked *(verify)* were current at framework creation (2026-10) but must be re-checked.

## Account & release path (personal account)
| ID | Rule | Sev | Check | When |
|---|---|---|---|---|
| G-A1 | Personal accounts created after 2023-11-13 must run a **closed test with ≥12 testers opted in for ≥14 consecutive days** before applying for production access (confirmed on Google's help page 2026-10-25) | B | Play Console testing dashboard; release plan dates | P6 start, P8 |
| G-A2 | Apply for production access after the closed test (questionnaire about testing and feedback) | B | PO action | P8 |
| G-A3 | Developer identity verified; contact details valid | B | PO checklist | P0 |
| G-A4 | Testers must genuinely use the app; collect and act on their feedback (evidence used in production-access application) | H | feedback log in `docs/08-release/closed-test.md` | P7–P8 |

## Technical
| ID | Rule | Sev | Check | When |
|---|---|---|---|---|
| G-T1 | `targetSdk` ≥ 36 (Android 16) for new apps and updates since 2026-08-31 (extension to 2026-11-01 on request) *(verify)* | B | `build.gradle(.kts)` | P5, P8 |
| G-T2 | Publish as Android App Bundle (AAB) with Play App Signing; upload key stored outside git | B | release build | P8 |
| G-T3 | Native libraries support 16 KB memory page sizes *(verify)* | B | `zipalign -c -P 16` / Play pre-launch report | P8 |
| G-T4 | Edge-to-edge layouts and predictive back handled (behavior changes on recent API levels) | H | UI QA on API 35+ emulator | P7 |
| G-T5 | Foreground services declare types and justify them in Play Console | B | manifest | P5, P8 |
| G-T6 | Pre-launch report: no crashes, accessibility and security warnings reviewed | H | Play Console | P8 |

## Permissions & data
| ID | Rule | Sev | Check | When |
|---|---|---|---|---|
| G-P1 | Privacy policy URL in Play Console **and** inside the app | B | URL + screen | P8 |
| G-P2 | Data safety form accurate for app + all SDKs (collection, sharing, encryption in transit, deletion) | B | data map | P8 |
| G-P3 | Account deletion: in-app path **and** a web link where users can request deletion without reinstalling | B | flow + URL | P2, P8 |
| G-P4 | Sensitive permissions (SMS/Call Log, All files access, background location, exact alarms, full photo/video access, accessibility API…) only if core and declared; prefer the photo picker | B | manifest review | P5 |
| G-P5 | Prominent disclosure + consent before collecting personal/sensitive data not obviously expected | B | flow | P4 |

## Content & monetization
| ID | Rule | Sev | Check | When |
|---|---|---|---|---|
| G-C1 | Digital goods via Google Play Billing (alternative billing only where Google's programs allow) *(verify)* | B | paywall | P2, P8 |
| G-C2 | Subscriptions: clear terms, price, trial conversion, easy cancellation info | B | paywall screenshot | P4, P8 |
| G-C3 | Ads: declared in Console; no disruptive/deceptive ads; families-safe ad SDKs if children are in audience | B | ads config | P5, P8 |
| G-C4 | Target audience & content questionnaire + IARC content rating completed truthfully; Families policy if under-13 audience | B | Console answers draft | P8 |
| G-C5 | AI-generated content policy: prevent generating restricted content; in-app way for users to report/flag offensive AI output | B | AI feature design | P2, P7 |
| G-C6 | User-generated content: moderation, report, block, terms acceptance | B | feature design | P2 |
| G-C7 | Health / financial / news / government features: required declarations filled | B | domain review | P2, P8 |
| G-C8 | Store listing: title ≤30 chars, short description ≤80, full ≤4000; no keyword stuffing, misleading claims, or rankings/testimonials; icon 512×512, feature graphic 1024×500 *(verify)* | H | listing lint | P8 |
| G-C9 | No impersonation / IP infringement in name, icon, content | B | brand check | P4, P8 |
