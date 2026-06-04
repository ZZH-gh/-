# Phase 5: Generation v2 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-04
**Phase:** 5-generation-v2
**Areas discussed:** 模块架构, 4级知识注入结构, 知识选择策略, 反模式过滤规则

---

## 模块架构

| Option | Description | Selected |
|--------|-------------|----------|
| 新建 generator_v2.py | 保持 generator.py 不动，新建独立模块 | |
| 重构现有 generator.py | 直接在 generator.py 中重构，替换旧模板逻辑 | ✓ |
| 拆成多文件包 | 新建 prompt_tool/synthesizer/ 包 | |

**User's choice:** 重构现有 generator.py
**Notes:** 与 v3.0 代码共存，不破坏现有功能

---

| Option | Description | Selected |
|--------|-------------|----------|
| 向后兼容，换类名 | PromptGeneratorV2 + PromptGenerator 留别名 | ✓ |
| 显式切换，改类名 | IntentDrivenGenerator，app.py 显式选择 | |
| 接口不变，内部重写 | 保持 PromptGenerator 类名和 generate_all() 不变 | |

**User's choice:** 向后兼容，换类名
**Notes:** PromptGeneratorV2 是新类，PromptGenerator 保留为别名

---

| Option | Description | Selected |
|--------|-------------|----------|
| app.py 通过开关分流 | app.py 根据 is_v4_flow 分流 | |
| 封装在 ConversationEngine 内 | ConversationEngine.generate_complete() 内部调用 | ✓ |
| v4 独占，v3 做降级 | v4 只调新版，v3 功能由旧分支保留 | |

**User's choice:** 封装在 ConversationEngine 内
**Notes:** app.py 不关心用哪个生成器，ConversationEngine 统一编排

---

| Option | Description | Selected |
|--------|-------------|----------|
| ConversationEngine 直接调用 | generate_complete() 直接调 PromptGeneratorV2 | ✓ |
| 中间加 SynthesisService | 抽取 PromptSynthesisService | |

**User's choice:** ConversationEngine.generate_complete() 直接调用
**Notes:** 不引入中间服务层，保持调用链简洁

---

## 4级知识注入结构

| Option | Description | Selected |
|--------|-------------|----------|
| 固定顺序段落 | 角色深度 → 质量标准 → 输出结构 → 反模式警告 | ✓ |
| 融合到提示词正文 | 四个维度融入各个段落中 | |
| 带标题的独立 Section | 用 ## 标题明确分区 | |

**User's choice:** 固定顺序段落
**Notes:** 按固定顺序排布，不额外加标题标记

---

| Option | Description | Selected |
|--------|-------------|----------|
| 知识包驱动 | 从 get_roles() 提取角色名+职责+KPI | |
| 混合模式 | 保留 v3 角色逻辑+知识包描述 | |
| 按任务匹配专业角色 | PRD→产品经理, 代码→架构师 | ✓ |

**User's choice:** 按任务匹配专业角色
**Notes:** 角色深度与任务类型绑定

---

| Option | Description | Selected |
|--------|-------------|----------|
| 行业场景质量标准 | 从知识包场景和流程提取 | |
| 通用+行业混合 | 通用标准 + 行业特有标准 | ✓ |
| 简略提示 | 一句话提示，靠 AI 自行判断 | |

**User's choice:** 通用+行业混合
**Notes:** 通用：清晰/具体/可执行；行业特有：从知识包场景提取

---

| Option | Description | Selected |
|--------|-------------|----------|
| 锁定格式模板 | 从知识包文档规范提取固定模板 | ✓ |
| 松散格式指引 | 仅提示"请按行业标准格式" | |
| 框架+要点 | 给出结构框架+内容要点 | |

**User's choice:** 锁定格式模板
**Notes:** 从知识包 get_doc_template() 提取，如 PRD 的 背景→目标→范围→方案→风险

---

| Option | Description | Selected |
|--------|-------------|----------|
| 根据数据存在性决定 | 知识包有数据才注入 | |
| 始终保留四个段落 | 内容多少不同，段落存在 | |
| 按任务类型选择 | 任务决定哪些维度出现 | ✓ |

**User's choice:** 按任务类型选择
**Notes:** 每个注入点有独立开关，由任务类型控制

---

## 知识选择策略

| Option | Description | Selected |
|--------|-------------|----------|
| 仅任务相关 | 只取当前任务的直接相关知识 | |
| 任务+行业背景 | 任务相关内容 + 行业核心概述 | ✓ |
| 全量注入 | 尽可能多的相关知识 | |

**User's choice:** 任务+行业背景
**Notes:** 折中方案，不过度也不遗漏

---

| Option | Description | Selected |
|--------|-------------|----------|
| 精选 3-5 个术语 | 高权重术语+一句话定义 | |
| 场景全部术语 | 当前场景全部术语+简短定义 | ✓ |
| 作为参考列表 | 仅列出术语名称 | |

**User's choice:** 场景全部术语
**Notes:** 8-15 个术语，每个附简短定义

---

| Option | Description | Selected |
|--------|-------------|----------|
| 注入核心流程 | 场景核心流程关键步骤 | |
| 注入 KPI+痛点 | 角色相关 KPI 和常见痛点 | ✓ |
| 整合为行业背景段 | 统一放在行业背景段落 | |

**User's choice:** 注入 KPI+痛点
**Notes:** 用于帮助 AI 理解质量标准和用户关注点

---

## 反模式过滤规则

| Option | Description | Selected |
|--------|-------------|----------|
| 关键词+正则规则 | 已知虚假表述的规则列表 | |
| 知识包痛点驱动 | 检查提示词是否与痛点清单冲突 | ✓ |
| 规则+知识包双重检查 | 两阶段检测 | |

**User's choice:** 知识包痛点驱动
**Notes:** 痛点清单中的每项可映射到具体过滤规则

---

| Option | Description | Selected |
|--------|-------------|----------|
| 去掉虚假权威用语 | "行业领先""最佳实践"等 | |
| 去掉行业刻板印象 | "销售就是忽悠"等 | |
| 两个都做 | 两者都检测过滤 | ✓ |

**User's choice:** 两个都做
**Notes:** 同时过滤虚假权威表述和行业刻板印象

---

| Option | Description | Selected |
|--------|-------------|----------|
| 自动替换后展示 | 过滤后直接展示 | ✓ |
| 仅警告不修改 | 标注 ⚠ 让用户决定 | |
| 生成时直接规避 | 合成逻辑中避免反模式 | |

**User's choice:** 自动替换后展示
**Notes:** 用户看到的是过滤后的最终版本

---

## Claude's Discretion

- 三种策略（直给式/角色式/完整式）的 v2 差异化方案
- 生成长度控制策略
- 核心流程（workflow）是否注入
- PromptGeneratorV2 的 generate_all() 返回值格式
- 反模式替换策略（替换为正确描述 vs 仅删除）
- is_v4_flow 标志在 app.py 中的判断逻辑

## Deferred Ideas

- 3 种策略的 v2 差异化方案 — 由规划者基于 GEN-03 设计
- 生成长度控制 — 由规划者设计合理截断机制
- JMESPath 查询接口 — 本阶段暂不用
