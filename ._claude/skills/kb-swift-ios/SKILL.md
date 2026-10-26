---
name: kb-swift-ios
description: Swift iOS team conventions - SwiftUI architecture, concurrency, SPM modules, theming from design tokens, current iOS design language, testing (Swift Testing/XCTest, XCUITest, Maestro), Xcode/XcodeBuildMCP commands and pitfalls.
user-invocable: false
---

# Swift / SwiftUI conventions

## Setup
- Latest Xcode on the Mac (App Store uploads require the current minimum SDK; check developer.apple.com/news/upcoming-requirements). Swift 6 language mode with strict concurrency where feasible.
- `apps/ios/`: Xcode project + local Swift packages: `Features/<Feature>`, `DesignSystem`, `Core` (networking, persistence, analytics), `AppTests`, `AppUITests`.

## Patterns
- SwiftUI + Observation (`@Observable`), unidirectional data flow per feature; dependency injection via environment or a lightweight container.
- Navigation: `NavigationStack` with typed paths; deep links via `onOpenURL`.
- Async/await, actors for shared mutable state; no blocking the main actor.
- Persistence: SwiftData or GRDB/Core Data per architecture; Keychain for secrets/tokens.
- Theming: design tokens → `Color`/`Font` extensions and asset catalog colors with dark variants; SF Symbols with consistent weights; support Dynamic Type.
- Adopt the current iOS visual language (materials, toolbar/tab styles) per HIG; widgets/Live Activities only if in scope.
- Motion: SwiftUI animations/transitions, `matchedGeometryEffect`, `PhaseAnimator`/`KeyframeAnimator`; Lottie/Rive packages if needed; `sensoryFeedback` / `UIImpactFeedbackGenerator` for haptics.
- StoreKit 2 for IAP/subscriptions (or RevenueCat if approved).

## Quality commands
- With XcodeBuildMCP: build/run on simulator, capture screenshots and logs.
- Otherwise: `xcodebuild -scheme <App> -destination 'platform=iOS Simulator,name=iPhone 16' test`, `xcrun simctl` for boot/install/screenshot; SwiftLint/SwiftFormat if configured; `maestro test tests/e2e/...`.

## Pitfalls
- `PrivacyInfo.xcprivacy` must declare Required Reason APIs (e.g. UserDefaults) — missing → upload rejection.
- Every permission needs a specific `NS*UsageDescription`.
- Background modes only for declared purposes; ATT before any tracking.
