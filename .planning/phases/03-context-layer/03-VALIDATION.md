---
phase: 3
slug: context-layer
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-03
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 (from Phase 1) |
| Config file | pytest.ini |
| Quick run command | `pytest tests/test_session_manager.py tests/test_context_builder.py -x --tb=short` |
| Full suite command | `pytest tests/ -x --tb=short` |
| Estimated runtime | ~3 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_session_manager.py tests/test_context_builder.py -x --tb=short`
- **After every plan wave:** Run `pytest tests/ -x --tb=short`
- **Before /gsd-verify-work:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | CONV-06 | T-3-01 | uuid4 session IDs, deepcopy-only snapshots | unit | `pytest tests/test_session_manager.py -x` | ❌ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | CONV-06 | — | No user input reaches filesystem via SessionManager | unit | `pytest tests/test_context_builder.py -x` | ❌ W0 | ⬜ pending |
| 03-01-03 | 01 | 1 | CONV-06 | — | Full lifecycle integration | integration | `pytest tests/test_session_manager.py::test_full_lifecycle -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Gaps

- [ ] `tests/test_session_manager.py` — unit tests: create_session, add_turn, update_confirmed, extracted_info, new_session, snapshot, error cases
- [ ] `tests/test_context_builder.py` — unit tests: output shape, conversation_summary, knowledge_pack_ref, empty session
- [ ] `tests/conftest.py` — fixtures: sample_session_turns, sample_extracted_info, session_manager_instance

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Thread safety under load | CONV-06 | Race conditions are probabilistic; automated tests can't guarantee absence | Run the full app, rapidly type inputs while clicking "生成", verify no corrupted session data or UI freezes |
| Session state in actual multi-turn conversation | CONV-06 | ContextBuilder output quality depends on realistic conversation data | Complete a multi-turn conversation scenario (3+ exchanges), inspect ContextBuilder.build() output for correctness |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] nyquist_compliant: true set in frontmatter

**Approval:** pending
