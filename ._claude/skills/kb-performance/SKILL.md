---
name: kb-performance
description: How to measure and budget mobile app performance (startup, frame rendering, memory, app size, stability, data and network) on Flutter, React Native and native builds - methods, commands, official thresholds, and how to report numbers that can be compared before and after a change.
user-invocable: false
---

# Measuring app performance

A performance claim is a number plus the conditions that produced it: build mode, device or emulator model, OS version, commit and the command. Without those, before-and-after comparisons are noise.

## Rules
1. **Measure profile or release builds**, never debug: debug builds of Flutter and React Native are many times slower and say nothing about users.
2. **Same device, same data, same commit, at least 5 runs**; report the median and the worst run. Cold start means the app process is killed first (`adb shell am force-stop <pkg>`; on iOS, terminate the app in the simulator).
3. **Emulators and simulators measure regressions, not absolute speed.** Say which you used. A physical device number from the PO beats any emulator number.
4. Run builds and benchmarks through `scripts/check.sh` (builds are never cached) and quote its summary line. Keep the log with `--keep <id>` when the number is evidence.
5. Record results in a table with these columns: metric, value (median and worst), device or OS, build mode, commit, command, date.

## Official thresholds (cite them; re-fetch if the page may have changed)
- Android vitals counts startup as excessive when cold start ≥ 5 s, warm ≥ 2 s or hot ≥ 1.5 s, measured as time to initial display. Source: https://developer.android.com/google/play/vitals/launch-time, accessed 2026-10-26.
- Android vitals bad-behavior thresholds: user-perceived crash rate 1.09% overall (8% per phone model) and user-perceived ANR rate 0.47% overall (8% per phone model). Above them an app loses visibility on Google Play. Source: https://developer.android.com/topic/performance/vitals, accessed 2026-10-26.
- Frame budget: 16.7 ms per frame at 60 Hz and 8.3 ms at 120 Hz (arithmetic).
- Apple publishes launch-time and hang guidance (Xcode Organizer metrics, MetricKit). Fetch the current page before quoting a number for iOS.
- The project's own budgets live in the constitution (`docs/00-intake/constitution.md`, or the engagement brief in a takeover). They must be at least as strict as the store thresholds.

## What to measure and how
| Metric | Flutter | React Native | Native Android | Native iOS |
|---|---|---|---|---|
| Cold start (time to first frame) | `flutter run --profile --trace-startup` (writes `build/start_up_info.json`) | `adb shell am start -W` / Xcode Instruments App Launch | `adb shell am start -W -n <pkg>/<activity>` → `TotalTime`; Macrobenchmark `StartupTimingMetric` | `xcrun xctrace record --template 'App Launch' --launch -- <app>`; XCTest `XCTApplicationLaunchMetric` |
| Frame rendering and jank | DevTools Performance (profile mode), `flutter drive --profile` timeline summary | Perf Monitor, Flipper/Hermes profiler, then the native tools | `adb shell dumpsys gfxinfo <pkg>` (janky frames, percentiles); Macrobenchmark `FrameTimingMetric` | Instruments Animation Hitches; `XCTOSSignpostMetric` |
| Memory | DevTools Memory | Hermes heap snapshot | `adb shell dumpsys meminfo <pkg>` | Instruments Allocations/Leaks |
| App size | `flutter build apk --analyze-size` / `flutter build ipa --analyze-size` | Android App Bundle size, `react-native-bundle-visualizer` | `bundletool get-size total` on the AAB | App Store Connect size report; Xcode export app thinning report |
| Data layer | Time the core-loop queries with the DB's explain/plan and the app's logging in profile mode | same | same | same |
| Stability | Crash/ANR reporting present? (Crashlytics, Sentry or store vitals) Without it, the app is flying blind: this is a finding | same | Play Console Android vitals | Xcode Organizer, MetricKit |

## Typical causes worth checking
- Startup: synchronous I/O, database opens or migrations and large asset or content loads before the first frame; too many plugins initialised eagerly.
- Jank: rebuilding large widget trees or lists without virtualisation, image decoding on the UI thread, heavy JSON or crypto work on the UI isolate or thread.
- Size: bundled content databases, audio or fonts that could be downloaded on demand; unused locales and assets.
- Memory: caches without limits, images kept at full resolution, leaks across navigation.

## Reporting
- In a takeover: `docs/t1-discovery/performance.md` (discovery) and `docs/t4-transition/baseline.md` (the numbers later work is compared against).
- In QA: `docs/07-qa/performance-<date>.md` with the same table, plus the baseline row and the delta.
- A regression above 10% against the baseline on startup, frame time or size is a bug. Severity rises when a store threshold is crossed.
