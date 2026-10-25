---
name: kb-kotlin-android
description: Kotlin Android team conventions - Jetpack Compose architecture, coroutines/Flow, Hilt, Material 3 theming from design tokens, testing (JUnit, Compose UI tests, Maestro), Gradle builds on the Windows machine and Play requirements.
user-invocable: false
---

# Kotlin / Jetpack Compose conventions

## Setup
- Android Studio + SDK on the Windows machine (see `state/environment.md`). Gradle Kotlin DSL with version catalog (`libs.versions.toml`). `targetSdk` per current Play requirement (check developer.android.com/google/play/requirements/target-sdk), `minSdk` per architecture.
- `apps/android/`: modules `app`, `core:designsystem`, `core:data`, `core:network`, `feature:<name>` (follow Now in Android–style modularization if the app is non-trivial).

## Patterns
- Compose + Material 3; MVVM/UDF with `ViewModel` + `StateFlow`; Hilt for DI; Navigation Compose with type-safe routes; Room / DataStore for persistence; EncryptedSharedPreferences/Keystore-backed storage for secrets.
- Theme: design tokens → `ColorScheme` (light/dark, dynamic color only if brand allows), `Typography`, `Shapes`, custom `CompositionLocal` for spacing/motion.
- Edge-to-edge with proper insets; predictive back; adaptive layouts (window size classes) for tablets/foldables if supported.
- Motion: Compose animation APIs, shared element transitions, Lottie Compose; `HapticFeedback` / `View.performHapticFeedback`.
- Google Play Billing Library for IAP/subscriptions (or RevenueCat if approved).
- Accessibility: `contentDescription`, `semantics { testTag }` (Maestro / UI tests), touch targets ≥48dp.

## Quality commands
- `./gradlew lint ktlintCheck test` (or detekt if configured), `./gradlew connectedAndroidTest` (emulator), `./gradlew bundleRelease` (signing by release-manager), `maestro test tests/e2e/...`.

## Pitfalls
- Foreground services need declared types; sensitive permissions need Play declarations; prefer Photo Picker over broad media permissions.
- 16 KB page size compatibility for native libraries.
- Avoid work on the main thread; collect flows with lifecycle awareness (`collectAsStateWithLifecycle`).
