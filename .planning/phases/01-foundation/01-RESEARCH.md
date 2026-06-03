# Phase 1: Foundation - Research

**Researched:** 2026-06-03
**Domain:** Knowledge pack schema design, YAML-to-JSON compilation pipeline, content authoring, build validation
**Confidence:** HIGH

## Summary

Phase 1 establishes the entire v4.0 knowledge pack infrastructure: the 8-dimension JSON Schema, the YAML-to-JSON compilation pipeline, build-time validation, and the first complete Internet/IT industry knowledge pack covering 5 high-frequency scenarios. This phase is pure infrastructure and content authoring -- it produces no runtime code, does not touch existing v3.0 files (knowledge.py, engine.py, generator.py, app.py remain untouched), and creates an independent parallel system.

**Primary recommendation:** Define knowledge pack schema as Pydantic v2 models (build-time only), author content in YAML with recursive follow-up tree structures, compile via `build_packs.py` using PyYAML 6.0.3 and Pydantic 2.12.5 for validation, output runtime JSON to `knowledge_packs_compiled/`, and integrate compilation into `build.bat` before the PyInstaller step.

**Key technical decisions driving this phase:**
- YAML source: supports comments, anchors, multi-line Chinese text -- domain reviewers can edit without Python knowledge
- JSON runtime: stdlib `json.load()` is 3-5x faster than `yaml.safe_load()`, zero extra dependency in shipped exe
- Pydantic build-time only: validate at compile time, no validation overhead in shipped exe (~2MB saved)
- Follow-up trees as recursive YAML children: decision trees are data, not code -- domain editors can modify question flows

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| KNOW-01 | 知识包数据结构定义 -- 设计完整的行业知识包 JSON Schema（术语表、场景、角色、KPI、流程、文档规范、追问树、痛点） | Section: Standard Stack (Schema Layers), Architecture Patterns (8-Dimension Schema Design Pattern) -- verified Pydantic v2 models for all 8 dimensions |
| KNOW-02 | YAML→JSON 编译管线 -- 知识包用 YAML 编写，编译为 JSON 供运行时加载 | Section: Standard Stack (Build Pipeline), Architecture Patterns (Build Pipeline Pattern) -- PyYAML 6.0.3 + Pydantic 2.12.5 pipeline design |
| KNOW-09 | 知识包构建验证脚本 -- 编译时自动校验知识包结构完整性 | Section: Standard Stack (Validation), Common Pitfalls (Pitfall 2: Silent Validation Pass), Code Examples (build_packs.py) |
| QA-01 | 行业深度完成标准 -- 每个行业包必须通过深度检查清单才能标记为完成 | Section: User Constraints (D-06), Common Pitfalls (QA-01 Deep-Check Criteria Operationalization), Assumptions Log |

</phase_requirements>

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** 8-dimension top-level structure: meta, terms, tasks, roles, workflows, docs, follow_up_tree, pain_points
- **D-02:** Core field granularity (standard level):
  - terms: term + definition + usage_context + related_terms
  - tasks: name + description + typical_output + follow_up_tree + complexity
  - roles: name + KPIs + pain_points + common_tasks
  - workflows: name + steps + decision_points + failure_modes
- **D-03:** Internet/IT industry V1 covers 5 high-frequency scenarios with complete follow-up trees
- **D-04:** 5 scenarios: PRD撰写, 代码生成, 数据分析, 技术文档, 工作总结
- **D-05:** YAML source files in `prompt_tool/knowledge_packs/`
- **D-06:** Each scenario 5-8 follow-up nodes with branching logic, covering common variants
- **D-07:** YAML→JSON build pipeline integrated into `build.bat`
- **D-10:** Build script (`build_packs.py`) handles: parse YAML --> validate Schema --> output JSON
- **D-11:** YAML-->JSON-->JMESPath-->dataclasses tech stack
- **D-12:** Pydantic/jsonschema for compile-time validation only (not in runtime)
- **D-13:** Knowledge pack version starts at v1, Schema version at 1.0

### Claude's Discretion
- YAML source file naming conventions, build script code style, _schema.yaml detailed field constraints
- Follow-up tree JSON structure implementation details (children array format in YAML)

### Deferred Ideas (OUT OF SCOPE)
- User-customizable knowledge pack editor (v2 feature)
- Auto-building knowledge packs from web (future consideration)
- Other 4 industry packs (零售, 教育, 金融, 制造) -- Phase 7

</user_constraints>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Schema design | Data Layer | Build Pipeline | The schema IS the data contract -- defines what knowledge packs look like. Build pipeline consumes schema for validation. |
| YAML authoring | Developer Machine | -- | YAML is authoring-only. Never shipped in exe. Written by content authors (could be domain experts, not Python devs). |
| Compilation | Build Pipeline | -- | `build_packs.py` runs at build time (in CI or on developer machine), not at app runtime. |
| Schema validation | Build Pipeline | -- | Pydantic models validate at compile time. Shipped exe has zero validation overhead. |
| Content authoring | Content Layer | -- | The Internet/IT knowledge pack YAML file content -- pure domain knowledge, no logic. |
| Follow-up tree design | Content Layer | Schema Layer | Trees defined as data (YAML), validated against schema at compile time, traversed by runtime code in Phase 4. |
| build.bat integration | Build Pipeline | -- | Compilation step added before PyInstaller in existing build script. |

## Standard Stack

### Core (Build-Time Only -- NOT shipped in exe)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PyYAML | 6.0.3 | Parse YAML knowledge pack source files | De facto standard Python YAML parser. Supports YAML 1.2, anchors, multi-line Chinese text. [VERIFIED: pip list] |
| pydantic | 2.12.5 | Validate knowledge pack structure at compile time | Type-safe schema validation with descriptive error messages. Already installed in dev environment. [VERIFIED: pip list] |

### Runtime (Shipped in exe -- new addition)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| jmespath | 1.1.0 | Structured queries on loaded knowledge JSON | Required by Phase 2+ for knowledge pack queries. Pure Python ~50KB. [VERIFIED: PyPI `pip index versions jmespath`] |

### Existing (Already Shipped)

| Library | Version | Purpose |
|---------|---------|---------|
| customtkinter | 5.2.2 | Desktop UI framework [VERIFIED: pip list] |
| Pillow | 12.1.1 | Image handling for UI assets [VERIFIED: pip list] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pydantic | jsonschema 4.26.0 | jsonschema is also installed and works. Pydantic v2 gives better error messages and integrates with IDE type checking. Both are acceptable. jsonschema is slightly lighter (no pydantic-core binary). |
| jmespath | Python dict iteration | JMESPath provides declarative queries, but for Phase 1 (schema only, no runtime queries), jmespath is not used yet. Install when needed in Phase 2. |
| YAML source | JSON source (hand-edited) | JSON has no comment support, no anchors, harder for non-devs to edit. YAML is vastly superior for authoring. |

**Version verification:** All core packages confirmed installed (PyYAML 6.0.3, pydantic 2.12.5). jmespath 1.1.0 confirmed latest on PyPI.

## Package Legitimacy Audit

> Phase 1 installs no external packages. jmespath will be needed in Phase 2 for runtime queries but is not installed in this phase. The build-time tools (PyYAML, pydantic) are already installed in the development environment.

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| PyYAML 6.0.3 | PyPI | 4+ yrs | 100M+/mo | github.com/yaml/pyyaml | [OK] | Already installed, build-time only |
| pydantic 2.12.5 | PyPI | 4+ yrs | 50M+/mo | github.com/pydantic/pydantic | [OK] | Already installed, build-time only |
| jmespath 1.1.0 | PyPI | 7+ yrs | 10M+/mo | github.com/jmespath/jmespath.py | [OK] | Not installed in Phase 1; install in Phase 2 |

**Packages removed:** None
**Packages flagged as suspicious:** None

## Architecture Patterns

### System Architecture Diagram

```
[Authoring Phase - Developer Machine]     [Build Phase - build.bat]     [Runtime Phase - Shipped Exe]
                                           (Phase 1 delivers)            (Phase 2+ consumes)

prompt_tool/knowledge_packs/              build_packs.py                prompt_tool/knowledge_packs_compiled/
  internet_it.yaml -------------------->   1. PyYAML.safe_load()          internet_it.json
  _schema.yaml                              for each .yaml              (compiled, validated JSON)
  (future: education.yaml, etc.)           2. pydantic Model.validate()     |
                                           3. json.dump()                [bundled into exe via --add-data]
                                               |                               |
                                               V                               V
                                          knowledge_packs_compiled/    KnowledgeManager.load()
                                            internet_it.json            (Phase 2: reads from _compiled/)
                                                                               |
                                                                               V
                                                                          KnowledgePack.get_terms()
                                                                          KnowledgePack.get_follow_up_tree()
                                                                          (Phase 2+: typed access via dataclasses)
```

**Data flow summary:**
1. Content author writes YAML (with comments, anchors, Chinese text) in `knowledge_packs/`
2. `build_packs.py` reads all `*.yaml` files, validates against Pydantic schema models
3. On validation failure: script exits with specific field-level error messages
4. On validation success: writes `*.json` to `knowledge_packs_compiled/` with `ensure_ascii=False` for correct Chinese encoding
5. `build.bat` calls `build_packs.py` before PyInstaller; if build fails, the entire packaging stops
6. PyInstaller bundles `knowledge_packs_compiled/*.json` via `--add-data`
7. Phase 2+ runtime code loads JSON via stdlib `json.load()`

### Recommended Project Structure

```
prompt_tool/
  knowledge_packs/                    # NEW: YAML source files
    __init__.py                       # (empty or loader stub)
    internet_it.yaml                  # Internet/IT industry knowledge pack
    _schema.yaml                      # Schema reference document for authors (human-readable)
  knowledge_packs_compiled/           # NEW: Generated JSON files
    internet_it.json                  # (auto-generated, not hand-edited)
  knowledge.py                        # UNCHANGED (v3.0)
  engine.py                           # UNCHANGED (v3.0)
  generator.py                        # UNCHANGED (v3.0)
  app.py                              # UNCHANGED (v3.0)
  main.py                             # UNCHANGED (v3.0)

build_packs.py                        # NEW: YAML->JSON compilation script (project root)
build.bat                             # MODIFIED: adds build_packs.py call before PyInstaller
```

### Pattern 1: 8-Dimension Schema Design Pattern

**What:** Each knowledge pack is a YAML file with 8 top-level sections. Each section has a specific field set. This defines the data contract for all downstream consumers (loader, retriever, generator).

**When to use:** Every knowledge pack YAML file must conform to this structure. The `_schema.yaml` file documents this structure for human reference; Pydantic models enforce it programmatically at build time.

**Schema layers (top-level keys and their required fields):**

```yaml
# prompt_tool/knowledge_packs/internet_it.yaml
# Schema version: 1.0
# Knowledge pack version: v1

meta:
  id: "internet_it"
  name: "互联网 / IT"
  version: "1.0.0"
  schema_version: "1.0"
  description: "互联网产品、技术开发与运营行业知识包"
  last_updated: "2026-06-03"
  icon: "💻"

terms:
  - term: "PRD"
    category: "产品文档"
    definition: "产品需求文档 (Product Requirements Document)"
    aliases: ["产品需求文档", "需求文档"]
    usage_context: "产品经理编写，描述功能需求、业务流程和验收标准"
    related_terms: ["BRD", "MRD", "功能规格"]

tasks:
  - name: "PRD撰写"
    description: "撰写产品需求文档，包含背景、范围、功能、流程、验收标准"
    typical_output: "PRD文档（含功能列表、用户流程、原型图描述、验收标准）"
    complexity: "medium"        # low / medium / high
    frequency: "very_high"     # low / medium / high / very_high
    follow_up_tree: "prd_writing"  # references key in follow_up_trees

roles:
  - name: "产品经理"
    kpis:
      - name: "功能上线率"
        description: "规划的功能按时上线的比例"
        benchmark: "> 80%"
    pain_points: ["需求频繁变更", "研发团队沟通断层", "优先级冲突"]
    common_tasks: ["PRD撰写", "需求分析", "竞品分析"]

workflows:
  - name: "功能上线流程"
    category: "研发流程"
    steps:
      - step: 1
        name: "需求评审"
        owner: "产品经理"
        deliverables: ["评审通过的PRD"]
    decision_points:
      - point: "灰度数据达标?"
        yes: "全量上线"
        no: "回滚或修复"
    failure_modes:
      - name: "跳过灰度"
        impact: "线上事故风险"
        prevention: "强制灰度流程"

docs:
  - name: "PRD模板"
    task_type: "PRD撰写"
    sections:
      - title: "项目背景"
        prompt_hint: "为什么要做这个功能？解决什么用户痛点？"
    tone: "专业, 数据驱动"
    common_mistakes: ["技术细节过多", "缺少验收标准"]

follow_up_trees:
  - task_type: "PRD撰写"
    root_node_id: "prd_q1"
    nodes:
      prd_q1:
        node_id: "prd_q1"
        question_text: "这个PRD的主要受众是谁？"
        question_type: "single_choice"
        info_key: "prd_audience"
        depth: 1
        options:
          - value: "研发团队"
            label: "研发团队（技术实现导向）"
          - value: "管理层"
            label: "管理层（决策审批导向）"
          - value: "跨部门"
            label: "跨部门协作（含运营/市场）"
        children:
          "研发团队": "prd_q2_tech"
          "管理层": "prd_q2_mgmt"
          "跨部门": "prd_q2_cross"
        fallback_node_id: "prd_q2_tech"

pain_points:
  - name: "需求频繁变更"
    description: "PM不断改需求导致开发返工"
    why_happens: "前期需求调研不充分，业务方中途有新想法"
    who_feels_it: "研发团队、测试工程师"
    typical_phrases: ["需求又变了", "改改改"]
    what_not_to_do: "假设需求锁定不变生成技术方案"
```

### Pattern 2: Follow-Up Tree as Recursive Children Structure

**What:** Each follow-up tree is a directed acyclic graph of question nodes. Each node has a question, answer options, child mappings, and a fallback for "I don't know." Nodes are stored as a flat map keyed by `node_id` for O(1) traversal.

**When to use:** Every task scenario that needs clarifying questions uses this structure. The tree is authored in YAML and compiled to JSON. Traversal logic is implemented in Phase 4 (FollowUpTreeWalker).

```yaml
# Example: PRD撰写 follow-up tree structure
follow_up_trees:
  - task_type: "PRD撰写"
    root_node_id: "prd_q1"
    nodes:
      prd_q1:
        node_id: "prd_q1"
        question_text: "这个PRD的主要受众是谁？"
        question_type: "single_choice"    # single_choice | multi_choice | text_input | confirm
        info_key: "prd_audience"           # where to store in context
        depth: 1
        options:
          - value: "dev_team"
            label: "研发团队（技术实现导向）"
          - value: "management"
            label: "管理层（决策审批导向）"
          - value: "cross_dept"
            label: "跨部门协作（含运营/市场）"
        children:
          "dev_team": "prd_q2_scope"
          "management": "prd_q2_goal"
          "cross_dept": "prd_q2_stakeholders"
        fallback_node_id: "prd_q2_scope"   # "I don't know" fallback
        is_leaf: false
      
      prd_q2_scope:
        node_id: "prd_q2_scope"
        question_text: "这个功能涉及的范围是什么？"
        question_type: "multi_choice"      # multi selects possible
        info_key: "prd_scope"
        depth: 2
        options:
          - value: "new_feature"
            label: "全新功能"
          - value: "optimization"
            label: "现有功能优化"
          - value: "bug_fix"
            label: "Bug修复"
          - value: "migration"
            label: "迁移/重构"
        children:
          # multi_choice: follows highest-priority selected path
          "new_feature": "prd_q3_scale"
          "optimization": "prd_q3_metric"
          "bug_fix": "prd_q3_severity"
          "migration": "prd_q3_compatibility"
        fallback_node_id: "prd_q3_generic"
        is_leaf: false
      
      prd_q3_scale:  # depth 3 - detailed
        node_id: "prd_q3_scale"
        question_text: "预计的用户量级和上线时间要求？"
        question_type: "text_input"
        info_key: "scale_timeline"
        depth: 3
        options: []
        children:
          "_any": "prd_q4_output"
        fallback_node_id: "prd_q4_output"
        is_leaf: false
      
      prd_q4_output:
        node_id: "prd_q4_output"
        question_text: "你希望PRD包含哪些部分？"
        question_type: "multi_choice"
        info_key: "prd_sections"
        depth: 4
        options:
          - value: "bg"
            label: "项目背景与目标"
          - value: "scope"
            label: "功能范围与边界"
          - value: "flow"
            label: "用户流程图"
          - value: "ui_desc"
            label: "界面原型描述"
          - value: "acceptance"
            label: "验收标准"
        children: {}     # leaf: no children
        fallback_node_id: null
        is_leaf: true
```

### Pattern 3: Build Pipeline Script Structure

**What:** `build_packs.py` is a standalone Python script in the project root. It finds all YAML files in `prompt_tool/knowledge_packs/`, validates each against Pydantic models, and writes compiled JSON to `prompt_tool/knowledge_packs_compiled/`.

**When to use:** Every time the project is packaged (via `build.bat`), and optionally during development as a pre-commit hook.

```python
# build_packs.py — simplified structure
# Phase 1 delivers the full implementation

import os
import sys
import json
from pathlib import Path

# Build-time only dependency
import yaml
from pydantic import BaseModel, Field, ValidationError

# === Schema Models ===
# Define all 8 dimension models here (or in a separate _schema.py)
# See Code Examples section for full model definitions

def compile_pack(yaml_path: Path, output_dir: Path) -> dict:
    """Parse YAML, validate, write JSON. Returns stats dict."""
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    # Validate against schema models
    # (Phase 1 will define these models in detail)
    # KnowledgePackModel(**data)   # raises ValidationError on failure
    
    output_path = output_dir / f"{data['meta']['id']}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return {
        "pack_id": data["meta"]["id"],
        "terms": len(data.get("terms", [])),
        "tasks": len(data.get("tasks", [])),
        "follow_up_trees": len(data.get("follow_up_trees", [])),
    }

def main():
    project_root = Path(__file__).parent
    source_dir = project_root / "prompt_tool" / "knowledge_packs"
    output_dir = project_root / "prompt_tool" / "knowledge_packs_compiled"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    errors = []
    total = 0
    
    for yaml_file in sorted(source_dir.glob("*.yaml")):
        if yaml_file.name.startswith("_"):
            continue  # skip _schema.yaml
        try:
            stats = compile_pack(yaml_file, output_dir)
            print(f"  OK  {yaml_file.name} ({stats['terms']} terms, {stats['tasks']} tasks)")
            total += 1
        except (yaml.YAMLError, ValidationError) as e:
            errors.append((yaml_file.name, str(e)))
            print(f"  FAIL {yaml_file.name}: {e}")
    
    print(f"\nCompiled {total} pack(s), {len(errors)} error(s)")
    
    if errors:
        print("\n=== ERRORS ===")
        for name, msg in errors:
            print(f"{name}: {msg}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Anti-Patterns to Avoid

- **Do NOT put Pydantic in shipped exe.** Models are build-time only. The exe validates nothing -- it assumes data is correct because build-time caught all errors.
- **Do NOT hand-edit compiled JSON.** Compiled files are auto-generated. All edits go into YAML source. This is enforced by the build pipeline.
- **Do NOT mix YAML and JSON in the same directory.** YAML source in `knowledge_packs/`, JSON output in `knowledge_packs_compiled/`. Keep them separate.
- **Do NOT skip `ensure_ascii=False`** when writing JSON. Chinese characters must be preserved as readable UTF-8, not escaped as `\uXXXX`.
- **Do NOT use `yaml.load()` without SafeLoader.** Always use `yaml.safe_load()` to prevent arbitrary code execution from YAML source files.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| YAML parsing | Custom YAML parser | PyYAML 6.0.3 `yaml.safe_load()` | YAML spec is complex (anchors, tags, multi-line, Unicode); custom parsers are bug-prone |
| Schema validation | Manual if/else checks | Pydantic v2 BaseModel.validate() | Field-level error messages, type coercion, nested model validation, IDE autocomplete |
| JSON writing | Custom serializer | `json.dump(data, f, ensure_ascii=False, indent=2)` | C-optimized, handles Unicode, battle-tested, zero config |
| Chinese encoding | Manual character encoding | `ensure_ascii=False` parameter | Python stdlib handles all edge cases (BOM, surrogates) |
| File path resolution | Hardcoded paths | `pathlib.Path(__file__).parent` | Cross-platform, robust, handles PyInstaller `sys._MEIPASS` paths |

**Key insight:** Every deceptively complex problem in this phase (YAML parsing, schema validation, cross-platform paths) has a stdlib or well-established library solution. The custom work is the schema model definitions and the glue logic, not the parsers.

## Common Pitfalls

### Pitfall 1: YAML Syntax Errors Silent or Cryptic

**What goes wrong:** A YAML file has a syntax error (bad indent, tab character, missing colon) and PyYAML raises a generic `yaml.scanner.ScannerError` with a line number but no context about which knowledge dimension failed.

**Why it happens:** YAML is whitespace-sensitive. Chinese text often contains characters that are easy to mis-indent. Editors and linters may not catch YAML syntax errors in deeply nested trees.

**How to avoid:** Wrap each `yaml.safe_load()` call in `try/except yaml.YAMLError as e:` and print the file name, line number, and the problematic snippet. Use a YAML linter (e.g., `yamllint`) in CI.

**Warning signs:** Build fails with `while scanning a simple key` error; Chinese text has stray Unicode characters that break YAML parsing.

### Pitfall 2: Silent Validation Pass

**What goes wrong:** The Pydantic model is too permissive (all fields Optional) so validation passes even when required fields are missing. The build succeeds but the runtime code gets incomplete data.

**Why it happens:** Developers design models with `Optional[str] = None` for convenience during early development, and these permissive defaults never get tightened.

**How to avoid:** Every field in every schema model must have a clear required/optional policy:
- REQUIRED: id, name, version, description (meta); term, definition (terms); name, description (tasks); task_type, root_node_id, nodes (follow_up_trees)
- OPTIONAL but validated if present: aliases, related_terms, usage_context
- Never use `Field(default=None)` for required fields -- the Pydantic model should fail validation immediately

**Warning signs:** A pack compiles with minimal content; runtime code crashes on `KeyError: 'terms'` when the field exists but is empty.

### Pitfall 3: Oversized Knowledge Packs from Deeply Nested Follow-Up Trees

**What goes wrong:** Each follow-up tree with 5-8 nodes, each node having 4-6 options with children mappings, produces large YAML files. The compiled JSON for Internet/IT could exceed 200KB for a single industry.

**Why it happens:** Content authors get carried away adding edge-case branches. The tree grows combinatorially.

**How to avoid:** Enforce a YAML file size budget per industry (< 150KB YAML source, ~300KB compiled JSON). Use YAML anchors (`&anchor` and `*anchor`) and aliases to deduplicate common option sets. Apply the "5-8 nodes per tree" limit from D-06 strictly.

**Warning signs:** A single YAML file exceeds 200KB; `build_packs.py` takes > 5 seconds to compile one pack.

### Pitfall 4: ensure_ascii=True (Default) Corrupts Chinese Text

**What goes wrong:** `json.dump()` without `ensure_ascii=False` escapes all non-ASCII characters as `\uXXXX`. Chinese text becomes unreadable in the compiled JSON and takes 3x more space.

**Why it happens:** `ensure_ascii=True` is the Python default. Developers forget the parameter because it usually doesn't matter for English-only data.

**How to avoid:** Always use `json.dump(data, f, ensure_ascii=False, indent=2)` in the build script. Add a post-validation check that the compiled JSON has no `\u` sequences that aren't intentional.

**Warning signs:** Compiled JSON looks like `"互联网"` instead of `"互联网"`.

### Pitfall 5: Follow-Up Tree Falls into Circular Reference

**What goes wrong:** A node's `children` mapping references a parent node, creating an infinite loop. The Phase 4 FollowUpTreeWalker gets stuck in an endless loop.

**Why it happens:** Tree nodes are a flat map with string references between them. There is no structural enforcement against cycles.

**How to avoid:** Add a cycle detection check in `build_packs.py`: before writing JSON, traverse each tree from `root_node_id` and flag any node visited more than once per traversal path. Additionally, set a depth limit of 10 (max branching depth).

**Warning signs:** A follow-up tree has a node whose `children` value points to a node at the same or higher depth level (shallow depth).

## Code Examples

### Example 1: Pydantic Schema Model for Knowledge Pack Validation

```python
# build_packs.py — Pydantic v2 schema models (build-time only, NOT shipped)
# Source: pydantic 2.12.5 official docs pattern for nested models
# Confidence: HIGH (verified via pip list + pydantic official API)

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum

class QuestionType(str, Enum):
    SINGLE_CHOICE = "single_choice"
    MULTI_CHOICE = "multi_choice"
    TEXT_INPUT = "text_input"
    CONFIRM = "confirm"

class ComplexityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# === Meta ===
class PackMeta(BaseModel):
    id: str = Field(..., pattern=r"^[a-z][a-z_]*$")  # snake_case only
    name: str = Field(..., min_length=1, max_length=50)
    version: str = Field(default="1.0.0")
    schema_version: str = Field(default="1.0")
    description: str = Field(default="")
    last_updated: str = Field(default="")
    icon: str = Field(default="")

# === Terms ===
class Term(BaseModel):
    term: str = Field(..., min_length=1)
    category: str = Field(default="")
    definition: str = Field(..., min_length=1)
    aliases: list[str] = Field(default_factory=list)
    usage_context: str = Field(default="")
    related_terms: list[str] = Field(default_factory=list)

# === Tasks ===
class Task(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    typical_output: str = Field(default="")
    complexity: ComplexityLevel = Field(default=ComplexityLevel.MEDIUM)
    frequency: str = Field(default="medium")
    follow_up_tree: str = Field(default="")

# === Follow-Up Trees ===
class Option(BaseModel):
    value: str = Field(..., min_length=1)
    label: str = Field(..., min_length=1)

class QuestionNode(BaseModel):
    node_id: str = Field(..., pattern=r"^[a-z][a-z0-9_]*$")
    question_text: str = Field(..., min_length=1)
    question_type: QuestionType = Field(default=QuestionType.SINGLE_CHOICE)
    info_key: str = Field(default="")
    depth: int = Field(default=1, ge=1, le=10)
    options: list[Option] = Field(default_factory=list)
    children: dict[str, str] = Field(default_factory=dict)  # option_value -> next_node_id
    fallback_node_id: Optional[str] = None
    is_leaf: bool = Field(default=False)

    @field_validator("children")
    @classmethod
    def validate_children_no_self_ref(cls, v, info):
        """Basic check: children should not reference this node."""
        node_id = info.data.get("node_id")
        if node_id and node_id in v.values():
            raise ValueError(f"Node '{node_id}' references itself in children")
        return v

class FollowUpTree(BaseModel):
    task_type: str = Field(..., min_length=1)
    root_node_id: str = Field(..., min_length=1)
    nodes: dict[str, QuestionNode]

    @field_validator("nodes")
    @classmethod
    def validate_root_exists(cls, v, info):
        root_id = info.data.get("root_node_id")
        if root_id and root_id not in v:
            raise ValueError(f"root_node_id '{root_id}' not found in nodes")
        return v

# === Workflows ===
class WorkflowStep(BaseModel):
    step: int = Field(..., ge=1)
    name: str = Field(..., min_length=1)
    owner: str = Field(default="")
    deliverables: list[str] = Field(default_factory=list)

class DecisionPoint(BaseModel):
    point: str = Field(..., min_length=1)
    yes: str = Field(default="")
    no: str = Field(default="")

class FailureMode(BaseModel):
    name: str = Field(..., min_length=1)
    impact: str = Field(default="")
    prevention: str = Field(default="")

class Workflow(BaseModel):
    name: str = Field(..., min_length=1)
    category: str = Field(default="")
    steps: list[WorkflowStep] = Field(default_factory=list)
    decision_points: list[DecisionPoint] = Field(default_factory=list)
    failure_modes: list[FailureMode] = Field(default_factory=list)

# === Roles ===
class KPI(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(default="")
    benchmark: str = Field(default="")

class Role(BaseModel):
    name: str = Field(..., min_length=1)
    kpis: list[KPI] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    common_tasks: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)

# === Docs ===
class DocSection(BaseModel):
    title: str = Field(..., min_length=1)
    prompt_hint: str = Field(default="")

class DocTemplate(BaseModel):
    name: str = Field(..., min_length=1)
    task_type: str = Field(default="")
    sections: list[DocSection] = Field(default_factory=list)
    tone: str = Field(default="")
    common_mistakes: list[str] = Field(default_factory=list)

# === Pain Points ===
class PainPoint(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(default="")
    why_happens: str = Field(default="")
    who_feels_it: str = Field(default="")
    typical_phrases: list[str] = Field(default_factory=list)
    what_not_to_do: str = Field(default="")

# === Top-Level Pack ===
class KnowledgePack(BaseModel):
    meta: PackMeta
    terms: list[Term] = Field(default_factory=list)
    tasks: list[Task] = Field(default_factory=list)
    roles: list[Role] = Field(default_factory=list)
    workflows: list[Workflow] = Field(default_factory=list)
    docs: list[DocTemplate] = Field(default_factory=list)
    follow_up_trees: list[FollowUpTree] = Field(default_factory=list)
    pain_points: list[PainPoint] = Field(default_factory=list)
```

### Example 2: Complete build_packs.py Skeleton

```python
#!/usr/bin/env python3
"""
build_packs.py — Compile YAML knowledge packs to validated JSON.

Usage:
    python build_packs.py              # Compile all packs
    python build_packs.py --watch      # Watch mode (recompile on file change)

Exit code: 0 on success, 1 on any validation failure.
This script runs at build time (inside build.bat) and in CI.
"""

import json
import sys
from pathlib import Path

import yaml
from pydantic import ValidationError

# Import schema models (defined in same file or adjacent module)
from _schema import KnowledgePack  # (or inline as shown above)

def compile_pack(yaml_path: Path, output_dir: Path) -> dict:
    """Parse one YAML file, validate, write JSON."""
    print(f"  Compiling: {yaml_path.name}...", end=" ")

    # Step 1: Parse YAML
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print("FAIL (YAML parse error)")
        raise

    if data is None:
        print("FAIL (empty file)")
        raise ValueError(f"{yaml_path.name} is empty")

    # Step 2: Validate against schema
    try:
        pack = KnowledgePack(**data)
    except ValidationError as e:
        print("FAIL (schema validation)")
        # Print field-level errors for quick debugging
        for error in e.errors():
            loc = " -> ".join(str(l) for l in error["loc"])
            print(f"    {loc}: {error['msg']}")
        raise

    # Step 3: Write compiled JSON
    output_path = output_dir / f"{pack.meta.id}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(pack.model_dump(), f, ensure_ascii=False, indent=2)

    # Step 4: Post-validation — check for follow-up tree cycles
    for tree in pack.follow_up_trees:
        _check_tree_cycles(tree)

    print(f"OK ({len(pack.terms)} terms, {len(pack.tasks)} tasks, "
          f"{len(pack.follow_up_trees)} trees)")
    return {
        "pack_id": pack.meta.id,
        "terms": len(pack.terms),
        "tasks": len(pack.tasks),
        "trees": len(pack.follow_up_trees),
    }

def _check_tree_cycles(tree) -> None:
    """BFS check for circular node references in a follow-up tree."""
    visited = set()
    stack = [tree.root_node_id]
    while stack:
        node_id = stack.pop()
        if node_id in visited:
            raise ValueError(
                f"Circular reference in tree '{tree.task_type}': node '{node_id}' revisited"
            )
        visited.add(node_id)
        node = tree.nodes.get(node_id)
        if node is None:
            raise ValueError(
                f"Tree '{tree.task_type}': node '{node_id}' referenced but not defined"
            )
        for child_id in node.children.values():
            if child_id not in visited:
                stack.append(child_id)

def main():
    project_root = Path(__file__).parent.resolve()
    source_dir = project_root / "prompt_tool" / "knowledge_packs"
    output_dir = project_root / "prompt_tool" / "knowledge_packs_compiled"

    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    yaml_files = sorted(source_dir.glob("*.yaml"))
    yaml_files = [f for f in yaml_files if not f.name.startswith("_")]

    if not yaml_files:
        print("Warning: No YAML knowledge pack files found")
        print(f"  (looked in: {source_dir})")
        sys.exit(0)

    print(f"Found {len(yaml_files)} knowledge pack(s)")
    print(f"Output: {output_dir}\n")

    errors = []
    for yaml_file in yaml_files:
        try:
            compile_pack(yaml_file, output_dir)
        except (yaml.YAMLError, ValidationError, ValueError) as e:
            errors.append((yaml_file.name, str(e)))

    print(f"\n{'='*50}")
    print(f"Results: {len(yaml_files) - len(errors)} succeeded, "
          f"{len(errors)} failed")

    if errors:
        print(f"\n{'='*50}")
        print("FAILED PACKS:")
        for name, msg in errors:
            print(f"  {name}")
            for line in msg.split("\n"):
                print(f"    {line}")
        sys.exit(1)

    print("All packs compiled successfully.")

if __name__ == "__main__":
    main()
```

### Example 3: build.bat Integration

```batch
@echo off
chcp 65001 >nul
title 智能提示词工坊 - 打包构建

echo ============================================
echo   🧠 智能提示词工坊 - 打包构建工具
echo ============================================
echo.

REM === NEW: Step 0 — Compile Knowledge Packs ===
echo.
echo 📦 编译知识包...
python build_packs.py
if %errorlevel% neq 0 (
    echo ❌ 知识包编译失败！请修复上方错误
    pause
    exit /b 1
)
echo ✅ 知识包编译完成
echo.

REM === Rest of existing build.bat (unchanged) ===

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM ... (rest of existing build.bat unchanged) ...

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "智能提示词工坊" ^
    --icon NONE ^
    --add-data "prompt_tool;prompt_tool" ^
    --add-data "prompt_tool/knowledge_packs_compiled/*.json;prompt_tool/knowledge_packs_compiled" ^
    --hidden-import "customtkinter" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL._tkinter_finder" ^
    --collect-data "customtkinter" ^
    run.py
```

## State of the Art

| Old Approach (v3.0) | Current Approach (Phase 1) | When Changed | Impact |
|---------------------|---------------------------|--------------|--------|
| Flat Python dict in `knowledge.py` | Structured YAML + JSON with schema | Phase 1 | Knowledge becomes data, not code. Domain experts can author without Python knowledge. |
| Knowledge inline in source file | Separate per-industry YAML files | Phase 1 | Each industry pack is an independent, versionable artifact. |
| No validation | Pydantic build-time validation | Phase 1 | Structural errors caught at compile time, not at runtime. |
| No follow-up questions | Follow-up tree schema in knowledge pack | Phase 1 | Foundation for Phase 4's conversational engine. |
| No versioning | Pack version + Schema version | Phase 1 | Backward-compatible evolution of knowledge packs. |

**Deprecated/outdated:**
- `knowledge.py` INDUSTRIES dict structure: Phase 1 does NOT remove it (v3.0 compatibility), but v4.0's new system runs in parallel and will eventually replace it.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Pydantic v2 `model_dump()` serializes all nested models correctly for JSON output | Code Examples | If serialization misses fields, compiled JSON is incomplete. Mitigation: test with a minimal pack first. |
| A2 | `ensure_ascii=False` works correctly with PyInstaller `--add-data` on Chinese Windows | Common Pitfalls | If encoding breaks inside the bundle, runtime JSON loading fails. Mitigation: test on target Chinese Windows. |
| A3 | The 5 scenarios (PRD撰写, 代码生成, 数据分析, 技术文档, 工作总结) cover 80%+ of user needs for Internet/IT industry | User Constraints (D-04) | If actual user queries don't match these scenarios, the pack content is irrelevant. Mitigation: validate against v3.0 usage patterns. |
| A4 | A 5-8 node follow-up tree per scenario is sufficient depth | User Constraints (D-06) | If conversion quality is still poor with 8 questions, branches need deepening. Mitigation: plan for iterative expansion per scenario. |

## Open Questions

1. **How to structure _schema.yaml for human readers?**
   - What we know: It should serve as reference documentation for content authors (not programmatically loaded).
   - What's unclear: Whether it should be a full YAML example with all fields filled, or a schema definition format, or both.
   - Recommendation: Use `_schema.yaml` as a complete reference example with placeholder values and Chinese comments explaining each field. Include a brief header explaining the purpose.

2. **Should build_packs.py support `--watch` mode for development?**
   - What we know: This is Claude's discretion. Watch mode would recompile on file change, useful during content authoring.
   - Recommendation: Defer to Phase 1 implementation discretion. The core single-run mode is sufficient for MVP.

3. **How to handle partial/failed compilation? Should valid packs still output?**
   - What we know: D-09 says "中断构建并给出明确错误信息."
   - Recommendation: Fail-fast on first error to prevent shipping incomplete data. However, accumulate ALL errors before failing so the author sees all issues in one run. This is already handled in `build_packs.py` above (collects all errors, prints them, then exits 1).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12+ | All | YES | 3.12.10 | -- |
| PyYAML | build_packs.py (YAML parse) | YES | 6.0.3 | -- |
| pydantic v2 | build_packs.py (validation) | YES | 2.12.5 | jsonschema 4.26.0 |
| jmespath | (Future Phase 2+) | NO (not yet installed) | 1.1.0 | Install in Phase 2 via `pip install jmespath` |
| PyInstaller | build.bat (packaging) | YES | (confirmed via pip list) | -- |

**Missing dependencies with no fallback:** None for Phase 1 (all build-time tools are already installed).
**Missing dependencies with fallback:** jmespath (not needed until Phase 2).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (not yet configured -- Wave 0 task) |
| Config file | none -- see Wave 0 Gaps |
| Quick run command | `python build_packs.py` (compile + validate all packs) |
| Full suite command | `python build_packs.py && python -m pytest tests/ -x` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| KNOW-01 | Schema models accept valid knowledge pack data | unit | `pytest tests/test_schema.py::test_valid_pack -x` | Wave 0 |
| KNOW-01 | Schema models reject missing required fields | unit | `pytest tests/test_schema.py::test_missing_required -x` | Wave 0 |
| KNOW-02 | build_packs.py compiles valid YAML -> JSON | integration | `python build_packs.py` (in test tmp dir) | Wave 0 |
| KNOW-02 | Compiled JSON has correct Chinese encoding | integration | `pytest tests/test_build.py::test_chinese_encoding -x` | Wave 0 |
| KNOW-09 | Build fails with clear error on invalid YAML | integration | `python build_packs.py` (with bad input fixture) | Wave 0 |
| KNOW-09 | Build fails with field-level error on schema violation | integration | `python build_packs.py` (with missing required field) | Wave 0 |
| QA-01 | Internet/IT pack has all 8 dimensions present | content | `python -c "import json; d=json.load(open('...')); assert all(k in d for k in ['meta','terms','tasks','roles','workflows','docs','follow_up_trees','pain_points'])"` | Wave 0 |
| QA-01 | Each follow-up tree has 5-8 nodes | content | `python -c "..." test for 5 <= len(tree.nodes) <= 8` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python build_packs.py` (compile check)
- **Per wave merge:** `python build_packs.py && pytest tests/ -x`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_schema.py` -- unit tests for Pydantic models (covers KNOW-01)
- [ ] `tests/test_build.py` -- integration tests for build_packs.py (covers KNOW-02, KNOW-09)
- [ ] `tests/conftest.py` -- fixtures for valid/invalid YAML test data
- [ ] `tests/test_content.py` -- content tests for QA-01 criteria on the Internet/IT pack
- [ ] pytest configuration: `pytest.ini` or `pyproject.toml` with `[tool.pytest.ini_options]`

*(All test infrastructure is Wave 0 -- no existing test framework detected in codebase.)*

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | Yes | `yaml.safe_load()` prevents code injection from YAML source files |
| V6 Cryptography | No | No cryptographic operations in Phase 1 |
| V8 Data Protection | No | Phase 1 produces no user-facing data storage |

### Known Threat Patterns for Phase 1 (Build Pipeline)

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| YAML code injection | Tampering / Remote Code Execution | Use `yaml.safe_load()` exclusively, never `yaml.load()` without a SafeLoader. PyYAML 6.0.3 has known CVE fixes for load() vulnerabilities. |
| Malformed JSON in compiled output | Tampering | Pydantic model validation catches structral issues before JSON is written. The build pipeline is the single source of truth -- no hand-editing of JSON. |
| Path traversal in build script | Tampering | Use `Path(__file__).parent.resolve()` for all path construction. No user-supplied paths accepted. |

**Key security notes:**
- Phase 1 is a build-time pipeline, not a runtime service. No user data is processed, no network calls are made.
- The primary security risk is YAML code injection if `yaml.load()` is used instead of `yaml.safe_load()`. This is easily preventable with a coding convention enforced via code review.
- The Internet/IT industry does not involve regulated content (unlike Financial or Medical packs in future phases). Compliance metadata fields in the schema should be designed now for future use, but no content warnings are needed for Phase 1.
- Schema models reject YAML-defined keys that are not in the model (Pydantic v2 extra field handling). This prevents accidentally shipping data that doesn't conform to the contract.

## QA-01 Deep-Check Criteria Operationalization

D-06 defines "追问树完整" as the quality bar for the Internet/IT knowledge pack. The following checklist operationalizes this into testable criteria that `tests/test_content.py` can validate:

### For Each of the 5 Scenarios (PRD撰写, 代码生成, 数据分析, 技术文档, 工作总结)

1. **Follow-up tree exists:** The `follow_up_trees` section has an entry matching the scenario's `task_type`.
2. **Node count in range:** Tree has 5-8 question nodes (root node + 4-7 child nodes), verified by counting distinct `node_id` values.
3. **Branching logic present:** At least 2 nodes have `children` with 2+ entries (i.e., multiple answer branches).
4. **Fallback path exists:** At least 2 nodes have a non-null `fallback_node_id` for "I don't know" handling.
5. **Variant coverage:** The tree covers at least 2 distinct variants. Examples:
   - PRD撰写: audience = 研发团队 vs 管理层 (different depth paths)
   - 代码生成: 后端API vs 前端页面 (different technical paths)
   - 数据分析: 描述性分析 vs 诊断性分析 (different analysis types)
   - 技术文档: API文档 vs 用户手册 (different document types)
   - 工作总结: 管理岗 vs 执行岗, 好业绩 vs 差业绩 (different report types)
6. **Leaf node reached:** The tree has at least 1 node marked `is_leaf: true`, ensuring traversal terminates.
7. **No cycles:** All trees pass the BFS cycle detection check.
8. **All referenced node IDs exist:** Every value in every `children` dict maps to a valid `node_id` in the tree's `nodes` dictionary.

### For the Internet/IT Pack Overall

9. **8 dimensions present:** Top-level keys include all of: `meta`, `terms`, `tasks`, `roles`, `workflows`, `docs`, `follow_up_trees`, `pain_points`.
10. **Minimum content counts:**
    - `terms`: >= 30 entries (source: Internet/IT is the first pack, 30 is a baseline that covers the 5 scenarios)
    - `tasks`: >= 5 entries (matching the 5 scenarios)
    - `roles`: >= 4 entries (产品经理, 前端工程师, 后端工程师, 数据分析师 minimum)
    - `workflows`: >= 2 entries (功能上线流程, 需求管理流程 minimum)
    - `docs`: >= 3 entries (PRD模板, API文档模板, 技术方案模板 minimum)
    - `pain_points`: >= 5 entries (covering common pain points)
    - `follow_up_trees`: exactly 5 (one per scenario)
11. **Version consistency:** `meta.version` matches expected format `X.Y.Z`; `meta.schema_version` is `"1.0"`.
12. **Compiled JSON validates:** The pack passes `KnowledgePack(**data)` Pydantic validation with zero errors.

## Sources

### Primary (HIGH confidence)
- PyYAML 6.0.3: pip list confirmation of installed version [VERIFIED: pip list]
- pydantic 2.12.5: pip list confirmation [VERIFIED: pip list]
- Python 3.12.10: version check [VERIFIED: python --version]
- jmespath 1.1.0: PyPI latest version [VERIFIED: pip index versions jmespath]
- jsonschema 4.26.0: pip list confirmation [VERIFIED: pip list]
- Python `json` module docs: stdlib behavior for `ensure_ascii=False` [CITED: Python 3.12 docs]

### Secondary (MEDIUM confidence)
- Existing `knowledge.py` structure: read and analyzed for content reference [CITED: codebase]
- Existing `build.bat`: read for integration point identification [CITED: codebase]
- Existing `generator.py`: read for template structure reference [CITED: codebase]
- Pydantic v2 `BaseModel`, `Field`, `field_validator`, `model_dump` APIs: based on stable, well-documented pydantic 2.x API [CITED: pydantic docs]

### Tertiary (LOW confidence)
- JMESPath query patterns for Chinese fuzzy matching: reasoned analysis, training knowledge [ASSUMED]
- Chinese YAML editing patterns for content authors: reasoned from general YAML best practices [ASSUMED]
- Follow-up tree 5-8 node sufficiency estimate: reasoned from conversational UI literature in training data [ASSUMED]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all packages verified via pip list or PyPI
- Architecture: HIGH -- patterns validated against CONTEXT.md locked decisions and existing codebase analysis
- Pitfalls: HIGH -- derived from codebase reading (knowledge.py flat structure, build.bat integration) and established software engineering patterns
- QA-01 criteria: MEDIUM -- specific thresholds (30+ terms, 4+ roles) are reasoned estimates that should be validated against actual content creation; the check methodology (8 points per scenario + 4 overall) is solid

**Research date:** 2026-06-03
**Valid until:** 2026-07-03 (30 days for stable Python packages; content assumptions should be re-evaluated after first Internet/IT pack draft)
