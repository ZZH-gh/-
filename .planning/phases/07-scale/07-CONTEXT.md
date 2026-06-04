# Phase 7: Scale - Context

**Gathered:** 2026-06-04
**Status:** Ready for planning

<domain>
## Phase Boundary

为 4 个核心行业编写完整的 YAML 知识包：销售/零售、教育、金融、制造业。每个包需达到 KNOW-05~08 的规格标准（术语 60+、场景 10+、追问树 2+），并全部通过 QA-01 深度检查清单。

**本阶段交付：** 4 个完整的 YAML 知识包源文件。
**本阶段不包含：** 运行时代码改动（Phase 2 已支持懒加载）、UI 改动（Phase 6 已完成）、打包改动（Phase 8）。

</domain>

<decisions>
## Implementation Decisions

### 推进策略
- **D-01:** 4 个行业包同时推进，不分批。
- **D-02:** 以互联网/IT 知识包（`01-internet-it.yaml`）为模板，保持一致的 YAML 结构和 8 维度 Schema。

### 各行业范围
- **D-03:** 金融行业包含信贷、理财、保险、证券、合规等场景，含合规声明和风险提示内容。
- **D-04:** 销售/零售行业覆盖零售门店、电商、批发、客户管理、销售流程等场景。
- **D-05:** 教育行业覆盖 K12 + 职业培训，含课程设计、学生评估、培训体系、教学管理等场景。
- **D-06:** 制造业覆盖生产管理、质量管控、供应链、设备维护等场景。

### QA-01 质量要求
- **D-07:** 每个包必须通过 `build_packs.py` 的 Schema 编译校验。
- **D-08:** 每个包必须满足：术语 60+、场景 10+、追问树 2+。
- **D-09:** 每个包编写完成后运行 `python -m pytest tests/test_schema.py -x` 验证 Schema 完整性。

### 文件名规范
- **D-10:** 文件名格式：`02-sales-retail.yaml`、`03-education.yaml`、`04-finance.yaml`、`05-manufacturing.yaml`，放在 `prompt_tool/knowledge_packs/` 目录下。

### Claude's Discretion
- 各行业的具体场景列表、术语内容、追问树结构
- 角色知识的详细 KPI 和痛点定义
- 文档规范和核心流程的具体内容
- 追问树的深度和分支细节

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 项目文档
- `.planning/ROADMAP.md` § Phase 7 — 阶段目标与成功标准
- `.planning/REQUIREMENTS.md` § KNOW-05, KNOW-06, KNOW-07, KNOW-08 — 需求定义
- `.planning/PROJECT.md` — 项目核心价值和约束

### 前置阶段参考（Schema + 现有知识包）
- `.planning/phases/01-foundation/01-CONTEXT.md` — Schema 8 维度结构和 D-01~D-13
- `prompt_tool/knowledge_packs/01-internet-it.yaml` — 互联网/IT 知识包完整模板（术语80+、场景15+）
- `prompt_tool/knowledge_packs/_schema.yaml` — Schema 定义文档
- `prompt_tool/knowledge_packs_compiled/01-internet-it.json` — 编译后的参考输出

### 编译和验证
- `build_packs.py` — YAML→JSON 编译脚本
- `tests/test_schema.py` — Schema 验证测试

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `prompt_tool/knowledge_packs/01-internet-it.yaml` — 完整参考模板（8 维度、15 场景、90+ 术语）
- `prompt_tool/knowledge_packs/_schema.yaml` — Schema 定义和字段约束
- `build_packs.py` — 编译脚本，编译时校验 Schema 完整性

### Established Patterns
- YAML 源文件格式：`meta` → `terms` → `tasks` → `roles` → `workflows` → `docs` → `follow_up_tree` → `pain_points`
- 追问树递归 children 结构：question/type/options/children/fallback
- 角色用 common_tasks 关联任务类型

### Integration Points
- `prompt_tool/knowledge_packs/` — YAML 源文件目录，添加 4 个新文件
- `build_packs.py` — 运行后自动编译新包，无需额外配置
- KnowledgeManager 自动发现新包（通过 index.json 重建）

</code_context>

<specifics>
## Specific Ideas

- 金融行业需特别注意：合规声明内容、风险提示文本、受管制行业的措辞规范
- 销售/零售可参考常见的 CRM 和电商系统场景编写流程和角色
- 教育行业区分 K12（学科教学、学生评价）和职业培训（技能认证、就业指导）
- 制造业区分生产现场管理（车间、排产、质检）和供应链管理（采购、库存、物流）

</specifics>

<deferred>
## Deferred Ideas

- **16 行业全覆盖** — v4.0 硬上限为 5 个核心行业，剩余为 v2 功能
- **用户自定义知识包编辑器** — v2 功能
- **知识包自动从网络构建** — 当前手动编写 YAML

</deferred>

---

*Phase: 7-Scale*
*Context gathered: 2026-06-04*
