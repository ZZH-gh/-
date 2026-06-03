# Phase 2: Knowledge Layer - Context

**Gathered:** 2026-06-03
**Status:** Ready for planning

<domain>
## Phase Boundary

构建 v4.0 运行时知识包加载层：KnowledgeManager 负责启动时加载轻量索引（~5KB），识别行业后按需加载完整知识包（~300KB），提供类型化的查询接口。同时将 Internet/IT 知识包从阶段 1 的 36 术语/5 场景扩展到 KNOW-04 完整规格（80+ 术语/15+ 场景/3+ 追问树）。

**不包含：** 会话状态管理（阶段 3）、对话引擎（阶段 4）、UI 改动（阶段 6）、其他 4 个行业包（阶段 7）。

**v3.0 兼容：** engine.py 的 `_identify_industry()` 将被 KnowledgeManager.match_industry() 替代；generator.py 通过 KnowledgePack getter 方法获取知识。knowledge.py 作为 fallback 保留。

</domain>

<decisions>
## Implementation Decisions

### 索引结构与匹配
- **D-01:** 启动索引（index.json）内容：每个行业的 meta（id/name/icon/description）+ 关键词列表 + pack_file + 统计信息（term_count/scenario_count）。目标体积 ~5KB。
- **D-02:** index.json 由 build_packs.py 编译时自动生成，放在 knowledge_packs_compiled/ 目录中。不需要单独的索引源文件。
- **D-03:** KnowledgeManager 提供 match_industry(user_input: str) -> list[IndustryMatch] 方法，返回置信度排名的行业列表。替代 engine.py 的 _identify_industry()。

### 加载策略
- **D-04:** 行业确认后加载完整知识包。流程：用户输入 → match_industry() 返回排名列表 → 确认行业 → load_pack(industry_id) 加载完整 JSON → 后续所有操作直接使用内存中的 KnowledgePack。
- **D-05:** 单例缓存 + LRU 策略，容量为 2（当前行业包 + 最近使用过的上一个包）。切换行业时大概率命中缓存。内存占用约 600KB。
- **D-06:** 运行时数据结构：JSON 用 json.load() 解析为 Python dict/list。KnowledgePack 包装类提供核心 getter 方法：get_terms(category?), get_task(task_type), get_roles(), get_workflow(name), get_doc_template(type), get_follow_up_tree(task_type), get_pain_points(), get_meta()。零额外运行时依赖。
- **D-07:** engine.py 通过 KnowledgeManager 实例获取知识包数据。KnowledgeManager 是纯数据层，engine.py 和 generator.py 是消费方。
- **D-08:** 单线程访问。KnowledgeManager 只在主线程中被调用。后台线程生成时知识包已加载到内存，dict 只读访问天然线程安全。不引入锁机制。
- **D-09:** 编译产物损坏或缺失时，静默 fallback 到 v3.0 knowledge.py 的扁平字典。状态栏显示警告但不断路。
- **D-10:** 模块级单例模式。`from prompt_tool.knowledge_manager import knowledge_manager`（类似 engine.py 的 default_engine 模式）。

### 初始化和分发
- **D-11:** 编译产物（index.json + 各行业 JSON）放在 `prompt_tool/knowledge_packs_compiled/`，作为 package_data 随 exe 打包。运行时用 pathlib 相对路径读取。
- **D-12:** app.py 启动时调用 knowledge_manager.initialize() 加载索引。首次 match_industry() 调用前索引必须就绪。

### 知识包内容扩展
- **D-13:** Internet/IT 知识包扩展至 KNOW-04 完整规格：术语 80+、场景 15+、追问树 3+。在阶段 2 完成，阶段 7 只做另外 4 个行业包。
- **D-14:** 新增 ~10 个场景覆盖更多 IT 子领域：面试招聘、项目管理、运维部署、UI/UX 设计、测试策略、架构设计、数据库优化、安全审计、性能优化、团队协作。每个配 3-5 个追问树。

### Claude's Discretion
- KnowledgePack 各 getter 方法具体参数签名和返回值类型
- index.json 的完整 JSON schema 字段
- LRU 缓存的实现方式（collections.OrderedDict 或自定义链表）
- KnowledgeManager.initialize() 的调用时机（app.run() 之前或 __init__ 中）
- 追问树的运行时数据结构转换（YAML 递归 → 编译后 JSON → 运行时访问方式）

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 项目文档
- `.planning/ROADMAP.md` § Phase 2 — 阶段目标与成功标准
- `.planning/REQUIREMENTS.md` § KNOW-03, KNOW-04 — 需求定义
- `.planning/PROJECT.md` — 项目核心价值和约束
- `.planning/config.json` — 工作流配置

### 阶段 1 产物
- `.planning/phases/01-foundation/01-CONTEXT.md` — Schema 设计和编译管线决策（D-01 到 D-13）
- `.planning/phases/01-foundation/01-RESEARCH.md` — 技术栈推荐（YAML→JSON→JMESPath→dataclasses）
- `build_packs.py` — 现有编译脚本（阶段 1 产出，阶段 2 需扩展 index.json 生成）
- `prompt_tool/knowledge_packs/01-internet-it.yaml` — 现有知识包源文件（阶段 2 需扩展）
- `prompt_tool/knowledge_packs/_schema.yaml` — Schema 参考文档

### 现有代码（需理解集成模式）
- `prompt_tool/engine.py` — 现有分析引擎（_identify_industry 将被替代，analyze 流程需调整）
- `prompt_tool/generator.py` — 现有生成器（阶段 2 不修改，阶段 5 会接入 KnowledgePack）
- `prompt_tool/knowledge.py` — 现有知识库（阶段 2 作为 fallback 保留）
- `prompt_tool/app.py` — 现有 UI（阶段 2 不修改，但需了解初始化时机）

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `prompt_tool/engine.py` 的 keyword 权重匹配模式 — KnowledgeManager 的 match_industry() 可借鉴此逻辑
- `prompt_tool/knowledge.py` 的 INDUSTRIES 字典结构 — 作为 fallback 直接复用

### Established Patterns
- 模块级单例：engine.py 已有 `default_engine = AnalysisEngine()` 模式，KnowledgeManager 照此
- Python dict 数据访问：generator.py 直接操作 dict 做模板填充，KnowledgePack 的 getter 方法设计需与之契合
- 编译产物在 prompt_tool/ 包内：与 __init__.py 同目录，作为 Python package data

### Integration Points
- `prompt_tool/knowledge_packs_compiled/` — 阶段 1 的编译输出目录，阶段 2 的运行时读取源
- `build_packs.py` — 阶段 1 的编译脚本，阶段 2 需要扩展：添加 index.json 自动生成
- `prompt_tool/knowledge_packs/01-internet-it.yaml` — 阶段 1 的 YAML 源文件，阶段 2 需要大量扩展内容
- engine.py 的 analyze() 方法 — 从直接 import knowledge.py 改为通过 knowledge_manager 获取
- app.py 的初始化流程 — 需要在 mainloop 前插入 knowledge_manager.initialize()

</code_context>

<specifics>
## Specific Ideas

- index.json 中每个行业保留其所有关键词（从 YAML meta + 术语 + 场景名中提取），用于与用户输入的权重匹配
- KnowledgePack 的 getter 方法返回类型保持为 Python 原生的 list/dict/str，不引入 Pydantic 模型到运行时
- 加载失败 fallback 时，仍使用 KnowledgePack 包装 existing knowledge.py 的 INDUSTRIES 字典，保持接口一致
- 阶段 2 不做 JMESPath 集成（D-11 中 JMESPath 在 Phase 2+ 实现时再评估）

</specifics>

<deferred>
## Deferred Ideas

- **JMESPath 查询接口** — D-11 技术栈包含 JMESPath，但本阶段先用 dict + getter 方法，后续阶段需要复杂查询时再引入
- **运行时知识包热更新** — 属于 v2 功能
- **用户自定义知识包编辑器** — 属于 v2 功能
- **其他 4 个行业包（销售/零售、教育、金融、制造业）** — 阶段 7 的任务

</deferred>

---

*Phase: 2-Knowledge-Layer*
*Context gathered: 2026-06-03*
