---
phase: 06
slug: ui
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-04
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `pytest.ini` |
| **Quick run command** | `python -m pytest tests/test_ui.py -x -v` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_ui.py -x`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 06-01-01 | 01 | 1 | UI-01, UI-02 | unit | `pytest tests/test_ui.py::test_app_controller_init` | ⬜ W0 |
| 06-01-02 | 01 | 1 | UI-01 | unit | `pytest tests/test_ui.py::test_chat_bubble_rendering` | ⬜ W0 |
| 06-01-03 | 01 | 1 | UI-01, UI-02 | unit | `pytest tests/test_ui.py::test_frame_switching` | ⬜ W0 |
| 06-02-01 | 02 | 2 | UI-01 | unit | `pytest tests/test_ui.py::test_message_types` | ⬜ W0 |
| 06-02-02 | 02 | 2 | UI-01 | unit | `pytest tests/test_ui.py::test_navigation` | ⬜ W0 |
| 06-03-01 | 03 | 3 | UI-03 | unit | `pytest tests/test_ui.py::test_optimization_panel` | ⬜ W0 |
| 06-03-02 | 03 | 3 | UI-04, QA-03 | unit | `pytest tests/test_generator_v2.py::test_compliance_disclaimer` | ⬜ W0 |

---

## Wave 0 Requirements

- [ ] `tests/test_ui.py` — stubs for UI-01~04 tests
- [ ] Existing `tests/conftest.py` — extend with UI fixtures if needed

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Dialog bubble visual layout | UI-01 | Requires visual inspection | Launch app, verify user/msg bubbles alternate left/right |
| Escape door UX | UI-02 | Requires manual interaction test | Start input, verify generate button triggers skip_follow_up |
| Optimization panel interaction | UI-03 | Requires visual inspection | Verify panel toggles, input, dropdown, re-generation |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
