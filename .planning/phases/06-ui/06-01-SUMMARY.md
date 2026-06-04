---
phase: 06-ui
plan: 01
subsystem: ui
tags: [customtkinter, conversation-ui, frame-switching, app-controller]

# Dependency graph
requires:
  - phase: 04-conversation-core
    provides: ConversationEngine 9-state state machine
  - phase: 05-generation-v2
    provides: PromptGeneratorV2 output format

provides:
  - AppController orchestrator for UI-backend mediation
  - Chat page with alternating user/system message bubbles
  - Result page with three-card strategy comparison layout
  - Frame switching mechanism (v3/v4/page-to-page)

affects:
  - 06-ui / 06-02-optimization (result page is extended with side panel)
  - 06-ui / 06-03-knowledge-visibility (knowledge pack button wires up)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "AppController: callback-based event mediation with thread safety"
    - "Frame switching via grid_remove/grid for page transitions"
    - "Chat bubble layout with sticky alignment for left/right messages"
    - "Three-card comparison grid with uniform column weights"

key-files:
  created:
    - prompt_tool/app_controller.py
    - tests/test_ui.py
  modified:
    - prompt_tool/app.py

key-decisions:
  - "D-01 (default show v3): backward compatible — v4 frames built but hidden"
  - "D-04 (back-to-chat): result page header includes return button"
  - "D-05 (new chat): result page header and chat page both new-chat button"
  - "D-06 (alternating bubbles): user sticky=e (right), system sticky=w (left)"
  - "D-09 (escape door position): 🎯 button in input bar, always visible"
  - "D-10 (escape door behavior): skip_follow_up + generate_complete"
  - "D-03 (three-card layout): uniform='card_col' equal-width columns"

patterns-established:
  - "AppController callbacks: background thread dispatches result, UI wraps with root.after"
  - "Page switching: v4_container.grid_remove/grid with v3 widget grid_remove/restore"
  - "Chat auto-scroll: _parent_canvas.yview_moveto(1.0) after message added"
  - "Button debounce: _v4_set_generating disables/enables send + escape buttons"
  - "Copy feedback: clipboard_clear + clipboard_append + 2s button text revert"

requirements-completed:
  - UI-01
  - UI-02
---

# Phase 6 Plan 01: Conversation UI + Basic Flow Summary

**AppController orchestrator with v4 dialog page (chat bubbles + input bar + escape door) and three-card result comparison page with frame switching**

## Performance

- **Duration:** 4 min
- **Started:** 2026-06-04T11:22:41Z
- **Completed:** 2026-06-04T11:26:26Z
- **Tasks:** 3 (1 TDD)
- **Files modified:** 3

## Accomplishments

- AppController orchestrator: mediates UI events with ConversationEngine via callback-based architecture, routes user input based on engine state machine (IDLE/CONFIRMING/CLARIFYING/FOLLOWING_UP), handles daemon thread lifecycle, concurrency guard prevents overlapping thread spawns (T-06-01 mitigation)
- Chat page: header bar with v4 title, CTkScrollableFrame for alternating user (right-aligned, light blue) and system (left-aligned, white) message bubbles, bottom input bar with textbox + send button + escape door, auto-scroll on new messages, welcome message on init
- AppController integration: thread-safe callback wrappers via `root.after(0, lambda: ...)`, engine state routing through unified `process_input()` entry point
- Escape door (D-09/D-10): "🎯 立即生成" always visible in input bar, calls `skip_follow_up()` + `generate_complete()`, skips remaining follow-up questions
- Result page: header with "← 返回对话" (D-04) and "🔄 新对话" (D-05) buttons, three equal-width strategy cards (direct/roleplay/detailed) using STRATEGIES constants, each card with title tag badge + read-only CTkTextbox + copy button with 2-second feedback animation
- Frame switching: `_switch_to_v4_page("chat"/"results")` hides v3 widgets and shows target v4 sub-frame; `_switch_to_v3()` restores v3 layout
- 6 unit tests: all passing (AppController lifecycle, concurrency guard, thread safety)

## Task Commits

Each task was committed atomically:

1. **Task 1 (TDD): AppController + V4 frame scaffolding + test_ui.py**
   - `66e2dd2` (test: add failing tests for AppController lifecycle and concurrency guard) — RED
   - `d7b3e65` (feat: implement AppController and v4 frame scaffolding) — GREEN

2. **Task 2: Dialog page — chat bubbles + input bar + escape door**
   - `3b3f200` (feat: implement chat page with bubbles, input bar, and escape door)

3. **Task 3: Result page — three-card comparison + frame switching wiring**
   - `096ef43` (feat: implement result page with three-card comparison layout)

## Files Created/Modified

- `prompt_tool/app_controller.py` — NEW: AppController orchestrator class (230 lines)
- `tests/test_ui.py` — NEW: 6 unit tests for AppController lifecycle and concurrency guard
- `prompt_tool/app.py` — MODIFIED: +450 lines for v4 scaffolding, chat page, result page, controller integration, v3 widget reference storage

## Decisions Made

- Followed all 7 D-* decisions from CONTEXT.md as specified in plan:
  - D-01 (page switching via grid_remove/grid)
  - D-03 (three-card horizontal comparison with uniform columns)
  - D-04 (back-to-chat button in result header)
  - D-05 (new-chat button resets conversation)
  - D-06 (user bubbles right-aligned, system left-aligned)
  - D-09 (escape door in input bar, always visible)
  - D-10 (escape door calls skip_follow_up + generate_complete)
- AppController uses callback-based architecture (does not hold root reference); app.py wraps callbacks with `root.after` for thread safety
- Result card copy button uses 2-second feedback animation matching existing v3 `_on_copy` pattern

## Deviations from Plan

None — plan executed exactly as written. All 3 tasks completed with correct commit types. TDD gate: `test(...)` commit followed by `feat(...)` commit for Task 1 (valid RED/GREEN sequence).

## Issues Encountered

None — all 15 tests pass (6 new + 9 existing conversation engine tests).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- v4 chat frame and result frame are built and ready for extension
- Chat method `_v4_on_question()` handles follow_up actions with option hints
- Result frame's `cards_area` grid is ready for side-panel column addition (Plan 02)
- Knowledge pack button (`_v4_kb_btn`) is created but disabled — ready for Plan 03 wiring
- Backward compatibility: v3 interface remains functional via `_switch_to_v3()`

---
*Phase: 06-ui*
*Completed: 2026-06-04*

## Self-Check: PASSED

| Check | Status |
|-------|--------|
| `prompt_tool/app_controller.py` | Created |
| `tests/test_ui.py` | Created |
| `prompt_tool/app.py` | Modified |
| `.planning/phases/06-ui/06-01-SUMMARY.md` | Created |
| `66e2dd2` (test RED commit) | Found |
| `d7b3e65` (feat GREEN commit) | Found |
| `3b3f200` (Task 2 commit) | Found |
| `096ef43` (Task 3 commit) | Found |
| All 6 test_ui.py tests pass | Verified |
| All 9 test_conversation_engine.py tests pass | Verified |
