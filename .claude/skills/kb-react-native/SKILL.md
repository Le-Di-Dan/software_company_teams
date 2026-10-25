---
name: kb-react-native
description: React Native team conventions - TypeScript project structure, Expo without paid EAS, navigation, state, styling with design tokens, testing (Jest, RNTL, Maestro), local iOS/Android builds and common pitfalls.
user-invocable: false
---

# React Native conventions

## Setup
- TypeScript strict. Prefer Expo (managed workflow + config plugins) with **local** native builds: `npx expo prebuild`, `npx expo run:ios` (Mac), `npx expo run:android` (machine with SDK). EAS cloud services are not used (no paid plan); `eas build --local` only if the PO approves an Expo account.
- Check the current stable RN/Expo SDK and the New Architecture defaults on official docs before init; pin versions.
- Folder layout in `apps/mobile/`: `src/app` (routes, Expo Router) or `src/navigation`, `src/features/<feature>/{components,hooks,api,model}`, `src/design-system/{tokens,components}`, `src/lib`, `src/services`.

## Patterns
- Navigation: Expo Router or React Navigation (native stack) — follow the architecture doc.
- Server state: TanStack Query; client state: Zustand or Context; forms: react-hook-form + zod.
- Styling: theme from design tokens (generated from `docs/04-design/design-system.md` JSON); no inline magic numbers. Dark mode via theme.
- Animation: Reanimated + Gesture Handler; Lottie (`lottie-react-native`) or Rive for illustrations; `expo-haptics` for haptics.
- Lists: FlashList for long lists; memoize row components.
- Accessibility: `accessibilityLabel`, `accessibilityRole`, `testID` on interactive elements (Maestro uses them).
- Secure storage: `expo-secure-store`; never AsyncStorage for tokens.

## Quality commands
- `npx tsc --noEmit`, `npx eslint .`, `npx jest` (React Native Testing Library), `maestro test tests/e2e/...`.

## Pitfalls
- Native module without config plugin → prebuild drift. Re-run `prebuild --clean` after native config changes; don't hand-edit generated `ios/`/`android/` unless the architecture says bare RN.
- iOS privacy manifests: confirm third-party native modules ship `PrivacyInfo.xcprivacy`.
- OTA updates (expo-updates) may only ship bug fixes per Apple 2.5.2; never feature changes.
- Hermes + large JSON parsing on the JS thread → jank; move heavy work off the JS thread.
