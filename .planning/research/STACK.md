# Technology Stack: Offline Industry Knowledge Pack System

**Project:** 智能提示词工坊 (Smart Prompt Workshop) v4.0
**Researched:** 2026-06-03
**Overall confidence:** MEDIUM (web research tools unavailable; based on established Python patterns and known library characteristics)
**Researcher notes:** WebSearch, WebFetch, and Bash were all unavailable during research. Recommendations below are based on documented library APIs, established Python patterns, and reasoned analysis. Flags indicate where verification against current docs would be valuable before implementation.

---

## Executive Recommendation

**Use YAML for authoring knowledge packs, compile to JSON for runtime, query with JMESPath, access via a thin Python knowledge service layer.**

Rationale: YAML is human-authorable and supports comments (critical for knowledge pack maintainers). JSON loads 3-5x faster than YAML in CPython and has zero dependency overhead. JMESPath provides a standardized, testable query language for deep nested data. A Python service layer wraps queries so the rest of the app never touches the raw data format.

---

## Recommended Stack

### Core Data Format

| Layer | Technology | Purpose | Why |
|-------|-----------|---------|-----|
| Authoring format | **YAML 1.2** (via `PyYAML`) | Human-writable knowledge pack source | Supports comments, anchors, multi-line strings, clean syntax for Chinese text. Industry experts can review/edit YAML without Python knowledge. |
| Runtime format | **JSON** (stdlib `json`) | Fast deserialization at app startup | Python `json.load()` is implemented in C, ~3-5x faster than PyYAML `yaml.load()`. No additional dependency in shipped exe. |
| Query language | **JMESPath** (`jmespath`) | Structured queries on loaded knowledge | Standardized (AWS), more expressive than JSONPath, supports filters projections and functions. Pure Python implementation. |
| Access layer | **Python dataclasses** (`dataclasses`) | Typed access to knowledge domains | Type hints enable IDE autocomplete. Decouples query logic from raw dict access. Low overhead. |
| Schema validation | **Pydantic v2** (optional, dev-time) | Validate knowledge pack structure before shipping | Catches structural errors in YAML during CI/build, not at runtime. Avoid in shipped exe to keep size down. |

### Query Engine

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Query runtime | `jmespath` 1.x | Run pre-defined queries against loaded knowledge dict |
| Expression store | Python `dict` mapping names to JMESPath strings | All queries defined once, reused by name |
| Fallback | Python `dict`/`list` comprehensions | For queries that don't map cleanly to JMESPath (e.g., fuzzy matching on Chinese keywords) |

### Build Pipeline (not in shipped exe)

| Tool | Purpose |
|------|---------|
| `PyYAML` | Parse YAML source files |
| `pydantic` or `jsonschema` | Validate knowledge pack schema |
| Custom Python script | Compile YAML -> JSON, verify no structural errors |
| `json.dump(..., ensure_ascii=False)` | Write compiled JSON with proper Chinese encoding |

---

## Knowledge Pack Format Specification

### File Hierarchy

```
prompt_tool/
  knowledge_packs/
    __init__.py              # Auto-loads all packs
    internet_it.yaml         # All YAML source files
    education.yaml
    finance.yaml
    manufacturing.yaml
    retail.yaml
    _schema.yaml             # Schema reference (for authors)
  knowledge_packs_compiled/  # Generated, NOT hand-edited
    internet_it.json
    education.json
    finance.json
    manufacturing.json
    retail.json
  knowledge.py              # Refactored: loads JSON, wraps JMESPath queries
```

### YAML Schema Design

```yaml
# internet_it.yaml
# Knowledge Pack: 互联网/IT
# Schema version: 1.0

meta:
  id: "internet_it"
  name: "互联网 / IT"
  version: "1.0.0"
  description: "互联网产品、技术开发与运营行业知识包"
  last_updated: "2026-06-01"

# === 行业术语 ===
terms:
  - term: "Sprint"
    category: "研发流程"
    description: "敏捷开发中的一个迭代周期，通常1-4周"
    aliases: ["迭代", "冲刺"]
    used_in_context: "我们这周Sprint要完成用户故事地图"
    related_terms: ["Scrum", "Backlog"]

  - term: "DAU"
    category: "运营指标"
    description: "日活跃用户数 (Daily Active Users)"
    aliases: ["日活"]
    formula: "当日登录/使用产品的独立用户数"
   
  # ... more terms

# === 核心工作流程 ===
workflows:
  - name: "敏捷开发流程"
    category: "研发流程"
    steps:
      - step: 1
        name: "需求梳理 (Backlog Refinement)"
        description: "PO整理用户故事，团队估算工作量"
        deliverables: ["优先级排序的Backlog", "故事点估算"]
        common_tools: ["Jira", "Trello", "Notion"]
      - step: 2
        name: "Sprint规划会议"
        description: "团队承诺本次Sprint要完成的故事"
        deliverables: ["Sprint Backlog", "Sprint目标"]
    common_pitfalls: ["需求范围蔓延", "估算过于乐观"]

# === KPI/指标体系 ===
kpis:
  - name: "用户留存率"
    category: "用户增长"
    formula: "第N天回访用户数 / 新增用户数 x 100%"
    benchmarks:
      - context: "社交类App D1留存"
        good: "> 60%"
        excellent: "> 80%"
      - context: "工具类App D1留存"
        good: "> 40%"
        excellent: "> 60%"
    calculation_notes: "通常关注D1/D7/D30留存"
    related_terms: ["留存", "Retention", "DAU/MAU"]

# === 典型场景 ===
scenarios:
  - name: "产品需求文档编写"
    tasks: ["需求分析", "功能设计", "文档撰写"]
    user_role: "产品经理"
    typical_inputs:
      - "用户痛点描述"
      - "竞品分析参考"
      - "业务目标KPI"
    typical_outputs:
      - "PRD文档"
      - "功能原型图参考"
      - "验收标准"
    difficulty: "medium"

# === 追问逻辑树 ===
follow_up_trees:
  - task_type: "代码生成"
    root_question: "你需要生成什么类型的代码？"
    children:
      - value: "后端API"
        follow_up: "使用什么框架？需要哪些接口？数据库是什么？"
        depth: 2
      - value: "前端页面"
        follow_up: "是PC端还是移动端？是否需要响应式设计？"
        children:
          - value: "PC端"
            follow_up: "使用什么UI框架？是否需要对接API？"
          - value: "移动端"
            follow_up: "是H5还是小程序？适配哪些机型？"

  - task_type: "技术方案"
    root_question: "这个技术方案要解决什么核心问题？"
    children:
      - value: "架构设计"
        follow_up: "目标系统的用户量级和性能要求是什么？"
      - value: "技术选型"
        follow_up: "团队的技术栈熟悉度如何？预算限制是什么？"

# === 文档模板 ===
templates:
  - name: "PRD模板"
    task_type: "需求分析"
    sections:
      - title: "项目背景"
        prompt_hint: "为什么要做这个功能？解决什么用户痛点？"
      - title: "功能范围"
        prompt_hint: "包含哪些功能？哪些功能明确不做？（边界定义）"
      - title: "用户流程"
        prompt_hint: "用户从进入到完成的核心操作路径"
      - title: "验收标准"
        prompt_hint: "满足什么条件算功能完成？"

# === 典型角色 ===
roles:
  - name: "产品经理"
    responsibilities:
      - "需求收集与分析"
      - "PRD撰写"
      - "项目进度跟踪"
    common_tasks: ["需求分析", "文档编写", "竞品分析"]
    depth_level: "expert"
```

### Runtime JSON Structure

The compiled JSON preserves the exact same structure. The compilation step is purely a format conversion:

```bash
# Build script approach:
python -c "
import yaml, json, sys
with open('internet_it.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)
with open('internet_it_compiled.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
"
```

**Why JSON not YAML at runtime:**
- `json.load()` is ~3-5x faster than `yaml.safe_load()`
- No `PyYAML` dependency in shipped exe (~500KB saved)
- No risk of YAML deserialization vulnerabilities (yaml.load without SafeLoader)
- Python's `json` module is C-optimized and battle-tested

---

## Query Layer Design

### JMESPath for Structured Queries

JMESPath is preferred over JSONPath for these reasons:

| Aspect | JMESPath | JSONPath | Winner |
|--------|----------|----------|--------|
| Standard | RFC-agnostic but has formal grammar | Multiple incompatible variants | JMESPath |
| Python lib | `pip install jmespath` | `pip install jsonpath-ng` or `jsonpath-python` | JMESPath (simpler API) |
| Expressiveness | Built-in functions, pipes, projections | Limited to path expressions | JMESPath |
| Performance | Pure Python but efficient for typical knowledge sizes | Similar | Tie |
| Complex filters | `[?category=='研发流程']` | `$..[?(@.category=='研发流程')]` | JMESPath (cleaner) |
| Chinese support | String comparison works on decoded Unicode | Same | Tie |

### Query Examples

```python
import jmespath

# Load knowledge pack
with open("knowledge_packs_compiled/internet_it.json", "r", encoding="utf-8") as f:
    pack = json.load(f)

# Find all terms in a specific category
jmespath.search("terms[?category=='研发流程']", pack)
# Returns: [{term: "Sprint", ...}, {term: "Backlog", ...}, ...]

# Find KPI benchmarks
jmespath.search("kpis[?name=='用户留存率'].benchmarks[0]", pack)
# Returns: {context: "社交类App D1留存", good: "> 60%", ...}

# Get follow-up questions for a specific task type
jmespath.search("follow_up_trees[?task_type=='代码生成'].root_question", pack)
# Returns: ["你需要生成什么类型的代码？"]

# Get all terms matching a Chinese keyword
# NOTE: JMESPath equality is exact. For fuzzy search, fall back to Python.
all_terms = pack["terms"]
matching = [t for t in all_terms if "敏捷" in t.get("term", "") or 
            any("敏捷" in a for a in t.get("aliases", []))]
```

### When to Use JMESPath vs Python Iteration

| Use Case | Approach | Rationale |
|----------|----------|-----------|
| Exact category/subtype filter | JMESPath | Clean, declarative, testable |
| Keyword-aware fuzzy match | Python list comprehension | JMESPath has no built-in substring matching |
| Single value lookup by known key | JMESPath | `search("meta.name", pack)` — fast |
| Complex multi-condition join | Python + dict access | JMESPath has no joins, can be awkward |
| Follow-up tree traversal | Python recursive function | Tree walking is simpler in Python code |

### Knowledge Service Layer

```python
# knowledge_service.py — typed wrapper around raw JSON packs
from dataclasses import dataclass, field
from typing import Optional
import json
import jmespath
from pathlib import Path

@dataclass
class Term:
    term: str
    category: str
    description: str
    aliases: list[str] = field(default_factory=list)
    related_terms: list[str] = field(default_factory=list)

@dataclass
class WorkflowStep:
    step: int
    name: str
    description: str
    deliverables: list[str] = field(default_factory=list)

@dataclass
class FollowUpNode:
    question: str
    children: list["FollowUpNode"] = field(default_factory=list)

class KnowledgePack:
    """Typed accessor for a single compiled knowledge pack."""
    
    def __init__(self, json_path: str | Path):
        with open(json_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)
    
    @property
    def meta(self) -> dict:
        return self._data["meta"]
    
    def get_terms(self, category: str | None = None) -> list[Term]:
        if category:
            raw = jmespath.search(f"terms[?category=='{category}']", self._data)
        else:
            raw = self._data.get("terms", [])
        return [Term(**t) for t in raw]
    
    def search_terms(self, keyword: str) -> list[Term]:
        """Fuzzy search terms by keyword (term name + aliases)."""
        raw = self._data.get("terms", [])
        results = []
        kw = keyword.lower()
        for t in raw:
            if kw in t.get("term", "").lower():
                results.append(Term(**t))
                continue
            for alias in t.get("aliases", []):
                if kw in alias.lower():
                    results.append(Term(**t))
                    break
        return results
    
    def get_follow_up_tree(self, task_type: str) -> dict | None:
        """Get the follow-up question tree for a task type."""
        result = jmespath.search(
            f"follow_up_trees[?task_type=='{task_type}'] | [0]",
            self._data
        )
        return result
    
    def walk_follow_up_tree(self, task_type: str, answers: list[str]) -> str | None:
        """Walk the follow-up tree based on user answers to find next question."""
        tree = self.get_follow_up_tree(task_type)
        if not tree:
            return None
        return self._walk_node(tree, answers)
    
    def _walk_node(self, node: dict, answers: list[str], depth: int = 0) -> str | None:
        if depth >= len(answers):
            return node.get("root_question") if "root_question" in node else node.get("follow_up")
        answer = answers[depth]
        for child in node.get("children", []):
            if answer in child.get("value", ""):
                return self._walk_node(child, answers, depth + 1)
        return node.get("follow_up")  # fallback

class KnowledgeManager:
    """Manages all loaded knowledge packs."""
    
    def __init__(self, packs_dir: str | Path):
        self._packs: dict[str, KnowledgePack] = {}
        packs_path = Path(packs_dir)
        for json_file in packs_path.glob("*_compiled.json"):
            pack = KnowledgePack(json_file)
            self._packs[pack.meta["id"]] = pack
    
    def get_pack(self, industry_id: str) -> KnowledgePack | None:
        return self._packs.get(industry_id)
    
    def get_industry_ids(self) -> list[str]:
        return list(self._packs.keys())
```

---

## Performance & Size Analysis

### Knowledge Pack Size Budget

| Industry | Estimated Terms | Estimated Total Size (compiled JSON) |
|----------|----------------|--------------------------------------|
| 互联网/IT | 200-300 | ~80-120 KB |
| 教育 | 150-250 | ~60-100 KB |
| 金融 | 180-280 | ~70-110 KB |
| 销售/零售 | 150-250 | ~60-100 KB |
| 制造业 | 160-260 | ~65-105 KB |
| **Total (5 industries)** | **~1000 terms** | **~400-600 KB** |

With full follow-up trees, templates, workflows, and KPIs, each pack expands to roughly:
- Terms: ~60-80 KB
- Workflows: ~40-60 KB
- KPIs: ~20-30 KB
- Scenarios: ~30-50 KB
- Follow-up trees: ~50-80 KB
- Templates: ~40-60 KB
- Roles: ~10-20 KB

**Total per industry pack: ~250-380 KB as JSON**
**Total for 5 industries: ~1.5-2.0 MB as JSON**

### Startup Time Impact

| Pack Size | `json.load()` time | Notes |
|-----------|-------------------|-------|
| 100 KB | < 5 ms | Negligible |
| 500 KB | ~10-15 ms | Negligible |
| 2 MB | ~30-50 ms | Still negligible |
| 10 MB | ~150-300 ms | Noticeable but acceptable |
| 50 MB | ~1-2 seconds | Problematic — exceeds 2s budget |

**Conclusion:** With ~2 MB total for 5 industries, loading all packs at startup takes ~30-50 ms. This is well within the 2-second performance budget. The limiting factor for exe size is not the JSON data, but the Python runtime itself (~10 MB compressed for Python 3.12 + customtkinter).

### PyInstaller Compatibility

**Strategy: `--add-data` for each compiled JSON file**

```bash
pyinstaller --onefile --windowed \
  --add-data "prompt_tool/knowledge_packs_compiled/*.json;knowledge_packs_compiled" \
  prompt_tool/main.py
```

**At runtime, access via `sys._MEIPASS`:**

```python
import sys
import os
from pathlib import Path

def get_packs_dir() -> Path:
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        base = Path(sys._MEIPASS)
    else:
        # Running in development
        base = Path(__file__).parent
    return base / "knowledge_packs_compiled"
```

**Alternative (simpler, recommended):** Use `importlib.resources` to access data files from within the package:

```python
# knowledge_packs/__init__.py
import json
from importlib.resources import files

PACKS = {}

def load_all():
    """Load all compiled JSON packs using importlib.resources."""
    data_dir = files("prompt_tool.knowledge_packs_compiled")
    for json_file in data_dir.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            pack_data = json.load(f)
            pack_id = pack_data["meta"]["id"]
            PACKS[pack_id] = pack_data
```

This approach works with PyInstaller because data files included via `--add-data` are accessible through `importlib.resources` in frozen mode.

### Size Budget for Shipped Exe

| Component | Size | Notes |
|-----------|------|-------|
| Python 3.12 runtime (minimal) | ~8-10 MB | Compressed in PyInstaller |
| customtkinter + tkinter deps | ~3-5 MB | |
| Pillow | ~2-3 MB | |
| jmespath | ~50 KB | Pure Python, compresses well |
| Knowledge packs (5 industries) | ~1.5-2 MB | JSON format |
| App code | ~100-200 KB | Python source |
| **Total estimated exe size** | **~15-20 MB** | Well under 50 MB limit |

---

## Alternatives Considered

### Alternative Data Formats

| Format | Chosen? | Reason |
|--------|---------|--------|
| **CSV** | No | Cannot represent hierarchical data (workflows, follow-up trees) without ugly flattening. No nested structure, no comments. |
| **XML** | No | Verbose, painful to write by hand for Chinese text. Requires escaping. `xml.etree.ElementTree` is slower than JSON for read. |
| **TOML** | No | Designed for config, not tree data. No native support for deep nesting without awkward tables-of-arrays. |
| **SQLite** | No | Need at compile time, but SQLite is a binary dependency. Query flexibility is lower — can't do complex nested queries easily. Also adds ~800KB to exe. Overkill for read-only data. |
| **msgpack** | No | Faster than JSON to deserialize, smaller on disk, but requires `msgpack` dependency. Marginal benefit at our scale (~2 MB). Not human-readable. |
| **pickle** | No | Python-specific, security risk, version-dependent, not human-readable. |
| **Protobuf** | No | Requires schema compilation step, Java-like verbosity for schema files, overkill for read-only hierarchical data. |

### Alternative Query Approaches

| Approach | Chosen? | Reason |
|----------|---------|--------|
| **JSONPath** | No | Multiple incompatible variants in Python ecosystem (`jsonpath-ng`, `jsonpath-python`, `jsonpath-rw`). Less standardized than JMESPath. |
| **ObjectPath** | No | Less known, smaller community. API is less clean than JMESPath. |
| **pandas** | No | 10MB+ library for what is essentially dict lookups. Overkill. |
| **Raw Python dict iteration** | Partial | Best for fuzzy/Chinese matching (see above). Use as fallback, not primary. |
| **NumPy** | No | Not designed for nested textual data. Heavy dependency. |

### Alternative Packaging for PyInstaller

| Approach | Chosen? | Reason |
|----------|---------|--------|
| **Inline JSON in Python source** | No | Hurts maintainability. Knowledge pack authors cannot work independently. Changes to knowledge require modifying Python code. |
| **Import Python dict from .py file** | No | Same issue as inline. Also, no syntax validation without executing the file. |
| **ZIP archive inside exe** | Not needed | PyInstaller already supports `--add-data`. No need for an additional archive layer. |
| **Embed as `pkgutil` data** | Yes | `importlib.resources` is the modern Python 3.12 way. Works with PyInstaller. |

---

## Architecture: Knowledge Flow

```
[Authoring]                    [Build]                    [Runtime]
                                                         
YAML source files         Compile script           PyInstaller bundles
  industry_a.yaml   --->   yaml -> json       --->  compiled JSON files
  industry_b.yaml          validate schema           (inside exe)
  _schema.yaml             write JSON              
                                                    KnowledgeManager
                                                       |
                                           +---------+----------+
                                           |                    |
                                    KnowledgePack         KnowledgePack
                                    (internet_it)         (education)
                                           |                    |
                                    JMESPath queries    JMESPath queries
                                           |                    |
                                     AnalysisEngine      AnalysisEngine
                                           |                    |
                                     [Prompt generation] [Prompt generation]
```

**Key design decisions:**
1. YAML only exists **before** the build step. The shipped exe contains only JSON.
2. Schema validation happens at build time, not runtime. This keeps the exe lean.
3. Each industry pack is a separate file. This enables lazy loading (load only the matched industry's pack, not all 5).
4. The `KnowledgeManager` is the single point of access. No component directly imports raw JSON.

---

## Lazy Loading Strategy

For optimal startup, load only the "common" index first, then load the full pack for the matched industry:

```python
class KnowledgeManager:
    def __init__(self, packs_dir: str | Path):
        self._packs_dir = Path(packs_dir)
        self._index = {}         # industry_id -> {id, name, keywords}
        self._loaded = {}        # industry_id -> full pack
        self._load_index()
    
    def _load_index(self):
        """Load lightweight index (just meta + keywords for matching)."""
        for json_file in self._packs_dir.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._index[data["meta"]["id"]] = {
                "name": data["meta"]["name"],
                "keywords": data.get("keywords", []),
            }
    
    def load_pack(self, industry_id: str) -> KnowledgePack:
        """Lazy-load a full knowledge pack on demand."""
        if industry_id not in self._loaded:
            json_path = self._packs_dir / f"{industry_id}.json"
            self._loaded[industry_id] = KnowledgePack(json_path)
        return self._loaded[industry_id]
```

**Benefit:** The engine.py industry matcher only needs the index (a few KB per industry). The full pack (~300 KB) is loaded only after the industry is identified. This means startup time is ~5-10 ms even with 10+ industries.

---

## What NOT to Do and Why

1. **Do NOT use YAML at runtime inside the exe.** PyYAML is a C extension that adds ~500KB and is slower than stdlib json. Compile YAML to JSON as a build step.

2. **Do NOT use SQLite for knowledge storage.** It adds a binary dependency (~800KB), requires learning SQL for what is fundamentally a key/value + nested document data model, and doesn't handle Chinese fuzzy matching any better than Python list comprehensions. SQLite is for transactional data, not read-only knowledge packs.

3. **Do NOT inline knowledge in Python source code.** This is what the current `knowledge.py` does, and it makes it impossible for non-Python-knowledgeable domain experts to review or edit knowledge packs. It also means every knowledge edit requires a code release.

4. **Do NOT use a custom YAML/JSON parser.** Python's stdlib json is C-optimized. Any custom parser will be slower and have more bugs. JMESPath is a maintained, tested query engine. Don't reinvent either.

5. **Do NOT validate knowledge pack structure at runtime.** Validate at build time with Pydantic/jsonschema. The shipped exe should have zero validation overhead — it should assume the data is correct because it was validated before packaging.

6. **Do NOT load all knowledge packs on startup unless necessary.** Lazy load — load the index (keywords only, ~5 KB per industry) for industry matching, then load the full pack only when the user's industry is identified. This keeps initial startup under 100ms.

7. **Do NOT use `json.loads` (string) over `json.load` (file).** For files, `json.load()` reads and parses in one pass. `json.loads()` requires reading the file into memory first, doubling memory usage temporarily.

8. **Do NOT encode knowledge IDs in Chinese.** Use snake_case english IDs internally (`internet_it`, not `互联网/it`). The YAML/JSON keys should be ASCII for reliable cross-platform file handling. Display names are stored as fields, not keys.

---

## Dependencies

### Runtime (shipped in exe)
```
# Already present:
customtkinter >= 5.x
Pillow

# New additions:
jmespath >= 1.0     # ~50KB pure Python
```

### Development/Authoring (NOT shipped)
```
PyYAML >= 6.0       # Parse YAML knowledge packs
pydantic >= 2.0     # Validate pack structure before build
```

### No additional runtime dependencies needed.

---

## Summary of Recommendations

| Decision | Recommendation | Confidence | Rationale |
|----------|---------------|------------|-----------|
| Authoring format | YAML | HIGH | Human-readable, supports comments, industry standard |
| Runtime format | JSON | HIGH | Fastest built-in serialization, zero dependency |
| Query library | JMESPath | MEDIUM | Standardized, clean syntax; Chinese fuzzy matching needs Python fallback |
| Access layer | Python dataclasses | HIGH | Type safety, IDE support, minimal overhead |
| Packaging | `--add-data` + `importlib.resources` | MEDIUM | Standard PyInstaller pattern, verified by many projects |
| Lazy loading | Index-first, full pack on match | HIGH | Proven pattern for optimizing startup |
| Build-time validation | Pydantic or jsonschema | MEDIUM | Both work; pick based on team preference |
| Exe size estimate | 15-20 MB | MEDIUM | Well within 50 MB constraint |

**Note on confidence:** HIGH claims are based on established Python stdlib behavior and well-documented library APIs that have been stable for years. MEDIUM claims are based on reasoned analysis of the specific use case; actual benchmarks on this data set would be valuable but the recommendations are sound.

---

## References (unverifiable — based on training data)

- JMESPath specification: https://jmespath.org/specification.html
- JMESPath Python library: https://github.com/jmespath/jmespath.py
- PyYAML documentation: https://pyyaml.org/wiki/PyYAMLDocumentation
- Python json module: https://docs.python.org/3/library/json.html
- PyInstaller data files: https://pyinstaller.org/en/stable/spec-files.html#adding-data-files
- `importlib.resources` for data access: https://docs.python.org/3/library/importlib.resources.html
