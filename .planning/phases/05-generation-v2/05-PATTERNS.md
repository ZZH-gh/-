# Phase 5: Generation v2 - Pattern Map

**Mapped:** 2026-06-04
**Files analyzed:** 5 (2 refactor, 1 modify, 2 test)
**Analogs found:** 5 / 5

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `prompt_tool/generator.py` | service | request-response | `prompt_tool/generator_v2.py` | exact (same role + data flow, is the draft being fixed) |
| `prompt_tool/conversation_engine.py` | service | request-response | `prompt_tool/conversation_engine.py` (self) | exact (self-modify: `generate_complete()` stub) |
| `prompt_tool/tests/test_generator_v2.py` | test | test | `tests/test_generator_v2.py` (self) | exact (self-modify: existing test class) |
| `prompt_tool/tests/conftest.py` | test | test | `tests/conftest.py` (self) | exact (self-modify: extend `sample_pack_json` fixture) |
| `prompt_tool/app.py` | controller | request-response | `prompt_tool/app.py` (self) | exact (self-modify: `_do_generate_v4` lines 284-318) |

## Pattern Assignments

### `prompt_tool/generator.py` (service, request-response) — REFACTOR

Add `PromptGeneratorV2` class alongside existing `PromptGenerator`, keep `generate_prompts()` factory unchanged.

**Analog:** `prompt_tool/generator_v2.py` (entire file, 215 lines) — the draft prototype. All structural code must be rewritten into `generator.py`.

**Key data flow fix:** The draft `generator_v2.py` line 33 accesses `self.pack_ref = self.ctx.get("knowledge_pack_ref")` which returns `pack.get_meta()` (metadata-only, no roles/pain_points). The new implementation must load the `KnowledgePack` directly via `knowledge_manager.load_pack()` as shown in RESEARCH.md lines 322-342.

**Imports pattern — existing generator.py lines 5-7:**
```python
import random
import re
from .knowledge import INDUSTRIES
```

New imports needed (add `from .knowledge_manager import knowledge_manager`):
```python
import random
import re
from .knowledge import INDUSTRIES
from .knowledge_manager import knowledge_manager
```

**Core class pattern — borrow from `generator.py` lines 10-24:**
```python
class PromptGenerator:

    def __init__(self, analysis_result: dict):
        self.r = analysis_result
        self.industry_key = analysis_result["industry_key"]
        self.industry_name = analysis_result["industry_name"]
        self.task_name = analysis_result["task_name"]
        self.original_input = analysis_result["original_input"]

    def generate_all(self) -> dict:
        return {
            "direct":   self._direct(),
            "roleplay": self._roleplay(),
            "detailed": self._detailed(),
        }
```

**Factory pattern — existing `generator.py` lines 272-273:**
```python
def generate_prompts(analysis_result: dict) -> dict:
    return PromptGenerator(analysis_result).generate_all()
```

**PromptGeneratorV2 generate_all() — borrow from `generator_v2.py` lines 35-40, but fix to apply filter per strategy:**
```python
def generate_all(self) -> dict:
    return {
        "direct": self._filter(self._direct()),
        "roleplay": self._filter(self._roleplay()),
        "detailed": self._filter(self._detailed()),
    }
```

**KnowledgePack loading fix — from RESEARCH.md lines 322-342:**
```python
class PromptGeneratorV2:
    def __init__(self, analysis_result: dict, generation_context: dict = None):
        self.r = analysis_result
        self.ctx = generation_context or {}
        self.industry_id = self.ctx.get("industry_id") or analysis_result.get("industry_key")
        self.industry_name = self.ctx.get("industry_name") or analysis_result.get("industry_name", "通用")
        self.summary = self.ctx.get("conversation_summary", "")
        self.confirmed = self.ctx.get("confirmed_info", {})

        # KEY FIX: Load KnowledgePack directly, not metadata from context_builder
        self._pack = None
        if self.industry_id:
            try:
                self._pack = knowledge_manager.load_pack(self.industry_id)
            except Exception:
                self._pack = None

        # Select task-relevant knowledge (cached, shared across 3 strategies)
        self._task_knowledge = self._select_task_knowledge()
```

**KnowledgePack getter API — from `prompt_tool/knowledge_pack.py` lines 50-58, 79-91, 104-106:**
```python
# Get roles for role depth injection
roles = self._pack.get_roles()                    # -> list[dict]
role = self._pack.get_role(role_name)             # -> dict | None

# Get doc templates for output structure injection
docs = self._pack.get_doc_templates(task_type)     # -> list[dict]
doc = self._pack.get_doc_template(template_name)   # -> dict | None

# Get pain points for anti-pattern injection
pains = self._pack.get_pain_points()               # -> list[dict]
```

**Anti-pattern filter — from RESEARCH.md lines 348-389 (pain point driven, D-15):**
```python
def _build_anti_pattern_rules(self) -> list:
    """Build filter rules from knowledge pack pain points + hardcoded supplements."""
    rules = []

    # Primary: pain point driven (D-15, D-18)
    if self._pack:
        for pp in self._pack.get_pain_points():
            what_not_to = pp.get("what_not_to_do", "")
            if what_not_to:
                rules.append({
                    "type": "pain_point",
                    "trigger_phrases": pp.get("typical_phrases", []),
                    "pattern": what_not_to,
                    "description": pp["name"],
                })

    # Secondary: general authority/stereotype patterns (D-16 supplement)
    rules.extend([
        {"type": "authority", "pattern": r"作为.*[资深|首席|全球].*专家", "replacement": ""},
        {"type": "authority", "pattern": r"行业[领先|标杆|顶尖|公认]", "replacement": "行业"},
        {"type": "stereotype", "pattern": r"毫无疑问.*(?:正确|有效|最佳)", "replacement": ""},
    ])
    return rules

def _filter(self, text: str) -> str:
    """GEN-04: Pain point driven + regex supplement."""
    for rule in self._build_anti_pattern_rules():
        if rule["type"] == "pain_point":
            for phrase in rule.get("trigger_phrases", []):
                if phrase in text:
                    text = text.replace(phrase, f"[注意：避免{rule['description']}]")
        else:
            pattern = rule["pattern"]
            replacement = rule.get("replacement", "")
            text = re.sub(pattern, replacement, text)
    return text.strip()
```

**Knowledge selection pattern — from RESEARCH.md lines 202-228:**
```python
def _select_task_knowledge(self) -> dict:
    """Select task-relevant slice of knowledge pack (D-12)."""
    task_key = self.ctx.get("task_type") or self.r.get("task_key", "")
    if not self._pack:
        return {}

    task = self._pack.get_task(task_key)
    doc_template = self._pack.get_doc_template(task_key)
    roles = self._pack.get_roles()
    pain_points = self._pack.get_pain_points()

    all_terms = self._pack.get_terms()
    task_terms = [t for t in all_terms
                  if t.get("term") in (task.get("keywords", []) if task else [])][:15]

    task_role = next((r for r in roles
                      if task_key in r.get("common_tasks", [])), roles[0] if roles else None)

    return {
        "task": task,
        "doc_template": doc_template,
        "role": task_role,
        "role_kpis": task_role.get("kpis", [])[:3] if task_role else [],
        "role_pain_points": task_role.get("pain_points", [])[:2] if task_role else [],
        "pain_points": pain_points[:3] if pain_points else [],
        "terms": task_terms,
    }
```

---

### `prompt_tool/conversation_engine.py` (service, request-response) — MODIFY

Update `generate_complete()` to call `PromptGeneratorV2` and return prompts payload. Also add a method or extend `generate_complete()` to invoke the generator.

**Analog:** `prompt_tool/conversation_engine.py` lines 193-196 (current stub) and lines 42-56 (class init pattern).

**Current `generate_complete()` stub — lines 193-196:**
```python
def generate_complete(self) -> dict:
    """生成完成，回到完成状态。"""
    self._transition(ConversationState.COMPLETE)
    return {"state": self.state.value, "action": "display_results"}
```

**New pattern — borrow `skip_follow_up()` flow from lines 179-191 (which already builds context) and `app.py` `_do_generate_v4()` lines 284-318 (which calls `generate_prompts_v2`):**
```python
def generate_complete(self) -> dict:
    """Orchestrate generation: build context -> call PromptGeneratorV2 -> return result."""
    self._transition(ConversationState.GENERATING)

    session = session_manager.get_active_session()
    context = build_generation_context(session) if session else {}

    from .generator import PromptGeneratorV2
    analysis_result = self._last_analysis
    gen = PromptGeneratorV2(analysis_result, context)
    prompts = gen.generate_all()

    self._transition(ConversationState.COMPLETE)
    return {
        "state": self.state.value,
        "action": "display_results",
        "prompts": prompts,
    }
```

**Engine init pattern — from lines 45-49:**
```python
class ConversationEngine:
    """9态对话引擎（CONV-01）"""

    def __init__(self):
        self.state = ConversationState.IDLE
        self._classifier = IntentClassifier()
        self._follow_up: FollowUpEngine | None = None
        self._last_analysis: dict = {}
```

**Error handling pattern — from lines 51-56 (state transition guard):**
```python
def _transition(self, to_state: ConversationState):
    if to_state not in VALID_TRANSITIONS.get(self.state, set()):
        raise ConversationError(
            f"非法状态转换: {self.state.value} -> {to_state.value}"
        )
    self.state = to_state
```

**Import pattern — from lines 6-9:**
```python
from .intent_classifier import IntentClassifier
from .follow_up_engine import FollowUpEngine
from .session_manager import session_manager
from .context_builder import build_generation_context
```

---

### `prompt_tool/tests/test_generator_v2.py` (test, test) — UPGRADE

Strengthen test coverage with explicit assertions for 4 injection points, D-12 partial injection, and D-15 pain point driven filtering.

**Analog:** `tests/test_generator_v2.py` lines 1-96 (self-modify) + `tests/test_knowledge_pack.py` lines 1-241 (inline data pattern) + `tests/test_conversation_engine.py` lines 1-80 (class organization).

**Test class organization — from `tests/test_generator_v2.py` lines 8-24 and `tests/test_conversation_engine.py` lines 10-16:**
```python
class TestGeneratorV2:
    """v4.0 生成器测试"""

    ANALYSIS = {
        "industry_key": "internet_it",
        "industry_name": "互联网 / IT",
        "task_name": "PRD撰写",
        "original_input": "帮我写一个电商PRD",
    }
    CONTEXT = {
        "industry_id": "internet_it",
        "industry_name": "互联网 / IT",
        "task_type": "PRD撰写",
        "confirmed_info": {"tone": "专业", "role": "产品经理"},
        "conversation_summary": "[用户] 需要电商PRD\n[系统] 已确认行业和任务",
        "knowledge_pack_ref": None,
    }
```

**Factory function import/use pattern — from `tests/test_generator_v2.py` lines 5, 72-73:**
```python
from prompt_tool.generator_v2 import PromptGeneratorV2, generate_prompts_v2

# ... in test method
def test_factory_function(self):
    result = generate_prompts_v2(self.ANALYSIS, self.CONTEXT)
    assert "direct" in result
```

**New: import path (after `PromptGeneratorV2` is moved to `generator.py`):**
```python
from prompt_tool.generator import PromptGeneratorV2
```

**Inline data pattern for KnowledgePack tests — from `tests/test_knowledge_pack.py` lines 15-22:**
```python
def test_get_meta(self):
    """Test 1: get_meta() 返回完整的 meta dict"""
    data = {"meta": {"id": "test", "name": "测试行业", "icon": "🔬"}}
    pack = KnowledgePack(data)
    meta = pack.get_meta()
    assert isinstance(meta, dict)
    assert meta["id"] == "test"
    assert meta["name"] == "测试行业"
```

**New fixture-based test pattern — conftest.py will provide `fully_loaded_pack` fixture:**
```python
def test_role_depth_injection_uses_pack_data(fully_loaded_pack):
    """GEN-02: Role depth uses pack roles, not metadata"""
    # Arrange
    from prompt_tool.knowledge_pack import KnowledgePack
    pack = fully_loaded_pack
    
    # Use RealKnowledgeManager to create generator with real pack
    ...
```

---

### `prompt_tool/tests/conftest.py` (test, test) — MODIFY

Extend `sample_pack_json` fixture to include roles (with kpis/pain_points), pain_points, and docs (with sections). Add a `fully_loaded_pack` fixture.

**Analog:** `tests/conftest.py` lines 77-130 (`sample_pack_json` fixture) and lines 1-215 (entire file structure).

**Current `sample_pack_json` fixture — lines 77-130 — add `roles`, `docs`, `pain_points`:**
```python
@pytest.fixture
def sample_pack_json() -> dict:
    """返回一个最小但完整的知识包 dict，结构与 internet_it.json 一致"""
    return {
        "meta": { ... },  # unchanged
        "terms": [ ... ],  # unchanged
        "tasks": [ ... ],  # unchanged
        "roles": [],       # currently empty — EXTEND
        "workflows": [],
        "docs": [],        # currently empty — EXTEND
        "follow_up_trees": [],
        "pain_points": [], # currently empty — EXTEND
    }
```

**Extended fields needed — pattern from internet_it.json (confirmed in RESEARCH.md sources):**
```python
"roles": [
    {
        "name": "产品经理",
        "common_tasks": ["PRD撰写", "需求分析"],
        "kpis": [
            {"name": "PRD质量", "description": "需求文档完整度", "benchmark": "90%"},
            {"name": "迭代效率", "description": "版本交付周期", "benchmark": "2周"},
        ],
        "pain_points": ["需求频繁变更", "跨团队沟通成本高"],
    }
],
"docs": [
    {
        "name": "PRD模板",
        "task_type": "PRD撰写",
        "sections": [
            {"title": "背景", "prompt_hint": "项目背景和目标"},
            {"title": "目标", "prompt_hint": "业务目标和产品目标"},
            {"title": "范围", "prompt_hint": "功能范围划分"},
        ],
    }
],
"pain_points": [
    {
        "name": "需求不明确",
        "description": "用户说不清楚自己要什么",
        "what_not_to_do": "假设需求一旦确定就不再变更",
        "typical_phrases": ["需求不会变了", "就这些需求"],
    },
],
```

**New `fully_loaded_pack` fixture pattern — from `tests/conftest.py` lines 170-188 (`temp_compiled_dir`):**
```python
@pytest.fixture
def fully_loaded_pack():
    """返回一个包含 roles/docs/pain_points 的 KnowledgePack 实例"""
    from prompt_tool.knowledge_pack import KnowledgePack

    data = { ... }  # full sample_pack_json with roles + docs + pain_points
    return KnowledgePack(data)
```

---

### `prompt_tool/app.py` (controller, request-response) — MODIFY

Update `_do_generate_v4()` to call `ConversationEngine.generate_complete()` instead of directly importing `generate_prompts_v2`.

**Analog:** `prompt_tool/app.py` lines 284-318 (current `_do_generate_v4` method).

**Current `_do_generate_v4()` — lines 284-318 (simplified):**
```python
def _do_generate_v4(self, content):
    """v4.0 conversation flow: analyze -> auto-confirm -> generate directly."""
    try:
        engine = ConversationEngine()
        result = engine.start(content)

        if result.get("needs_clarification"):
            # v3.0 fallback
            manual = self.industry_combo.get()
            if manual == "自动识别": manual = None
            self.analysis_result = self.engine.analyze(content, manual)
            self.generated_prompts = generate_prompts(self.analysis_result)
            self.root.after(0, lambda: self._show_generate_result(engine, result))
            return

        # Auto-confirm -> skip follow-up -> generate with v4.0
        engine.handle_confirmation(True)
        self._engine = engine

        from .generator_v2 import generate_prompts_v2    # <-- REMOVE direct import
        from .context_builder import build_generation_context

        session = session_manager.get_active_session()
        context = build_generation_context(session) if session else {}
        self.analysis_result = self.engine.analyze(content, context.get("industry_name"))
        self.generated_prompts = generate_prompts_v2(self.analysis_result, context)  # <-- REPLACE
        engine.generate_complete()
        self.root.after(0, self._on_done)
    except Exception as e:
        self.root.after(0, lambda: self._on_error(str(e)))
```

**New pattern — encapsulate generation in `ConversationEngine.generate_complete()`:**
```python
def _do_generate_v4(self, content):
    try:
        engine = ConversationEngine()
        result = engine.start(content)

        if result.get("needs_clarification"):
            manual = self.industry_combo.get()
            if manual == "自动识别": manual = None
            self.analysis_result = self.engine.analyze(content, manual)
            self.generated_prompts = generate_prompts(self.analysis_result)
            self.root.after(0, lambda: self._show_generate_result(engine, result))
            return

        engine.handle_confirmation(True)
        self._engine = engine

        # generate_complete() now internally builds context + calls PromptGeneratorV2
        gen_result = engine.generate_complete()

        self.analysis_result = engine._last_analysis
        self.generated_prompts = gen_result.get("prompts", {})
        self.root.after(0, self._on_done)
    except Exception as e:
        self.root.after(0, lambda: self._on_error(str(e)))
```

**Import management — keep existing line 20:**
```python
from .conversation_engine import ConversationEngine, ConversationState
```
Remove unused `from .generator_v2 import generate_prompts_v2`.

**Thread pattern — from `app.py` line 281:**
```python
thread = threading.Thread(target=self._do_generate_v4, args=(content,), daemon=True)
thread.start()
```

**Error handling — from `app.py` lines 337-340:**
```python
def _on_error(self, msg):
    self.gen_btn.configure(state="normal", text="🎯  生成提示词")
    self.set_status(f"❌ 出错：{msg}")
    messagebox.showerror("错误", f"生成出错：\n{msg}")
```

---

## Shared Patterns

### KnowledgePack Loading Pattern
**Source:** `prompt_tool/knowledge_manager.py` lines 93-110 (`load_pack()`) + `prompt_tool/knowledge_pack.py` lines 10-107 (getter methods)
**Apply to:** `PromptGeneratorV2.__init__()` in `generator.py`

```python
from .knowledge_manager import knowledge_manager

# Load pack by industry_id - always safe (returns fallback pack on error)
self._pack = knowledge_manager.load_pack(industry_id)

# Use typed getters - never access raw dict
roles = self._pack.get_roles()               # list[dict], not self.pack_ref.get("roles", [])
doc = self._pack.get_doc_template(task_key)  # dict | None
pains = self._pack.get_pain_points()         # list[dict]
terms = self._pack.get_terms(category=...)   # list[dict]
```

### Singleton Import Pattern
**Source:** `prompt_tool/knowledge_manager.py` line 208 + `prompt_tool/session_manager.py` + `prompt_tool/conversation_engine.py` line 8
**Apply to:** `prompt_tool/generator.py` (import `knowledge_manager` at module level)

```python
# Module-level singleton import (established pattern)
from .knowledge_manager import knowledge_manager

# Used inside class method:
pack = knowledge_manager.load_pack(self.industry_id)
```

### Module-Level Factory Function Pattern
**Source:** `prompt_tool/generator.py` lines 272-273, `prompt_tool/generator_v2.py` lines 213-214
**Apply to:** New `PromptGeneratorV2` factory in `generator.py`

```python
# Keep backward-compatible factory (D-02: from .generator import PromptGenerator still works)
def generate_prompts(analysis_result: dict) -> dict:
    return PromptGenerator(analysis_result).generate_all()

# New factory for v4.0 flow
def generate_prompts_v2(analysis_result: dict, context: dict = None) -> dict:
    return PromptGeneratorV2(analysis_result, context).generate_all()
```

### ContextBuilder Output Shape Pattern
**Source:** `prompt_tool/context_builder.py` lines 54-61
**Apply to:** `PromptGeneratorV2.__init__()` — consuming dict with 6 fields

```python
context = {
    "industry_id": str | None,
    "industry_name": str,
    "task_type": str | None,
    "confirmed_info": dict[str, str],
    "conversation_summary": str,
    "knowledge_pack_ref": dict | None,  # DO NOT USE for pack data - metadata only!
}
# Correct: generator loads KnowledgePack itself via knowledge_manager
```

### Thread + Error Dispatch Pattern
**Source:** `prompt_tool/app.py` lines 281-318
**Apply to:** All async UI interactions in `app.py`

```python
# Launch background thread
thread = threading.Thread(target=self._do_generate_v4, args=(content,), daemon=True)
thread.start()

# Inside thread, dispatch UI updates to main thread
self.root.after(0, self._on_done)  # success
self.root.after(0, lambda: self._on_error(str(e)))  # error

# Error handler re-enables UI
def _on_error(self, msg):
    self.gen_btn.configure(state="normal", text="🎯  生成提示词")
    self.set_status(f"❌ 出错：{msg}")
    messagebox.showerror("错误", f"生成出错：\n{msg}")
```

### Test Fixture + Inline Data Pattern
**Source:** `tests/conftest.py` lines 77-130, `tests/test_knowledge_pack.py` lines 15-42
**Apply to:** `tests/conftest.py` fixture upgrade, `tests/test_generator_v2.py` test methods

```python
# conftest.py pattern: factory fixture returning complete dict
@pytest.fixture
def sample_pack_json() -> dict:
    return { "meta": {...}, "terms": [...], ... }

# test method pattern: inline data creation
def test_get_meta(self):
    data = {"meta": {"id": "test", ...}}
    pack = KnowledgePack(data)
    assert pack.get_meta()["id"] == "test"
```

### Strategy Return Shape Pattern
**Source:** `prompt_tool/generator.py` lines 19-24, `prompt_tool/generator_v2.py` lines 35-40, `prompt_tool/app.py` lines 362-365
**Apply to:** `PromptGeneratorV2.generate_all()` return value

```python
# Three strategies, preserved shape (D-02 compatibility):
{"direct": str, "roleplay": str, "detailed": str}

# UI consumes this:
prompt = self.generated_prompts.get(self.current_strategy, "")
```

### 4-Level Injection Order (D-06)
**Source:** RESEARCH.md lines 26-32 + `generator_v2.py` lines 79-87 (`_inject_all()`)
**Apply to:** `PromptGeneratorV2` strategy methods

```python
# Fixed order: role depth -> quality standards -> output structure -> anti-patterns
# Each has independent switch (D-11) based on task type + strategy depth
parts = [
    self._inject_role_depth(),       # 1: Role with KPI + pain points
    self._inject_quality_standards(), # 2: General + industry-specific quality
    self._inject_output_structure(),  # 3: Doc template sections
    self._inject_anti_patterns(),     # 4: Pain point warnings
]
```

## No Analog Found

All 5 files have exact analogs. No files require external patterns from RESEARCH.md.

## Metadata

**Analog search scope:** `prompt_tool/generator.py`, `prompt_tool/generator_v2.py`, `prompt_tool/conversation_engine.py`, `prompt_tool/context_builder.py`, `prompt_tool/knowledge_manager.py`, `prompt_tool/knowledge_pack.py`, `prompt_tool/app.py`, `tests/test_generator_v2.py`, `tests/test_qa_evaluation.py`, `tests/conftest.py`, `tests/test_knowledge_pack.py`, `tests/test_conversation_engine.py`
**Files scanned:** 12 source files, all fully read
**Pattern extraction date:** 2026-06-04
