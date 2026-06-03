---
phase: 1
slug: foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-03
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (Wave 0 installs) |
| **Config file** | `pytest.ini` or `pyproject.toml` (Wave 0) |
| **Quick run command** | `python build_packs.py` (compile + validate all packs) |
| **Full suite command** | `python build_packs.py && python -m pytest tests/ -x` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python build_packs.py`
- **After every plan wave:** Run `python build_packs.py && python -m pytest tests/ -x`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | KNOW-01 | T-1-01 / — | yaml.safe_load() prevents code injection | unit | `pytest tests/test_schema.py::test_valid_pack -x` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | KNOW-01 | — | Pydantic model rejects invalid data | unit | `pytest tests/test_schema.py::test_missing_required -x` | ❌ W0 | ⬜ pending |
| 01-01-03 | 01 | 1 | KNOW-02 | T-1-01 | build_packs.py uses safe YAML parsing | integration | `pytest tests/test_build.py::test_chinese_encoding -x` | ❌ W0 | ⬜ pending |
| 01-01-04 | 01 | 1 | KNOW-09 | — | Build fails with clear error on invalid input | integration | `python build_packs.py` (bad input fixture) | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 2 | KNOW-02 | — | Internet/IT YAML compiles to valid JSON | integration | `python build_packs.py` | ❌ W0 | ⬜ pending |
| 01-02-02 | 02 | 2 | QA-01 | — | 8 dimensions present, content thresholds met | content | `pytest tests/test_content.py -x` | ❌ W0 | ⬜ pending |
| 01-02-03 | 02 | 2 | KNOW-02 | — | Compiled JSON has correct Chinese encoding | integration | `pytest tests/test_build.py::test_chinese_encoding -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_schema.py` — unit tests for Pydantic models (covers KNOW-01)
- [ ] `tests/test_build.py` — integration tests for build_packs.py (covers KNOW-02, KNOW-09)
- [ ] `tests/conftest.py` — fixtures for valid/invalid YAML test data
- [ ] `tests/test_content.py` — content tests for QA-01 criteria on the Internet/IT pack
- [ ] pytest configuration: `pytest.ini` or `pyproject.toml` with `[tool.pytest.ini_options]`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Follow-up tree completeness review | QA-01 | Content quality requires human judgment | For each of 5 scenarios, review the YAML follow-up tree: does the branching cover realistic user paths? Are the variant cases (管理层 vs 一线, 好业绩 vs 差业绩) differentiated? Is the question wording natural in Chinese? |
| Internet/IT knowledge pack accuracy | QA-01 | Domain accuracy requires SME review | Spot-check 10 terms, 3 tasks, and 2 workflows for factual accuracy and industry relevance. Verify role descriptions match real Internet/IT job functions. |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
