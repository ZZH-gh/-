---
phase: 2
slug: knowledge-layer
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-03
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 (from Phase 1) |
| Config file | pytest.ini |
| Quick run command | `python build_packs.py && python -m pytest tests/test_knowledge_manager.py tests/test_knowledge_pack.py -x --tb=short` |
| Full suite command | `python build_packs.py && python -m pytest tests/ -x --tb=short` |
| Estimated runtime | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python build_packs.py && pytest tests/test_knowledge_manager.py tests/test_knowledge_pack.py -x --tb=short`
- **After every plan wave:** Run `python build_packs.py && pytest tests/ -x --tb=short`
- **Before /gsd-verify-work:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | KNOW-03 | T-2-01 | json.load() from trusted compiled artifacts only | unit | `pytest tests/test_knowledge_manager.py -x` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | KNOW-03 | T-2-01 | No user input reaches json.load() | integration | `pytest tests/test_build.py::test_index_generated -x` | ❌ W0 | ⬜ pending |
| 02-01-03 | 01 | 1 | KNOW-03 | — | Fallback to knowledge.py on load failure | unit | `pytest tests/test_knowledge_manager.py::test_fallback -x` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 2 | KNOW-04 | — | Expanded pack passes all 8 dimensions + thresholds | content | `pytest tests/test_content.py -x` | Existing (update) | ⬜ pending |
| 02-02-02 | 02 | 2 | KNOW-04 | — | Each new scenario has 5-8 node follow-up tree | content | `pytest tests/test_content.py::TestFollowUpTreeChecks -x` | Existing (update) | ⬜ pending |
| 02-02-03 | 02 | 2 | KNOW-03 | — | build_packs.py generates valid index.json with all packs | integration | `python build_packs.py && python -c "import json; d=json.load(open(...)); assert 'industries' in d"` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Gaps

- [ ] `tests/test_knowledge_manager.py` — unit tests: initialize, match_industry, load_pack, LRU cache, fallback
- [ ] `tests/test_knowledge_pack.py` — unit tests: getter methods, None returns, empty collections
- [ ] `tests/test_build.py::test_index_generated` — integration test for index.json auto-generation
- [ ] `tests/conftest.py` — fixtures for compiled JSON test data, KnowledgeManager test harness
- [ ] `tests/test_content.py` — update THRESHOLDS: terms→80, tasks→15, trees→15, roles→8, workflows→5, docs→6, pain_points→8
- [ ] `tests/test_content.py` — add VARIANT_CHECKS for each of the 10 new scenarios

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Knowledge pack expansion content quality | KNOW-04 | Domain accuracy requires SME review | Spot-check 5 new scenarios for realistic branching logic, term accuracy, and Chinese naturalness |
| engine.py integration correctness | KNOW-03 | Integration behavior across engine/generator/app interaction | Run the full app, type an IT-related input, verify industry detection and prompt generation still work with new KnowledgeManager |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] nyquist_compliant: true set in frontmatter

**Approval:** pending
