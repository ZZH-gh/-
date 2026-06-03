# Phase 1: Foundation - Context

**Gathered:** 2026-06-03
**Status:** Ready for planning

<domain>
## Phase Boundary

建立 v4.0 行业知识包的基础设施：定义知识包的 JSON Schema 数据结构、YAML→JSON 编译管线、构建验证脚本，并完成互联网/IT 行业第一个知识包 V1。Phase 1 不涉及运行时加载（那是 Phase 2 的事），也不涉及对话引擎（Phase 4）。

**v3.0 兼容：** 现有 `knowledge.py` / `engine.py` / `generator.py` / `app.py` 保持完整不动。Phase 1 产出的知识包+编译管线是独立的新增基础设施，新旧两套系统并行存在。

</domain>

<decisions>
## Implementation Decisions

### Schema 结构设计
- **D-01:** 采用 8 维度的顶层结构：meta、术语表、任务场景、角色知识、核心流程、文档规范、追问逻辑树、痛点清单
- **D-02:** 核心字段采用"标准版"粒度：
  - **术语表**: term + 定义 + 使用场景 + 相关术语
  - **任务场景**: name + 描述 + 典型输出 + 追问树 + 复杂度
  - **角色知识**: name + KPI + 痛点 + 常见任务
  - **核心流程**: name + 步骤 + 决策节点 + 失败模式

### 知识包内容范围
- **D-03:** 互联网/IT 行业 V1 覆盖 5 个高频场景，每个配完整追问树
- **D-04:** 5 个高频场景：PRD撰写、代码生成、数据分析、技术文档、工作总结
- **D-05:** 知识包 YAML 源文件存放在 `prompt_tool/knowledge_packs/` 目录下

### 深度检查标准（QA-01）
- **D-06:** 每个场景的质量标准为"追问树完整"，具体要求：
  - 每个场景 5-8 个追问节点 + 分支逻辑
  - 覆盖常见变体（如"写总结"区分管理层 vs 一线、好业绩 vs 差业绩）
  - 追问树走通后可生成有行业细节的提示词

### 编译管线设计
- **D-07:** YAML→JSON 编译管线集成到 `build.bat` 中，打包 exe 时自动编译
- **D-08:** 编译产物进入 Python 包，随 exe 一起分发
- **D-09:** 添加编译验证步骤，在 YAML 结构错误时中断构建并给出明确错误信息
- **D-10:** 编译脚本（`build_packs.py`）负责：解析 YAML → 校验 Schema → 输出 JSON

### 研究与技术方案
- **D-11:** 采用研究中建议的 YAML→JSON→JMESPath→dataclasses 技术栈
- **D-12:** 编译时用 Pydantic/jsonschema 校验，但 Pydantic 不进入 exe 运行时
- **D-13:** 知识包版本号从 v1 开始，Schema 版本号从 1.0 开始

### Claude's Discretion
- YAML 源文件的具体命名规范、编译脚本的代码风格、_schema.yaml 的详细字段约束
- 追问树 JSON 结构的具体实现方式（YAML 中的 children 数组格式细节）

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 项目文档
- `.planning/PROJECT.md` — 项目整体上下文和核心价值
- `.planning/REQUIREMENTS.md` § 知识包体系 (KNOW) — KNOW-01, KNOW-02, KNOW-09 的具体定义
- `.planning/ROADMAP.md` § Phase 1 — 阶段目标与成功标准
- `.planning/config.json` — 工作流配置

### 研究文档
- `.planning/research/STACK.md` — 技术栈推荐（YAML→JSON→JMESPath→dataclasses）
- `.planning/research/FEATURES.md` — 8 个知识维度定义和追问树设计
- `.planning/research/ARCHITECTURE.md` — 四层架构和知识包格式
- `.planning/research/PITFALLS.md` — 常见陷阱（特别关注 Pitfall 2 扁平知识、Pitfall 8 行业膨胀）
- `.planning/research/SUMMARY.md` — 综合研究摘要

### 现有代码（参考用，Phase 1 不动）
- `prompt_tool/knowledge.py` — 现有扁平行业知识库（Phase 1 产出将替代此文件）
- `prompt_tool/engine.py` — 现有分析引擎
- `prompt_tool/app.py` — 现有 UI

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `prompt_tool/knowledge.py` 的 INDUSTRIES 字典结构 — 可作为知识包内容的参考来源（16 个行业的关键词、任务模板等）
- `prompt_tool/engine.py` 的 keyword 匹配模式 — 知识包索引层的轻量匹配可以借鉴此模式
- `build.bat` — 现有 PyInstaller 打包脚本，编译管线集成到此处

### Established Patterns
- 项目使用 Python 3.12 + stdlib 为主，无额外数据库依赖
- knowledge.py 使用纯 Python 字典作为数据存储（Phase 1 将升级为结构化 JSON）
- build.bat 调用 PyInstaller，编译脚本应放在此流程之前

### Integration Points
- `prompt_tool/knowledge_packs/` — 新建目录，放 YAML 源文件
- `prompt_tool/knowledge_packs_compiled/` — 编译输出目录（或在 build 过程中生成）
- `build.bat` — 在 PyInstaller 调用前插入编译步骤
- Phase 2 会将此知识包接入运行时（KnowledgeManager 加载 JSON）

</code_context>

<specifics>
## Specific Ideas

- 追问树采用 YAML 的递归 children 结构，每个节点有 question/type/options/children/fallback 字段
- 第一个知识包（互联网/IT）建议在开发过程中通过实际 AI 测试验证提示词质量
- Schema 版本管理：知识包内容版本（如 v1）和 Schema 定义版本（如 1.0）分开管理
- 建议研究中的 _schema.yaml 放在 knowledge_packs/ 目录下作为参考文档

</specifics>

<deferred>
## Deferred Ideas

- **用户自定义知识包编辑器** — 属于 v2 功能，等知识包结构稳定后再开放
- **知识包自动从网络构建** — 当前由我们手动编写 YAML，后续可考虑自动化工具
- **其他 4 个行业包（销售/零售、教育、金融、制造）** — Phase 7 的任务

</deferred>

---

*Phase: 1-Foundation*
*Context gathered: 2026-06-03*
