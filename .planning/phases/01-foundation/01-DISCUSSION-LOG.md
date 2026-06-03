# Phase 1: Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-03
**Phase:** 1-Foundation
**Areas discussed:** Schema结构设计, 知识包内容范围, 深度检查标准, 编译管线设计

---

## Schema结构设计

| Option | Description | Selected |
|--------|-------------|----------|
| 合理，按这个结构细化 | 8个维度合适，开始往下设计每个维度的详细字段 | ✓ |
| 太复杂，精简一下 | 减少维度数量，先做核心的3-4个维度 | |
| 调整结构 | 有自己的想法，想重新组织 | |

**User's choice:** 合理，按这个结构细化，采用标准版字段粒度

| Option | Description | Selected |
|--------|-------------|----------|
| 精简版 | 术语表(term+定义)、场景(name+描述+追问树) | |
| 标准版 | 术语表(term+定义+使用场景+相关术语)、场景(name+描述+典型输出+追问树+复杂度)、角色(name+KPI+痛点+常见任务)、流程(name+步骤+决策节点+失败模式) | ✓ |
| 详细版 | 标准版+场景含示例输入输出、角色含汇报关系、流程含时间估计和责任人 | |

**Notes:** 8维度结构确认，核心字段采用标准版粒度。

---

## 知识包内容范围

| Option | Description | Selected |
|--------|-------------|----------|
| 聚焦5个高频场景 | PRD撰写、代码生成、数据分析、技术文档、工作总结 — 先做透最常见的，每个配完整追问树 | ✓ |
| 做10-15个场景 | 把IT行业主要使用场景都覆盖到 | |
| 极广极浅 | 做20+场景，但没有追问树 | |

**User's choice:** 5个高频场景: PRD撰写、代码生成、数据分析、技术文档、工作总结

**Notes:** 这5个场景覆盖了互联网/IT行业最常用的需求，每个要有完整追问树。

---

## 深度检查标准

| Option | Description | Selected |
|--------|-------------|----------|
| 追问树完整（推荐） | 每条>=3个问句分支+覆盖5种典型变体 | ✓ |
| 量化达标卡 | 有量化指标，比如术语数量>=60、追问树>=3条 | |
| 输出质量验证 | 每个场景生成的提示词必须经过实际AI验证 | |
| 综合 | 追问树+量化+AI实测 | |

**User's choice:** 追问树完整

| Sub-option | Description | Selected |
|-------------|-------------|----------|
| 轻量 | 每个场景3-5个关键问题，问完就能生成 | |
| 标准（推荐） | 每个场景5-8个问题+分支逻辑，覆盖主要变体 | ✓ |
| 深度 | 像资深顾问一样层层深挖 | |

**Notes:** "标准"深度 — 5-8个问题+分支逻辑，区分常见变体。

---

## 编译管线设计

| Option | Description | Selected |
|--------|-------------|----------|
| 独立脚本 | 放在项目根目录，手动运行 | |
| 打包时自动编译 | 每次构建exe时自动编译 | |
| 集成到build.bat | 调用命令行，和现有打包流程整合 | ✓ |

**User's choice:** 集成到build.bat

| Option | Description | Selected |
|--------|-------------|----------|
| 集成到Python包（推荐） | YAML在prompt_tool/knowledge_packs/，编译后进入Python包 | ✓ |
| 独立目录 | YAML单独放在项目根目录下knowledge_packs/ | |

**Notes:** YAML源文件放在 prompt_tool/knowledge_packs/，编译脚本 build_packs.py，在 build.bat 的 PyInstaller 步骤前调用。

---

## Claude's Discretion

- YAML 源文件的具体命名规范
- 编译脚本的代码风格和结构
- _schema.yaml 的详细字段约束设计
- 追问树 YAML 结构中 children 数组的具体格式细节

## Deferred Ideas

- 用户自定义知识包编辑器 — v2 功能
- 知识包自动从网络构建 — 未来考虑
- 其他4个行业包（销售/零售、教育、金融、制造） — Phase 7
