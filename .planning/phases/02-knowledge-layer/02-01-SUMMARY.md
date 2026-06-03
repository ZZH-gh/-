---
phase: 02-knowledge-layer
plan: 01
subsystem: knowledge-runtime
tags: knowledge-manager, knowledge-pack, lazy-loading, lru-cache, industry-matching, build-automation, pytest
requires:
  - Phase 1 build pipeline (build_packs.py, compiled JSON in knowledge_packs_compiled/)
provides:
  - KnowledgePack runtime wrapper class with 8 typed getter methods
  - KnowledgeManager singleton (initialize, match_industry, load_pack, LRU-2 cache, fallback)
  - build_packs.py _generate_index() for auto-creating index.json from compiled packs
  - index.json for internet_it (3.7KB, 1 entry, 147 keywords)
  - engine.py integration: _identify_industry() delegates to KnowledgeManager
  - app.py integration: knowledge_manager.initialize() in __init__ before AnalysisEngine
  - 25 new passing tests (15 knowledge_pack + 10 knowledge_manager + 1 build)
affects: [03-context, 04-conversation, 05-generation, 08-packaging]

tech-stack:
  added:
    - Python stdlib collections.OrderedDict (LRU-2 cache)
    - Python stdlib typing.NamedTuple (IndustryMatch)
    - Python stdlib pathlib (path resolution, PyInstaller-aware)
  patterns:
    - Lazy loading: load index at startup (~5KB), load full pack on demand (~300KB)
    - LRU-2 cache with OrderedDict move_to_end() / popitem(last=False)
    - Module-level singleton (knowledge_manager = KnowledgeManager())
    - Fallback to v3.0 knowledge.py on load failure (silent degradation)
    - Local import inside load_pack/_load_from_disk to avoid circular imports

key-files:
  created:
    - prompt_tool/knowledge_pack.py (KnowledgePack class, 8 typed getters, 0 runtime deps)
    - prompt_tool/knowledge_manager.py (KnowledgeManager singleton, LRU-2, match_industry)
    - tests/test_knowledge_pack.py (15 unit tests)
    - tests/test_knowledge_manager.py (10 unit tests)
  modified:
    - build_packs.py (added _generate_index(), called in main() after compile success)
    - prompt_tool/engine.py (_identify_industry() delegates to knowledge_manager.match_industry)
    - prompt_tool/app.py (knowledge_manager.initialize() + fallback warning in __init__)
    - tests/conftest.py (added sample_pack_json, sample_index_json, temp_compiled_dir fixtures)
    - tests/test_build.py (added TestIndexGenerated for index.json auto-generation)
  compiled:
    - prompt_tool/knowledge_packs_compiled/index.json (3.7KB, auto-generated)

key-decisions:
  - "KnowledgePack uses only Python stdlib dict/list operations — zero runtime dependencies"
  - "Local import of KnowledgePack inside KnowledgeManager methods avoids circular imports"
  - "LRU-2 cache capacity of 2 uses OrderedDict (not custom linked list) — matches RESEARCH.md Don't Hand-Roll guidance"
  - "_resolve_compiled_dir() handles both dev (Path(__file__).parent) and PyInstaller (sys._MEIPASS) modes"
  - "minimum input length threshold of 2 characters prevents short input false matches"
  - "industry_id comes from index keys (compile-time defined), never from user input — prevents path traversal"
  - "keywords in index exclude related_terms to prevent bloat (147 keywords at 3.7KB, under 5KB target)"
  - "engine.py still imports INDUSTRIES for _identify_task / _get_industry_key — Phase 5 will migrate these"

requirements-completed:
  - KNOW-03

duration: 12min
completed: 2026-06-03
---

# Phase 2 Plan 1: Knowledge Layer — Runtime Knowledge Pack Loader

**Lazy-loading knowledge pack infrastructure: KnowledgeManager singleton loads lightweight index (~5KB) at startup, matches industry via keyword scoring, loads full packs (~300KB) on demand with LRU-2 cache, with silent fallback to v3.0 knowledge.py on load failure.**

## Performance

- **Duration:** 12 minutes
- **Started:** 2026-06-03T14:11:28Z
- **Completed:** 2026-06-03T14:23:28Z (approx)
- **Tasks:** 3 (2 TDD, 1 integration)
- **Files created:** 2 (+ 2 test files)
- **Files modified:** 5 (+ 2 for app.py/engine.py cleanup)
- **Tests added:** 26 (15 KnowledgePack + 10 KnowledgeManager + 1 build index)
- **Full suite:** 51 tests, all PASS

## Accomplishments

### KnowledgePack (prompt_tool/knowledge_pack.py)
- 8 typed getter methods: get_meta(), get_terms(category?), get_task(name), get_tasks(), get_roles(), get_role(name), get_workflow(name), get_workflows(category?), get_doc_template(name), get_doc_templates(task_type?), get_follow_up_tree(task_type), get_pain_points()
- All methods return native Python types (dict/list/None) -- no Pydantic in runtime
- Filter parameters on list methods for category/task_type scoping
- Null-safe: missing keys return empty list or None, never raise KeyError

### KnowledgeManager (prompt_tool/knowledge_manager.py)
- Module-level singleton: `knowledge_manager = KnowledgeManager()`
- `initialize()`: resolves compiled dir via dual-path (dev sys._MEIPASS), loads index.json, fallback on failure
- `match_industry(text)`: keyword weight scoring (exact +3, case-insensitive +2), sorted ranking
- `load_pack(id)`: LRU-2 cache via OrderedDict, disk load on miss, popitem(last=False) eviction
- `_build_fallback_index()`: constructs minimal index from knowledge.py INDUSTRIES dict
- `_build_fallback_pack()`: wraps knowledge.py industry data in KnowledgePack-compatible dict
- `is_fallback_active()`: status check for UI warning display

### build_packs.py _generate_index()
- Iterates all compiled JSONs, skips existing index.json
- Collects keywords from term names + aliases + task names (excludes related_terms to prevent bloat)
- Computes stats: term_count, scenario_count, tree_count, role_count, workflow_count
- Writes index.json with ensure_ascii=False, indent=2
- Called in main() after all packs compile successfully, before "All packs compiled" message
- Generated index.json: 3.7KB, 1 entry (internet_it), 147 keywords

### engine.py Integration
- `_identify_industry()` now calls `knowledge_manager.match_industry(text)`
- industry_scores dict format preserved: {industry_id: score} for top-3 matches
- Method signature unchanged: `(self, text, keywords) -> tuple` -- caller compatibility
- INDUSTRIES import retained for _identify_task, _get_industry_key, get_industry_context

### app.py Integration
- `knowledge_manager.initialize()` called before AnalysisEngine() construction
- Fallback warning deferred to after `_setup_ui()` when set_status() is available
- Zero changes to event loop, threading, or generation pipeline

## Task Commits

Each task was committed atomically:

1. **Task 1: Test Infrastructure (RED)** — `d3fd09c` — `test(02-knowledge-layer): add failing tests for KnowledgePack, KnowledgeManager, and _generate_index`
2. **Task 2: Implementation (GREEN)** — `941f322` — `feat(02-knowledge-layer): implement KnowledgePack, KnowledgeManager, and _generate_index`
3. **Task 3: Integration** — `c7aa128` — `feat(02-knowledge-layer): integrate engine.py and app.py with KnowledgeManager`

## TDD Gate Compliance

- RED gate: `test(02-knowledge-layer): add failing tests for KnowledgePack...` (d3fd09c) — PASS
- GREEN gate: `feat(02-knowledge-layer): implement KnowledgePack, KnowledgeManager...` (941f322) — PASS
- Sequence: test commit precedes feat commit — PASS

## Test Results

Full suite: `pytest tests/ -x --tb=short` — 51 passed in 0.11s

| Test file | Count | Status |
|-----------|-------|--------|
| tests/test_schema.py | 8 | PASS (all) |
| tests/test_build.py | 6 | PASS (all) |
| tests/test_content.py | 12 | PASS (all) |
| tests/test_knowledge_manager.py | 10 | PASS (all) |
| tests/test_knowledge_pack.py | 15 | PASS (all) |

## Files Created/Modified

- `prompt_tool/knowledge_pack.py` — NEW: KnowledgePack wrapper class with 8 typed getter methods
- `prompt_tool/knowledge_manager.py` — NEW: KnowledgeManager singleton with LRU-2 cache and industry matcher
- `build_packs.py` — MODIFIED: added _generate_index(), called in main() on success
- `prompt_tool/engine.py` — MODIFIED: _identify_industry() delegates to KnowledgeManager
- `prompt_tool/app.py` — MODIFIED: knowledge_manager.initialize() in __init__
- `tests/conftest.py` — MODIFIED: added 3 new fixtures (sample_pack_json, sample_index_json, temp_compiled_dir)
- `tests/test_knowledge_pack.py` — NEW: 15 KnowledgePack getter tests
- `tests/test_knowledge_manager.py` — NEW: 10 KnowledgeManager tests
- `tests/test_build.py` — MODIFIED: added TestIndexGenerated test
- `prompt_tool/knowledge_packs_compiled/index.json` — COMPILED: auto-generated index (3.7KB)

## Deviations from Plan

None — plan executed exactly as written.

## Threat Flags

None — all threat model mitigations implemented:
- T-2-01: All json.load() wrapped in try/except (FileNotFoundError, json.JSONDecodeError)
- T-2-02: industry_id sourced from index keys, not user input; fallback handles missing packs
- T-2-03: Fallback errors printed to stdout in dev mode, suppressed in exe
- T-2-SC: No new packages installed

## Known Stubs

None — all "empty" data paths are in the fallback path which is documented as intentional degradation.

## Verification Results

1. `pytest tests/ -x --tb=short` — 51/51 PASS
2. `python build_packs.py` — exit 0, "Generated index.json with 1 industry entries"
3. `prompt_tool/knowledge_packs_compiled/index.json` — 3.7KB (under 5KB target)
4. Smoke test: `knowledge_manager.match_industry("帮我写一个PRD文档")` → Internet/IT, score 3.0
5. Smoke test: `knowledge_manager.match_industry("写代码实现一个API接口")` → Internet/IT
6. Smoke test: `knowledge_manager.load_pack("internet_it")` → 36 terms, 5 tasks
7. No circular imports: `from prompt_tool.knowledge_manager import knowledge_manager` works

## Next Phase Readiness

- KnowledgeManager is ready for Phase 2 Plan 2 (Internet/IT content expansion)
- LRU-2 cache with capacity 2 is in place for multi-industry support
- Fallback path proven: missing index.json gracefully degrades to v3.0 knowledge.py
- build_packs.py automatically regenerates index.json on every compile
- Next wave (Plan 2) will extend knowledge_packs/01-internet-it.yaml to KNOW-04 specs

## Self-Check: PASSED

- All 6 key files exist and verified
- All 3 commits (d3fd09c, 941f322, c7aa128) present in git history
- 51/51 tests passing
- `python build_packs.py` runs with exit code 0, generates index.json
- KnowledgeManager, KnowledgePack, _generate_index all verified via smoke tests
