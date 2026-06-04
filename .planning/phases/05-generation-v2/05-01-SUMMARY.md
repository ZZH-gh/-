---
phase: 05-generation-v2
plan: 01
subsystem: generation
tags: [knowledge-pack, prompt-generation, conversation-engine, injection]

# Dependency graph
requires:
  - phase: 04-conversation-core
    provides: ConversationEngine, ConversationState, ConversationEngine.generate_complete() entry point
  - phase: 02-knowledge-layer
    provides: KnowledgeManager, KnowledgePack (get_roles, get_pain_points, get_doc_templates, get_terms)
  - phase: 03-context-layer
    provides: context_builder.build_generation_context(), SessionManager

provides:
  - PromptGeneratorV2 class in generator.py (v4.0 generation engine)
  - KnowledgePack loading via knowledge_manager.load_pack() (fixes metadata-only bug)
  - 4 knowledge injection methods: role depth, quality standards, output structure, anti-patterns
  - _select_task_knowledge() task-relevant slice (D-12)
  - 3 strategy stubs (direct, roleplay, detailed) for Plan 02 differentiation
  - generate_prompts_v2() factory function
  - Updated ConversationEngine.generate_complete() orchestrating generation pipeline (D-03)
  - app.py _do_generate_v4() now calls engine.generate_complete() instead of direct generator import (D-03)

affects:
  - Phase 5 Plan 02 (strategy differentiation)
  - Phase 5 Plan 03 (anti-pattern filtering)
  - Phase 4 conversation_engine (method updated)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Direct KnowledgePack loading via knowledge_manager.load_pack() in generator, bypassing context_builder metadata-only knowledge_pack_ref"
    - "4-level injection in D-06 fixed order concatenated via _inject_all()"
    - "Knowledge selection cached once at __init__, shared across 3 strategies"
    - "Local import of PromptGeneratorV2 inside ConversationEngine.generate_complete() to avoid circular dependency"

key-files:
  created: []
  modified:
    - prompt_tool/generator.py (+365 lines)
    - prompt_tool/conversation_engine.py (+20/-11 lines)
    - prompt_tool/app.py (+13/-11 lines)

key-decisions:
  - "D-01: Refactored existing generator.py, did not create a new file"
  - "D-02: PromptGeneratorV2 coexists with backward-compatible PromptGenerator"
  - "D-03: Generation encapsulated in ConversationEngine.generate_complete(); app.py unaware of which generator"
  - "D-04: generate_complete() calls PromptGeneratorV2 directly, no intermediate service layer"
  - "D-05: v3.0 flow (engine.analyze -> generate_prompts) preserved unchanged"
  - "D-06: 4 injection points in fixed order: role depth -> quality standards -> output structure -> anti-patterns"
  - "D-07: Role matched by common_tasks list; fallback to first role or v3.0 INDUSTRIES mapping"
  - "D-08: Quality standards always-on with general + doc template common_mistakes extract"
  - "D-09: Output structure from get_doc_templates(task_type) sections"
  - "D-10: Anti-pattern warnings from get_pain_points() what_not_to_do"
  - "D-12: Knowledge selection returns task-relevant slice, not full pack"
  - "v4 auto-confirm path uses engine._last_analysis, not re-analysis via AnalysisEngine"

patterns-established:
  - "Direct KnowledgePack loading in generator: consumer loads its own data rather than relying on context_builder passing correct ref"
  - "Knowledge selection at init, cached instance-wide: _task_knowledge computed once, shared by all 3 strategies"
  - "Local import inside method for cross-module dependencies at runtime (PromptGeneratorV2 in conversation_engine.py)"
  - "Fallback chain for role: task-matched role from pack -> first role from pack -> v3.0 INDUSTRIES mapping"

requirements-completed: [GEN-01, GEN-02]
---

# Phase 5 Generation v2 — Plan 01 Summary

**Core PromptGeneratorV2 class with direct KnowledgePack loading, 4 knowledge injection methods, and ConversationEngine generation pipeline orchestration**

## Performance

- **Duration:** 18 min
- **Started:** 2026-06-04T10:30:00Z
- **Completed:** 2026-06-04T10:48:00Z
- **Tasks:** 2 of 2
- **Files modified:** 3

## Accomplishments

- Added `PromptGeneratorV2` class (365 lines) in `generator.py` alongside existing `PromptGenerator` class
- Fixed critical data flow bug: generator loads `KnowledgePack` directly via `knowledge_manager.load_pack()`, not from context_builder's metadata-only `knowledge_pack_ref`
- Implemented `_select_task_knowledge()` for D-12 task-relevant slice (role matching by common_tasks, doc template by task_type, pain points, terms)
- Implemented all 4 injection methods in D-06 fixed order: role depth (with KPIs + benchmarks), quality standards (general + industry-specific), output structure (doc template sections), anti-pattern warnings (pain point what_not_to_do)
- Created 3 strategy stubs (direct, roleplay, detailed) as placeholders for Plan 02 differentiation
- Added `generate_prompts_v2()` factory function
- Rewired `ConversationEngine.generate_complete()` to build context, instantiate `PromptGeneratorV2`, and return prompts payload (D-03)
- Updated `app.py _do_generate_v4()` to call `engine.generate_complete()` instead of directly importing `generate_prompts_v2` (D-03)
- Preserved v3.0 fallback path for low-confidence clarify case unchanged (D-05)

## Task Commits

Each task was committed atomically:

1. **Task 1: Add PromptGeneratorV2 class to generator.py with KnowledgePack loading and 4 injection methods** - `a6158ba` (feat)
2. **Task 2: Wire ConversationEngine.generate_complete() to PromptGeneratorV2 and update app.py** - `384bbe3` (feat)

## Files Created/Modified

- `prompt_tool/generator.py` (+365 lines) - Added `PromptGeneratorV2` class with KnowledgePack loading, 4 injection methods, strategy stubs, helper methods, and `generate_prompts_v2()` factory
- `prompt_tool/conversation_engine.py` (+20/-11 lines) - Rewrote `generate_complete()` to orchestrate context building, PromptGeneratorV2 instantiation, and prompt generation
- `prompt_tool/app.py` (+13/-11 lines) - Updated `_do_generate_v4()` to call `engine.generate_complete()` and read prompts from result; removed direct `generate_prompts_v2` import

## Decisions Made

- **Data flow fix:** Generator loads `KnowledgePack` directly via `knowledge_manager.load_pack()` instead of relying on `knowledge_pack_ref` from context_builder (which only returns `pack.get_meta()` — metadata with no roles/pain_points/terms)
- **Doc template lookup:** Used `get_doc_templates(task_name)` (by task_type field) instead of `get_doc_template(task_name)` (by doc name field), matching the actual data structure where task_type = "PRD撰写" maps to doc name = "PRD模板"
- **Strategy stubs:** All 3 strategy methods intentionally return minimal content as placeholders for Plan 02's differentiated implementation
- **Fallback chain:** Role selection falls back through: task-matched role from pack -> first role from pack -> v3.0 INDUSTRIES role mapping

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Doc template API mismatch: get_doc_template vs get_doc_templates**
- **Found during:** Task 1 (PromptGeneratorV2._select_task_knowledge)
- **Issue:** Plan specified `get_doc_template(self.task_name)` which searches by doc `name` field. KnowledgePack doc templates use a `task_type` field to associate with tasks (e.g., doc `name="PRD模板"` has `task_type="PRD撰写"`). `get_doc_template("PRD撰写")` would search for a doc named "PRD撰写" which doesn't exist, returning None.
- **Fix:** Used `get_doc_templates(self.task_name)[0]` which filters by `task_type` field and returns the correct doc template.
- **Files modified:** `prompt_tool/generator.py` (PromptGeneratorV2._select_task_knowledge)
- **Verification:** get_doc_templates('PRD撰写') returns 1 doc with name 'PRD模板'; injection produces 6 sections.
- **Committed in:** `a6158ba` (Task 1 commit)

**2. [Rule 3 - Blocking] get_doc_template name match assumption**
- **Found during:** Task 1 (PromptGeneratorV2._select_task_knowledge)
- **Issue:** Plan assumed `get_doc_template` matches by name field which "corresponds to task name", but doc names include 模板/模板 suffix (e.g., "PRD模板") while task names don't.
- **Fix:** Used `get_doc_templates(task_type)` instead, which matches by the `task_type` field that directly corresponds to task names.
- **Files modified:** `prompt_tool/generator.py` (PromptGeneratorV2._select_task_knowledge)
- **Verification:** Documented in same commit fix as #1 above.
- **Committed in:** `a6158ba`

---

**Total deviations:** 2 auto-fixed (both Rule 3 - blocking)
**Impact on plan:** Both fixes are corrections to API calls that would have resulted in empty output structure sections. No scope creep.

## Known Stubs

The following are intentionally documented as placeholders for future plans:

| Stub | File | Line | Reason |
|------|------|------|--------|
| `_direct()` simple placeholder | generator.py:297 | Intentionally minimal; Plan 02 adds strategy differentiation |
| `_roleplay()` simple placeholder | generator.py:301 | Intentionally minimal; Plan 02 adds strategy differentiation |
| `_detailed()` uses _inject_all() | generator.py:305 | Minimal injection placement; Plan 02 reworks strategy-specific injection profiles |

These are explicitly per the plan spec: "Strategy stubs — add three placeholder methods that Plan 02 will fully implement."

## Issues Encountered

- KnowledgeManager requires `initialize()` call before `load_pack()` works. This is handled by PromptToolApp.__init__() at startup (existing architecture).
- Fallback pack returned by `knowledge_manager.load_pack()` for unknown industry IDs is a valid KnowledgePack with empty data (no roles, terms, pain_points). Injection methods handle this gracefully by returning empty strings.

## Next Phase Readiness

- `PromptGeneratorV2` class is ready for Plan 02 to add differentiated strategy implementations (`_direct()`, `_roleplay()`, `_detailed()`)
- Knowledge injection infrastructure (_inject_all + 4 individual methods) is ready for Plan 02 to use selectively per strategy
- `generate_prompts_v2()` factory is available for direct import if needed
- ConversationEngine.generate_complete() pipeline is fully wired and tested

## Self-Check: PASSED

- All 3 files modified verified present (generator.py, conversation_engine.py, app.py)
- Both task commits verified (`a6158ba`, `384bbe3`)
- SUMMARY.md verified present and committed (`103f151`)
- No unintended side effects on existing functionality

---
*Phase: 05-generation-v2*
*Completed: 2026-06-04*
