# Testing Patterns

**Analysis Date:** 2026-06-03

## Test Framework

**Runner:** Not detected -- no testing framework is installed or configured.

**Assertion Library:** Not detected.

**Run Commands:** No test commands exist.

## Test File Organization

**Location:** No test directory or test files exist anywhere in the project.

- No `tests/` directory at the project root.
- No test files inside `prompt_tool/`.
- No `conftest.py` anywhere.
- No `setup.py`, `pyproject.toml`, or `setup.cfg` with test configuration.

**Naming:** No test files found matching `*test*.py`, `*_test.py`, or `*_spec.py` patterns in the project source.

## Test Structure

**Suite Organization:** No test suites exist.

**Patterns:** Not applicable.

## Mocking

**Framework:** Not detected.

**Patterns:** Not applicable.

**What to Mock:** Not applicable.

**What NOT to Mock:** Not applicable.

## Fixtures and Factories

**Test Data:** Not applicable.

**Location:** Not applicable.

## Coverage

**Requirements:** None enforced.

**View Coverage:** No coverage tool configured.

## Test Types

**Unit Tests:** None.

**Integration Tests:** None. The project has no integration with external services (fully offline).

**E2E Tests:** None. The application is a desktop GUI (customtkinter/tkinter) with no automated UI testing.

## Testing Recommendations

**Priority: High -- the codebase has zero test coverage.**

### High-Value Test Targets

The following components are well-suited for unit testing and would benefit most from coverage:

1. **`prompt_tool/engine.py` (AnalysisEngine):**
   - `_clean_text()` -- input sanitization, edge cases with mixed Chinese/English/special chars.
   - `_extract_keywords()` -- keyword extraction with bigrams, trigrams, stop word filtering.
   - `_identify_industry()` -- industry matching logic, scoring, fallback to "通用 / 其他".
   - `_identify_task()` -- task identification with industry-scoped and general task types.
   - `_fallback_task()` -- default task determination when no match found.
   - `_extract_requirements()` -- regex-based requirement extraction from varied input.
   - `_identify_tone()` -- tone/style detection with keyword matching.
   - `analyze()` -- full pipeline integration test with known inputs.

2. **`prompt_tool/generator.py` (PromptGenerator):**
   - `_direct()` / `_roleplay()` / `_detailed()` -- strategy-specific prompt generation.
   - `_task_line()` -- input normalization and action prefix detection.
   - `_bullets()` -- requirement formatting with task-specific content.
   - `_format_line()` -- output format detection from keywords.
   - `_tone_hint()` -- tone/style hint selection.
   - `_get_role()` -- role assignment per industry.
   - `_spec_req()` -- industry/task-specific requirements mapping.
   - `generate_all()` -- full integration producing all three strategies.

3. **`prompt_tool/knowledge.py`:**
   - `get_all_industry_names()` -- completeness check (should return all 15 industry names).
   - `get_industry_key()` -- name-to-key lookup correctness.
   - `get_task_types_for_industry()` -- task type retrieval per industry.

### Suggested Test Framework

Given it is a Python 3.14 project with no external API dependencies:

**Recommended:** `pytest` with `pytest-cov`
- Install: `pip install pytest pytest-cov`
- Minimal `pyproject.toml` configuration:
  ```toml
  [tool.pytest.ini_options]
  testpaths = ["tests"]
  python_files = ["test_*.py"]
  ```

### Suggested Test Structure

```
tests/
├── conftest.py                  # Shared fixtures (sample analysis results, industry data)
├── test_engine.py               # AnalysisEngine tests
│   ├── test_clean_text()
│   ├── test_extract_keywords()
│   ├── test_identify_industry()
│   ├── test_identify_task()
│   ├── test_fallback_task()
│   ├── test_extract_requirements()
│   ├── test_identify_tone()
│   ├── test_identify_output_format()
│   └── test_analyze_full()
├── test_generator.py             # PromptGenerator tests
│   ├── test_direct_strategy()
│   ├── test_roleplay_strategy()
│   ├── test_detailed_strategy()
│   ├── test_task_line_parsing()
│   ├── test_bullets_by_task_type()
│   └── test_format_line_detection()
├── test_knowledge.py             # Knowledge module tests
│   ├── test_get_all_industry_names()
│   ├── test_get_industry_key()
│   └── test_get_task_types_for_industry()
└── fixtures/
    ├── sample_inputs.py          # Sample user inputs for parametrized tests
    └── expected_outputs.py       # Expected analysis/prompt results
```

### Suggested Testing Patterns

**Parametrized tests for keyword/industry matching:**
```python
@pytest.mark.parametrize("input_text,expected_industry", [
    ("写一个React组件", "互联网 / IT"),
    ("设计初中数学教案", "教育 / 培训"),
    ("分析销售数据报表", "零售 / 电商"),
])
def test_identify_industry(input_text, expected_industry):
    engine = AnalysisEngine()
    key, name = engine._identify_industry(input_text, engine._extract_keywords(input_text))
    assert name == expected_industry
```

**Edge case testing for text cleaning:**
```python
def test_clean_text_removes_special_chars():
    engine = AnalysisEngine()
    assert engine._clean_text("  hello  世界  ") == "hello 世界"
    assert "！" not in engine._clean_text("你好！世界")
```

**Output format contract testing:**
```python
def test_generate_all_returns_three_strategies():
    result = generate_prompts(SAMPLE_ANALYSIS)
    assert "direct" in result
    assert "roleplay" in result
    assert "detailed" in result
    assert all(isinstance(v, str) and len(v) > 50 for v in result.values())
```

---

*Testing analysis: 2026-06-03*
