---
name: kb-figma
description: Figma team conventions - when the team runs, Figma MCP session and plugin skills, file and page structure, variables/styles/components naming that maps 1:1 to the design tokens, screen and state frames, incremental writes with screenshot checks, one writer per page, cost and rate limits, register files, the Figma hygiene checklist, and what agents may never do in the PO's Figma account.
user-invocable: false
---

# Figma conventions (figma-* team)

## When the team runs
- Only when `state/project.json → figma.enabled` is `true` (the PO opted in and connected the Figma MCP). Otherwise the markdown specs in `docs/04-design/` are the whole design deliverable.
- **The specs are the source of truth.** `docs/04-design/design-system.md` (tokens JSON), `screens/SCR-nnn-*.md`, `web/<surface>/SCR-W-nnn-*.md`, `copy.md`, `motion-sound-haptics.md` and `assets-plan.md` are the contract engineers implement. Figma renders them; it never invents values. A gap or contradiction in a spec goes in your `## Challenges` for ui-designer, not into the canvas as a guess.
- Human edits in Figma (PO or a hired designer) flow back through the spec: figma-handoff-specialist reports the diff, ui-designer updates the spec, then the canvas is re-synced.

## Access and tools
1. The brief gives the file key (`figma.file_key`, and `figma.library_file_key` if the library is a separate file). Parse links per the Figma MCP instructions (`node-id=1-2` → `1:2`; branch URLs use the branch key).
2. Call `create_session` with the file key and a one-line task before any other file tool; pass the returned `sessionId` on every later call of the task.
3. Load the Figma plugin skills with the Skill tool before the tools that need them (fallback when the plugin is not installed: read `skill://figma/<name>/SKILL.md` with ReadMcpResourceTool):

| Before | Load |
|---|---|
| any `use_figma` call | `figma:figma-use` (mandatory) |
| variables, styles, components, library | `figma:figma-generate-library` |
| screens, pages, composed UI | `figma:figma-generate-design` |
| prototype animation, keyframes, easing | `figma:figma-use-motion` |
| FigJam boards | `figma:figma-use-figjam`; `generate_diagram` needs `figma:figma-generate-diagram` |
| Code Connect | `figma:figma-code-connect` |
| reading a design for code (`get_design_context`) | `figma:figma-design-to-code` |
| SwiftUI either way | `figma:figma-swiftui` |

4. No access, permission errors or rate limits: call `whoami` once, report the plan/seat it shows, and stop. Never retry in a loop. Write access and MCP limits depend on the PO's Figma plan and seat; quote the current Figma help page when you report it, never memory.
5. `create_new_file` only when the brief says the PO approved a new file and names the plan (from `whoami`). Return the new key; the director records it in `state/project.json`.

## File structure
One product file `<App> — Product`. Pages, in this order (skip what the project doesn't have):
`Cover` · `Foundations` · `Components` · `iOS` · `Android` · `Web / <surface>` (one page per surface) · `Prototype` · `Today (v1)` (takeover only) · `Archive`.
A separate library file only if the brief says so (the PO wants to reuse the library across products); then `Foundations` and `Components` live there and the product file uses its published library. Publishing the library is the PO's click in Figma.

## Foundations: variables and styles
- Collections: `Primitives` (raw palette and scales, one mode, hidden from publishing), `Color` (semantic roles; modes `Light`, `Dark`; aliases to Primitives only), `Spacing`, `Radius`, `Size`, `Motion` (durations as numbers), `Typography` (font family, sizes, line heights, weights as variables where Figma supports them).
- **Variable names mirror the token keys** in the design-system JSON with `/` for `.`: token `color.bg.surface` → variable `color/bg/surface`. Set code syntax for each platform in the squad (WEB `var(--color-bg-surface)`, iOS/Android names from the tokens block) so Dev Mode shows the engineers' names.
- Scopes set on every variable (a spacing variable can't be picked as a fill).
- Text styles per type-scale step (`Display/L`, `Title/M`, `Body/M`, `Caption/S`, …), per platform when the scale differs (`iOS/Body`, `Android/Body`, `Web/Body`), bound to typography variables. Effect styles for elevation/materials. No color styles: color comes from variables.

## Components
- One component set per component in `design-system.md`, same name. Variant properties use the spec's words: `Variant`, `Size`, `State` (`Default`, `Pressed`, `Focused`, `Disabled`, `Loading`, `Selected` as specified), plus boolean/instance-swap/text properties for optional parts and labels.
- Auto layout on every frame; padding, gap, radius, fills, strokes and text bound to variables/styles. Zero hard-coded values.
- Platform adaptations as a `Platform` property (`iOS`, `Android`, `Web`) only where anatomy differs; otherwise one component.
- Description on each component set: purpose, spec link (`docs/04-design/design-system.md#<anchor>`), accessibility note.
- Icons: one family from `assets-plan.md`, as components named `Icon/<name>`, 24 px base, color bound to a variable.

## Screens
- Frame name = spec id + state: `SCR-012 Home / Empty / Dark`, `SCR-W-003 Pricing / 768 / Light`. One Section per screen holding all its states, named `SCR-012 Home`.
- Device frames: the sizes listed in `design-system.md` (mobile) and 390 / 768 / 1280 px (web). Record the sizes you used in your register file.
- Every state the spec lists (default, loading skeleton, empty with illustration and CTA, error with recovery, offline, permission denied, success), light and dark.
- Built only from library instances; never detach. A missing component is a request to figma-library-designer, not a local one-off.
- Text from `copy.md` in the primary language; the text layer name is the copy key (`home.empty.title`). Longest target language checked on at least one screen per flow for +30% expansion.
- Images and illustrations only from sources licensed in `assets-plan.md`, placed with `upload_assets`. No lorem ipsum, no "Item 1", no stock without a license.

## Writing to the canvas
- Incremental: one section or component per `use_figma` call, small scripts, return the created node ids. After each section call `get_screenshot` on that node (default size, URL + curl path) and fix what looks wrong before moving on.
- Idempotent: find by name before creating; update in place instead of duplicating. Never delete or move nodes you didn't create; anything prefixed `🔒` or on a page not in your brief is off limits.
- **One writer per page.** The director gives parallel agents disjoint pages; touching another page is a lane violation, reported, not done.
- Save evidence screenshots with curl to `docs/04-design/figma/shots/<frame-name-slug>.png` (only the frames the brief or a review needs; not every iteration).

## Cost and limits
- Read cheap first: `get_metadata` (structure, ids) → `get_screenshot` of one node → `get_design_context` only for the node you need. Never request a whole page's design context.
- Screenshots at the default `maxDimension` (1024); raise it only to inspect fine detail.
- MCP calls count against the PO's Figma plan limits. Batch work into fewer, larger `use_figma` calls once a pattern works.

## Register files (each agent writes only its own)
`docs/04-design/figma/library.md` (library designer), `screens-<page-slug>.md` (screen designer, one per page), `prototypes.md` (prototype designer), `audit-<date>.md`, `code-connect.md`, `parity-<date>.md` (handoff specialist). Each lists node links as `https://www.figma.com/design/<fileKey>/?node-id=<id with ->` next to the spec id they render.

## Figma hygiene checklist (pass/fail, used by the audit)
- [ ] Every fill, stroke, text, spacing and radius on library components and screens is bound to a variable or style (report coverage %).
- [ ] 0 detached instances; 0 local one-off components on screen pages.
- [ ] Auto layout on every container; no absolute positioning except overlays, badges and illustrations.
- [ ] Layer names meaningful (no `Frame 123`, `Rectangle 4`); text layers named by copy key.
- [ ] Every spec id and every listed state has a frame, light and dark; nothing in Figma that no spec describes.
- [ ] Contrast WCAG AA in both modes; touch targets ≥44 pt / 48 dp; web focus states drawn.
- [ ] The design passes `kb-production-ui-bar` (mobile) / `kb-web-ui-bar` (web) like the specs it renders.

## Never (PO-only, golden rule 7)
Change sharing or permissions, invite people, publish a library, move or delete files, buy plugins, fonts, assets or seats, or post comments addressed to people outside the company. Prepare it and list it in "Questions for PO".
