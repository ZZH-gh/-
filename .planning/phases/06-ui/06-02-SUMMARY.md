---
phase: 06-ui
plan: 02
type: execute
subsystem: "UI - Conversation Interaction"
tags: ["ui", "conversation", "multi-message", "navigation", "status-bar"]
requires: ["06-01"]
provides: ["multi-message-type rendering", "chat navigation", "persistent status bar"]
affects: ["prompt_tool/app.py", "prompt_tool/app_controller.py"]
tech-stack:
  added: []
  patterns: ["multi-message type dispatch in _v4_on_question", "live option controls in CTkScrollableFrame"]
key-files:
  created: []
  modified:
    - "prompt_tool/app.py"
    - "prompt_tool/app_controller.py"
decisions:
  - "escape button (D-09) always enabled — not disabled during generating state; _v4_is_generating flag prevents re-entry"
  - "option frames cleaned up immediately after selection to avoid residue in scrollable area"
  - "status bar moved to root grid row 5 for cross-page persistence (v3/v4)"
  - "empty multi_choice selection accepted per T-06-03 — sends '未选择' text, engine continues"
metrics:
  plan_duration: "~15 min"
  tasks_completed: 2/2
  files_modified: 2
  commits: 2
---

# Phase 6 Plan 02: Full Interaction — Multi-Message Types + Navigation

## One-liner

Complete conversational interaction controls — single-choice option buttons, multi-choice checkboxes, confirm prompts, result-to-chat navigation, new-chat reset with session isolation, and persistent status bar across all views.

## Summary

This plan extends the v4 conversational UI from basic text-only Q&A to full interactive message types per decision D-08. It adds three interactive control patterns below system message bubbles and completes the navigation contract (D-04 back-to-chat, D-05 new-chat reset) while fixing a cross-page visibility issue with the status bar.

### Task 1: Multi-message-type interaction controls

- Single choice (`_add_single_choice_options`): horizontal option buttons, click to submit
- Multi choice (`_add_multi_choice_options`): checkboxes per option + confirm button, joined value submission
- Confirm prompt (`_add_confirm_buttons`): confirm/modify two-button layout
- Central cleanup (`_cleanup_options_frame`): destroys active frame and resets tracking state
- `_v4_on_question` dispatches per `question_type`: single_choice / multi_choice / confirm / text_input
- Added `process_answer` method to AppController for direct option value submission
- Escape door (D-09) always remains clickable — not disabled during generation, guarded by flag

### Task 2: Navigation + status bar persistence + auto-scroll

- Status bar moved from root grid row 4 to row 5, removed from `_switch_to_v4_page`/`_switch_to_v3` hide/show cycle — persists across all views
- `_on_v4_new_chat` enhanced: calls `session_manager.new_session()`, clears input, resets generated_prompts, cleans up options frame
- `_scroll_chat_to_bottom` enhanced: added `update_idletasks()` before scroll for layout correctness

## Commits

| Commit | Message |
|--------|---------|
| `26c5a36` | feat(06-ui-02): implement multi-message-type interaction controls |
| `f1d63bf` | feat(06-ui-02): add navigation, status bar persistence, auto-scroll enhancement |

## Key Design Decisions

### Option interaction flow

```
User clicks option button
  → _on_option_selected(value)
    → _add_user_message("选择：{value}") — shows user's selection as chat bubble
    → _cleanup_options_frame() — destroys buttons immediately
    → self._v4_controller.process_answer(value) — submits via daemon thread
    → engine.handle_answer() in thread → _dispatch_action()
      → on_question callback: re-enables input, shows next question
      → on_results callback: switches to result page
```

### Status bar persistence

The status bar was historically part of the v3 layout (row 4), hidden by `grid_remove` during v4 page switching. By moving it to root grid row 5 and excluding it from `_switch_to_v4_page`'s hide cycle, it remains visible during both v3 and v4 views without any restore logic.

### Threat compliance

- T-06-03 (multi_choice empty selection): handled — sends "未选择" as answer text, engine continues
- T-06-04 (session isolation): `session_manager.new_session()` creates entirely new session ID — no cross-session leak

## Verification

- All message types (text_input, single_choice, multi_choice, confirm) render without crash
- Methods all present on PromptToolApp: `_add_single_choice_options`, `_on_option_selected`, `_add_multi_choice_options`, `_on_multi_choice_confirm`, `_add_confirm_buttons`, `_on_confirm_response`, `_cleanup_options_frame`
- `process_answer` present on AppController
- Status bar verified on root grid row 5
- `_on_v4_new_chat` completes without error
- `_on_v4_back_to_chat` switches to chat frame

## Deviations from Plan

None — plan executed as written.

## Known Stubs

None identified. All added controls are fully wired and functional.

## Threat Flags

None found. All new surface is UI-only (option buttons, checkboxes) — no new network, auth, file access, or schema changes.
