# Project Constitution — {{App name}}

> Owner: business-analyst (draft), PO (approval at G0). Non-negotiable principles every agent follows. Change only via change request.

## Product principles
1. {{e.g. "Every session must leave the learner measurably closer to their target band score."}}
2. …

## Quality bar
- Crash-free sessions ≥ 99.5% · cold start < 2 s on mid-range devices · 60 fps scrolling
- UI meets `.claude/skills/kb-production-ui-bar` (no placeholder or "AI-minimal" screens)
- Accessibility: Dynamic Type / font scaling, VoiceOver / TalkBack labels, contrast WCAG AA

## Platform & store principles
- Follow Apple HIG on iOS and Material 3 on Android unless a deliberate, documented brand exception
- Designed to pass App Store Review and Google Play policy on first submission (see `company/compliance/`)

## Privacy & data
- Collect the minimum data; every data type maps to a feature and to the privacy labels / Data safety form
- Account deletion in-app if accounts exist

## Engineering principles
- Tests accompany every feature; E2E flows for every critical path
- Secrets never in git; keys for AI/LLM providers live server-side only

## Decision rights
- PO decides: scope (G1), stack (G2), release (G3), anything costing money
- Teams decide within their lane and record significant decisions as ADRs
