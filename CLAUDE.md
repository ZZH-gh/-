<!-- GSD:project-start source:PROJECT.md -->

## Project

**智能提示词工坊 (Smart Prompt Workshop)**

一款面向各行业普通用户的桌面工具。用户只需输入一句简短的需求描述，工具通过行业专家级知识库和对话式引导，生成可以直接扔给 AI（ChatGPT/Claude/文心一言等）执行的高质量、细致入微的提示词。

当前已有 v3.0 基础版本（Python + customtkinter 桌面应用，16行业覆盖，3种策略，30MB单文件exe），但提示词偏模板化、缺乏行业深度。v4.0 将重点攻克"细致入微"的问题。

**Core Value:** **让不懂写提示词的普通人，用最简短的语言，最快拿到能让AI真正干活的、有行业深度的提示词。**

### Constraints

- **离线运行**: 运行时绝不能依赖外部API或网络连接 — 所有知识包固化在exe中
- **单文件分发**: 最终产物是一个<50MB的.exe文件，双击即用，无需安装
- **中文优先**: 所有交互界面和知识包内容为中文
- **Windows兼容**: 支持 Windows 10/11 中文系统
- **性能**: 知识分析+提示词生成必须在 2 秒内完成

<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->

## Technology Stack

## Languages

- Python 3.12+ (environment: 3.14.4) - All application code
- Not detected (pure Python project)

## Runtime

- Python runtime, desktop application (tkinter-based GUI)
- pip (via requirements.txt)
- Lockfile: Not present (no requirements-lock.txt or pip freeze output committed)
- Virtual environment: `.venv/` (created with `uv`/venv)

## Frameworks

- customtkinter 5.2.2 - Modern themed tkinter GUI framework for the desktop UI
- tkinter (stdlib) - Base GUI toolkit, used for messagebox, clipboard operations
- Not detected (no test framework configured)
- PyInstaller - Bundles the application into a single Windows executable (`智能提示词工坊.exe`)

## Key Dependencies

- `customtkinter>=5.2.2` - All UI components (buttons, text inputs, combo boxes, labels, frames)
- `pillow>=10.0.0` (Pillow 12.1.1 installed) - Image handling support (transitive dependency of customtkinter for theme assets/icons)
- None beyond the above. The application has zero network dependencies.

## Configuration

- No `.env` file detected. No environment variables required.
- Application runs with zero configuration.
- `build.bat` - Windows batch script for PyInstaller packaging
- `run.py` - Entry point for PyInstaller `--onefile` packaging mode

## Platform Requirements

- Python 3.8+ (as noted in `build.bat`)
- Windows (target platform; PyInstaller builds Windows .exe)
- Packages: `customtkinter>=5.2.2`, `pillow>=10.0.0`
- Windows OS (the packaged .exe runs on Windows without Python)
- No internet connection required

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

## Naming Patterns

- Python source files use `snake_case.py`.
- Entry points use `run.py` (standalone script in project root).
- Example: `prompt_tool/engine.py`, `prompt_tool/generator.py`, `prompt_tool/knowledge.py`.
- Functions and methods use `snake_case`.
- Private/helper methods prefixed with a single underscore: `_clean_text()`, `_build_header()`, `_on_generate()`.
- Public methods have no underscore prefix: `analyze()`, `generate_all()`, `run()`.
- Method names are descriptive Chinese-English hybrids in some cases (e.g., `_on_focus_in`, `_build_input_area`) but primarily English.
- Standalone module-level functions use same `snake_case` convention: `generate_prompts()`, `get_all_industry_names()`.
- Variables use `snake_case`: `analysis_result`, `industry_key`, `best_industry_name`.
- Instance attributes use `self.snake_case` pattern.
- Boolean flags sometimes prefixed with underscore: `self._ph_active` (placeholder active).
- Some variables use short abbreviations: `btn`, `kw`, `fmt`, `bg`, `ind`, `r` (result dict), `f` (frame), `h` (header frame), `c` (color), `df` (display frame).
- Classes use `PascalCase`: `AnalysisEngine`, `PromptGenerator`, `PromptToolApp`.
- Class names are descriptive noun phrases that describe the component's purpose.
- Data structures use Python built-in dicts and lists rather than custom types/dataclasses.
- Module-level constants use `UPPER_SNAKE_CASE`: `INDUSTRIES`, `TASK_TYPES`, `ROLES`, `STRATEGIES`, `OUTPUT_FORMATS`, `STOP_WORDS`, `TONE_KEYWORDS`.

## Code Style

- No formatter detected. The codebase has no `.editorconfig`, `pyproject.toml`, or formatter configuration.
- Inconsistent whitespace: `analysis_result` dictionary literals (engine.py line 70-84) use consistent spacing, but other parts vary.
- String concatenation uses f-strings (`f"..."`) and implicit string concatenation in f-string expressions.
- Multi-line imports use backslash continuation (app.py line 15-17) rather than parenthesized imports.
- No linter configuration detected (no `.flake8`, `pyproject.toml` with linter config, or `setup.cfg`).
- No type checker (mypy/pyright) configuration detected.
- Lines frequently exceed 80 characters. The longest lines are in `prompt_tool/generator.py` (e.g., line 113: 168 chars) and `prompt_tool/app.py` (line 425: 140 chars).
- No enforced maximum line length.

## Import Organization

- `customtkinter` imported as `ctk`: `import customtkinter as ctk`.
- `tkinter` imported as `tk`: `import tkinter as tk`.
- No path alias configuration (no `sys.path` manipulation beyond the entry point adding the project root).
- Module-internal imports use relative imports: `from .engine import AnalysisEngine`, `from .knowledge import INDUSTRIES`.
- Entry points (`run.py`, `main.py`) use `sys.path.insert(0, ...)` then absolute imports: `from prompt_tool.app import PromptToolApp`.

## Error Handling

- `try/except` blocks used at entry points for fatal errors with user-friendly messages via `messagebox.showerror()`.
- No custom exception classes defined.
- Error handling is minimal in core logic -- `AnalysisEngine` and `PromptGenerator` do not catch exceptions internally.
- `PromptToolApp._do_generate()` wraps the generation call in `try/except` and dispatches errors to the UI thread via `self.root.after(0, lambda: self._on_error(str(e)))`.
- `PromptToolApp._on_export()` has a simple `try/except` that falls back to clipboard-only if file export fails.
- No explicit error return types -- methods return empty/fallback values instead: empty list `[]`, default strings, or `None`/falsy values.
- `AnalysisEngine._identify_industry()` returns `("通用", "通用 / 其他")` fallback when no industry matches.
- `AnalysisEngine._fallback_task()` returns a dict with score 1 as default when no task is identified.

## Logging

- Debug/info messages: written to the UI status bar via `self.set_status()` (e.g., `self.set_status("✅ 已生成 3 个提示词方案")`).
- Errors: shown via `messagebox.showerror()` for blocking errors and `self.set_status()` for informational status.
- No structured logging (no log levels, no log files).

## Comments

- Module-level docstrings explain the file's purpose and architecture.
- Section headers use Chinese comment blocks with `# ========` separators to group related methods.
- Brief Chinese inline comments mark subsections (e.g., `# 策略标签`, `# 操作栏`, `# 提示词展示框`).
- Module-level docstrings use `"""..."""` with triple quotes in Chinese.
- Class docstrings are present in some files (e.g., `engine.py` line 13-15).
- Method docstrings are sparse: only `analyze()` in `engine.py` has an Args/Returns docstring.
- `knowledge.py` uses docstrings for public helper functions (e.g., `get_all_industry_names()`).
- `generator.py` has no method docstrings.
- `app.py` has minimal docstrings on some methods: `_build_info_bar`, `_build_strategies_area`.

## Function Design

- Functions range from 1-3 lines (simple getters) to ~50 lines (complex UI builders and analysis methods).
- No enforced maximum function length. The largest methods are UI build methods in `app.py` (e.g., `_build_input_area` at ~50 lines).
- Parameters use `snake_case` with optional type hints inconsistently applied.
- Default parameter values used where sensible (e.g., `manual_industry: str = None`, `_darken(self, c, a=0.2)`).
- Event handlers accept `_` as a dummy parameter: `def _on_input_change(self, _=None)`.
- Core logic methods return typed values consistently (dict, str, list, tuple).
- UI event handlers have no return value (return `None`).
- Pattern: return early with fallback/default values for error cases rather than raising exceptions.

## Module Design

- Modules export classes and functions at module level.
- `__init__.py` contains only a single comment line -- no explicit re-exports.
- Factory function pattern: `generate_prompts()` in `generator.py` wraps `PromptGenerator` class usage.
- `knowledge.py` exports a mix of constants (`INDUSTRIES`, `STRATEGIES`, etc.) and helper functions.
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

- `engine.py` line 328: `default_engine = AnalysisEngine()` -- global engine instance created at module level.
- `app.py` line 19-20: `ctk.set_appearance_mode("light")` and `ctk.set_default_color_theme("blue")` run at module import time.
- `knowledge.py` contains all industry data, roles, strategies, and output formats inline (~860 lines). This is intentional for offline operation but makes the file very large and hard to maintain.
- Mix of `"` and `'` string literals within and across files with no consistent convention.
- Some strings use backslash continuation for long lines, others let them exceed 120+ characters.
- UI dimensions (window size `"1050x740"`, font sizes `22`, `12`, `13`, padding values like `12`, `15`, `25`) are scattered through `app.py` without named constants.

<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

## System Overview

```text

```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| PromptToolApp | Full GUI lifecycle, user input handling, display/output | `prompt_tool/app.py` |
| AnalysisEngine | NLP-light analysis: industry/task detection, keyword extraction, tone identification | `prompt_tool/engine.py` |
| PromptGenerator | Generates 3 prompt strategy variants (direct/roleplay/detailed) | `prompt_tool/generator.py` |
| Knowledge Base | Static data dictionaries for 15 industries, task types, roles, formats | `prompt_tool/knowledge.py` |
| main.py | Module entry point, imports app and runs it | `prompt_tool/main.py` |
| run.py | PyInstaller packaging entry point | `run.py` |

## Pattern Overview

- Completely offline — no network calls, no external API dependencies
- Single-threaded UI with background thread for generation work
- Data flows unidirectionally: User Input -> Analysis -> Generation -> Display
- Knowledge base acts as a pure data source (no side effects, no mutations)
- Each module imports from `knowledge.py` but not from each other (except `app.py` which orchestrates)

## Layers

- Purpose: All user interaction — input capture, result display, copy/export actions
- Location: `prompt_tool/app.py`
- Contains: `PromptToolApp` class with `_setup_ui()`, `_build_*()` methods, event handlers
- Depends on: `engine.py` (AnalysisEngine), `generator.py` (generate_prompts), `knowledge.py` (STRATEGIES, get_all_industry_names)
- Used by: `main.py`, `run.py`
- Purpose: Parse user input to extract industry, task type, requirements, tone, output format using keyword scoring
- Location: `prompt_tool/engine.py`
- Contains: `AnalysisEngine` class with `analyze()` as the main method
- Depends on: `knowledge.py` (INDUSTRIES, TASK_TYPES, ROLES, STOP_WORDS, OUTPUT_FORMATS, TONE_KEYWORDS)
- Used by: `app.py`
- Purpose: Produce 3 ready-to-use prompt strings from analysis result dict
- Location: `prompt_tool/generator.py`
- Contains: `PromptGenerator` class with `generate_all()` returning dict of 3 prompts
- Depends on: `knowledge.py` (INDUSTRIES)
- Used by: `app.py`
- Purpose: Static data dictionaries — no logic, no classes, just module-level constants and helper functions
- Location: `prompt_tool/knowledge.py`
- Contains: INDUSTRIES, TASK_TYPES, ROLES, STRATEGIES, OUTPUT_FORMATS, STOP_WORDS, TONE_KEYWORDS, and 3 helper functions
- Depends on: Nothing (standard library only)
- Used by: `engine.py`, `generator.py`, `app.py`

## Data Flow

### Primary Request Path (Generate Prompts)

### Analysis Data Flow (engine.py)

### Strategy Switching

- Instance state held on `PromptToolApp`: `analysis_result`, `generated_prompts`, `current_strategy`, `_ph_active`
- No persistence between sessions (no database, no config files)
- No global mutable state beyond the module-level `default_engine` in `engine.py:328`

## Key Abstractions

- Purpose: The single structured data contract between analysis and generation layers
- Fields: industry_key, industry_name, task_name, task_key, task_description, requirements (list), tone (str), output_format (dict), all_industries, all_tasks, original_input, cleaned_input, keywords
- Consumed by: `PromptGenerator.__init__()` and UI display
- Purpose: Output contract — 3 pre-generated prompt strings keyed by strategy name
- Shape: `{"direct": str, "roleplay": str, "detailed": str}`
- Produced by: `PromptGenerator.generate_all()`
- Purpose: Static data backbone — no I/O, no init, loaded at module import time
- Pattern: Plain Python dicts with consistent nested structures (key -> {name, icon, keywords, templates})
- Industries nested structure: `INDUSTRIES[key] = {name, icon, keywords[], templates{task_name: {task_keywords[], description}}}`

## Entry Points

- Location: `d:\文件\提示词工具\run.py`
- Triggers: User double-clicks `智能提示词工坊.exe` (built via `build.bat`)
- Responsibilities: Inserts project root into sys.path, imports `PromptToolApp`, wraps in try/except with tkinter error dialog
- Location: `d:\文件\提示词工具\prompt_tool/main.py`
- Triggers: `python -m prompt_tool.main` or `python prompt_tool/main.py`
- Responsibilities: Inserts parent dir into sys.path, tries relative import then absolute import fallback, runs app
- Location: `d:\文件\提示词工具\prompt_tool/app.py` (line 441: `run()`)
- Triggers: Called by either entry point above
- Responsibilities: Calls `self.root.mainloop()` to start the Tkinter event loop

## Architectural Constraints

- **Threading:** Single-threaded Tkinter event loop. Analysis and generation offloaded to `threading.Thread` with `daemon=True` to keep UI responsive. All UI mutations dispatched via `self.root.after(0, ...)`. No thread synchronization primitives (lock, queue) — relies on atomic dict assignment.
- **Global state:** One module-level singleton `default_engine = AnalysisEngine()` in `prompt_tool/engine.py:328`. Not used by the app (which creates its own `self.engine = AnalysisEngine()`), but accessible to any importer.
- **Circular imports:** None detected. Dependency graph is strictly acyclic: `app.py -> engine.py -> knowledge.py` and `app.py -> generator.py -> knowledge.py`.
- **Offline constraint:** Zero network dependencies. No HTTP calls, no API keys, no external services. The entire program runs with only the Python standard library + customtkinter + pillow.

## Anti-Patterns

### Global engine instance not used

### UI logic mixed with business logic

### Daemon thread without error queue

### Knowledge base as a single huge file

## Error Handling

- `run.py:19-28` — Wraps entire app launch in try/except, shows error dialog with traceback excerpt
- `main.py:24-33` — Catches `ImportError` with fallback to absolute import, prints error to console
- `app.py:259-270` — `_do_generate()` catches all exceptions, dispatches to `_on_error()` which re-enables UI and shows messagebox
- `app.py:376-378` — Export file write failure caught silently (falls back to clipboard-only)

## Cross-Cutting Concerns

<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
