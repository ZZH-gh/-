---
phase: 05
slug: generation-v2
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-04
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (stdlib unittest) |
| **Config file** | none — Wave 0 should create `pyproject.toml` or `pytest.ini` |
| **Quick run command** | `python -m pytest prompt_tool/tests/test_generator_v2.py -x` |
| **Full suite command** | `python -m pytest prompt_tool/tests/ -v` |
| **Estimated runtime** | ~2 seconds (existing 87 tests + ~30 new) |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest prompt_tool/tests/test_generator_v2.py -x`
- **After every plan wave:** Run `python -m pytest prompt_tool/tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | GEN-01 | — | N/A | unit | `pytest test_generator_v2.py::test_intent_driven_synthesis` | ❌ W0 | ⬜ pending |
| 05-01-02 | 01 | 1 | GEN-02 | — | N/A | unit | `pytest test_generator_v2.py::test_knowledge_injection_role` | ❌ W0 | ⬜ pending |
| 05-01-03 | 01 | 1 | GEN-02 | — | N/A | unit | `pytest test_generator_v2.py::test_knowledge_injection_quality` | ❌ W0 | ⬜ pending |
| 05-01-04 | 01 | 1 | GEN-02 | — | N/A | unit | `pytest test_generator_v2.py::test_knowledge_injection_output` | ❌ W0 | ⬜ pending |
| 05-01-05 | 01 | 1 | GEN-04 | — | N/A | unit | `pytest test_generator_v2.py::test_anti_pattern_filter` | ❌ W0 | ⬜ pending |
| 05-02-01 | 02 | 1 | GEN-03 | — | N/A | unit | `pytest test_generator_v2.py::test_strategy_direct` | ❌ W0 | ⬜ pending |
| 05-02-02 | 02 | 1 | GEN-03 | — | N/A | unit | `pytest test_generator_v2.py::test_strategy_roleplay` | ❌ W0 | ⬜ pending |
| 05-02-03 | 02 | 1 | GEN-03 | — | N/A | unit | `pytest test_generator_v2.py::test_strategy_detailed` | ❌ W0 | ⬜ pending |
| 05-03-01 | 03 | 2 | QA-02 | — | N/A | integration | `pytest test_generator_v2.py::test_quality_comparison_v3_vs_v4` | ❌ W0 | ⬜ pending |
| 05-03-02 | 03 | 2 | GEN-01 | — | N/A | integration | `pytest test_generator_v2.py::test_conversation_to_generation_flow` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `prompt_tool/tests/test_generator_v2.py` — stubs for all GEN-01~04 + QA-02 tests
- [ ] `prompt_tool/tests/conftest.py` — KnowledgePack fixture for test isolation
- [ ] `prompt_tool/tests/__init__.py` — package marker if missing

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| QA-02 quality comparison | QA-02 | Requires human judgment comparing v3 vs v4 output quality | Generate same input with v3 and v4 paths, compare output depth and usability |
| Anti-pattern naturalness | GEN-04 | Regex/pain-point check can't fully evaluate semantic naturalness | Review filtered outputs for false positives and remaining unnatural patterns |
| Conversation flow integration | GEN-01 | End-to-end flow involves UI threading | Run app, type input, verify complete generation flow through ConversationEngine |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
