---
name: kb-flutter
description: Flutter team conventions - project structure, state management, theming from design tokens, adaptive Cupertino/Material UI, animation, testing (unit, widget, golden, integration, Maestro), builds per machine and pitfalls.
user-invocable: false
---

# Flutter conventions

## Setup
- Latest stable Flutter channel (check `flutter --version`; the Mac has Flutter installed). Null safety, `very_good_analysis` or `flutter_lints` strict.
- Layout in `apps/mobile/`: `lib/app/` (app, router, theme), `lib/features/<feature>/{data,domain,presentation}`, `lib/design_system/{tokens,components}`, `lib/core/` (networking, storage, errors), `test/`, `integration_test/`.

## Patterns
- State: Riverpod (or Bloc if the architecture says so); immutable models (freezed + json_serializable).
- Routing: go_router with typed routes and deep links.
- Theme: `ThemeData` + `ThemeExtension`s generated from the design-token JSON; Material 3 color scheme on Android; adaptive widgets (`.adaptive` constructors, Cupertino navigation/dialogs on iOS when the spec requires).
- Motion: implicit animations, `AnimationController` for custom, Hero for shared elements, `lottie`/`rive` for illustrations; `HapticFeedback` for haptics.
- Accessibility: `Semantics` labels, `MediaQuery.textScaler` respected, `Key`/semantics identifiers for Maestro.
- Secure storage: `flutter_secure_storage`; never SharedPreferences for tokens.

## Quality commands
- `flutter analyze`, `dart format --set-exit-if-changed .`, `flutter test`, `flutter test integration_test` (device/simulator), golden tests for key components, `maestro test tests/e2e/...`.
- Builds: `flutter build ios --release` / `flutter build ipa` on the Mac; `flutter build appbundle` where the Android SDK exists.

## Pitfalls
- Rebuild storms: use `select`/`Consumer` scopes, `const` constructors.
- Platform views and heavy shaders cause jank on first run; warm-up and test on real-ish devices.
- iOS: run `pod install` via Flutter tooling; check plugin privacy manifests; set `NS*UsageDescription` strings.
- Android: `targetSdk` per current Play requirement, edge-to-edge insets, predictive back (`PopScope`).
