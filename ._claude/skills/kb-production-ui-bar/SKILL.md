---
name: kb-production-ui-bar
description: The production UI quality bar - concrete, checkable criteria that separate a polished store-ready app from minimal, generic AI-generated UI. Used by UI/UX R&D, UI designer, mobile engineers and QA.
user-invocable: false
---

# Production UI quality bar

AI-built UIs fail in predictable ways: default system colors and fonts, flat white screens, no hierarchy, no motion, empty states that say "No data", identical card lists everywhere, no brand. Each item below is a **pass/fail** check. Any FAIL on a core screen (onboarding, home, core loop, paywall) is a major defect.

## 1. Identity
- [ ] A distinctive brand palette (primary, secondary, accent, semantic colors) with light and dark variants; not default blue on white.
- [ ] Deliberate typography: a type scale with clear hierarchy (display/title/body/caption), weights used intentionally; custom display font only if licensed.
- [ ] App icon and launch experience consistent with the brand.
- [ ] A recognizable visual motif (illustration style, shapes, patterns or mascot) used consistently.

## 2. Hierarchy & layout
- [ ] Each screen has one obvious primary focus and action; secondary actions are visually quieter.
- [ ] Consistent spacing scale (e.g. 4/8 pt grid); generous whitespace; alignment is consistent.
- [ ] Rich content presentation where it helps: hero areas, progress visuals, charts, imagery; not just plain lists of text rows.
- [ ] Adapts to small phones, large phones, tablets (if supported), landscape where relevant, and safe areas / edge-to-edge.

## 3. Depth, material & detail
- [ ] Uses the current platform material language appropriately (iOS materials/translucency and current visual style; Android Material color roles, elevation, shapes).
- [ ] Components have polished states: pressed, focused, disabled, selected, loading.
- [ ] Icons from a single consistent family (SF Symbols / Material Symbols / custom set), sized and weighted consistently.

## 4. Motion
- [ ] Navigation transitions follow the platform and feel continuous (shared-element/hero where it clarifies).
- [ ] Micro-interactions on key actions (button feedback, toggles, adding items, completing tasks) with defined durations/easing from motion tokens.
- [ ] Loading uses skeletons/shimmer or meaningful progress, not a lone spinner on a blank screen.
- [ ] Celebration moments for achievements (subtle confetti, check animations, Lottie/Rive) where the product has wins.
- [ ] Respects Reduce Motion settings.

## 5. Haptics & sound
- [ ] Haptic feedback mapped to events (success, warning, selection, impact) per platform guidelines; not overused.
- [ ] Optional UI sounds where they add meaning (e.g. learning/gaming feedback), respecting silent mode, with an in-app toggle.

## 6. States & content
- [ ] Empty states have an illustration, a helpful explanation and a clear call to action.
- [ ] Error states explain and offer recovery (retry, offline mode); no raw error codes.
- [ ] Onboarding shows value before asking for sign-up or permissions.
- [ ] Real, realistic content in designs and screenshots (no lorem ipsum, no "Item 1").
- [ ] Copy follows the voice & tone guide.

## 7. Accessibility
- [ ] Contrast meets WCAG AA (4.5:1 body text, 3:1 large text and UI components) in light and dark.
- [ ] Dynamic Type / font scaling up to the largest accessibility sizes without broken layouts on key screens.
- [ ] Screen reader labels, traits/roles and logical focus order; touch targets ≥44 pt (iOS) / 48 dp (Android).

## 8. Performance feel
- [ ] Smooth scrolling and animations (60 fps target; 120 Hz where supported), no jank on mid-range devices.
- [ ] Perceived speed: optimistic UI, cached content, instant feedback on tap.

## Review output format
`| # | Item | PASS/FAIL | Screen(s) | Evidence (screenshot path / spec ref) | Fix |`
