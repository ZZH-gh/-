---
phase: 02-knowledge-layer
plan: 02
subsystem: knowledge-content
tags: knowledge-pack, internet-it, know-04, follow-up-trees, content-expansion, pytest
requires:
  - Phase 1 V1 schema (knowledge_packs/_schema.yaml, build_packs.py)
  - Phase 2 Plan 1 (KnowledgePack, KnowledgeManager, _generate_index)
provides:
  - Internet/IT knowledge pack KNOW-04 complete: 90 terms, 15 tasks, 15 follow-up trees, 10 roles, 5 workflows, 6 docs, 8 pain points
  - 10 new IT sub-domain scenarios with deep follow-up decision trees
  - Updated test thresholds and variant checks in test_content.py
affects: [04-conversation, 05-generation, 07-industry-expansion]

tech-stack:
  added: {}
  patterns:
    - Offline YAML content authoring with Pydantic validation at compile time
    - Follow-up tree design: 5-8 nodes per tree, >=2 branching, >=2 fallback, >=1 leaf
    - Knowledge content structured across 8 dimensions (meta/terms/tasks/roles/workflows/docs/trees/pain_points)

key-files:
  modified:
    - prompt_tool/knowledge_packs/01-internet-it.yaml (706 + 1295 lines: complete KNOW-04 expansion)
    - tests/test_content.py (THRESHOLDS updated to KNOW-04, VARIANT_CHECKS extended to 15 entries)
  compiled:
    - prompt_tool/knowledge_packs_compiled/internet_it.json (90 terms, 15 tasks, 15 trees)
    - prompt_tool/knowledge_packs_compiled/index.json (auto-regenerated: 380 keywords, updated stats)

key-decisions:
  - "Term definitions use Chinese with English abbreviations preserved for technical terms"
  - "related_terms cross-reference both existing V1 terms and new KNOW-04 terms for term network density"
  - "Follow-up tree node_id prefixes match task_type (ih_, pm_, ops_, ux_, ts_, ad_, db_, sa_, po_, tc_) for readability"
  - "YAML yes/no option values quoted in children keys to prevent YAML boolean interpretation (po_q2)"

requirements-completed:
  - KNOW-04

duration: ~30min
completed: 2026-06-03
---

# Phase 2 Plan 2: Internet/IT Knowledge Pack KNOW-04 Expansion

**Internet/IT knowledge pack expanded from 36 terms/5 scenarios to KNOW-04 complete specification: 90 terms, 15 scenarios, 15 follow-up decision trees, 10 roles, 5 workflows, 6 doc templates, 8 pain points. Test thresholds and variant checks updated to match.**

## Performance

- **Duration:** ~30 minutes
- **Started:** 2026-06-03
- **Completed:** 2026-06-03
- **Tasks:** 3 (all auto-type)
- **Files modified:** 2
- **Tests:** 51/51 all PASS (12 content + 15 knowledge_pack + 10 knowledge_manager + 8 schema + 6 build)

## Accomplishments

### Task 4: Term/Role/Workflow Expansion (8c7f7fc)
- Added 54 new terms across 10 IT sub-domains (5-6 terms each):
  - 面试招聘 (5): 行为面试, 技术面试, 结构化面试, 胜任力模型, 面试题库
  - 项目管理 (5): 甘特图, 里程碑管理, 关键路径, 风险管理, 项目章程
  - 运维部署 (6): Docker, Kubernetes, 监控告警, 日志分析, 容灾备份, CI/CD 管道
  - UI/UX 设计 (5): 用户体验, 信息架构, 交互设计, 设计系统, 可用性测试
  - 测试策略 (6): 单元测试, 集成测试, 端到端测试, 回归测试, 压力测试, 自动化测试框架
  - 架构设计 (6): 分层架构, 事件驱动架构, CQRS, 领域驱动设计, 服务网格, 微服务治理
  - 数据库优化 (5): 索引优化, 查询计划, 分库分表, 读写分离, 缓存策略
  - 安全审计 (6): 渗透测试, 漏洞扫描, 安全基线, 访问控制, 数据加密, 零信任架构
  - 性能优化 (5): CDN, 懒加载, 并发优化, 异步处理, 性能剖析
  - 团队协作 (5): 每日站会, 回顾会议, 需求梳理, 任务拆解, 跨部门协作
- Each term includes full fields: category, definition (50-150 chars), aliases, usage_context, related_terms cross-referencing existing terms
- Added 5 new roles: 项目经理, QA测试工程师, 运维/SRE工程师, UI/UX设计师, 安全工程师
- Added 2 new workflows: 敏捷开发Sprint流程 (7 steps), 代码审查流程 (6 steps)
- Added 2 new doc templates: 项目计划模板, 测试方案模板
- Added 2 new pain points: 项目进度不透明, 面试官缺乏结构化评估能力
- Total: terms=90, roles=10, workflows=5, docs=6, pain_points=8

### Task 5: Scenario/Tree Expansion (92e4863)
- Added 10 new task scenarios following V1 format (name, description, typical_output, complexity, frequency, follow_up_tree)
- Added 10 new follow-up decision trees (5-8 nodes each):
  - interview_hiring (6 nodes, 3 branches): 面试类型->经验级别->考察重点->产出物
  - project_mgmt (7 nodes, 3 branches): 阶段区分->启动/执行/收尾->工具需求->交付物
  - ops_deployment (5 nodes): 环境->技术栈->监控需求->SLA->产出物
  - uiux_design (8 nodes, 4 branches): 阶段区分->分支细分->交付物->额外支持
  - test_strategy (6 nodes): 层级->技术栈->覆盖目标->类型/自动化->产出物
  - arch_design (5 nodes): 系统类型->规模->非功能需求->约束->交付物
  - db_optimization (5 nodes): 问题类型->数据库类型->数据量级->优化手段->产出物
  - security_audit (5 nodes): 范围->合规标准->风险等级->方法->产出物
  - perf_optimization (5 nodes): 瓶颈类型->基线->目标值->手段->产出物
  - team_collab (6 nodes): 痛点->规模->方法论->改善方向->优先级->产出物
- Every tree passes: 5-8 node count, >=2 branching nodes, >=2 fallback, >=1 leaf
- All children references verified valid, no cycles detected by BFS

### Task 6: Test Updates (19262c9)
- Updated THRESHOLDS: terms=80, tasks=15, roles=8, workflows=5, docs=6, pain_points=8, follow_up_trees=15
- Extended VARIANT_CHECKS from 5 to 15 entries (all 10 new scenarios covered)
- Full test suite: 51/51 PASS

## Success Criteria Verification

| Criterion | Result |
|-----------|--------|
| terms >= 80 | 90 |
| tasks >= 15 | 15 |
| follow_up_trees == 15 | 15 |
| roles >= 8 | 10 |
| workflows >= 5 | 5 |
| docs >= 6 | 6 |
| pain_points >= 8 | 8 |
| Tree node count 5-8 | All trees pass |
| Tree branching >=2 | All trees pass |
| Tree fallback >=2 | All trees pass |
| Tree leaf >=1 | All trees pass |
| Children reference integrity | All valid |
| Tree-task_type matching | All matched |
| Variant coverage (15/15) | All pass |
| python build_packs.py exit 0 | Yes |
| Full test suite 51/51 | PASS |

## Task Commits

| Task | Message | Hash | Files |
|------|---------|------|-------|
| 4 | feat(02-knowledge-layer): expand Internet/IT pack terms to 90, roles to 10, workflows to 5 | 8c7f7fc | 01-internet-it.yaml |
| 5 | feat(02-knowledge-layer): expand Internet/IT pack scenarios to 15 and follow-up trees to 15 | 92e4863 | 01-internet-it.yaml |
| 6 | test(02-knowledge-layer): update thresholds and variant checks to KNOW-04 standard | 19262c9 | test_content.py |

## Deviations from Plan

- **Build system import path**: Running `pytest tests/` directly fails on `test_build.py` and `test_schema.py` because `build_packs.py` is at project root but not added to sys.path. Workaround: use `python -m pytest tests/` which adds CWD to sys.path. This is a pre-existing issue from Phase 1, not caused by this plan.
- **YAML boolean interpretation**: The `po_q2` node in the performance optimization tree uses `"yes"` and `"no"` as option values. In the children dict mapping, these must be quoted (`"yes"`, `"no"`) to prevent YAML interpreting them as boolean True/False. Fixed during compilation.

## Threat Flags

None. All threat model mitigations apply:
- T-2-04: Pydantic validation at compile time catches all structural errors
- T-2-05: BFS cycle detection in build_packs.py catches circular tree references
- T-2-SC: No new packages installed

## Known Stubs

None. All knowledge pack content is fully authored with no placeholder or mock data.

## Self-Check: PASSED

- [x] All 3 commits present: 8c7f7fc, 92e4863, 19262c9
- [x] prompt_tool/knowledge_packs/01-internet-it.yaml exists (3420 lines)
- [x] tests/test_content.py updated (THRESHOLDS, VARIANT_CHECKS)
- [x] `python build_packs.py` exit 0
- [x] `python -m pytest tests/ -x --tb=short` 51/51 PASS
- [x] All dimension counts meet or exceed KNOW-04 thresholds
- [x] All 15 follow-up trees pass quality checks
