<!-- refreshed: 2026-06-03 -->
# Architecture

**Analysis Date:** 2026-06-03

## System Overview

```text
┌──────────────────────────────────────────────────────────────┐
│                  Presentation Layer (GUI)                    │
│                    `prompt_tool/app.py`                       │
│     PromptToolApp class (customtkinter-based Tkinter GUI)    │
└──────────┬───────────────────────────────────┬───────────────┘
           │  AnalysisEngine().analyze()        │ generate_prompts()
           ▼                                    ▼
┌────────────────────┐          ┌────────────────────────────┐
│  Analysis Layer    │          │  Generation Layer          │
│  `engine.py`       │          │  `generator.py`            │
│  AnalysisEngine    │          │  PromptGenerator           │
│  - Keyword match   │          │  - 3 strategy templates    │
│  - Pattern recog   │          │  - Industry-aware roles    │
└────────┬───────────┘          └────────┬───────────────────┘
         │   Reads from                   │   Reads from
         ▼                                ▼
┌──────────────────────────────────────────────────────────────┐
│                    Knowledge / Data Layer                    │
│                    `prompt_tool/knowledge.py`                │
│  INDUSTRIES (15 industries), TASK_TYPES (12 types),         │
│  ROLES (4 perspectives), STRATEGIES (3 templates),          │
│  OUTPUT_FORMATS, TONE_KEYWORDS, STOP_WORDS                  │
└──────────────────────────────────────────────────────────────┘
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

**Overall:** Modular single-window desktop application with a data-down/action-up layered architecture.

**Key Characteristics:**
- Completely offline — no network calls, no external API dependencies
- Single-threaded UI with background thread for generation work
- Data flows unidirectionally: User Input -> Analysis -> Generation -> Display
- Knowledge base acts as a pure data source (no side effects, no mutations)
- Each module imports from `knowledge.py` but not from each other (except `app.py` which orchestrates)

## Layers

**Presentation Layer (app.py):**
- Purpose: All user interaction — input capture, result display, copy/export actions
- Location: `prompt_tool/app.py`
- Contains: `PromptToolApp` class with `_setup_ui()`, `_build_*()` methods, event handlers
- Depends on: `engine.py` (AnalysisEngine), `generator.py` (generate_prompts), `knowledge.py` (STRATEGIES, get_all_industry_names)
- Used by: `main.py`, `run.py`

**Analysis Layer (engine.py):**
- Purpose: Parse user input to extract industry, task type, requirements, tone, output format using keyword scoring
- Location: `prompt_tool/engine.py`
- Contains: `AnalysisEngine` class with `analyze()` as the main method
- Depends on: `knowledge.py` (INDUSTRIES, TASK_TYPES, ROLES, STOP_WORDS, OUTPUT_FORMATS, TONE_KEYWORDS)
- Used by: `app.py`

**Generation Layer (generator.py):**
- Purpose: Produce 3 ready-to-use prompt strings from analysis result dict
- Location: `prompt_tool/generator.py`
- Contains: `PromptGenerator` class with `generate_all()` returning dict of 3 prompts
- Depends on: `knowledge.py` (INDUSTRIES)
- Used by: `app.py`

**Knowledge Layer (knowledge.py):**
- Purpose: Static data dictionaries — no logic, no classes, just module-level constants and helper functions
- Location: `prompt_tool/knowledge.py`
- Contains: INDUSTRIES, TASK_TYPES, ROLES, STRATEGIES, OUTPUT_FORMATS, STOP_WORDS, TONE_KEYWORDS, and 3 helper functions
- Depends on: Nothing (standard library only)
- Used by: `engine.py`, `generator.py`, `app.py`

## Data Flow

### Primary Request Path (Generate Prompts)

1. User types input in `self.input_text` Textbox and clicks "Generate" button (`prompt_tool/app.py:247`)
2. `_on_generate()` validates input, disables button, spawns background thread (`prompt_tool/app.py:256`)
3. `_do_generate(content)` runs on background thread (`prompt_tool/app.py:259`):
   - Calls `self.engine.analyze(content, manual_industry)` (`prompt_tool/engine.py:21`)
   - Calls `generate_prompts(analysis_result)` (`prompt_tool/generator.py:272`)
4. Results dispatched back to main thread via `self.root.after(0, self._on_done)` (`prompt_tool/app.py:268`)
5. `_on_done()` updates info bar, displays prompt, re-enables controls (`prompt_tool/app.py:272`)

### Analysis Data Flow (engine.py)

1. `_clean_text()` — strip whitespace, filter allowed chars (`prompt_tool/engine.py:89`)
2. `_extract_keywords()` — chars, bigrams, trigrams, english words (`prompt_tool/engine.py:103`)
3. `_identify_industry()` — score each of 15 industries against keywords (`prompt_tool/engine.py:135`)
4. `_identify_task()` — score tasks within matched industry + fallback (`prompt_tool/engine.py:178`)
5. `_extract_requirements()` — regex patterns on goal/constraint phrases (`prompt_tool/engine.py:250`)
6. `_identify_tone()` — match TONE_KEYWORDS (`prompt_tool/engine.py:285`)
7. `_identify_output_format()` — match OUTPUT_FORMATS keywords (`prompt_tool/engine.py:301`)

### Strategy Switching

1. User clicks strategy tab button (direct/roleplay/detailed) (`prompt_tool/app.py:289`)
2. `_switch_strategy(key)` updates `self.current_strategy` and calls `_show_prompt()` (`prompt_tool/app.py:289-291`)
3. `_show_prompt()` reads `self.generated_prompts[key]` and inserts into display textbox, updates title and button colors (`prompt_tool/app.py:293`)

**State Management:**
- Instance state held on `PromptToolApp`: `analysis_result`, `generated_prompts`, `current_strategy`, `_ph_active`
- No persistence between sessions (no database, no config files)
- No global mutable state beyond the module-level `default_engine` in `engine.py:328`

## Key Abstractions

**AnalysisResult dict:**
- Purpose: The single structured data contract between analysis and generation layers
- Fields: industry_key, industry_name, task_name, task_key, task_description, requirements (list), tone (str), output_format (dict), all_industries, all_tasks, original_input, cleaned_input, keywords
- Consumed by: `PromptGenerator.__init__()` and UI display

**PromptStrategy dict (generated_prompts):**
- Purpose: Output contract — 3 pre-generated prompt strings keyed by strategy name
- Shape: `{"direct": str, "roleplay": str, "detailed": str}`
- Produced by: `PromptGenerator.generate_all()`

**Knowledge Base dictionaries:**
- Purpose: Static data backbone — no I/O, no init, loaded at module import time
- Pattern: Plain Python dicts with consistent nested structures (key -> {name, icon, keywords, templates})
- Industries nested structure: `INDUSTRIES[key] = {name, icon, keywords[], templates{task_name: {task_keywords[], description}}}`

## Entry Points

**PyInstaller Packaged Entry Point:**
- Location: `d:\文件\提示词工具\run.py`
- Triggers: User double-clicks `智能提示词工坊.exe` (built via `build.bat`)
- Responsibilities: Inserts project root into sys.path, imports `PromptToolApp`, wraps in try/except with tkinter error dialog

**Python Module Entry Point:**
- Location: `d:\文件\提示词工具\prompt_tool/main.py`
- Triggers: `python -m prompt_tool.main` or `python prompt_tool/main.py`
- Responsibilities: Inserts parent dir into sys.path, tries relative import then absolute import fallback, runs app

**Application Entry Point:**
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

**What happens:** `prompt_tool/engine.py:328` creates `default_engine = AnalysisEngine()` at module level, but `PromptToolApp.__init__()` (`prompt_tool/app.py:34`) creates `self.engine = AnalysisEngine()` instead.
**Why it's wrong:** The module-level singleton is dead code — it exists but is never referenced anywhere.
**Do this instead:** Remove the `default_engine` global, or use it in `app.py` to avoid redundant instantiation.

### UI logic mixed with business logic

**What happens:** Some business-ish decisions live in UI methods — for example, `_on_export()` in `prompt_tool/app.py:340` constructs the export text directly and handles file I/O itself.
**Why it's wrong:** Makes the presentation layer harder to test and the export format harder to reuse.
**Do this instead:** Move export text formatting to `generator.py` as a method like `format_export(analysis_result, generated_prompts) -> str`.

### Daemon thread without error queue

**What happens:** The generation thread (`prompt_tool/app.py:256-257`) is a `daemon=True` thread that catches exceptions and dispatches to `_on_error()` via `after(0)`, but there is no thread-safe queue or future abstraction.
**Why it's wrong:** If `_do_generate` encounters an exception before the `after(0)` call, the exception is lost (daemon thread). Only the broad `except Exception` in `_do_generate` is the safety net.
**Do this instead:** Use `concurrent.futures.ThreadPoolExecutor` with a Future, or at minimum a `queue.Queue` for results.

### Knowledge base as a single huge file

**What happens:** `knowledge.py` is 856 lines containing all 15 industry definitions, task types, roles, strategies, output formats, stop words, and tone keywords — all in one file.
**Why it's wrong:** Single-file bloat makes navigation and maintenance harder. An edit to one industry's keywords requires scrolling through the entire file.
**Do this instead:** Split into `knowledge/industries.py`, `knowledge/strategies.py`, `knowledge/formats.py`, etc., or at minimum use a data directory with JSON/YAML files loaded at startup.

## Error Handling

**Strategy:** Catch-all try/except blocks at entry points and generation with tkinter `messagebox.showerror()` for user-facing error display.

**Patterns:**
- `run.py:19-28` — Wraps entire app launch in try/except, shows error dialog with traceback excerpt
- `main.py:24-33` — Catches `ImportError` with fallback to absolute import, prints error to console
- `app.py:259-270` — `_do_generate()` catches all exceptions, dispatches to `_on_error()` which re-enables UI and shows messagebox
- `app.py:376-378` — Export file write failure caught silently (falls back to clipboard-only)

## Cross-Cutting Concerns

**Logging:** Not used. No `logging` module imports anywhere. Status updates go to the UI status bar only.
**Validation:** Minimal. Input validation is presence-only (`if not content`). No schema validation on the analysis_result dict contract.
**Authentication:** Not applicable (offline desktop tool).

---

*Architecture analysis: 2026-06-03*
