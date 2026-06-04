# Phase 6: UI - Pattern Map

**Mapped:** 2026-06-04
**Files analyzed:** 4 new/modified files
**Analogs found:** 4 / 4

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `prompt_tool/app.py` | component | event-driven + request-response | `prompt_tool/app.py` (existing self) | exact (refactor) |
| `prompt_tool/app_controller.py` | controller | event-driven | `prompt_tool/conversation_engine.py` | role-match |
| `prompt_tool/conversation_engine.py` | service | event-driven | `prompt_tool/conversation_engine.py` (existing self) | exact (integration) |
| `tests/test_ui.py` | test | request-response | `tests/test_conversation_engine.py` | exact |

## Pattern Assignments

### `prompt_tool/app.py` (component, event-driven + request-response)

**Analog:** `prompt_tool/app.py` (existing PromptToolApp class, 507 lines)

**Role:** Refactor target — add v4 frames (chat_frame, result_frame), page switching, chat bubbles, result cards, optimization panel while preserving v3 code.

**Imports pattern** (lines 6-21):
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
from .knowledge_manager import knowledge_manager
from .session_manager import session_manager
from .conversation_engine import ConversationEngine, ConversationState
```

**Class structure & color palette** (lines 26-50):
```python
class PromptToolApp:

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("...")
        self.root.geometry("1050x740")
        self.root.minsize(850, 580)

        self.colors = {
            "primary": "#2B579A", "secondary": "#4A90D9",
            "accent": "#E67E22", "success": "#27AE60",
            "text": "#2C3E50", "text_light": "#7F8C8D",
            "card": "#FFFFFF", "body": "#F0F2F5", "border": "#DEE2E6",
        }

        self._setup_ui()
        self._center_window()
```

**Grid-based layout setup** (lines 70-82):
```python
def _setup_ui(self):
    self.root.grid_columnconfigure(0, weight=1)
    self.root.grid_rowconfigure(0, weight=0)  # header
    self.root.grid_rowconfigure(1, weight=0)  # input
    self.root.grid_rowconfigure(2, weight=0)  # info bar
    self.root.grid_rowconfigure(3, weight=1)  # strategies
    self.root.grid_rowconfigure(4, weight=0)  # status bar

    self._build_header()
    self._build_input_area()
    self._build_info_bar()
    self._build_strategies_area()
    self._build_status_bar()
```

**Header construction pattern** (lines 84-100):
```python
def _build_header(self):
    h = ctk.CTkFrame(self.root, height=60, corner_radius=0,
                     fg_color=self.colors["primary"])
    h.grid(row=0, column=0, sticky="nsew")
    h.grid_propagate(False)
    h.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(h, text="🧠  智能提示词工坊",
                 font=ctk.CTkFont(size=22, weight="bold"),
                 text_color="white").grid(row=0, column=0, padx=25, pady=(6, 0), sticky="w")
```

**Daemon thread + root.after() async pattern** (lines 271-282, 284-313):
```python
def _on_generate(self):
    content = self.input_text.get("1.0", "end-1c").strip()
    if not content or self._ph_active:
        messagebox.showwarning("提示", "请先输入你的需求描述")
        return

    self.gen_btn.configure(state="disabled", text="⏳ 生成中...")
    self.set_status("🔍 正在分析需求并生成提示词...")

    thread = threading.Thread(target=self._do_generate_v4, args=(content,), daemon=True)
    thread.start()

def _do_generate_v4(self, content):
    try:
        engine = ConversationEngine()
        result = engine.start(content)
        # ... backend work ...
        self.root.after(0, self._on_done)
    except Exception as e:
        self.root.after(0, lambda: self._on_error(str(e)))
```

**Error handling - UI error dispatch** (lines 332-335):
```python
def _on_error(self, msg):
    self.gen_btn.configure(state="normal", text="🎯  生成提示词")
    self.set_status(f"❌ 出错：{msg}")
    messagebox.showerror("错误", f"生成出错：\n{msg}")
```

**Status bar setter** (lines 497-498):
```python
def set_status(self, msg):
    self.status.configure(text=msg)
```

**CTkTextbox display pattern (read-only, insert/disable)** (lines 248-254, 357-368):
```python
# Setup:
self.display = ctk.CTkTextbox(
    df, font=ctk.CTkFont(size=13, family="Microsoft YaHei"),
    wrap="word", fg_color="white", text_color=self.colors["text"],
    border_width=0, corner_radius=4,
)
self.display.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")

# Write content:
self.display.configure(state="normal")
self.display.delete("1.0", "end")
self.display.insert("1.0", prompt)
self.display.configure(state="disabled")
```

**Clipboard copy pattern** (lines 388-402):
```python
def _on_copy(self):
    if not self.generated_prompts:
        return
    prompt = self.generated_prompts.get(self.current_strategy, "")
    if not prompt:
        return

    self.root.clipboard_clear()
    self.root.clipboard_append(prompt)

    sn = STRATEGIES[self.current_strategy]["name"]
    self.set_status(f"✅ 已复制：{sn}")
    self.copy_btn.configure(text="✅ 已复制", fg_color=self.colors["secondary"])
    self.root.after(2000, lambda: self.copy_btn.configure(
        text="📋 复制此提示词", fg_color=self.colors["success"]))
```

---

### `prompt_tool/app_controller.py` (controller, event-driven)

**Analog:** `prompt_tool/conversation_engine.py` (state-machine orchestration, 252 lines)

**Role:** New file. Mediates between UI events and backend (ConversationEngine). Handles threading, state synchronization, and event routing.

**Class structure pattern** (from conversation_engine lines 42-49):
```python
class ConversationEngine:
    def __init__(self):
        self.state = ConversationState.IDLE
        self._classifier = IntentClassifier()
        self._follow_up: FollowUpEngine | None = None
        self._last_analysis: dict = {}
```

**State management pattern** (from conversation_engine lines 51-56):
```python
def _transition(self, to_state: ConversationState):
    if to_state not in VALID_TRANSITIONS.get(self.state, set()):
        raise ConversationError(
            f"非法状态转换: {self.state.value} -> {to_state.value}"
        )
    self.state = to_state
```

**Architecture reference for AppController** (from .planning/research/ARCHITECTURE.md lines 536-558):
```python
class AppController:
    """
    Mediates between UI and backend components.
    Runs blocking operations in background threads.
    Manages session lifecycle.
    """
    def __init__(self, engine: ConversationEngine):
        self._engine = engine
        self._session_id: str | None = None

    def start_new_session(self):
        self._session_id = self._engine.start_session()

    def process_input(self, text: str) -> None:
        """Called by UI when user submits input. Runs in thread."""
        response = self._engine.handle_input(self._session_id, text)
        self._apply_response(response)

    def process_answer(self, question_id: str, answer: Any) -> None:
        """Called by UI when user answers a question. Runs in thread."""
        response = self._engine.handle_answer(self._session_id, question_id, answer)
        self._apply_response(response)
```

**Module-level singleton pattern** (from knowledge_manager.py lines 207-208):
```python
# Module-level singleton
knowledge_manager = KnowledgeManager()
```

---

### `prompt_tool/conversation_engine.py` (service, event-driven)

**Analog:** `prompt_tool/conversation_engine.py` (existing self, 252 lines)

**Role:** Integration point — no structural changes needed. The existing API is consumed by the new UI:

- `engine.start(user_input: str) -> dict` — returns action dict with question data
- `engine.handle_answer(answer: str) -> dict` — process user answer, returns next action
- `engine.handle_confirmation(confirmed: bool, ...) -> dict` — confirm/correct industry
- `engine.skip_follow_up() -> dict` — escape door, generate immediately
- `engine.generate_complete() -> dict` — final generation, returns prompts dict

**Return dict format** (lines 82-91, 144-149, 193-212):
```python
# start() return format:
{
    "state": state.value,
    "needs_clarification": False,
    "industry_id": ...,
    "industry_name": ...,
    "task_key": ...,
}

# handle_answer() return when more questions:
{
    "state": state.value,
    "action": "follow_up",
    "question": {"question_text": "...", "question_type": "...", "options": [...]},
    "question_number": 1,
    "max_questions": 3,
}

# generate_complete() return:
{
    "state": "complete",
    "action": "display_results",
    "prompts": {
        "direct": "...",
        "roleplay": "...",
        "detailed": "...",
    }
}
```

---

### `tests/test_ui.py` (test, request-response)

**Analog:** `tests/test_conversation_engine.py` (class-based pytest, 80 lines)

**Role:** New test file for UI controller logic. Tests AppController state transitions, page switching, input handling, escape door.

**Test class structure** (from test_conversation_engine.py lines 10-59):
```python
class TestConversationState:
    """状态枚举定义测试"""
    def test_all_states_defined(self):
        assert len(ConversationState) == 9
        for s in ("idle", "analyzing", ...):
            assert ConversationState(s) is not None

class TestStateMachine:
    """状态机转换规则测试"""
    def test_starts_from_idle(self):
        engine = ConversationEngine()
        assert engine.state == ConversationState.IDLE

    def test_start_transitions_to_confirming(self):
        engine = ConversationEngine()
        result = engine.start("帮我写一个电商PRD")
        assert engine.state in (ConversationState.CONFIRMING, ConversationState.CLARIFYING)

    def test_invalid_transition_raises_error(self):
        engine = ConversationEngine()
        with pytest.raises(ConversationError):
            engine.handle_answer("test")

    def test_reset_goes_to_idle(self):
        engine = ConversationEngine()
        engine.start("test")
        engine.reset()
        assert engine.state == ConversationState.IDLE

    def test_skip_follow_up_generates(self):
        engine = ConversationEngine()
        engine.start("帮我写一个PRD文档")
        if engine.state == ConversationState.CONFIRMING:
            engine.handle_confirmation(True)
        result = engine.skip_follow_up()
        assert engine.state == ConversationState.GENERATING
```

**Test imports pattern** (lines 4-7):
```python
import pytest
from prompt_tool.conversation_engine import (
    ConversationEngine, ConversationState, ConversationError,
)
```

**Lifecycle end-to-end test pattern** (from test_session_manager.py lines 131-167):
```python
def test_full_lifecycle(self):
    """端到端生命周期：创建→3轮→确认→提取→快照→新建→验证隔离"""
    sm = SessionManager()

    # 创建
    sid = sm.create_session()
    assert sm.has_active_session()

    # 3 轮对话
    sm.add_turn("system", "...", "question")
    sm.add_turn("user", "...", "answer")
    sm.add_turn("system", "...", "confirm")

    # 确认行业 & 任务
    sm.update_confirmed_industry("internet_it")
    sm.update_confirmed_task("code_generation")

    # 新建会话
    new_sid = sm.new_session()
    assert new_sid != sid
    assert sm.get_turn_count() == 0
```

---

## Shared Patterns

### Thread Safety: Daemon Thread + UI Dispatching

**Source:** `prompt_tool/app.py` lines 271-313
**Apply to:** All generation/analysis triggers in the new UI

```python
# In UI event handler:
thread = threading.Thread(target=self._do_backend_work, args=(...), daemon=True)
thread.start()

# In background thread:
def _do_backend_work(self, ...):
    try:
        result = backend.do_work(...)
        self.root.after(0, lambda: self._on_result(result))
    except Exception as e:
        self.root.after(0, lambda: self._on_error(str(e)))
```

**Key detail:** All UI mutations must go through `self.root.after(0, lambda: ...)`. Background thread rendering of CTk widgets will crash or corrupt UI state.

### Button Debounce / Disable-While-Working

**Source:** `prompt_tool/app.py` lines 276-277
**Apply to:** Send button, generate button, optimize button

```python
self.gen_btn.configure(state="disabled", text="⏳ 生成中...")
# ... on completion:
self.gen_btn.configure(state="normal", text="🎯  生成提示词")
```

### Frame Construction: grid with `sticky="nsew"` + Grid Configure

**Source:** `prompt_tool/app.py` lines 70-82 (entire _setup_ui)
**Apply to:** All v4 frames, chat area, result area, optimization panel

```python
# Parent must configure weights before children use them:
parent.grid_columnconfigure(0, weight=1)
parent.grid_rowconfigure(0, weight=0)  # fixed row
parent.grid_rowconfigure(1, weight=1)  # expanding row
parent.grid_rowconfigure(2, weight=0)  # fixed row

# Children use sticky="nsew" to fill:
child.grid(row=0, column=0, padx=12, pady=8, sticky="nsew")
```

**CRITICAL:** Do not mix `pack()` and `grid()` in the same parent. The existing app.py uses grid exclusively.

### Color Palette

**Source:** `prompt_tool/app.py` lines 45-50
**Apply to:** All new UI components

```python
self.colors = {
    "primary": "#2B579A", "secondary": "#4A90D9",
    "accent": "#E67E22", "success": "#27AE60",
    "text": "#2C3E50", "text_light": "#7F8C8D",
    "card": "#FFFFFF", "body": "#F0F2F5", "border": "#DEE2E6",
}
```

### Knowledge Manager Integration

**Source:** `prompt_tool/app.py` lines 39-40, 338-351
**Apply to:** Knowledge pack visibility display (UI-04), compliance check (QA-03)

```python
# Initialize at startup:
knowledge_manager.initialize()

# Check fallback:
if knowledge_manager.is_fallback_active():
    self.set_status("⚠️ 知识包加载失败，使用 v3.0 兼容模式")

# Get index for display:
index = knowledge_manager.get_index()
for kid, entry in index.items():
    msg += f"🏢 {entry.get('name', kid)}\n"
```

### STRATEGIES Constants

**Source:** `prompt_tool/knowledge.py` lines 762-777
**Apply to:** Result card titles, card metadata

```python
STRATEGIES = {
    "direct": {
        "name": "⚡ 高效直给式",
        "tag": "推荐",
        "color": "#4A90D9",
    },
    "roleplay": {
        "name": "🎭 角色委派式",
        "tag": "专业",
        "color": "#E67E22",
    },
    "detailed": {
        "name": "📋 完整详细式",
        "tag": "全面",
        "color": "#27AE60",
    },
}
```

---

## No Analog Found

All files have close analogs in the existing codebase. No new technology or patterns needed.

| File | Role | Data Flow | Analog Used |
|------|------|-----------|-------------|
| `prompt_tool/app.py` | component | event-driven | Existing PromptToolApp class |
| `prompt_tool/app_controller.py` | controller | event-driven | ConversationEngine + ARCHITECTURE.md |
| `prompt_tool/conversation_engine.py` | service | event-driven | Existing self (no changes) |
| `tests/test_ui.py` | test | request-response | test_conversation_engine.py |

## Metadata

**Analog search scope:** `prompt_tool/` (all .py files), `tests/` (all .py files), `.planning/research/ARCHITECTURE.md`
**Files scanned:** 18 source files, 13 test files
**Pattern extraction date:** 2026-06-04
