# Phase 5: Generation v2 — Research

**Researched:** 2026-06-04
**Domain:** Intent-driven prompt composition — knowledge pack integrated generation
**Confidence:** HIGH (verified against codebase, existing tests, and architecture decisions)

## Summary

Phase 5 replaces v3.0's template-filling `PromptGenerator` with a knowledge-pack-driven `PromptGeneratorV2` that composes prompts from conversation context + knowledge pack data. The existing `generator_v2.py` is a draft prototype with two critical bugs that must be fixed: (1) it references knowledge pack data fields (roles, pain_points) from `knowledge_pack_ref` which context_builder only populates with metadata (pack.get_meta()), and (2) its anti-pattern filter uses hardcoded regex instead of knowledge pack pain points as required by D-15. The planner should treat the existing file as a structural starting point requiring significant rework, not a complete implementation.

**Primary recommendation:** Fix the data flow so `PromptGeneratorV2` loads the `KnowledgePack` directly via `knowledge_manager.load_pack()` rather than relying on the metadata-only `knowledge_pack_ref` from context_builder, and reimplement anti-pattern filtering using knowledge pack pain point `what_not_to_do` values.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### 模块架构
- **D-01:** 重构现有 `generator.py`，不新建独立模块。保持文件结构简洁。
- **D-02:** 新类命名为 `PromptGeneratorV2`，旧类 `PromptGenerator` 保留为向后兼容别名。
- **D-03:** v4 调用路径封装在 `ConversationEngine.generate_complete()` 内部。`app.py` 无感知，不关心使用哪个生成器。
- **D-04:** `ConversationEngine.generate_complete()` 直接调用 `PromptGeneratorV2`，不引入中间服务层。
- **D-05:** v3 流程保留不动，v4 流程通过 `ConversationEngine` 编排，两者通过 `is_v4_flow` 标志分流。

#### 4 级知识注入结构
- **D-06:** 四个注入点按固定顺序组织：角色深度 → 质量标准 → 输出结构 → 反模式警告。
- **D-07:** 角色深度按任务匹配专业角色，从知识包 `get_roles()` 和场景描述中提取。
- **D-08:** 质量标准采用通用+行业混合策略，从知识包场景和流程中提取。
- **D-09:** 输出结构使用知识包文档规范中的锁定格式模板，从 `get_doc_template()` 提取。
- **D-10:** 反模式警告基于知识包痛点清单 `get_pain_points()` 生成。
- **D-11:** 四个注入点是否全部出现由任务类型决定，每个注入点有独立开关。

#### 知识选择策略
- **D-12:** 每次生成包含"任务相关核心知识 + 行业背景简要概述"，不全量注入知识包。
- **D-13:** 术语呈现方式：当前任务场景涉及的全部术语（8-15 个），每个词附带简短定义。
- **D-14:** 注入与当前任务角色相关的 KPI 和痛点。

#### 反模式过滤规则
- **D-15:** 反模式检测基于知识包痛点清单驱动。
- **D-16:** 过滤两类内容：虚假权威用语 + 行业刻板印象。
- **D-17:** 检测到反模式后自动替换违规内容再展示最终版。
- **D-18:** 过滤规则以痛点清单为主，关键词匹配为辅。

### Claude's Discretion
- 三种策略（直给式/角色式/完整式）在 v2 中的具体差异化方案
- 生成长度控制策略
- 核心流程（workflow）是否注入
- PromptGeneratorV2 的 `generate_all()` 返回值格式
- 反模式替换的具体策略（替换为知识包中的正确描述 vs 仅删除）
- `is_v4_flow` 标志在 `app.py` 中的具体判断逻辑

### Deferred Ideas (OUT OF SCOPE)
- 3 种策略的 v2 差异化方案的具体设计
- 生成长度控制的平衡策略
- JMESPath 查询接口
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GEN-01 | 意图驱动合成器 — 基于对话上下文+知识包组合提示词，替代模板填充 | Data flow redesign: generator loads KnowledgePack directly + consumes conversation context from ContextBuilder |
| GEN-02 | 4 级知识注入 — 角色深度、质量标准、输出结构、反模式警告 | Each injection point maps to a KnowledgePack getter method; task-type-dependent switches control which appear |
| GEN-03 | 3 种策略升级 — 更新直给式/角色式/完整式三种生成策略 | Each strategy uses a different subset of injection points; strategy differentiation detailed below |
| GEN-04 | 反模式过滤 — 自动检测并移除虚假权威表述和刻板信息 | Pain point driven + keyword supplement; applied post-generation for all strategies |
| QA-02 | 提示词质量评估 — 对比 v3.0 模板 vs v4.0 知识包生成 | Existing test_qa_evaluation.py provides baseline; needs knowledge pack data fixture upgrade |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Knowledge pack loading | KnowledgeManager (data layer) | — | Generator delegates pack loading to existing single-instance manager |
| Conversation context assembly | ContextBuilder (data layer) | ConversationEngine (orchestration) | `build_generation_context()` assembles industry/task/summary dict |
| Prompt composition logic | PromptGeneratorV2 (generation layer) | — | Pure Python string composition; no I/O, no state mutation |
| Anti-pattern filtering | PromptGeneratorV2 (generation layer) | — | Post-generation step; consumes pain points from loaded pack |
| Strategy selection | PromptGeneratorV2 (generation layer) | — | Internal dispatch; three strategies share same knowledge data |
| Generation orchestration | ConversationEngine (orchestration layer) | — | D-03: `generate_complete()` calls generator, app.py unaware |

## Standard Stack

### Core
| Library/Tool | Version | Purpose | Why Standard |
|-------------|---------|---------|--------------|
| Python stdlib | 3.12+ | All composition logic | Zero external dependencies; offline constraint |
| `re` (stdlib) | — | Anti-pattern regex matching | Lightweight pattern detection for type 2 patterns |
| `json` (stdlib) | — | No JSON parsing needed | Knowledge pack already loaded as Python dict |

### Supporting
| Component | Version | Purpose | When to Use |
|-----------|---------|---------|-------------|
| KnowledgeManager | existing | Load knowledge pack data | On PromptGeneratorV2 init, load relevant pack |
| KnowledgePack | existing | Typed getter methods | Query roles, pain_points, doc_templates, terms |
| ContextBuilder | existing | Build generation context | Before generator init, assemble context dict |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Direct dict access on KnowledgePack | JMESPath queries | JMESPath deferred; dict access is sufficient for this phase's simple queries |
| string.Template/stdlib formatting | Jinja2 templates | Jinja2 adds external dependency; offline constraint prevents net dependencies |
| In-generator pack loading | Passing pack via context_builder | Simpler data flow; generator owns its data source, doesn't depend on context_builder passing correct ref |

**Installation:**
```
No new packages. All dependencies are stdlib + existing project code.
```

**Version verification:** No new package dependencies for this phase. All components are existing project code or Python stdlib.

## Package Legitimacy Audit

> No external packages are installed by this phase. Generation v2 uses only Python stdlib (`re`, `json`, `random`) and existing project modules (`KnowledgePack`, `KnowledgeManager`, `ContextBuilder`). No registry verification needed.

## Architecture Patterns

### System Architecture Diagram

```
User Input
     |
     v
ConversationEngine (orchestrator)
     |
     |-- start() --> IntentClassifier --> Confirm --> FollowUpEngine (3 questions max)
     |
     |-- generate_complete() -->
     |                              SessionState (with turns, confirmed industry/task)
     |                                   |
     |                                   v
     |                              ContextBuilder.build_generation_context()
     |                                   | returns dict with:
     |                                   |   industry_id, industry_name, task_type,
     |                                   |   confirmed_info, conversation_summary
     |                                   |
     |                                   v
     |                              PromptGeneratorV2.__init__(analysis_result, context dict)
     |                                   |
     |                                   |-- knowledge_manager.load_pack(industry_id)
     |                                   |       -> KnowledgePack (roles, pain_points, doc_templates, terms)
     |                                   |
     |                                   |-- Select task-relevant data (D-12):
     |                                   |      get_role(task_type), get_doc_template(task_type),
     |                                   |      get_pain_points(), filter_terms(task_context)
     |                                   |
     |                                   v
     |                              PromptGeneratorV2.generate_all()
     |                                   |
     |                                   |-- _direct():   task + requirements + 1 injection point
     |                                   |-- _roleplay(): role depth + quality standards + 2 injection points
     |                                   |-- _detailed(): all 4 injection points + full structure
     |                                   |       |
     |                                   |       v (each strategy output)
     |                                   |-- _filter(): anti-pattern scan + replace
     |                                   |
     |                                   v
     |                              {"direct": str, "roleplay": str, "detailed": str}
     |
     v
App._on_done() -> display prompt, enable copy/export
```

### Recommended Project Structure (minimal change to existing)

```
prompt_tool/
├── generator.py           # PromptGenerator (v3.0) + PromptGeneratorV2 (v4.0) [D-01]
└── ...                    # No new files
```

### Strategy Differentiation Pattern

This is a Claude Discretion area. Recommendation based on research:

**Direct:** "_direct()_"
- Knowledge injection: 1 point only (quality standards, minimal)
- No role preamble, no conversation context section
- Structure: task line -> requirements (bullets) -> quality hint (1-2 lines)
- Length target: ~100-200 chars beyond task description

**Roleplay:** "_roleplay()_"
- Knowledge injection: 2 points (role depth + quality standards)
- Role preamble from KnowledgePack.get_role(task_type) with KPI
- No output structure section, no anti-patterns
- Structure: role preamble -> task line -> role depth section -> requirements -> format hint
- Length target: ~300-500 chars

**Detailed:** "_detailed()_"
- Knowledge injection: all 4 points (role depth + quality standards + output structure + anti-patterns)
- Full role preamble with KPIs + responsibilities
- Conversation context section (from context.summary)
- Output structure from doc template sections
- Anti-pattern warnings at the end
- Structure: role preamble -> background -> conversation context -> task -> all 4 injections -> requirements -> output format -> warnings
- Length target: ~500-800 chars

### Knowledge Selection Pattern (D-12, D-13, D-14)

```python
# Pseudocode pattern for task-relevant knowledge selection

def _select_task_knowledge(self, pack: KnowledgePack, task_key: str) -> dict:
    """Select task-relevant slice of knowledge pack (D-12)."""
    task = pack.get_task(task_key)
    doc_template = pack.get_doc_template(task_key)
    roles = pack.get_roles()
    pain_points = pack.get_pain_points()

    # Filter terms: 8-15 terms related to this task (D-13)
    all_terms = pack.get_terms()
    task_terms = [t for t in all_terms
                  if t.get("category", "") in task.get("related_categories", [])
                  or t["term"] in task.get("keywords", [])][:15]

    # Select role matching this task (D-07)
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

### Anti-pattern Filter Pattern (GEN-04, D-15 to D-18)

```
Generated prompt text
     |
     v
Scan for known pain point patterns (D-15):
  - For each pain_point in pack.get_pain_points():
    - Check if prompt contradicts pain_point["what_not_to_do"]
    - Use pain_point["typical_phrases"] as keyword triggers (D-18)
     |
     v
Scan for authority/stereotype patterns (D-16):
  - Type 1: False authority claims
    - keywords: "行业领先", "最佳实践", "国际标准" (without context)
    - Regex anchor: standalone modifiers not tied to specific evidence
  - Type 2: Industry stereotypes
    - keywords: "一如既往", "众所周知", "唯一标准"
    - Regex anchor: absolute assertions without qualification
     |
     v
Replace or remove violations (D-17):
  - Type 1: Replace authority claim with evidence-based alternative from pack
  - Type 2: Remove stereotype, leave rest of sentence intact
     |
     v
Return filtered text (user sees only filtered version)
```

### Injection Point to KnowledgePack Method Mapping

| Injection Point | KnowledgePack Method | ContextBuilder Field | Switch Condition |
|----------------|---------------------|---------------------|------------------|
| Role depth (1) | `get_role(task_type)`, `get_roles()` | confirmed_info["role"] | Task has associated role |
| Quality standards (2) | workflow failure_modes[], doc_template.common_mistakes[] | — | Always (minimal) |
| Output structure (3) | `get_doc_template(task_type).sections[]` | — | Task has doc template |
| Anti-pattern warning (4) | `get_pain_points()[].what_not_to_do` | — | Pain points exist |

### Anti-Patterns to Avoid

- **Passing meta dict as knowledge data:** The existing context_builder returns `knowledge_pack_ref` as `pack.get_meta()` (a dict with id/name/icon/version), but generator_v2.py treats it as if it contains roles and pain_points. These fields don't exist in meta. **Fix:** Generator loads the pack itself.
- **Hardcoded anti-pattern regex:** Current generator_v2.py has a fixed `ANTI_PATTERNS` list. D-15 requires pain point-driven filtering. The hardcoded patterns should supplement the pain point data, not replace it.
- **All 4 injection points in all strategies:** D-11 says injection points have independent switches per task type. Strategies should also vary their injection depth.
- **Direct import bypassing ConversationEngine:** D-03 says generation call is inside `generate_complete()`. Current app.py directly calls `generate_prompts_v2()`, which needs to be moved.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Knowledge pack data access | Custom query logic | KnowledgePack.getter methods | Already exists and tested (Phase 2); 8 typed getters |
| Context assembly | Custom dict assembly | ContextBuilder.build_generation_context() | Already exists (Phase 3); returns all 6 required fields |
| Conversation state tracking | Custom session data structures | SessionManager + SessionState | Already exists (Phase 3); thread-safe with snapshot |
| Generation orchestration | App-level generation flow control | ConversationEngine.generate_complete() | D-03 mandates this; encapsulation keeps app.py simple |

**Key insight:** Every data source PromptGeneratorV2 needs is already available through existing infrastructure. The only gap is the data flow — context_builder passes metadata instead of pack data, and the generator needs to bridge that itself.

## Common Pitfalls

### Pitfall 1: Empty metadata from context_builder
**What goes wrong:** `PromptGeneratorV2._inject_role_depth()` accesses `self.pack_ref.get("roles", [])` which returns `[]` because `knowledge_pack_ref` from `context_builder.py` is `pack.get_meta()` — a dict with only `{id, name, icon, description, version, schema_version}` — no roles, no pain_points, no terms.
**Why it happens:** Phase 3 design decided to "store ID, not snapshot" (D-03 in Phase 3 context), but no downstream code updated the generator to load the pack itself.
**How to avoid:** Have `PromptGeneratorV2` load the pack via `knowledge_manager.load_pack(self.ctx.get("industry_id"))` in its `__init__`. This is a one-line fix.
**Warning signs:** All injection sections return empty strings even with valid knowledge packs loaded.

### Pitfall 2: Regex-only anti-pattern filtering
**What goes wrong:** Anti-pattern filtering uses a static regex list instead of knowledge pack pain points. This misses industry-specific false claims, violates D-15, and fails QA-02's stereotype check for non-IT industries.
**Why it happens:** The draft prototype used regex as a quick placeholder, but the design requires pain point-driven filtering.
**How to avoid:** Implement a two-layer filter — primary: pain point `what_not_to_do` mapping; secondary: regex for general authority claims.
**Warning signs:** Anti-pattern filter never changes behavior between industries; pain points exist in packs but are ignored.

### Pitfall 3: Over-injection in direct strategy
**What goes wrong:** The "direct" strategy becomes as long as "detailed" because all 4 injection points are included, defeating the purpose of having a concise option.
**Why it happens:** Without explicit injection switches per strategy, developers add all knowledge content to all strategies.
**How to avoid:** Define injection profiles per strategy (see Strategy Differentiation Pattern above) and enforce them.
**Warning signs:** All three strategies produce nearly identical output length.

### Pitfall 4: generate_complete() bypass
**What goes wrong:** `app.py` continues to directly import `generate_prompts_v2` and call it, bypassing `ConversationEngine.generate_complete()`, violating D-03.
**Why it happens:** The existing `_do_generate_v4` in app.py was written before the decision to encapsulate generation in the ConversationEngine.
**How to avoid:** Move the `generate_prompts_v2` call inside `ConversationEngine.generate_complete()`. Change app.py to call `conversation_engine.generate_complete()` which returns the generation result.
**Warning signs:** `app.py` has any import of `generate_prompts_v2` after the migration.

### Pitfall 5: Not handling missing pack gracefully
**What goes wrong:** When KnowledgeManager falls back to v3.0 mode (fallback_active = True), `load_pack()` returns a pack with no roles, pain_points, or doc_templates. All injection sections return empty.
**Why it happens:** The fallback pack has minimal data (terms and tasks only).
**How to avoid:** When no roles/pain_points are available, gracefully fall back to the v3.0 generator's approach (simple role strings from INDUSTRIES mapping). Don't produce a prompt with empty sections.

## Code Examples

### PromptGeneratorV2 Data Flow Fix

```python
# Source: Research finding — fix for data flow bug in existing draft
class PromptGeneratorV2:
    def __init__(self, analysis_result: dict, generation_context: dict = None):
        self.r = analysis_result
        self.ctx = generation_context or {}
        self.industry_id = self.ctx.get("industry_id") or analysis_result.get("industry_key")
        self.industry_name = self.ctx.get("industry_name") or analysis_result.get("industry_name", "通用")
        self.summary = self.ctx.get("conversation_summary", "")
        self.confirmed = self.ctx.get("confirmed_info", {})

        # Load knowledge pack — THIS IS THE KEY FIX
        self._pack = None
        if self.industry_id:
            try:
                from .knowledge_manager import knowledge_manager
                self._pack = knowledge_manager.load_pack(self.industry_id)
            except Exception:
                self._pack = None

        # Select task-relevant knowledge (cached, shared across 3 strategies)
        self._task_knowledge = self._select_task_knowledge()
```

### Anti-pattern filter using knowledge pack pain points

```python
# Source: Research recommendation — pain point driven filtering (D-15)
def _build_anti_pattern_rules(self) -> list:
    """Build filter rules from knowledge pack pain points + hardcoded supplements."""
    rules = []

    # Primary: pain point driven (D-15, D-18)
    if self._pack:
        for pp in self._pack.get_pain_points():
            what_not_to = pp.get("what_not_to_do", "")
            if what_not_to:
                # Extract actionable verb from what_not_to_do
                # e.g., "假设需求一旦确定就不再变更" -> pattern to detect "需求不会变了"
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
        {"type": "stereotype", "pattern": r"所有.*?(?:企业|公司|产品).*?都[必须|应该|需要]", "replacement": ""},
    ])
    return rules

def _filter(self, text: str) -> str:
    """GEN-04: Pain point driven + regex supplement."""
    for rule in self._build_anti_pattern_rules():
        if rule["type"] == "pain_point":
            for phrase in rule.get("trigger_phrases", []):
                if phrase in text:
                    # Replace the problematic phrasing
                    text = text.replace(phrase, f"[注意：避免{rule['description']}]")
        else:
            pattern = rule["pattern"]
            replacement = rule.get("replacement", "")
            text = re.sub(pattern, replacement, text)
    return text.strip()
```

### Role depth injection with KnowledgePack.get_role()

```python
# Source: KnowledgePack.get_role() API + research recommendation
def _inject_role_depth(self) -> str:
    """Inject 1: Role depth with KPI + pain points (D-07, D-14)."""
    knowledge = self._task_knowledge
    role = knowledge.get("role")
    if not role:
        return ""

    kpis = role.get("kpis", [])[:3]
    pains = role.get("pain_points", [])[:2]

    lines = [f"你是一位{role['name']}。"]
    if kpis:
        kpi_texts = [f"  - {k['name']}: {k['description']} (基准: {k.get('benchmark', '')})" for k in kpis]
        lines.append("\n你的考核KPI：")
        lines.extend(kpi_texts)
    if pains:
        lines.append(f"\n常见痛点：{'、'.join(pains)}")

    return "\n".join(lines)
```

### Output structure injection with doc template

```python
# Source: KnowledgePack.get_doc_template() API
def _inject_output_structure(self) -> str:
    """Inject 3: Output structure from doc template (D-09)."""
    if not self._task_knowledge.get("doc_template"):
        return ""

    doc = self._task_knowledge["doc_template"]
    sections = doc.get("sections", [])
    if not sections:
        return ""

    lines = ["## 输出结构"]
    for s in sections:
        lines.append(f"- {s['title']}：{s.get('prompt_hint', '')}")
    return "\n".join(lines)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| keyword-to-template mapping (v3.0) | intent-driven composition from knowledge pack (v4.0) | Phase 5 | Prompts include industry role depth, KPIs, and pain points instead of generic templates |
| Hardcoded ANTI_PATTERNS regex list | Knowledge pack pain point + regex hybrid | Phase 5 | Industry-specific anti-pattern detection; different industries get different warnings |
| 3 strategies with identical structure | 3 strategies with differentiated injection depth | Phase 5 | Direct stays concise, detailed gets full knowledge injection |
| Generation logic in app.py | Generation encapsulated in ConversationEngine.generate_complete() | Phase 5 | app.py doesn't import generator directly; cleaner architecture |
| ContextBuilder passes metadata only | PromptGeneratorV2 loads KnowledgePack itself | Phase 5 | Fixes data availability bug; generator owns its data source |

**Deprecated/outdated:**
- `APP_ANTI_PATTERNS` module-level constant in draft generator_v2.py: Replace with knowledge-pack-driven rules.
- Direct import of `generate_prompts_v2` in app.py: Replace with `ConversationEngine.generate_complete()` call.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `knowledge_manager.load_pack(industry_id)` returns a valid `KnowledgePack` with all getter methods | Data flow | Generator would get empty pack; injection sections silently empty |
| A2 | KnowledgePack roles have `kpis` and `pain_points` fields with the observed structure | Injection pattern | internet_it.json confirms this structure; other industry packs may vary |
| A3 | `get_doc_template(task_type)` returns a dict with `sections` list | Injection pattern | Present in internet_it.json; confirmed in KNOW-01 schema |
| A4 | pain_point entries have `what_not_to_do`, `typical_phrases`, `name` fields | Anti-pattern filter | Verified in internet_it.json pain_points section |

## Open Questions

1. **How should `generate_complete()` return results to app.py?**
   - What we know: D-03 says app.py uses ConversationEngine.generate_complete() which calls PromptGeneratorV2.
   - What's unclear: Should generate_complete() return `{"direct": str, ...}` directly, or wrap it in a structured response dict? The existing `generate_complete()` in conversation_engine.py returns `{"state": "complete", "action": "display_results"}` with no generation data.
   - Recommendation: Return `{"state": "complete", "action": "display_results", "prompts": {"direct": str, "roleplay": str, "detailed": str}}`. This keeps the existing action-based response pattern and adds the prompts payload.

2. **Injection point switches per task type — how to determine which apply?**
   - What we know: D-11 says each injection point has an independent switch determined by task type.
   - What's unclear: Is the switch logic based on task metadata (e.g., `complexity`, `typical_output` fields from KnowledgePack.get_task()) or hardcoded mapping?
   - Recommendation: **Use task complexity as the switch heuristic.** `low` complexity tasks get 2 injection points (quality + anti-patterns), `medium` get 3 (+ role depth), `high` get all 4. This avoids hardcoded task-injection mappings while being data-driven.

3. **What does ConversationEngine.generate_complete() do with the result?**
   - What we know: D-03 says it encapsulates generation, app.py is unaware of the generator.
   - What's unclear: Does generate_complete() store the result internally for app.py to fetch, or return it directly from the method call?
   - Recommendation: Return directly. The existing `_do_generate_v4` pattern (analyze -> confirm -> generate -> display) suggests a synchronous call chain.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12+ | All code | Yes | 3.12.10 | — |
| pytest | Tests | Yes | 9.0.3 | — |
| KnowledgeManager | Data loading | Yes (existing) | — | v3.0 knowledge.py fallback |

**Missing dependencies with no fallback:** None. All dependencies are existing project code or Python stdlib.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 |
| Config file | None detected (default pytest discovery) |
| Quick run command | `python -m pytest tests/test_generator_v2.py -x -q` |
| Full suite command | `python -m pytest tests/ -x -q` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| GEN-01 | Generates 3 strategies from context+knowledge | unit | `test_generator_v2.py::TestGeneratorV2::test_generates_three_strategies` | Yes |
| GEN-01 | Empty context produces valid output | unit | `test_generator_v2.py::TestGeneratorV2::test_empty_context_works` | Yes |
| GEN-02 | Roleplay strategy includes KPI/pain points | unit | `test_generator_v2.py::TestGeneratorV2::test_context_injection` | Yes (weak check) |
| GEN-02 | Detailed strategy has structural sections | unit | `test_qa_evaluation.py::TestQA02Comparison::test_v4_detailed_has_structure_sections` | Yes |
| GEN-03 | All 3 strategies are distinct and non-empty | unit | `test_generator_v2.py::TestGeneratorV2::test_generates_three_strategies` | Yes |
| GEN-03 | Each strategy has different structure | unit | `test_qa_evaluation.py::TestQA02Comparison::test_v4_direct_has_more_content_than_v3` | Yes (weak) |
| GEN-04 | Anti-pattern filter removes authority claims | unit | `test_generator_v2.py::TestAntiPatternFilter::test_filters_authority_claim` | Yes |
| GEN-04 | Anti-pattern filter removes absolute statements | unit | `test_generator_v2.py::TestAntiPatternFilter::test_filters_absolute_statements` | Yes |
| GEN-04 | Normal content not affected | unit | `test_generator_v2.py::TestAntiPatternFilter::test_preserves_normal_content` | Yes |
| GEN-04 | No stereotypes in any strategy output | unit | `test_qa_evaluation.py::TestQA02Comparison::test_v4_no_stereotypes` | Yes |
| QA-02 | v4 output more substantial than v3 | integration | `test_qa_evaluation.py::TestQA02Comparison::test_v4_direct_has_more_content_than_v3` | Yes |
| QA-02 | v4 preserves industry context | integration | `test_qa_evaluation.py::TestQA02Comparison::test_v4_preserves_industry_context` | Yes |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_generator_v2.py -x -q`
- **Per wave merge:** `python -m pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_generator_v2.py` — Tests need upgrade to cover:
  - **GEN-02 verification:** Explicit assertions for role depth paragraph, quality standards paragraph, output structure paragraph, anti-pattern paragraph in detailed strategy output
  - **D-12 verification:** Assert that output doesn't contain all knowledge pack terms (partial injection only)
  - **D-15 verification:** Assert filter rules loaded from knowledge pack pain points, not just hardcoded regex
  - **Knowledge pack fixture:** `conftest.py` needs a fixture providing a real KnowledgePack (not just metadata) so generator_v2 tests can test with actual pack data
- [ ] `tests/conftest.py` — Add fixture that provides a real `KnowledgePack` instance (from sample_pack_json) so `PromptGeneratorV2` tests can create a properly initialized generator that loads pack data
- [ ] Framework check — pytest discovery works; no additional config needed

## Security Domain

> `security_enforcement` is enabled (absent from config means enabled; explicitly check config.json shows `"security_enforcement": true`).

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | No (minimal) | Generated text is displayed to user; no execution context |
| V8 Data Protection | No | All data is local in-memory Python dicts |

### Known Threat Patterns for Generation Layer

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Generated content contains executable instructions | Information disclosure | Not applicable — output is plain text intended for LLM prompt use, no execution context in app |
| Injection of special characters breaking clipboard/export | Tampering | Only plain .txt export and clipboard copy; no rendering context |

**Risk assessment:** This phase has no new security risks. Prompt text generation is pure string composition with no I/O beyond reading already-in-memory knowledge packs. Output goes to clipboard or .txt file — no SQL, HTML, or shell context.

## Sources

### Primary (HIGH confidence)
- [Codebase: `prompt_tool/generator.py`] — Existing v3.0 generator; confirms `generate_prompts()` factory + `generate_all()` return pattern
- [Codebase: `prompt_tool/generator_v2.py`] — Existing v4.0 draft prototype; confirms structure, reveals data flow bug with pack_ref
- [Codebase: `prompt_tool/conversation_engine.py`] — ConversationEngine.generate_complete() signature and state management
- [Codebase: `prompt_tool/context_builder.py`] — Confirms knowledge_pack_ref returns pack.get_meta(), not pack data
- [Codebase: `prompt_tool/knowledge_pack.py`] — All 8 getter method signatures confirmed
- [Codebase: `prompt_tool/knowledge_manager.py`] — load_pack(), get_index() method signatures confirmed
- [Codebase: `prompt_tool/knowledge_packs_compiled/internet_it.json`] — Pain point structure with what_not_to_do, typical_phrases fields confirmed
- [Codebase: `prompt_tool/app.py`] — _do_generate_v4 pattern; confirms direct import of generate_prompts_v2 (contradicts D-03)
- [Codebase: `tests/test_generator_v2.py`] — Existing test coverage; confirms areas needing upgrade
- [Codebase: `tests/test_qa_evaluation.py`] — QA-02 test baselines
- [Codebase: `.planning/config.json`] — Confirms `nyquist_validation: true`, `security_enforcement: true`

### Secondary (MEDIUM confidence)
- [CONTEXT.md D-01 to D-18] — All implementation decisions verified against codebase architecture

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — Zero new packages; all existing code or stdlib
- Architecture: HIGH — Verified by reading all relevant source files; data flow bug found and documented with fix
- Pitfalls: HIGH — P1 (empty pack_ref) confirmed by reading context_builder.py + generator_v2.py side by side; P2 (regex-only) confirmed by examining current ANTI_PATTERNS constant

**Research date:** 2026-06-04
**Valid until:** Stable (code-only phase; no external dependency changes expected)
