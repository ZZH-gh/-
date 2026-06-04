---
phase: 05-generation-v2
plan: 03
type: execute
subsystem: generation
tags: [GEN-04, QA-02, anti-pattern, filter, pain-point, TDD]
requires: [05-01, 05-02]
provides: [GEN-04, QA-02-injection-tests, QA-02-quality-verify]
affects: [prompt_tool/generator.py]
tech-stack:
  added: []
  patterns:
    - "Pain-point-driven anti-pattern filtering (two-layer: knowledge pack + regex)"
    - "Lazy-init rules cache in class attribute"
key-files:
  created: []
  modified:
    - prompt_tool/generator.py
    - tests/conftest.py
    - tests/test_generator_v2.py
    - tests/test_qa_evaluation.py
decisions:
  - "Anti-pattern filter uses two-layer architecture: pain_point phrase replacement (primary, D-15) + regex authority/stereotype removal (secondary, D-16)"
  - "Filter is wired as post-generation step in generate_all() — each strategy output passes through _filter() before return"
  - "Rules are cached lazily (_anti_pattern_rules = None in __init__, built on first _filter() call)"
metrics:
  duration: "~5 minutes"
  completed_date: "2026-06-04"
---

# Phase 5 Plan 3: Anti-Pattern Filter and Test Infrastructure Upgrade — Summary

Implement pain-point-driven anti-pattern filter (GEN-04) inside PromptGeneratorV2, replacing the draft's hardcoded ANTI_PATTERNS regex list with a data-driven two-layer filter. Upgrade test fixtures with real KnowledgePack data (roles, docs, pain_points). Strengthen QA-02 assertions to conclusively verify v4.0 > v3.0 quality.

## Tasks Executed

| # | Task | Type | Result |
|---|------|------|--------|
| 1 | Implement _build_anti_pattern_rules() + _filter() with pain-point-driven logic, wire into generate_all() | auto (TDD) | **RED** `577e734` (6 failing tests) → **GREEN** `0e10237` (13 passing, 20 total after import update) |
| 2 | Extend conftest.py fixtures (roles/docs/pain_points), add fully_loaded_pack, upgrade injection point tests + QA-02 assertions | auto | `431071b` — 27 tests pass across test_generator_v2.py and test_qa_evaluation.py |
| 3 | Run full test suite and verify QA-02 quality comparison | auto | All 114 tests pass, zero regressions. QA-02: v4 total 798 chars vs v3 576 chars (138.5%) |

## Key Implementation Details

### _build_anti_pattern_rules() — Two-layer filter design

- **PRIMARY layer (D-15, D-18):** Iterates `self._pack.get_pain_points()`, extracts `typical_phrases` as trigger keywords. Generates pain_point rules with `{"type": "pain_point", "trigger_phrases": [...], "description": "...", "replacement": "..."}`.
- **SECONDARY layer (D-16):** 8 hardcoded regex rules for false authority claims (e.g., `作为.*[资深|首席|全球].*专家`) and industry stereotypes (e.g., `毫无疑问.*(?:正确|有效|最佳)`).
- When `self._pack` is None (fallback mode), only the 8 regex rules are active — still provides baseline anti-pattern protection.

### _filter() execution (D-17)

1. Pain point rules: phrase `in` check → `str.replace()` with warning note
2. Regex authority/stereotype rules: `re.sub()` with empty replacement
3. Result stripped of leading/trailing whitespace

Rules are lazily built on first `_filter()` call and cached in `self._anti_pattern_rules`.

### Test infrastructure upgrades

- **conftest.py:** `sample_pack_json` extended with 2 roles (with KPIs + pain_points), 1 PRD doc template (4 sections + common_mistakes), 2 pain_points (typical_phrases + what_not_to_do). New `fully_loaded_pack` fixture returns `KnowledgePack` instance.
- **test_generator_v2.py:** 4 injection point tests verifying KPI, structure sections, anti-pattern warnings, and quality standards in strategy outputs. 2 pain-point-driven filter tests. `ANTI_PATTERNS` constant verification.
- **test_qa_evaluation.py:** Import path fixed to `prompt_tool.generator`. Threshold raised from 0.5 to 0.7. Structure markers minimum increased from 2 to 3. Anti-pattern coverage expanded from 3 to 8 patterns. New role depth test.

## Deviations from Plan

None. Plan executed exactly as written.

## Test Results

### test_generator_v2.py: 20/20 passed
- TestGeneratorV2: 12 passed (8 original + 4 injection point tests)
- TestAntiPatternFilter: 8 passed (4 original + 2 pain-point + 1 no-hardcoded + 1 list-check)

### test_qa_evaluation.py: 7/7 passed
- All QA-02 assertions strengthened; thresholds met

### Full suite: 114/114 passed
- Zero regressions across all 14 test modules

## QA-02 Quality Comparison

| Strategy | v3 (chars) | v4 (chars) | Ratio |
|----------|-----------|-----------|-------|
| direct | 120 | 198 | 165.0% |
| roleplay | 151 | 228 | 151.0% |
| detailed | 305 | 372 | 122.0% |
| **Total** | **576** | **798** | **138.5%** |

Anti-patterns found: **0** across all strategies.

## Commit History

| Hash | Message |
|------|---------|
| `577e734` | test(05-generation-v2-03): add failing tests for anti-pattern filter (TDD RED) |
| `0e10237` | feat(05-generation-v2-03): implement anti-pattern filter (TDD GREEN) |
| `431071b` | feat(05-generation-v2-03): extend fixtures and upgrade test assertions |

## Self-Check: PASSED

- [x] All files created/modified verified to exist
- [x] All commits verified in git log
- [x] All 114 tests pass
- [x] QA-02 conclusively shows v4.0 > v3.0
- [x] No stubs found in implementation
- [x] No new threat surface beyond modeled T-05-05, T-05-06
