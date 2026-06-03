# Phase 3: Context Layer - Context

**Gathered:** 2026-06-03
**Status:** Ready for planning

<domain>
## Phase Boundary

定义多轮对话的会话状态数据模型，实现 SessionManager 追踪会话历史与已确认信息，实现 ContextBuilder 从原始会话上下文构建供 Phase 5 生成器使用的 GenerationContext。

**本阶段交付：** ConversationTurn + SessionState 数据结构、SessionManager（会话创建/更新/查询）、ContextBuilder（构建生成上下文）。

**不包含：** 对话引擎/状态机（Phase 4）、追问逻辑（Phase 4）、生成器改造（Phase 5）、UI 改动（Phase 6）。

**v3.0 兼容：** engine.py 的 analyze() 仍可用，但新增的 SessionManager 和 ContextBuilder 是独立模块。Phase 4 对话引擎会编排 engine → SessionManager → ContextBuilder 的流程。

</domain>

<decisions>
## Implementation Decisions

### 会话数据模型
- **D-01:** ConversationTurn 结构：role（"user" | "system"）、content（str）、turn_type（"question" | "answer" | "confirm" | "info"）、timestamp（float）。
- **D-02:** SessionState 结构：session_id（str）、created_at（float）、turns（list[ConversationTurn]）、confirmed_industry（str | None）、confirmed_task（str | None）、extracted_info（dict，如 {"role": "产品经理", "tone": "正式"}）。

### 知识包关联
- **D-03:** SessionState 存储知识包 ID 引用（confirmed_industry: "internet_it"），不存储数据快照。Phase 5 生成器通过 KnowledgeManager 按需查询最新知识包数据。

### 会话生命周期
- **D-04:** 单会话模式。SessionManager 只管理一个活跃会话。应用启动时无活跃会话，用户首次输入时自动创建。用户主动"新建会话"时旧会话丢弃。

### 上下文构建
- **D-05:** ContextBuilder.build(session) → dict。输出字段：industry_id、industry_name、task_type、confirmed_info（已确认信息字典）、conversation_summary（最近 N 轮问答摘要）、knowledge_pack_ref。与 Phase 2 KnowledgePack 和现有 generator.py 的 dict 风格一致。

### 线程安全
- **D-06:** 主线程唯一写入者（创建/更新会话），后台 daemon 线程只读。不加锁，依赖 Python GIL 保障 dict 操作原子性。生成开始前会话状态已稳定（所有追问已完成），生成期间不会修改 session。与 Phase 2 D-08 决策一致。

### Claude's Discretion
- conversation_summary 的摘要算法（最近 N 轮拼接 vs 关键词提取）
- SessionState 的 extracted_info 字典中 key 的命名规范
- ContextBuilder 的具体实现方式（独立类 vs SessionManager 的方法）
- 会话 ID 的生成方式（uuid4 vs 时间戳）
- SessionManager 的模块组织（独立文件 vs 与 ContextBuilder 合并）
- 单会话模式下 new_session() 替换旧会话时是否需要回调通知

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 项目文档
- `.planning/ROADMAP.md` § Phase 3 — 阶段目标与成功标准
- `.planning/REQUIREMENTS.md` § CONV-06 — 需求定义
- `.planning/PROJECT.md` — 项目核心价值和约束

### 前置阶段产物
- `.planning/phases/01-foundation/01-CONTEXT.md` — Schema 设计和 D-11 技术栈
- `.planning/phases/02-knowledge-layer/02-CONTEXT.md` — KnowledgeManager 接口（match_industry, load_pack）
- `.planning/phases/02-knowledge-layer/02-RESEARCH.md` — KnowledgePack getter 方法清单

### 现有代码（参考模式）
- `prompt_tool/app.py` — 现有 threading 模式（daemon thread + self.root.after），SessionManager 需与之兼容
- `prompt_tool/engine.py` — analyze() 返回 dict 的模式，ContextBuilder 需与之对接
- `prompt_tool/knowledge_manager.py` — 模块级单例模式参考

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `prompt_tool/engine.py` analyze() 返回 dict 模式 — ContextBuilder.build() 应遵循同样的风格
- `prompt_tool/knowledge_manager.py` 单例模式 — SessionManager 可采用同模式

### Established Patterns
- 模块级单例：engine.py 的 default_engine、knowledge_manager.py 的 knowledge_manager
- Python dict 作为数据交换格式（无 dataclass 依赖）
- 主线程写 + daemon 线程读的并发模型

### Integration Points
- `prompt_tool/app.py` — 需在 __init__ 中初始化 SessionManager，在用户输入事件中更新会话
- Phase 4 对话引擎 — 编排 engine.analyze() → SessionManager 更新 → ContextBuilder.build()
- Phase 5 生成器 — 消费 ContextBuilder.build() 输出的 dict

</code_context>

<specifics>
## Specific Ideas

- ContextBuilder.build() 的 conversation_summary 字段建议采用"最近 5 轮 Q&A 拼接"的简单策略，保持低延迟
- SessionManager 可复用 knowledge_manager.py 的单例模式 + initialize() 范式
- 会话 ID 使用 uuid4 生成，即使不持久化也保持唯一性

</specifics>

<deferred>
## Deferred Ideas

- **会话磁盘持久化** — 关闭 app 后恢复上次会话，属于后续增强
- **多会话切换** — 多标签页式同时进行多个会话，v2 功能
- **会话导出/导入** — JSON 格式导出会话历史，v2 功能

</deferred>

---
*Phase: 3-Context-Layer*
*Context gathered: 2026-06-03*
