# Codebase Concerns

**Analysis Date:** 2026-06-03

## Tech Debt

### Thread Safety Gap in UI State Mutation

- Issue: The background thread `_do_generate` in `prompt_tool/app.py` mutates instance attributes `self.analysis_result` and `self.generated_prompts` (line 266-267) without any lock or synchronization. Although `self.root.after(0, ...)` is correctly used to update the UI, the shared state is written from the worker thread. If the user clicks "Generate" rapidly while a previous generation is still running, a second thread can overwrite `self.analysis_result` before the first thread's `_on_done` callback reads it, leading to stale/corrupt data displayed.
- Files: `prompt_tool/app.py` (lines 259-270)
- Impact: Race condition causes mismatched analysis data and generated prompts, or duplicate concurrent generations wasting CPU.
- Fix approach: Add a `self._generating` flag (set True before thread start, checked in `_do_generate`), or use `threading.Lock` to protect shared state writes, or disable the generate button more permanently until the callback fires.

### Arbitrary Sleep for UI Update

- Issue: `time.sleep(0.15)` on line 264 of `prompt_tool/app.py` is a magic-number delay inserted before the heavy analysis call. Its purpose appears to let the UI thread process the button state change ("Generating...") before the worker thread monopolizes the GIL. This is fragile — the delay may be too short on slow hardware or unnecessarily long on fast hardware.
- Files: `prompt_tool/app.py` (line 264)
- Impact: Unreliable UI feedback during generation start. On very slow machines the button may not visually update before analysis begins.
- Fix approach: Call `self.root.update_idletasks()` after disabling the button to force UI refresh synchronously, rather than sleeping.

### Module-Level Global Engine Instance (Unused)

- Issue: `prompt_tool/engine.py` line 328 creates a module-level `default_engine = AnalysisEngine()` that is never imported or used anywhere in the codebase. It wastes memory (the engine instance contains dicts that accumulate state across calls) and suggests incomplete refactoring.
- Files: `prompt_tool/engine.py` (line 328)
- Impact: Minor memory overhead. State leakage risk if someone later imports `default_engine` inadvertently, since the engine carries instance-level score caches.
- Fix approach: Remove the unused global instance. `PromptToolApp` creates its own engine instance at `app.py` line 34.

### Desktop Path Hardcoded for English Windows

- Issue: Export function at `prompt_tool/app.py` line 368 uses `os.path.join(os.path.expanduser("~"), "Desktop")` to find the desktop directory. On Chinese Windows, "Desktop" is localized to "桌面", so this path will not exist. The fallback (line 370) uses the home directory, so it doesn't crash, but the user experience is degraded — files save to home instead of desktop without clear indication.
- Files: `prompt_tool/app.py` (lines 367-373)
- Impact: Export-to-desktop fails silently on non-English Windows (the `os.path.exists` check catches it, but the fallback folder is not communicated to the user).
- Fix approach: Use `%USERPROFILE%/Desktop` and `%USERPROFILE%/桌面` (both checked), or use a proper desktop path API like `ctypes.windll.shell32.SHGetKnownFolderPath`.

### Scoring Algorithm False Positives

- Issue: The industry identification algorithm in `prompt_tool/engine.py` (lines 135-176) uses keyword overlap scoring. Many keywords like "数据", "分析", "用户" appear in multiple industries (互联网_IT, 零售电商, 金融, etc.), leading to ambiguous or incorrect classification. The scoring weights (3 for exact match, 2 for case-insensitive, 1 for bigram partial match) are arbitrary and were never tuned against a test dataset.
- Files: `prompt_tool/engine.py` (lines 135-176)
- Impact: Users frequently see wrong industry auto-detection, requiring manual industry dropdown override. This undermines the "auto" value proposition.
- Fix approach: Introduce negative scoring for cross-industry keyword conflicts, or use a TF-IDF-like weighting that down-weights common keywords. Add a confidence threshold below which auto-detection returns "不确定" and prompts the user.

### No Issue Tracker References in Code

- Issue: Zero `TODO`, `FIXME`, `HACK`, or `XXX` comments exist in the entire codebase. This is not inherently bad, but it means all known issues exist only as tribal knowledge — there is no inline documentation of known limitations, shortcuts, or future work.
- Files: All source files
- Impact: New developers (or Claude instances) have no awareness of intentional shortcuts versus bugs. Every code quality decision is invisible.
- Fix approach: Add TODO comments for known tech debt items with brief context. No code change required — just documentation markup.

## Known Bugs

### Clipboard Overwrite on Copy Without Lock

- Issue: `_on_copy` at `app.py` lines 324-338 calls `self.root.clipboard_clear()` then `self.root.clipboard_append(prompt)` in sequence. If a user copies something else between these two calls (e.g., from another window), the prompt text that was cleared is lost and the user gets whatever they copied externally — but the UI reports success.
- Symptoms: Intermittent "copy didn't work" — user sees the old clipboard content after clicking copy. Reproducible by alt-tabbing away between the clear and append calls.
- Files: `prompt_tool/app.py` (lines 331-332)
- Trigger: Slow machine or user alt-tabs rapidly after clicking copy.
- Workaround: Click copy again.

### Display Textbox State Flicker

- Issue: The `display` CTkTextbox is toggled between `state="normal"` and `state="disabled"` every time content is updated (`app.py` lines 301-304, 416-429). In customtkinter, this toggle can cause focus loss, cursor position reset, and in some versions, visual flickering of the scrollbar.
- Symptoms: Display area scroll position resets to top on strategy switch or regeneration. Occasional visual flicker.
- Files: `prompt_tool/app.py` (lines 301-304)
- Trigger: Every call to `_show_prompt()` or `_set_placeholder()`.
- Workaround: None, but cosmetic only.

### Stop Words Only Applied to N-grams, Not Characters

- Issue: In `prompt_tool/engine.py`, stop word filtering is only applied to bigrams (line 121: `filtered_bigrams = [w for w in bigrams if w not in STOP_WORDS]`) and trigrams (line 122), but NOT to single-character keywords (`words` list, line 108-110). Common single-character stop words like "的", "了", "在", "是", "我" are kept in the keyword list and contribute to scoring, diluting signal.
- Symptoms: Industry/task matching may be weakened because stop-word characters dilute real signal keywords. A sentence starting with many stop words may bias scoring.
- Files: `prompt_tool/engine.py` (lines 107-122)
- Trigger: Any input containing common Chinese stop words.

## Security Considerations

### No Input Validation for Textbox Content Length

- Risk: The input textbox accepts arbitrary-length content. A user pasting a very large document (e.g., 100,000+ characters) will cause the regex operations and keyword extraction in `engine.py` to consume excessive CPU, potentially freezing the UI on the generation thread.
- Files: `prompt_tool/app.py` (line 248), `prompt_tool/engine.py` (lines 89-132)
- Current mitigation: The `original_input[:200]` truncation in `generator.py` helps output, but the analysis engine processes the full input.
- Recommendations: Add a character limit (e.g., 2000 chars) with a visible counter in the UI, and truncate input at the analysis boundary.

### Built Executable Has No Code Signing

- Risk: The PyInstaller-built EXE (`dist/智能提示词工坊.exe`) is not code-signed. Windows SmartScreen will flag it as an unknown publisher, browsers will warn before download, and antivirus software may quarantine it heuristically.
- Files: `dist/智能提示词工坊.exe` (build artifact), `build.bat` (build script)
- Current mitigation: None.
- Recommendations: Add a `codesign` step to `build.bat` after PyInstaller completes, referencing a purchased code signing certificate.

### Clipboard Data Remains in System Clipboard

- Risk: Generated prompts (which may contain proprietary business logic or sensitive requirements) are copied to the system clipboard shared by all applications. No clipboard clearing after timeout or application exit.
- Files: `prompt_tool/app.py` (lines 331-332, 364-365)
- Current mitigation: None.
- Recommendations: Offer a "clear clipboard on exit" option in the UI, or set clipboard TTL using platform-specific APIs.

## Performance Bottlenecks

### Full Input Regex Processing on Main Worker Thread

- Problem: The `analyze()` method in `engine.py` runs multiple regex passes over the entire user input (goal extraction, constraint patterns, format identification). For inputs over a few hundred characters, this is measurable but not severe. For large pasted inputs, this becomes the bottleneck.
- Files: `prompt_tool/engine.py` (lines 250-283, 285-298, 301-308)
- Cause: Multiple independent regex scans over the full text for different extraction goals. Each regex pattern runs `re.findall` separately.
- Improvement path: Compile regex patterns at module load time (currently not compiled — implicit re cache used). Process the text once with a combined pattern, or iterate character-by-character for the simple keyword matching cases.

### No Caching of Analysis Results

- Problem: Every "Generate" click re-runs the full analysis pipeline even for the same input text (e.g., if a user is switching between industries manually and regenerating). The engine has no input-content hashing or memoization.
- Files: `prompt_tool/app.py` (lines 259-267)
- Cause: Simple architecture — no caching layer.
- Improvement path: Add a dict-based memoization keyed by `(cleaned_input, manual_industry)` with a max size of ~10 entries.

## Fragile Areas

### Strategy Button Color Mapping Duplicated

- Files: `prompt_tool/app.py` (lines 309-316)
- Why fragile: The color mapping from strategy key to hex color is defined in `_build_strategies_area` (lines 174-177 as a tuple) and duplicated in `_show_prompt` (lines 309-312 as a dict literal). If a new strategy is added or a color changed, both locations must be updated in sync. No test validates this.
- Safe modification: Always update both locations when changing strategy colors. Better: extract to a class-level constant dict `STRATEGY_COLORS`.
- Test coverage: None.

### Multi-threaded Tkinter Access Pattern

- Files: `prompt_tool/app.py` (lines 256-270)
- Why fragile: Tkinter is not thread-safe. The code correctly uses `self.root.after(0, ...)` to marshal UI updates back to the main thread, but any future modification that touches tkinter objects directly in `_do_generate` will cause intermittent crashes or corruption. The pattern is easy to accidentally break.
- Safe modification: Always use `self.root.after(0, callback)` for any tkinter/ctkinter object access. Never mutate `self.display`, `self.status`, `self.info_bar`, or any `ctk.CTk*` widget from the worker thread.
- Test coverage: None.

### Prompt Generator Spec Requirement Tuples

- Files: `prompt_tool/generator.py` (lines 237-266)
- Why fragile: The `_spec_req` method uses a flat list of `((industry_key, task_substring), requirement_string)` tuples. The matching logic checks `t in self.task_name or t in inp`. This is order-dependent (first match wins) and `in` substring matching can catch unintended matches. Adding new industries or tasks requires extending this list.
- Safe modification: Extend with new tuples following the same pattern. Do not reorder existing entries unless the precedence change is intentional.
- Test coverage: None.

## Scaling Limits

### Industry Knowledge Dictionary Size

- Current capacity: 15 industries, ~90 task types, ~850 lines in `knowledge.py`. The data is fully loaded into memory on import.
- Limit: At approximately 50+ industries and 300+ task types, the module import time and memory usage will become noticeable (~5+ seconds import, 50+ MB RAM). The current approach of a single Python dict with all data in one file does not scale to hundreds of industries.
- Scaling path: Split knowledge base into per-industry files (`knowledge/互联网_IT.py`, `knowledge/教育.py`, etc.) with lazy loading, or use a SQLite database for the knowledge base. The `get_all_industry_names()` function would need to be async or list-based.

### Single-File Knowledge Base

- Current capacity: All 15 industries' keywords, templates, roles, strategies, stop words, tone keywords, and output formats in one file (`knowledge.py`, 855 lines).
- Limit: Beyond ~20 industries or ~5000 lines, the file becomes difficult to navigate and edit, with merge conflicts becoming inevitable in team development.
- Scaling path: Split into `knowledge/industries.py`, `knowledge/strategies.py`, `knowledge/roles.py`, etc., or migrate to structured data files (JSON/YAML) loaded at startup.

## Dependencies at Risk

### customtkinter (>=5.2.2)

- Risk: customtkinter does not guarantee API stability across minor versions. The `CTkTextbox` state-toggle pattern used in `app.py` (lines 301-304) has been known to exhibit different behavior between v5.2.x releases. A future upgrade could break the display widget or change color handling.
- Impact: UI rendering issues, broken textbox interaction, or color scheme changes.
- Migration plan: Pin to exact version `customtkinter==5.2.2` in `requirements.txt` and test upgrades explicitly. Add a `--version` test that checks the installed version matches the tested version.

### pillow (>=10.0.0)

- Risk: Used by customtkinter for image handling. No direct usage in application code. Breaking changes in Pillow 11+ could affect customtkinter's internal image cache and cause icon/rendering issues.
- Impact: Primarily cosmetic (icons, images) or application crash at startup if PIL load fails.
- Migration plan: Same version pinning strategy.

### No Dependency Lock File

- Risk: `requirements.txt` uses unbounded `>=` version specifiers. Two builds performed weeks apart may install different dependency versions, introducing behavioral differences that are hard to diagnose.
- Files: `requirements.txt`
- Impact: Non-reproducible builds. "Works on my machine" bugs.
- Fix approach: Generate `requirements.lock` or use `pip freeze > requirements-locked.txt` after testing, and add a pre-build check comparing installed versions against the lock file.

## Missing Critical Features

### No Error Boundary for Generation Failures

- Problem: If `generate_prompts()` or `engine.analyze()` crashes with an exception not caught by the generic `except Exception` (e.g., `SystemExit`, `KeyboardInterrupt`), the UI remains in a broken "Generating..." state with the button disabled.
- Files: `prompt_tool/app.py` (lines 259-270)
- Blocks: Graceful recovery from crashes during generation.
- Priority: Medium

### No Undo for Clear Action

- Problem: Clicking "清空" (Clear) immediately destroys all analysis results and regenerated prompts with no confirmation dialog and no undo.
- Files: `prompt_tool/app.py` (lines 398-410)
- Blocks: User recovery from accidental clear. If the user spent time crafting input and got good results, then accidentally clicks clear (or the button label is misinterpreted), all work is lost.
- Priority: Low

## Test Coverage Gaps

### Zero Test Coverage

- What's not tested: The entire codebase. Zero test files exist. No test runner configured. No test dependencies in `requirements.txt`.
- Files: All `prompt_tool/*.py` files
- Risk: A single line change to any core logic (industry detection algorithm, prompt generation template, UI state machine) has zero safety net. Regression bugs introduced during refactoring will surface only to end users.
- Critical untested areas:
  - `AnalysisEngine.analyze()` — industry detection, task detection, keyword extraction all have branching logic with no characterization tests
  - `PromptGenerator.generate_all()` — template rendering correctness for all 3 strategies across all 15 industries (45 output variants)
  - `_on_generate` / `_on_clear` / `_on_copy` — UI state transitions and button enable/disable logic
  - Clipboard operations — especially the clear/append race window
  - Export file path resolution — desktop path logic on non-English Windows
- Priority: High

### No Integration Smoke Tests

- What's not tested: Launch, input entry, generation trigger, copying flow. No end-to-end validation that the GUI starts, accepts input, and produces output.
- Files: `run.py` (entry point)
- Risk: A broken import, missing dependency, or Python version incompatibility is only caught when a user tries to launch the application.
- Priority: Medium

---

*Concerns audit: 2026-06-03*
