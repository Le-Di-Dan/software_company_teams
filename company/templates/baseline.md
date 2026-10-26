# Baseline — {{App name}}

> Owners: performance-engineer (performance), test-automation-engineer (tests), devops-engineer (build & CI) · Takeover T4
> Commit measured: {{sha}} on `company/v2` (= audited baseline + characterization tests only) · Date: {{YYYY-MM-DD}}

Every later change is compared against this file. Do not edit the numbers after T4; add a dated "re-baseline" section if the PO approves one.

## Build & CI
| Target | Command (via check.sh) | Result | Machine | Notes |
|---|---|---|---|---|
| Android debug/release | | | windows | |
| iOS | | | mac | |
| Backend / services | | | | |
| CI workflow(s) | | green / red / absent | GitHub | |

## Existing automated tests
| Suite | Command | Passed / failed / skipped | Duration | Flaky? |
|---|---|---|---|---|

## Characterization tests added in T4
Flows that lock in today's behavior for modules marked keep, fix or rebuild, so refactors cannot silently change them.
| Flow / test | Path in client/ | Covers (module, finding ids) | Platforms | Result |
|---|---|---|---|---|

## Performance (kb-performance)
| Metric | Median | Worst | Device / OS | Build mode | Command |
|---|---|---|---|---|---|
| Cold start (TTID) | | | | | |
| Core-loop frame time / jank % | | | | | |
| Memory on the core loop | | | | | |
| App size (download / install) | | | | | |
| Core-loop query or request time | | | | | |

## Gaps
What could not be measured or tested at baseline, why, and the plan.
