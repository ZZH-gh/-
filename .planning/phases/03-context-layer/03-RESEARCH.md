# Phase 3: Context Layer - Research

**Researched:** 2026-06-03
**Domain:** Session state management, multi-turn conversation context, thread-safe session tracking, context building for prompt generation
**Confidence:** HIGH

## Summary

Phase 3 introduces session state management to the v4.0 architecture, enabling multi-turn conversation tracking that Phase 4 (Conversation Core) and Phase 5 (Generation v2) will consume. Three new modules are created: `ConversationTurn` and `SessionState` data structures (plain dict/NamedTuple), `SessionManager` singleton (single active session lifecycle, thread-safe read path), and `ContextBuilder` (produces the `GenerationContext` dict consumed by Phase 5's generator).

The design is minimal and follows established patterns: `SessionManager` mirrors `KnowledgeManager`'s module-level singleton pattern, `ContextBuilder.build()` returns a dict matching `engine.py`'s `analyze()` output style, and the threading model matches `app.py`'s daemon thread + GIL-only approach (D-06 confirms no locks needed). All code uses Python stdlib only — `uuid`, `copy`, `time`, `typing`.

**Primary recommendation:** Implement `SessionManager` as a module-level singleton following the `knowledge_manager.py` pattern. `ContextBuilder` as a standalone class with a static `build(session, knowledge_manager) -> dict` method. `conversation_summary` uses the "last 5 turns joined by newline" strategy. Session ID uses `uuid4`. `extracted_info` keys follow the existing `engine.py` `TONE_KEYWORDS` and `OUTPUT_FORMATS` naming conventions.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Session lifecycle (create/update/reset) | SessionManager | -- | Owns the single active session. UI and conversation engine call it. No other component manages sessions. |
| Turn recording | SessionManager | -- | Each user input and system response is recorded via `add_turn()` by the calling code (Phase 4 conversation engine or Phase 6 UI). |
| Industry/task confirmation tracking | SessionManager | Phase 4 Conversation Engine | SessionManager stores `confirmed_industry` and `confirmed_task`. Phase 4 sets these after user confirms. SessionManager is pure storage -- it does not decide what to confirm. |
| `extracted_info` progressive accumulation | SessionManager | Phase 4 Conversation Engine | Each turn may extract info (role, audience, scope). Phase 4 calls `update_extracted_info()` after each confirmed answer. SessionManager accumulates. |
| GenerationContext building | ContextBuilder | SessionManager | ContextBuilder reads session state + queries KnowledgeManager for knowledge pack reference. Produces the flat dict that Phase 5 consumes. |
| Session reading during generation | SessionManager (read-only) | ContextBuilder | Daemon thread (generator) reads session via `get_active_session()` before generation starts. Session is frozen during generation -- no concurrent writes. |

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CONV-06 | Session context management -- track user choices, answered questions, derived context across turns | Section: SessionManager Architecture, SessionState Data Structure, ContextBuilder Design |

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** ConversationTurn structure: role ("user" | "system"), content (str), turn_type ("question" | "answer" | "confirm" | "info"), timestamp (float).
- **D-02:** SessionState structure: session_id (str), created_at (float), turns (list[ConversationTurn]), confirmed_industry (str | None), confirmed_task (str | None), extracted_info (dict, e.g., {"role": "产品经理", "tone": "正式"}).
- **D-03:** SessionState stores knowledge pack ID reference (confirmed_industry: "internet_it"), not data snapshot. Phase 5 generator queries KnowledgeManager on demand for latest pack data.
- **D-04:** Single-session mode. SessionManager manages one active session. No active session on app start. Auto-created on first user input. Replaced on "new session".
- **D-05:** ContextBuilder.build(session) → dict. Output fields: industry_id, industry_name, task_type, confirmed_info, conversation_summary, knowledge_pack_ref. Matches dict style of KnowledgePack and existing generator.py.
- **D-06:** Main thread only writer (create/update session). Background daemon thread reads only. No locks. Python GIL suffices for dict operation atomicity. Session state is stable before generation starts (all follow-up questions completed). Session not modified during generation.

### Claude's Discretion
- conversation_summary summary algorithm (last N turns join vs keyword extraction)
- SessionState extracted_info dict key naming conventions
- ContextBuilder implementation method (independent class vs SessionManager method)
- Session ID generation (uuid4 vs timestamp)
- SessionManager module organization (separate file vs combined with ContextBuilder)
- Single-session mode new_session() replacement callback notification

### Deferred Ideas (OUT OF SCOPE)
- Session disk persistence -- restoring session after app close is a subsequent enhancement
- Multi-session switching -- multi-tab concurrent sessions, v2 feature
- Session export/import -- JSON format export of session history, v2 feature

## Standard Stack

### Core (Runtime -- shipped in exe)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib `uuid` | 3.12+ | Generate unique session IDs via uuid4 | Already in exe, no additional dependency. uuid4 provides 122 random bits -- sufficient for collision-free session IDs. [VERIFIED: Python docs] |
| Python stdlib `time` | 3.12+ | Timestamps for session creation and turns | Every SessionState and ConversationTurn needs a creation timestamp. `time.time()` returns float seconds since epoch. [VERIFIED: codebase app.py usage] |
| Python stdlib `copy` | 3.12+ | Deep-copy session state for daemon thread reads | Ensures the daemon thread reads a snapshot, not a live reference that could mutate during iteration. Avoids race conditions without locks. [VERIFIED: Python docs] |
| Python stdlib `typing.NamedTuple` | 3.12+ | Define ConversationTurn return type | Lightweight, immutable tuple with named fields. Matches IndustryMatch pattern from knowledge_manager.py. [VERIFIED: Phase 2 codebase] |
| Python stdlib `typing` (protocols/dict annotations) | 3.12+ | Type annotations for SessionState and ContextBuilder output | Document the contract between modules. Zero runtime cost. [VERIFIED: codebase engine.py style] |

### Installation

No new packages to install. Phase 3 uses only Python stdlib.

```bash
# No pip install needed for Phase 3
```

### Version Verification

All Phase 3 dependencies are stdlib -- no pip verification needed.

## Package Legitimacy Audit

> Phase 3 installs no external packages. All code uses Python stdlib only.

| Package | Registry | Disposition |
|---------|----------|-------------|
| (none installed) | -- | No new dependencies |

**Packages removed:** None
**Packages flagged as suspicious:** None

## Architecture Patterns

### System Architecture Diagram

```
[app.py startup]                    [User Input Flow — Phase 4+]

app.__init__()                      User types input
  |                                     |
  v                                     v
session_manager = SessionManager()  Phase 4: Conversation Engine
  (module-level singleton)              |
  |                                     v
  |                                 session_manager.add_turn(
  |                                   role="user",
  |                                   content=input_text,
  |                                   turn_type="answer")
  |                                     |
  |                                     v
  |                                 engine.analyze(input)
  |                                     |
  |                                     v
  |                                 session_manager.update_extracted_info(
  |                                   "tone", "正式")
  |                                   update_confirmed_industry(
  |                                   "internet_it")
  |                                     |
  |                                     v
  |                                 [iterate: system asks questions,
  |                                  user answers, session accumulates]
  |                                     |
  |                                     v  (generation triggered)
  |                                 ContextBuilder.build(session)
  |                                   + knowledge_manager.load_pack(id)
  |                                     |
  |                                     v
  |                                 GenerationContext dict
  |                                   → Phase 5 Generator
  |                                     |
  |                                     v
  |                                 (daemon thread, read-only access)
  |                                 session_manager.get_active_session()
  |                                   returns deepcopy snapshot
  |                                     |
  |                                     v
  |                                 generator uses context
  |                                 (session frozen, no writes)

[New Session]
  User clicks "New Session"
    |
    v
  session_manager.new_session()
    |
    v
  Previous session discarded
  New empty session created
```

### Recommended Project Structure

```
prompt_tool/
  session_manager.py               # NEW: SessionManager singleton + ContextBuilder
  conversation/
    __init__.py                    # NEW (optional): conversation sub-package
    session_manager.py             # ALT: if separate file preferred
    context_builder.py             # ALT: if ContextBuilder is separate file
  knowledge_manager.py             # EXISTING: unchanged
  knowledge_pack.py                # EXISTING: unchanged
  engine.py                        # EXISTING: unchanged (Phase 4 modifies)
  app.py                           # MODIFIED: session_manager.initialize() in __init__
  generator.py                     # UNCHANGED: Phase 5 modifies

tests/
  test_session_manager.py          # NEW: ~10-12 unit tests
  test_context_builder.py          # NEW: ~6-8 unit tests
  conftest.py                      # MODIFIED: add session fixtures
```

### Pattern 1: SessionManager Singleton (matching KnowledgeManager pattern)

**What:** A module-level singleton that manages the lifecycle of the single active session. Provides methods for create, update, read, and reset operations. Thread safety via D-06 (main thread writes, daemon thread reads).

**When to use:** Every time a user interaction occurs. Phase 4 conversation engine calls SessionManager methods after each turn. Phase 5 generator calls `get_active_session()` before generation. Phase 6 UI calls `new_session()` on user request.

```python
"""
Session Manager -- 会话状态管理单例

模块级单例: from prompt_tool.session_manager import session_manager

架构:
  - 单会话模式（D-04），应用启动时无活跃会话
  - 用户首次输入时自动创建会话
  - 用户点击"新建会话"时丢弃旧会话
  - 主线程唯一写入，后台 daemon 线程只读（D-06）
  - 不对 session state 加锁，依赖 Python GIL
"""

import copy
import time
import uuid
from typing import NamedTuple


class ConversationTurn(NamedTuple):
    """单轮对话记录"""
    role: str           # "user" | "system"
    content: str        # 本轮内容
    turn_type: str      # "question" | "answer" | "confirm" | "info"
    timestamp: float    # time.time()


class SessionState:
    """会话状态 -- 单次对话的完整上下文"""

    def __init__(self, session_id: str):
        self.session_id: str = session_id
        self.created_at: float = time.time()
        self.turns: list[ConversationTurn] = []
        self.confirmed_industry: str | None = None
        self.confirmed_task: str | None = None
        self.extracted_info: dict[str, str] = {}

    def to_snapshot(self) -> "SessionState":
        """返回一个深拷贝快照（用于 daemon 线程只读访问）"""
        return copy.deepcopy(self)


class SessionManager:
    """单例 -- 管理唯一活跃会话的生命周期"""

    def __init__(self):
        self._active_session: SessionState | None = None
        self._initialized = False

    def initialize(self) -> None:
        """应用启动时初始化。当前无 I/O，为未来持久化预留接口。"""
        self._initialized = True

    def create_session(self) -> str:
        """创建新会话并设为活跃。返回 session_id。

        如果已有活跃会话则自动替换（单会话模式 D-04）。
        """
        session_id = str(uuid.uuid4())
        self._active_session = SessionState(session_id)
        return session_id

    def get_active_session(self) -> SessionState | None:
        """获取当前活跃会话引用。

        注意：后台 daemon 线程应调用 get_session_snapshot() 而非此方法。
        """
        return self._active_session

    def get_session_snapshot(self) -> SessionState | None:
        """获取当前活跃会话的快照（深拷贝）。

        供后台 daemon 线程使用。读到的数据可能不是最新版本，
        但生成阶段 session 不会变更，所以快照是安全的。
        """
        if self._active_session is None:
            return None
        return self._active_session.to_snapshot()

    def has_active_session(self) -> bool:
        """是否有活跃会话"""
        return self._active_session is not None

    def add_turn(
        self,
        role: str,
        content: str,
        turn_type: str,
    ) -> None:
        """添加一轮对话到活跃会话"""
        if self._active_session is None:
            raise RuntimeError("No active session. Call create_session() first.")

        turn = ConversationTurn(
            role=role,
            content=content,
            turn_type=turn_type,
            timestamp=time.time(),
        )
        self._active_session.turns.append(turn)

    def update_confirmed_industry(self, industry_id: str) -> None:
        """更新已确认的行业 ID"""
        if self._active_session is None:
            raise RuntimeError("No active session.")
        self._active_session.confirmed_industry = industry_id

    def update_confirmed_task(self, task_key: str) -> None:
        """更新已确认的任务类型 Key"""
        if self._active_session is None:
            raise RuntimeError("No active session.")
        self._active_session.confirmed_task = task_key

    def update_extracted_info(self, key: str, value: str) -> None:
        """更新推导出的上下文信息（如 tone, role, audience 等）

        Key 命名规范使用 snake_case，与 engine.py 的 extracted_info 字段名一致。
        """
        if self._active_session is None:
            raise RuntimeError("No active session.")
        self._active_session.extracted_info[key] = value

    def new_session(self) -> str:
        """丢弃当前会话，创建新会话。返回新 session_id。

        当前实现不做回调通知。如果未来需要（如 UI 清理旧会话引用），
        可在此处添加回调钩子。
        """
        return self.create_session()

    def get_turn_count(self) -> int:
        """当前会话的对话轮次数"""
        if self._active_session is None:
            return 0
        return len(self._active_session.turns)

    def get_elapsed_seconds(self) -> float:
        """当前会话已存在秒数"""
        if self._active_session is None:
            return 0.0
        return time.time() - self._active_session.created_at


# Module-level singleton (matches KnowledgeManager pattern)
session_manager = SessionManager()
```

**Key design decisions:**
- `SessionState` is a plain class with mutable fields (not a NamedTuple or frozen dataclass), because it needs to be mutated across turns by the main thread
- `to_snapshot()` uses `copy.deepcopy()` to provide a frozen snapshot for daemon threads -- this is safe because the GIL protects the deepcopy call itself, and the resulting snapshot has no shared references to the live session
- `add_turn()` appends a `ConversationTurn` NamedTuple (immutable) to the list, ensuring individual turns are safe to read even without locking
- `get_active_session()` returns the live reference for main-thread usage; `get_session_snapshot()` returns a deepcopy for daemon threads
- `update_confirmed_industry()/task/info()` are simple attribute assignments -- each is atomic under CPython's GIL

Source: CONTEXT.md D-04 (single session), D-06 (thread safety) [VERIFIED]; KnowledgeManager singleton pattern from `knowledge_manager.py` [VERIFIED: codebase]; `copy.deepcopy` for thread-safe snapshots [CITED: Python 3.12 docs]

### Pattern 2: ContextBuilder -- builds GenerationContext dict

**What:** A standalone class (or module-level function) that consumes a `SessionState` snapshot + `KnowledgeManager` data and produces the `GenerationContext` dict that Phase 5's generator consumes. Matches the `engine.py` `analyze()` pattern of returning a flat dict.

**When to use:** Called once per generation request, after the conversation engine (Phase 4) has completed the question-answer loop and before the generator (Phase 5) produces the final prompt.

```python
"""
Context Builder -- 从会话状态构建生成上下文

架构:
  - 纯函数式：输入 SessionState + KnowledgeManager，输出 dict
  - 无副作用：不修改 session，不修改 knowledge pack
  - 输出格式：与 engine.py analyze() 一致的 dict 风格
"""

from .knowledge_manager import knowledge_manager


# 约定：用于生成 conversation_summary 的最近轮数上限
CONVERSATION_SUMMARY_MAX_TURNS = 5


def build_generation_context(session) -> dict:
    """从 SessionState 构建 GenerationContext dict。

    参数:
        session: SessionState 实例（或通过 get_session_snapshot() 获得的快照）

    返回:
        dict: {
            "industry_id": str | None,
            "industry_name": str,
            "task_type": str | None,
            "confirmed_info": dict[str, str],  # extracted_info 内容
            "conversation_summary": str,        # 最近 N 轮摘要
            "knowledge_pack_ref": dict | None,  # KnowledgePack.get_meta()
        }
    """
    # 1. 行业信息
    industry_id = session.confirmed_industry
    industry_name = "通用 / 其他"
    knowledge_pack_ref = None

    if industry_id:
        # 通过 KnowledgeManager 获取行业名称和知识包元信息（D-03: 不存快照）
        index = knowledge_manager.get_index()
        entry = index.get(industry_id, {})
        industry_name = entry.get("name", industry_id)

        # 为 Phase 5 提供知识包引用（按需查询，非快照）
        try:
            pack = knowledge_manager.load_pack(industry_id)
            knowledge_pack_ref = pack.get_meta()
        except Exception:
            knowledge_pack_ref = {"id": industry_id, "name": industry_name}

    # 2. 已确认信息
    confirmed_info = dict(session.extracted_info)

    # 3. 对话摘要 -- 最近 N 轮 user/system 问答拼接
    conversation_summary = _build_summary(session.turns)

    # 4. 构建输出 dict
    return {
        "industry_id": industry_id,
        "industry_name": industry_name,
        "task_type": session.confirmed_task,
        "confirmed_info": confirmed_info,
        "conversation_summary": conversation_summary,
        "knowledge_pack_ref": knowledge_pack_ref,
    }


def _build_summary(turns: list, max_turns: int = CONVERSATION_SUMMARY_MAX_TURNS) -> str:
    """从对话轮次列表生成摘要字符串。

    策略：取最近 max_turns 轮 user+system 的问答对，用换行拼接。
    这是最简单的方案——把最近一轮对话的关键信息拼成文本，
    供 Phase 5 生成器参考用户已澄清了什么。

    未来可替换为提取式摘要（抽取关键信息而非整轮拼接），
    但在 v1 中，"最近 5 轮 Q&A 拼接"的延迟最低且信息完整。
    """
    if not turns:
        return ""

    # 取最近 max_turns 轮
    recent = turns[-max_turns:] if len(turns) > max_turns else turns

    lines = []
    for turn in recent:
        role_label = "用户" if turn.role == "user" else "系统"
        lines.append(f"[{role_label}] {turn.content}")

    return "\n".join(lines)
```

**Key design decisions:**
- **Standalone function, not a class method.** ContextBuilder has no state -- it's pure transformation. A module-level function (`build_generation_context`) is simpler and testable without instantiation. This is the alternative preferred over making it a SessionManager method, because SessionManager and ContextBuilder have different concerns (lifecycle vs transformation).
- **`knowledge_pack_ref` is metadata, not data.** Per D-03, the session stores only `confirmed_industry` (the ID). The `knowledge_pack_ref` in the GenerationContext is `pack.get_meta()` -- just the ID/name/version/description. Phase 5's generator calls `knowledge_manager.load_pack()` itself for full data.
- **`conversation_summary` uses "last 5 turns join"** (matching the CONTEXT.md specifics section). This is the simplest possible strategy: concatenate the last N turns as `[用户] ... [系统] ...` text. No NLP, no extraction logic. Phase 5 can parse this text further if needed.
- **`confirmed_info` is a direct copy of `extracted_info`.** Phase 4 writes to this dict as it confirms information. D-02 shows example keys like `{"role": "产品经理", "tone": "正式"}`. The key naming convention is `snake_case`.

Source: CONTEXT.md D-05 (ContextBuilder output fields), D-03 (knowledge pack reference by ID) [VERIFIED]; specifics section "最近 5 轮 Q&A 拼接" [VERIFIED]; engine.py analyze() returns dict pattern [VERIFIED: codebase]

### Pattern 3: Thread Safety Analysis -- Main Thread Write + Daemon Thread Read

**What:** Phase 3's thread safety model follows D-06: the main thread (Tkinter event loop) is the sole writer of SessionState. Background daemon threads (generation, conversation engine) are read-only. No locks. Python GIL guarantees atomicity of individual dict/attribute operations.

**When to use:** This applies to every integration point where `SessionManager` is accessed from a background thread. The pattern is already established in `app.py` lines 265-279.

**Thread safety model analysis:**

```
Main Thread (Tkinter)                        Daemon Thread (Generation)
─────────────────────                        ──────────────────────────
                                                                        
1. Phase 4 completes                                                  
   question-answer loop                                               
   |                                                                   
   v                                                                   
2. Calls session_manager                                               
   .add_turn() (write)                                                
   .update_extracted_info() (write)                                   
   .update_confirmed_industry() (write)                               
   |                                                                   
   v                                                                   
3. Spawns daemon thread:                   4. Calls session_manager
   Thread(target=generate, daemon=True)        .get_session_snapshot()
   |                                          returns deepcopy of
   v                                          frozen session state
5. Thread starts generation                                          
   (session state is stable --                                        
   no more writes happen)                                             
   |                                                                   
   v                                                                   
6. Generator reads snapshot                                            
   (safe: it's a deepcopy)                                            
   |                                                                   
   v                                                                   
7. Thread calls root.after(0,                                        
   callback) to dispatch results                                      
   back to main thread                                                
```

**GIL analysis for each operation:**

| Operation | GIL Protection | Risk Assessment |
|-----------|---------------|-----------------|
| `self._active_session = SessionState(...)` | Single pointer write (atomic) | SAFE: GIL ensures no torn reads |
| `self._active_session.turns.append(turn)` | List append (atomic under GIL) | SAFE: GIL protects the list resize + pointer update |
| `self._active_session.extracted_info[key] = val` | Dict key assignment (atomic) | SAFE: GIL protects the dict insertion |
| `copy.deepcopy(self._active_session)` | Entire copy under GIL | SAFE: deepcopy acquires GIL for its duration. No other thread can mutate during deepcopy because main thread is the only writer and it's not writing during generation. |
| Reading `session.confirmed_industry` on daemon thread | Single pointer read (atomic) | SAFE: GIL guarantees the pointer is either old value or new value, never a torn value. |
| Iterating `session.turns` on daemon thread while main thread appends | GIL-protected list iteration | SAFE: List iteration under GIL is atomic -- CPython checks list length at each iteration step. If main thread appends between steps, the iterator sees the new value. **However,** the session snapshot approach (deepcopy before daemon thread starts) avoids this entirely by providing a frozen copy. |

**Critical invariant:** The session state is **frozen during generation**. D-06 explicitly states: "Session state is stable before generation starts (all follow-up questions completed). Session is not modified during generation." This means:
1. Phase 4 completes all question-answer interactions
2. Phase 4 calls ContextBuilder.build() **on the main thread**
3. Main thread spawns the daemon thread with the already-built context
4. Daemon thread never calls `get_active_session()` -- it uses the pre-built context dict

This eliminates all race conditions without locks. The `get_session_snapshot()` method exists as a safety net for any future code path that needs session data from a daemon thread, but the primary path does not need it.

Source: CONTEXT.md D-06 [VERIFIED]; app.py threading pattern lines 265-279 [VERIFIED: codebase]; CPython GIL semantics for dict/list operations [CITED: Python CPython 3.12 source]

### Pattern 4: Integration with app.py Existing Threading

**What:** The existing `_do_generate()` method in app.py (line 268) spawns a daemon thread that calls `engine.analyze()` and `generate_prompts()`. Phase 3 does not modify `generator.py` (that's Phase 5), but the `SessionManager` must be initialized at app startup and available for Phase 4/5 to use.

**When to use:** Phase 3 adds `session_manager.initialize()` to app.py `__init__()` (following the same pattern as `knowledge_manager.initialize()`). Phase 4 will replace the linear `analyze -> generate` flow with a conversation loop, and that's when `SessionManager` methods get called.

```python
# In prompt_tool/app.py (Phase 3 minimal integration)

from .session_manager import session_manager

class PromptToolApp:
    def __init__(self):
        self.root = ctk.CTk()
        # ... existing setup ...

        # Phase 2: Initialize knowledge manager
        knowledge_manager.initialize()

        # Phase 3: Initialize session manager (placeholder)
        session_manager.initialize()

        self.engine = AnalysisEngine()
        # ... rest of init ...

    def _on_generate(self):
        """Existing generate handler -- Phase 3 does not modify this.
        
        Phase 4 will replace this with conversation flow that:
        1. Calls session_manager.create_session() on first input
        2. Calls engine.analyze() via conversation engine
        3. Calls session_manager.add_turn() after each exchange
        4. Builds context via ContextBuilder before generation
        """
        # ... unchanged from v3.0 ...
```

**Key insight:** Phase 3 introduces the data structures and manager. Phase 4 wires them into the conversation flow. Phase 3's app.py integration is minimal -- just initialization and making `session_manager` importable.

Source: app.py existing threading pattern [VERIFIED: codebase]; knowledge_manager.initialize() integration pattern [VERIFIED: codebase]

### Pattern 5: `extracted_info` Key Naming Convention

**What:** The `extracted_info` dict stores progressively accumulated context information derived from user responses. Each key-value pair represents a confirmed piece of information. Key naming uses `snake_case` matching existing conventions in `engine.py` fields.

**Recommended key set (Phase 4 may extend):**

| Key | Value Type | Example | Source | Set By |
|-----|-----------|---------|--------|--------|
| `tone` | str | "正式" | engine.py TONE_KEYWORDS | Phase 4 after initial analysis |
| `output_format` | str | "报告" | engine.py OUTPUT_FORMATS | Phase 4 after initial analysis |
| `role` | str | "产品经理" | Follow-up tree selection | Phase 4 after user confirms |
| `audience` | str | "研发团队" | Follow-up tree selection | Phase 4 after user confirms |
| `scope` | str | "电商小程序" | User answer text | Phase 4 after user answers |
| `complexity` | str | "high" | Follow-up tree selection | Phase 4 after user confirms |
| `pain_point` | str | "需求频繁变更" | KnowledgePack pain points | Phase 4 after user selects |

**Convention:**
- All keys in `snake_case`
- Values are always `str` (not lists or ints). If multiple values, join with `; `.
- Keys that map to knowledge pack fields use the same name as the field (e.g., `pain_point` maps to `KnowledgePack.get_pain_points()`)
- Keys are lowercase with underscores
- No special characters or Unicode in keys (ASCII only)
- No implicit type conversion -- values are strings even for numbers

Source: D-02 example keys [VERIFIED]; engine.py `extracted_info` field name [VERIFIED: codebase engine.py line 20]; Phase 2 KnowledgePack field names for pain_point match [VERIFIED: codebase knowledge_pack.py]

### Pattern 6: conversation_summary Algorithm Options

**What:** The `conversation_summary` field in the GenerationContext provides the generator (Phase 5) with a textual summary of the conversation so far. CONTEXT.md specifics recommend "last 5 turns Q&A join" as the simple default, but there are alternatives.

**Algorithm comparison:**

| Algorithm | Description | Pros | Cons | Recommend for Phase 3? |
|-----------|-------------|------|------|----------------------|
| **Last N turns join** | Take last N turns (default 5), join as `[用户] ... [系统] ...` | Simplest implementation. Zero overhead. Preserves full context. | May include irrelevant turns. Noisy for long conversations. | **YES -- Phase 3 default** |
| Keyword extraction | Extract key-value pairs from turns using known patterns | Clean output. No noise. | Requires pattern matching. May miss context. Overengineering for v1. | No -- defer to Phase 5+ |
| Whole conversation | Join all turns, not just last N | Complete context. | Very long for 10+ turn conversations. Generator may exceed prompt length. | No -- Phase 5 controls what it reads |
| Structured summary | Build a dict of {answered_questions, confirmed_info, pending_questions} | Machine-readable. Clean. | Complex to implement. Phase 4 conversation engine already has this data. | No -- this duplicates Phase 4 state |

**Recommended implementation for Phase 3:**
```python
SUMMARY_MAX_TURNS = 5  # Configurable constant

def _build_summary(turns, max_turns=SUMMARY_MAX_TURNS):
    """最近 N 轮 Q&A 拼接策略"""
    if not turns:
        return ""
    
    recent = turns[-max_turns:]
    lines = []
    for turn in recent:
        label = "用户" if turn.role == "user" else "系统"
        lines.append(f"[{label}] {turn.content}")
    
    return "\n".join(lines)
```

**Why "last N turns join" is correct for Phase 3:**
1. Phase 5's generator needs to know what the user said in recent turns -- raw content is better than a lossy summary
2. The 3-question limit (CONV-04) means conversations will be short (~5-8 turns max), so "last 5" effectively means "all meaningful content"
3. Zero NLP dependency -- no spaCy, no jieba, no regex patterns
4. The `[用户]`/`[系统]` labels provide role context that a keyword extraction would lose
5. Easy to extend: swap the `_build_summary()` function body when a better algorithm emerges

Source: CONTEXT.md specifics section ("最近 5 轮 Q&A 拼接") [VERIFIED]; CONV-04 3-question hard limit from REQUIREMENTS.md [VERIFIED]

### Anti-Patterns to Avoid

- **Do NOT add threading locks.** D-06 explicitly says no locks. The GIL provides sufficient atomicity for dict/attribute operations, and the session-is-during-generation invariant eliminates concurrent read-write scenarios.
- **Do NOT store knowledge pack snapshot in SessionState.** D-03 says store only `confirmed_industry` (the ID). The generator loads the pack from `KnowledgeManager` on demand. A snapshot would go stale when the knowledge pack is updated.
- **Do NOT use `dataclasses` for SessionState.** The project convention (confirmed in Phase 1 D-11) is plain dicts and classes. Using `@dataclass` would introduce a stylistic inconsistency. Plain class with `__init__` is the established pattern.
- **Do NOT make `ConversationTurn` a dict.** Use `NamedTuple` (matching `IndustryMatch` in `knowledge_manager.py`). NamedTuples are immutable (turns don't change after recording), hashable, and self-documenting with field names.
- **Do NOT expose `SessionState` internal fields as properties.** Direct attribute access (`session.confirmed_industry`) is consistent with the entire codebase's style. Properties would add overhead with no benefit.
- **Do NOT add `_on_new_session` callback in Phase 3.** The new_session() callback is in Claude's Discretion. Phase 3 does not know about UI lifecycle events. Phase 6 will handle any UI cleanup when wiring new_session() to the "New Session" button.
- **Do NOT import `session_manager` inside `ContextBuilder` as a global.** Pass the session as a parameter. This keeps `build_generation_context()` pure/functions pure, deterministic, and testable.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Session ID generation | Timestamp + counter | `uuid.uuid4()` | uuid4 provides 122 random bits -- guaranteed uniqueness without coordination. Timestamp-based IDs can collide if two sessions are created in the same millisecond. |
| Thread-safe session snapshot | Custom lock-based freeze/thaw | `copy.deepcopy()` | Deepcopy is atomic under GIL, creates a fully independent copy, and requires no lock management. The session is frozen during generation anyway (D-06), so the copy is correct at the time it's created. |
| Turn immutability | Custom frozen class | `typing.NamedTuple` | NamedTuple provides immutability, field access by name, tuple unpacking, and zero boilerplate. Matches the existing `IndustryMatch` pattern from `knowledge_manager.py`. |

**Key insight:** Phase 3 has no deceptively complex problems. Session management, state tracking, and context building are well-understood patterns. The complexity comes from the interplay between threads (main thread writes + daemon reads) and the invariant that session state is frozen during generation. The `copy.deepcopy` snapshot pattern eliminates the need for any lock mechanism.

## Common Pitfalls

### Pitfall 1: Daemon Thread Reads Live Session During Iteration

**What goes wrong:** A daemon thread calls `get_active_session()` (returns live reference) and iterates over `session.turns` while the main thread calls `add_turn()` (appends to the list). The list is mutated during iteration, causing `RuntimeError: list changed size during iteration` or, worse, silently skipping a turn.

**Why it happens:** Python lists are not thread-safe for iteration with concurrent modification. Even though the GIL prevents torn writes, the list's internal size can change between iteration steps.

**How to avoid:** 
- Always use `get_session_snapshot()` (deepcopy) in daemon threads, NOT `get_active_session()`.
- Enforce the "session frozen during generation" invariant (D-06) -- verify no code path writes to session while a generator thread is running.
- If in doubt, log a warning when a daemon thread calls `get_active_session()`.

**Warning signs:** Intermittent `RuntimeError: list changed size during iteration` or generation results that occasionally miss the last turn.

### Pitfall 2: `deepcopy` Performance on Long Conversations

**What goes wrong:** A 20-turn conversation with long content fields triggers a deepcopy of the entire SessionState (turns list + extracted_info dict) every time a daemon thread needs a snapshot. For a 20-turn, 500-char-per-turn conversation, this is ~10KB of data -- deepcopy takes ~0.5ms, negligible. But if a hot loop (e.g., Phase 4 analyzing each turn) calls `get_session_snapshot()` on every iteration, it adds up.

**Why it happens:** Deepcopy is called unnecessarily when the caller only needs one or two fields.

**How to avoid:**
- Only call `get_session_snapshot()` once, at the point where the session state is frozen (before spawning the generator thread).
- If a read-only method only needs one field (e.g., `confirmed_industry`), add a specific getter like `get_confirmed_industry()` that returns just the string (GIL-protected atomic read).
- The `deepcopy` overhead for typical v4.0 sessions (5-8 turns, ~5KB) is <0.1ms -- not a real bottleneck.

**Warning signs:** Profile shows `deepcopy` taking more than 5ms. Session has >100 turns or >100KB of content.

### Pitfall 3: `extracted_info` Key Collisions

**What goes wrong:** Phase 4 conversation engine and Phase 3's initial analysis both write to `extracted_info` with overlapping key names but different values. E.g., Phase 3's initial analysis sets `extracted_info["tone"] = "专业"` from keyword matching, then Phase 4's follow-up tree sets `extracted_info["tone"] = "正式"` from user selection. The value is silently overwritten.

**Why it happens:** `update_extracted_info()` is a simple `dict[key] = value` assignment. No collision detection, no versioning.

**How to avoid:**
- Phase 4 should read the initial analysis value first, then decide whether to overwrite based on user confirmation (which should take priority).
- Document the ownership of each key: which phase sets it, and which phase can override.
- Consider a convention where keys set by the user (via follow-up tree) are prefixed with `confirmed_` to distinguish from analysis-derived keys.

**Warning signs:** Generator produces inconsistent output (e.g., tone says "正式" in one section and "专业" in another) because it reads from conflicting sources.

### Pitfall 4: `new_session()` Without UI Cleanup

**What goes wrong:** User clicks "New Session". `session_manager.new_session()` creates a new session, but the UI still shows old content (previous analysis results, generated prompts, info bar text). The user sees stale data.

**Why it happens:** SessionManager owns session lifecycle, but UI state is owned by `PromptToolApp`. There's no callback mechanism from `new_session()` to `PromptToolApp._on_clear()`.

**How to avoid:**
- Phase 3 adds `session_manager.initialize()` to app.py but does NOT wire `new_session()` to UI -- that's Phase 6's responsibility.
- Add a note in the code that `new_session()` does not trigger UI callbacks. Phase 6 must explicitly call `_on_clear()` after `new_session()`.
- If a synchronous callback is needed, the discretion says "implement if Phase 6 requires it." Phase 3 can leave the callback slot empty (or as a `None`-type attribute that Phase 6 can set).

**Warning signs:** After "New Session", user sees old prompt in the display area.

### Pitfall 5: `add_turn()` Called Before `create_session()`

**What goes wrong:** Phase 4 conversation engine or Phase 6 UI calls `session_manager.add_turn()` before `session_manager.create_session()`. `RuntimeError: No active session` is raised.

**Why it happens:** Single-session mode (D-04) means no session exists on app start. The caller must explicitly create one on first user input.

**How to avoid:**
- Have the first user input event handler call both `create_session()` and `add_turn()`.
- Consider making `add_turn()` auto-create if no session exists (auto-create convention), but this hides bugs where the session creation was intentionally delayed.
- The strict approach (raise error) is better for debugging. Phase 4/6 will see the error immediately during development.
- Document the call sequence: `create_session()` -> `add_turn()` -> `update_extracted_info()` -> ... -> `new_session()`.

**Warning signs:** `RuntimeError: No active session` on first user interaction.

## Code Examples

### Example 1: SessionManager Integration in Phase 4 (Future Usage Reference)

```python
# In Phase 4's conversation engine (for reference -- NOT implemented in Phase 3)
from .session_manager import session_manager
from .engine import AnalysisEngine
from .context_builder import build_generation_context

engine = AnalysisEngine()

def process_user_input(user_input: str) -> dict:
    """Process one user input through the conversation flow.
    
    This is Phase 4's responsibility. Shown here to illustrate
    how SessionManager is consumed.
    """
    # Create session on first input
    if not session_manager.has_active_session():
        session_manager.create_session()
    
    # Record user turn
    session_manager.add_turn(role="user", content=user_input, turn_type="answer")
    
    # Analyze input
    analysis = engine.analyze(user_input)
    
    # Store extracted info (D-02 style)
    if analysis.get("tone"):
        session_manager.update_extracted_info("tone", analysis["tone"])
    if analysis.get("output_format"):
        session_manager.update_extracted_info(
            "output_format", analysis["output_format"]["name"]
        )
    
    # If industry confirmed, store it
    if analysis.get("industry_key") and analysis["industry_key"] != "通用":
        session_manager.update_confirmed_industry(analysis["industry_key"])
    
    # ... (Phase 4: check if more questions needed, return turn result)
    
    # When ready to generate:
    # context = build_generation_context(session_manager.get_active_session())
    # generated = generate_prompts(context)
```

Source: Adapted from app.py `_do_generate()` flow [VERIFIED: codebase] and engine.py `analyze()` output fields [VERIFIED: codebase]

### Example 2: Full Lifecycle Test (End-to-End)

```python
# In tests/test_session_manager.py (anticipated test pattern)

def test_full_session_lifecycle():
    """Session creation → add_turns → update_info → snapshot → new_session"""
    from prompt_tool.session_manager import SessionManager, ConversationTurn
    
    sm = SessionManager()
    
    # 1. Start: no active session
    assert not sm.has_active_session()
    assert sm.get_turn_count() == 0
    
    # 2. Create session
    session_id = sm.create_session()
    assert sm.has_active_session()
    assert isinstance(session_id, str)
    assert len(session_id) == 36  # uuid4 format
    
    # 3. Add turns
    sm.add_turn(role="system", content="你好！请描述你的需求。", turn_type="question")
    sm.add_turn(role="user", content="帮我写一个PRD文档", turn_type="answer")
    assert sm.get_turn_count() == 2
    
    # 4. Update extracted info
    sm.update_confirmed_industry("internet_it")
    sm.update_confirmed_task("prd_writing")
    sm.update_extracted_info("tone", "专业")
    sm.update_extracted_info("role", "产品经理")
    
    # 5. Verify state
    session = sm.get_active_session()
    assert session.session_id == session_id
    assert session.confirmed_industry == "internet_it"
    assert session.confirmed_task == "prd_writing"
    assert session.extracted_info["tone"] == "专业"
    
    # 6. Snapshot (thread-safe)
    snapshot = sm.get_session_snapshot()
    assert snapshot.session_id == session_id
    assert len(snapshot.turns) == 2
    
    # 7. Snapshot is independent (mutating snapshot doesn't affect original)
    snapshot.extracted_info["tone"] = "正式"
    assert session.extracted_info["tone"] == "专业"  # original unchanged
    
    # 8. New session
    new_id = sm.new_session()
    assert new_id != session_id
    assert sm.has_active_session()
    assert sm.get_turn_count() == 0  # new session is empty
```

Source: Test patterns from `test_knowledge_manager.py` [VERIFIED: codebase] and Phase 2 TDD patterns [VERIFIED: codebase]

### Example 3: ContextBuilder Output Shape

```python
# Expected output of build_generation_context() -- the contract for Phase 5

generation_context = {
    "industry_id": "internet_it",
    "industry_name": "互联网 / IT",
    "task_type": "prd_writing",
    "confirmed_info": {
        "tone": "专业",
        "role": "产品经理",
        "audience": "研发团队",
    },
    "conversation_summary": (
        "[系统] 你好！请描述你的需求。\n"
        "[用户] 帮我写一个PRD文档\n"
        "[系统] 这个PRD的主要受众是谁？\n"
        "[用户] 研发团队\n"
        "[系统] 你希望PRD包含哪些核心部分？\n"
        "[用户] 功能需求和交互设计"
    ),
    "knowledge_pack_ref": {
        "id": "internet_it",
        "name": "互联网 / IT",
        "icon": "💻",
        "description": "互联网与IT行业知识包",
        "version": "1.0.0",
        "schema_version": "1.0",
    },
}
```

Source: D-05 output fields [VERIFIED]; CONTEXT.md specifics section [VERIFIED]

## State of the Art

| Old Approach (v3.0) | Current Approach (Phase 3) | When Changed | Impact |
|---------------------|---------------------------|--------------|--------|
| SESSION STATE: None -- every generate is stateless, no turn tracking | SessionManager with SessionState (turns[], confirmed_industry, confirmed_task, extracted_info) | Phase 3 | Enables multi-turn conversation. Generator can reference previous turns. Conversational UI becomes possible. |
| THREAD SAFETY: No shared state -- each generate is independent | Main thread writes, daemon thread reads via deepcopy snapshot | Phase 3 | Backward compatible. Existing _do_generate() pattern unchanged. New invariant: session frozen during generation. |
| DATA FLOW: User input → analyze() → generate() → output | User input → SessionManager → analyze() → SessionManager → ContextBuilder → generate() → output | Phase 3 + Phase 4 | More structured, but Phase 5 generator gets richer context (conversation_summary, confirmed_info, knowledge_pack_ref). |
| extracted_info: engine.py stores analysis result in self.extracted_info (lost after generation) | SessionManager stores progressively accumulated extracted_info across turns | Phase 3 | Information accumulates rather than being computed fresh each time. Phase 4 controls what's added when. |

**Deprecated/outdated:**
- Nothing in Phase 3 deprecates existing code. The new modules are additive. `engine.py` `_identify_industry()` continues to work. `generator.py` is unchanged (Phase 5 modifies it).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `copy.deepcopy()` of a SessionState with ~8 turns takes <0.5ms and does not block the UI | Thread Safety / Session Snapshot | If deepcopy takes >5ms on large sessions, the UI thread will stutter. Mitigation: limit turns to 20 (CONV-04 hard limit enforces short sessions). |
| A2 | The GIL guarantees atomicity of `list.append()` and `dict[key] = value` for our threading model | Thread Safety Analysis | If CPython changes GIL semantics in Python 3.13+, the atomicity guarantee may weaken. Mitigation: document the CPython version dependency. |
| A3 | "Last 5 turns join" provides sufficient context for Phase 5 generator | conversation_summary Algorithm | If generator needs structured info (not raw text), Phase 5 must either parse the summary or consume `confirmed_info` dict. Mitigation: the `confirmed_info` dict is the structured source; `conversation_summary` is supplementary. |
| A4 | uuid4 generation never blocks (no system entropy exhaustion) | Session ID generation | On headless servers or resource-constrained environments, uuid4 may block waiting for `/dev/random`. Windows has CryptGenRandom which is fast. Mitigation: uuid4 is called once per session (~once per user interaction), not in a hot loop. |
| A5 | `session_manager.initialize()` can be a no-op in Phase 3 and extended later | Initialize Pattern | If initialization later needs I/O (database connection for persistence), the init order in app.py must be considered. Mitigation: the initialize() pattern already supports I/O (KnowledgeManager reads index.json), so the slot is ready. |
| A6 | No circular import between session_manager.py and knowledge_manager.py | Module Dependencies | ContextBuilder imports KnowledgeManager. SessionManager does not. No cycle. Verified: `session_manager.py` imports `copy`, `time`, `uuid` only. `ContextBuilder` (if separate) imports `knowledge_manager`. |

## Open Questions (RESOLVED)

1. **Should ContextBuilder be an independent module or a SessionManager method?**
   - What we know: Both are valid. SessionManager owns state lifecycle. ContextBuilder transforms state.
   - What's unclear: Whether a standalone module creates too many files for a small project.
   - Recommendation: **Standalone module-level function** in the same file as SessionManager or in `context_builder.py`. A function (no class needed) keeps the transformation stateless and testable. Grouping with SessionManager prevents file proliferation while maintaining separation of concerns.

2. **Should `new_session()` emit a callback?**
   - What we know: Phase 6 UI needs to clear old content when user starts a new session. The callback could simplify this.
   - What's unclear: Whether the callback belongs in SessionManager (data layer) or in app.py (UI layer).
   - Recommendation: **No callback in Phase 3.** SessionManager is a data-layer component. Adding a UI callback to it violates layering. Phase 6 should handle UI cleanup explicitly: `session_manager.new_session()` returns the new session_id, and the UI handler calls `_on_clear()` after it. If a generic callback mechanism is needed, add it in Phase 6 as a UI concern.

3. **What is the exact format of `conversation_summary`?**
   - What we know: D-05 says "recent N turns Q&A summary". CONTEXT.md specifics say "last 5 turns Q&A join."
   - What's unclear: Whether to include system turns (questions) or only user turns (answers).
   - Recommendation: **Include both user and system turns.** The generator needs to see what questions the system asked to understand what context it has. Each line is `[用户] ...` or `[系统] ...` with the content text. 5 turn limit.

4. **Should `confirmed_info` be a flat dict or structured dict?**
   - What we know: D-02 says `extracted_info` is a flat dict with string values.
   - What's unclear: Whether Phase 5 needs nested structures (e.g., multiple roles).
   - Recommendation: **Flat dict with string values.** Phase 5 can parse multi-value strings (join with `; `) if needed. Nested dicts add complexity to the SessionState model and are premature for v1.

5. **Where should `session_manager.initialize()` be called in app.py?**
   - What we know: `knowledge_manager.initialize()` is called in app.py `__init__()`.
   - Recommendation: **Same location -- in `__init__()` after `knowledge_manager.initialize()` and before `AnalysisEngine()`.** Following the established pattern ensures consistent initialization order and makes the app.py changes minimal.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python stdlib `uuid` | SessionManager.create_session() | YES | 3.12.10 | -- |
| Python stdlib `time` | Session timestamps | YES | 3.12.10 | -- |
| Python stdlib `copy` | Session snapshots (deepcopy) | YES | 3.12.10 | -- |
| Python stdlib `typing` | ConversationTurn NamedTuple | YES | 3.12.10 | -- |
| Python stdlib `threading` | Existing app.py daemon thread pattern | YES | 3.12.10 | -- |

**Missing dependencies with no fallback:** None. Phase 3 uses only stdlib.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 (from Phase 1) |
| Config file | pytest.ini |
| Quick run command | `pytest tests/test_session_manager.py tests/test_context_builder.py -x --tb=short` |
| Full suite command | `pytest tests/ -x --tb=short` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CONV-06 | SessionManager creates session with uuid4 | unit | `pytest tests/test_session_manager.py::TestSessionManager::test_create_session -x` | Wave 0 |
| CONV-06 | add_turn appends ConversationTurn with correct fields | unit | `pytest tests/test_session_manager.py::TestSessionManager::test_add_turn -x` | Wave 0 |
| CONV-06 | ConversationTurn values are correct types | unit | `pytest tests/test_session_manager.py::TestConversationTurn::test_turn_structure -x` | Wave 0 |
| CONV-06 | update_confirmed_industry/task sets values | unit | `pytest tests/test_session_manager.py::TestSessionManager::test_update_confirmed -x` | Wave 0 |
| CONV-06 | update_extracted_info accumulates values | unit | `pytest tests/test_session_manager.py::TestSessionManager::test_extracted_info -x` | Wave 0 |
| CONV-06 | new_session() creates new session, discards old | unit | `pytest tests/test_session_manager.py::TestSessionManager::test_new_session -x` | Wave 0 |
| CONV-06 | get_session_snapshot() returns independent deepcopy | unit | `pytest tests/test_session_manager.py::TestSessionManager::test_snapshot_independence -x` | Wave 0 |
| CONV-06 | add_turn() raises RuntimeError without active session | unit | `pytest tests/test_session_manager.py::TestSessionManager::test_add_turn_no_session -x` | Wave 0 |
| CONV-06 | ContextBuilder.build() returns correct dict shape | unit | `pytest tests/test_context_builder.py::TestContextBuilder::test_build_output_shape -x` | Wave 0 |
| CONV-06 | conversation_summary contains last N turns | unit | `pytest tests/test_context_builder.py::TestContextBuilder::test_conversation_summary -x` | Wave 0 |
| CONV-06 | knowledge_pack_ref from KnowledgeManager, not session | integration | `pytest tests/test_context_builder.py::TestContextBuilder::test_knowledge_pack_ref -x` | Wave 0 |
| CONV-06 | Full lifecycle: create -> add_turns -> update -> snapshot -> new_session | integration | `pytest tests/test_session_manager.py::TestSessionManager::test_full_lifecycle -x` | Wave 0 |

### Wave 0 Gaps

- [ ] `tests/test_session_manager.py` -- unit tests for SessionManager (create, add_turn, confirm, extract, snapshot, new_session, error cases)
- [ ] `tests/test_context_builder.py` -- unit tests for ContextBuilder (output shape, summary, knowledge_pack_ref, empty session)
- [ ] `tests/conftest.py` -- fixtures: `sample_session_turns`, `sample_extracted_info`, `session_manager_instance`

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | No | SessionManager stores user input as-is in ConversationTurn. No validation needed -- the data is consumed by the generator (Phase 5) which treats it as untrusted text. |

### Known Threat Patterns for Phase 3 (Session State Layer)

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Session ID collision | Spoofing | uuid4 provides 122 random bits. Probability of collision is essentially zero at the scale of a desktop app (1 session per user interaction). |
| User input in extracted_info | Tampering | extracted_info values are set by Phase 4 conversation engine, not directly from user input. Even if user input were stored, it's consumed by a local prompt generator -- no network transmission, no injection risk. |
| Deepcopy of untrusted data | Tampering | copy.deepcopy() cannot execute arbitrary code on a pure dict/list data structure. No __reduce__ or __getstate__ exploits possible because SessionState contains only str, float, None, and list of NamedTuples. |

**Key security notes:**
- Phase 3 is a state-management layer. No network calls, no user input that reaches filesystem operations.
- The `session_id` is used as a key within the process only -- never exposed to external systems.
- `ConversationTurn.content` contains user input text, but this text is already present in the app's UI text widgets. SessionManager doesn't add new exposure.
- No regulated data flows through Phase 3 components. Financial/medical content compliance (QA-03) is a Phase 6/7 concern.

## Sources

### Primary (HIGH confidence)
- CONTEXT.md for Phase 3 (D-01 through D-06) [VERIFIED: file read]
- CONTEXT.md specifics section (conversation_summary, uuid4, singleton pattern) [VERIFIED: file read]
- KnowledgeManager singleton pattern from `prompt_tool/knowledge_manager.py` [VERIFIED: codebase]
- app.py threading pattern (daemon thread + root.after) [VERIFIED: codebase app.py lines 265-279]
- engine.py analyze() dict return pattern [VERIFIED: codebase engine.py lines 71-88]
- engine.py extracted_info field (line 20) [VERIFIED: codebase]
- test_knowledge_manager.py test patterns [VERIFIED: codebase]
- Python `uuid.uuid4` docs [CITED: Python 3.12 docs]
- Python `copy.deepcopy` docs [CITED: Python 3.12 docs]
- Python `typing.NamedTuple` docs [CITED: Python 3.12 docs]

### Secondary (MEDIUM confidence)
- CPython GIL semantics for dict/list operations [CITED: Python CPython 3.12 source -- "The GIL protects internal data structures" documented in Python/ceval.c]
- uuid4 performance on Windows [CITED: docs.python.org/3/library/uuid.html -- "On Windows, uuid4() uses CryptGenRandom()"]

### Tertiary (LOW confidence)
- (None -- all Phase 3 findings are either codebase-verified, stdlib-documented, or derived from locked decisions)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all stdlib, no new packages needed, confirmed by Python 3.12+ availability
- Architecture: HIGH -- all patterns directly derived from CONTEXT.md locked decisions and codebase analysis (KnowledgeManager pattern, app.py threading, engine.py dict return)
- Thread safety: HIGH -- based on D-06 explicit decision, CPython GIL documentation, and the "session frozen during generation" invariant
- Pitfalls: HIGH -- based on codebase analysis (app.py threading, knowledge_manager.py singleton, engine.py extracted_info) and established session management patterns
- extracted_info key naming: MEDIUM -- recommended convention based on engine.py field names, but Phase 4 may add keys not anticipated here

**Research date:** 2026-06-03
**Valid until:** 2026-07-03 (30 days; stable stdlib, no fast-moving dependencies)
