# Phase 5: Generation v2 - Context

**Gathered:** 2026-06-04
**Status:** Ready for planning

<domain>
## Phase Boundary

替换 v3.0 的模板填充式生成器，实现基于对话上下文（Phase 4 ConversationEngine）+ 知识包（Phase 1/2 KnowledgeManager）的意图驱动提示词合成引擎。

**本阶段交付：** PromptGeneratorV2（重构 generator.py）、4 级知识注入机制、反模式过滤、三种升级策略。
**本阶段不包含：** 对话式 UI 改造（Phase 6）、知识包扩展（Phase 7）、打包改动（Phase 8）。

</domain>

<decisions>
## Implementation Decisions

### 模块架构
- **D-01:** 重构现有 `generator.py`，不新建独立模块。保持文件结构简洁。
- **D-02:** 新类命名为 `PromptGeneratorV2`，旧类 `PromptGenerator` 保留为向后兼容别名。`from .generator import PromptGenerator` 仍然可用。
- **D-03:** v4 调用路径封装在 `ConversationEngine.generate_complete()` 内部。`app.py` 无感知，不关心使用哪个生成器。
- **D-04:** `ConversationEngine.generate_complete()` 直接调用 `PromptGeneratorV2`，不引入中间服务层。
- **D-05:** v3 流程（`engine.analyze()` → `generate_prompts()`）保留不动，v4 流程通过 `ConversationEngine` 编排，两者在 `app.py` 通过 `is_v4_flow` 标志分流。

### 4 级知识注入结构
- **D-06:** 四个注入点在提示词正文中按固定顺序组织为独立段落：角色深度 → 质量标准 → 输出结构 → 反模式警告。
- **D-07:** 角色深度按任务匹配专业角色——PRD 写作用产品经理角色定义，代码生成用架构师定义。从知识包 `get_roles()` 和场景描述中提取角色名称 + 职责 + KPI。
- **D-08:** 质量标准采用通用+行业混合策略：通用标准（清晰、具体、可执行）+ 行业特有标准（如金融的合规性要求），从知识包场景和流程中提取。
- **D-09:** 输出结构使用知识包文档规范中的锁定格式模板（如 PRD 的：背景 → 目标 → 范围 → 方案 → 风险），从 `get_doc_template()` 提取。
- **D-10:** 反模式警告嵌入第四个段落，基于知识包痛点清单 `get_pain_points()` 生成"需要避免的常见问题"部分。
- **D-11:** 四个注入点是否全部出现由任务类型决定——不同任务类型选择不同的注入维度组合。每个注入点有独立开关。

### 知识选择策略
- **D-12:** 每次生成包含"任务相关核心知识 + 行业背景简要概述"，不全量注入知识包。
- **D-13:** 术语呈现方式：当前任务场景涉及的全部术语（8-15 个），每个词附带简短定义。
- **D-14:** 注入与当前任务角色相关的 KPI 和痛点，作为行业背景的一部分，帮助 AI 理解质量标准和用户关注点。

### 反模式过滤规则（GEN-04）
- **D-15:** 反模式检测基于知识包痛点清单驱动——生成后检查提示词是否与已知痛点相矛盾。
- **D-16:** 过滤两类内容：虚假权威用语（无依据的 "行业领先"、"最佳实践" 等修饰词）+ 行业刻板印象（过时/片面的行业标签）。
- **D-17:** 检测到反模式后自动替换违规内容再展示最终版，用户看到的是过滤后的提示词。
- **D-18:** 过滤规则以痛点清单为主，关键词匹配为辅。痛点清单中的每项可映射到具体的过滤规则。

### Claude's Discretion
- 三种策略（直给式/角色式/完整式）在 v2 中的具体差异化方案——保留三种策略，差异化方式由规划者决定
- 生成长度控制策略——如何平衡深度与简洁
- 核心流程（workflow）是否注入——D-14 未明确选择，规划者可根据实际场景判断
- PromptGeneratorV2 的 `generate_all()` 返回值格式（保持现有 `{"direct": str, "roleplay": str, "detailed": str}` 或扩展）
- 反模式替换的具体策略——替换为知识包中的正确描述 vs 仅删除
- `is_v4_flow` 标志在 `app.py` 中的具体判断逻辑

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 项目文档
- `.planning/ROADMAP.md` § Phase 5 — 阶段目标与成功标准（GEN-01~04, QA-02）
- `.planning/REQUIREMENTS.md` § GEN-01~04, QA-02 — 需求定义
- `.planning/PROJECT.md` — 项目核心价值和约束

### 前置阶段关键文档
- `.planning/phases/04-conversation-core/04-01-SUMMARY.md` — ConversationEngine 接口（generate_complete, 9-state 状态机, IntentResult）
- `.planning/phases/04-conversation-core/04-VERIFICATION.md` — Phase 4 验证详情
- `.planning/phases/03-context-layer/03-CONTEXT.md` — SessionState 结构（D-01~D-06）、ContextBuilder.build() 输出字典
- `.planning/phases/02-knowledge-layer/02-CONTEXT.md` — KnowledgeManager 接口（D-03~D-10）、KnowledgePack getter 方法清单
- `.planning/phases/01-foundation/01-CONTEXT.md` — Schema 8 维度结构（D-01~D-12）

### 现有代码（参考模式）
- `prompt_tool/generator.py` — 重构目标，现有 PromptGenerator 类
- `prompt_tool/conversation_engine.py` — ConversationEngine.generate_complete() 入口
- `prompt_tool/knowledge_manager.py` — 模块级单例模式参考
- `prompt_tool/context_builder.py` — ContextBuilder.build() 输出格式参考
- `prompt_tool/app.py` — _do_generate_v4 已有 ConversationEngine 调用模式参考

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `prompt_tool/generator.py` — 现有 PromptGenerator 类（generate_all 模式可复用），即将重构
- `prompt_tool/conversation_engine.py` — ConversationEngine.generate_complete() 为 v4 入口点
- `prompt_tool/knowledge_manager.py` — 提供知识包查询（get_terms, get_roles, get_pain_points 等）
- `prompt_tool/context_builder.py` — 输出已确认行业、任务、对话摘要的 dict

### Established Patterns
- 模块级单例（knowledge_manager.py）— 生成器无需单例，但可复用其 initialize() 范式
- Python dict 作为数据交换格式 — ContextBuilder.build() 返回 dict，生成器消费 dict
- daemon thread + self.root.after() — 生成器本身同步执行，由 ConversationEngine 管理多线程
- 策略切换模式（直给式/角色式/完整式）— 保留三种策略，内部实现重写

### Integration Points
- `prompt_tool/generator.py` — 重构目标文件，新增 PromptGeneratorV2 类
- `prompt_tool/conversation_engine.py` — generate_complete() 内调用 PromptGeneratorV2
- `prompt_tool/app.py` — _do_generate_v4() 通过 is_v4_flow 切换，实际调用 ConversationEngine
- `prompt_tool/knowledge_packs_compiled/` — 知识包 JSON 数据源，PromptGeneratorV2 通过 KnowledgeManager 读取

</code_context>

<specifics>
## Specific Ideas

- 生成的提示词结构建议：开场白（角色定义）→ 任务描述 → 具体要求（质量标准） → 输出格式（输出结构）→ 注意事项（反模式警告）
- 反模式过滤作为 PromptGeneratorV2.generate_all() 的最后一步，对三个策略的输出统一过滤
- 知识选择在 PromptGeneratorV2 初始化时完成（读取 ContextBuilder dict → 通过 KnowledgeManager 查询相关知识 → 缓存），后续三个策略共用同一份知识数据

</specifics>

<deferred>
## Deferred Ideas

- **3 种策略的 v2 差异化方案** — 直给式/角色式/完整式的具体升级方案未深入讨论，由规划者基于 GEN-03 设计
- **生成长度控制** — 知识包深度与提示词简洁性的平衡策略未深入讨论，由规划者设计合理截断机制
- **JMESPath 查询接口** — 从 Phase 1 研究推荐的，本阶段暂不用复杂查询

</deferred>

---

*Phase: 5-Generation-v2*
*Context gathered: 2026-06-04*
