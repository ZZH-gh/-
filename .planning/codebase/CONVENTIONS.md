# Coding Conventions

**Analysis Date:** 2026-06-03

## Naming Patterns

**Files:**
- Python source files use `snake_case.py`.
- Entry points use `run.py` (standalone script in project root).
- Example: `prompt_tool/engine.py`, `prompt_tool/generator.py`, `prompt_tool/knowledge.py`.

**Functions:**
- Functions and methods use `snake_case`.
- Private/helper methods prefixed with a single underscore: `_clean_text()`, `_build_header()`, `_on_generate()`.
- Public methods have no underscore prefix: `analyze()`, `generate_all()`, `run()`.
- Method names are descriptive Chinese-English hybrids in some cases (e.g., `_on_focus_in`, `_build_input_area`) but primarily English.
- Standalone module-level functions use same `snake_case` convention: `generate_prompts()`, `get_all_industry_names()`.

**Variables:**
- Variables use `snake_case`: `analysis_result`, `industry_key`, `best_industry_name`.
- Instance attributes use `self.snake_case` pattern.
- Boolean flags sometimes prefixed with underscore: `self._ph_active` (placeholder active).
- Some variables use short abbreviations: `btn`, `kw`, `fmt`, `bg`, `ind`, `r` (result dict), `f` (frame), `h` (header frame), `c` (color), `df` (display frame).

**Types:**
- Classes use `PascalCase`: `AnalysisEngine`, `PromptGenerator`, `PromptToolApp`.
- Class names are descriptive noun phrases that describe the component's purpose.
- Data structures use Python built-in dicts and lists rather than custom types/dataclasses.

**Constants:**
- Module-level constants use `UPPER_SNAKE_CASE`: `INDUSTRIES`, `TASK_TYPES`, `ROLES`, `STRATEGIES`, `OUTPUT_FORMATS`, `STOP_WORDS`, `TONE_KEYWORDS`.

## Code Style

**Formatting:**
- No formatter detected. The codebase has no `.editorconfig`, `pyproject.toml`, or formatter configuration.
- Inconsistent whitespace: `analysis_result` dictionary literals (engine.py line 70-84) use consistent spacing, but other parts vary.
- String concatenation uses f-strings (`f"..."`) and implicit string concatenation in f-string expressions.
- Multi-line imports use backslash continuation (app.py line 15-17) rather than parenthesized imports.

**Linting:**
- No linter configuration detected (no `.flake8`, `pyproject.toml` with linter config, or `setup.cfg`).
- No type checker (mypy/pyright) configuration detected.

**Line Length:**
- Lines frequently exceed 80 characters. The longest lines are in `prompt_tool/generator.py` (e.g., line 113: 168 chars) and `prompt_tool/app.py` (line 425: 140 chars).
- No enforced maximum line length.

## Import Organization

**Order:**
1. Python standard library (in logical groups)
2. Third-party packages
3. Local/relative imports

Example from `prompt_tool/app.py`:
```python
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import threading
import time
import os

from .engine import AnalysisEngine
from .generator import generate_prompts
from .knowledge import (
    STRATEGIES, get_all_industry_names
)
```

**Path Aliases:**
- `customtkinter` imported as `ctk`: `import customtkinter as ctk`.
- `tkinter` imported as `tk`: `import tkinter as tk`.
- No path alias configuration (no `sys.path` manipulation beyond the entry point adding the project root).

**Relative vs Absolute:**
- Module-internal imports use relative imports: `from .engine import AnalysisEngine`, `from .knowledge import INDUSTRIES`.
- Entry points (`run.py`, `main.py`) use `sys.path.insert(0, ...)` then absolute imports: `from prompt_tool.app import PromptToolApp`.

## Error Handling

**Patterns:**
- `try/except` blocks used at entry points for fatal errors with user-friendly messages via `messagebox.showerror()`.
- No custom exception classes defined.
- Error handling is minimal in core logic -- `AnalysisEngine` and `PromptGenerator` do not catch exceptions internally.
- `PromptToolApp._do_generate()` wraps the generation call in `try/except` and dispatches errors to the UI thread via `self.root.after(0, lambda: self._on_error(str(e)))`.
- `PromptToolApp._on_export()` has a simple `try/except` that falls back to clipboard-only if file export fails.

Example from `prompt_tool/app.py`:
```python
def _do_generate(self, content):
    try:
        manual = self.industry_combo.get()
        if manual == "自动识别":
            manual = None
        time.sleep(0.15)

        self.analysis_result = self.engine.analyze(content, manual)
        self.generated_prompts = generate_prompts(self.analysis_result)
        self.root.after(0, self._on_done)
    except Exception as e:
        self.root.after(0, lambda: self._on_error(str(e)))
```

**Return Values for Errors:**
- No explicit error return types -- methods return empty/fallback values instead: empty list `[]`, default strings, or `None`/falsy values.
- `AnalysisEngine._identify_industry()` returns `("通用", "通用 / 其他")` fallback when no industry matches.
- `AnalysisEngine._fallback_task()` returns a dict with score 1 as default when no task is identified.

## Logging

**Framework:** No logging framework used. Uses `print()` only for startup errors in `main.py` and `messagebox` for user-facing errors.

**Patterns:**
- Debug/info messages: written to the UI status bar via `self.set_status()` (e.g., `self.set_status("✅ 已生成 3 个提示词方案")`).
- Errors: shown via `messagebox.showerror()` for blocking errors and `self.set_status()` for informational status.
- No structured logging (no log levels, no log files).

## Comments

**When to Comment:**
- Module-level docstrings explain the file's purpose and architecture.
- Section headers use Chinese comment blocks with `# ========` separators to group related methods.
- Brief Chinese inline comments mark subsections (e.g., `# 策略标签`, `# 操作栏`, `# 提示词展示框`).

**Docstrings:**
- Module-level docstrings use `"""..."""` with triple quotes in Chinese.
- Class docstrings are present in some files (e.g., `engine.py` line 13-15).
- Method docstrings are sparse: only `analyze()` in `engine.py` has an Args/Returns docstring.
- `knowledge.py` uses docstrings for public helper functions (e.g., `get_all_industry_names()`).
- `generator.py` has no method docstrings.
- `app.py` has minimal docstrings on some methods: `_build_info_bar`, `_build_strategies_area`.

## Function Design

**Size:**
- Functions range from 1-3 lines (simple getters) to ~50 lines (complex UI builders and analysis methods).
- No enforced maximum function length. The largest methods are UI build methods in `app.py` (e.g., `_build_input_area` at ~50 lines).

**Parameters:**
- Parameters use `snake_case` with optional type hints inconsistently applied.
- Default parameter values used where sensible (e.g., `manual_industry: str = None`, `_darken(self, c, a=0.2)`).
- Event handlers accept `_` as a dummy parameter: `def _on_input_change(self, _=None)`.

**Return Values:**
- Core logic methods return typed values consistently (dict, str, list, tuple).
- UI event handlers have no return value (return `None`).
- Pattern: return early with fallback/default values for error cases rather than raising exceptions.

## Module Design

**Exports:**
- Modules export classes and functions at module level.
- `__init__.py` contains only a single comment line -- no explicit re-exports.
- Factory function pattern: `generate_prompts()` in `generator.py` wraps `PromptGenerator` class usage.
- `knowledge.py` exports a mix of constants (`INDUSTRIES`, `STRATEGIES`, etc.) and helper functions.

**Barrel Files:**
- No barrel/index pattern. Each consumer imports directly from the source module.
- `app.py` imports `STRATEGIES` and `get_all_industry_names` from `.knowledge`.
- `engine.py` imports multiple named exports from `.knowledge`.

## Type Annotations

- Used consistently in `prompt_tool/engine.py` (return types on every method, parameter types on `analyze`).
- Used in `prompt_tool/generator.py` (return types on every method, no parameter types except `__init__`).
- NOT used in `prompt_tool/app.py` (no type annotations on any method).
- NOT used in `prompt_tool/main.py` or `prompt_tool/knowledge.py`.
- Pattern: type annotations used in module-level function signatures in `knowledge.py` -- they are not annotated.

## Anti-Patterns

**Module-level mutable state:**
- `engine.py` line 328: `default_engine = AnalysisEngine()` -- global engine instance created at module level.
- `app.py` line 19-20: `ctk.set_appearance_mode("light")` and `ctk.set_default_color_theme("blue")` run at module import time.

**Hardcoded data in source:**
- `knowledge.py` contains all industry data, roles, strategies, and output formats inline (~860 lines). This is intentional for offline operation but makes the file very large and hard to maintain.

**Inconsistent string quoting:**
- Mix of `"` and `'` string literals within and across files with no consistent convention.
- Some strings use backslash continuation for long lines, others let them exceed 120+ characters.

**Magic numbers:**
- UI dimensions (window size `"1050x740"`, font sizes `22`, `12`, `13`, padding values like `12`, `15`, `25`) are scattered through `app.py` without named constants.

---

*Convention analysis: 2026-06-03*
