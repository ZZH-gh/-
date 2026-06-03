# Phase 2: Knowledge Layer - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-03
**Phase:** 2-knowledge-layer
**Areas discussed:** 索引结构设计, 懒加载触发时机, 知识包扩展范围

---

## 索引结构设计

### 索引内容

| Option | Description | Selected |
|--------|-------------|----------|
| 关键词索引 | 索引包含行业 meta + 关键词列表 + 统计信息，匹配方式与现有 engine._identify_industry() 一致，改动最小 | ✓ |
| 术语预览索引 | 索引包含前 10 个高频术语定义，体积更大（~15KB）但减少后续加载 | |
| 场景感知索引 | 索引包含场景列表和任务类型，匹配更精确但索引结构更复杂 | |

**User's choice:** 关键词索引（推荐）
**Notes:** 使用 confidence-ranked 匹配。

### 索引生成方式

| Option | Description | Selected |
|--------|-------------|----------|
| build_packs.py 自动生成 | 编译 JSON 时从 meta + terms 提取关键词生成 index.json | ✓ |
| 手写 index.yaml | YAML 源文件独立管理 | |
| 运行时扫描 | 启动时扫描 JSON meta 段动态构建 | |

**User's choice:** build_packs.py 自动生成（推荐）

### 行业匹配集成方式

| Option | Description | Selected |
|--------|-------------|----------|
| 独立匹配层 | KnowledgeManager 提供 match_industry() 替代 engine._identify_industry() | ✓ |
| 保留 engine 匹配 | engine.py 匹配不动，KnowledgeManager 仅负责加载 | |
| 合并升级 | 匹配逻辑全部迁移到 KnowledgeManager | |

**User's choice:** 独立匹配层（推荐）

---

## 懒加载触发时机

### 加载触发时机

| Option | Description | Selected |
|--------|-------------|----------|
| 行业确认后加载 | 确认行业 → 立即加载完整包，后续所有操作直接使用内存数据 | ✓ |
| 自动静默加载 | 后台直接加载，用户无感知但有浪费风险 | |
| 分段按需加载 | 先术语表→再角色/流程/痛点，追问→生成切换时有停顿 | |

**User's choice:** 行业确认后加载（推荐）

### 缓存策略

| Option | Description | Selected |
|--------|-------------|----------|
| 单例缓存 + LRU（容量 2） | 当前包 + 上一个包保留在内存，切换行业大概率命中缓存 | ✓ |
| 仅缓存当前包 | 切换时立即释放，最省内存但需重新解析 JSON | |
| 全预加载 | 启动时加载所有行业包，最快但浪费内存 | |

**User's choice:** 单例缓存 + LRU（推荐）

### 运行时数据结构

| Option | Description | Selected |
|--------|-------------|----------|
| Python dict + 辅助方法 | json.load() 解析为 dict，KnowledgePack 包装类提供 getter 方法 | ✓ |
| Pydantic/dataclass | 类型安全但增加运行时依赖 | |
| JMESPath 查询 | 灵活查询但需要 jmespath 依赖 | |

**User's choice:** Python dict + 辅助方法（推荐）

### engine 集成方式

| Option | Description | Selected |
|--------|-------------|----------|
| engine 调用 KnowledgeManager | engine.py 通过 knowledge_manager 获取知识包数据 | ✓ |
| KnowledgeManager 替代 engine | 分析逻辑整体迁移 | |
| generator.py 直接使用 | engine 只做匹配，generator 取知识包做生成 | |

**User's choice:** engine 调用 KnowledgeManager（推荐）

### 线程安全

| Option | Description | Selected |
|--------|-------------|----------|
| 不需要锁 | 单线程访问，dict 只读天然安全 | ✓ |
| 加锁保护 | 防止极端并发 | |
| 线程局部存储 | 每线程独立副本 | |

**User's choice:** 不需要 — 单线程访问（推荐）

### 文件分发方式

| Option | Description | Selected |
|--------|-------------|----------|
| knowledge_packs_compiled/ 随包分发 | 编译产物作为 package_data 打包进 exe | ✓ |
| 独立 data 目录 | exe 同级目录，方便替换但增加分发复杂度 | |
| 单文件内嵌 | base64 内嵌到代码中 | |

**User's choice:** knowledge_packs_compiled/ 随包分发（推荐）

### 错误处理

| Option | Description | Selected |
|--------|-------------|----------|
| fallback 到 v3.0 knowledge.py | 加载失败时静默回退，状态栏警告但不断路 | ✓ |
| 硬错误 | 弹窗报错，拒绝启动 | |
| 降级模式 | 空包替代，生成质量大幅下降 | |

**User's choice:** fallback 到 v3.0 knowledge.py（推荐）

### 初始化方式

| Option | Description | Selected |
|--------|-------------|----------|
| 模块级单例 | 全局 import，类似 default_engine 模式 | ✓ |
| PromptToolApp 实例属性 | 依赖注入，但改动面大 | |
| 延迟初始化 | 首次调用时初始化 | |

**User's choice:** 模块级单例（推荐）

### 查询接口设计

| Option | Description | Selected |
|--------|-------------|----------|
| 核心 getter 方法集 | get_terms()/get_task()/get_roles() 等覆盖所有维度 | ✓ |
| 极简接口 | 只返回 dict，调用方自己访问 | |
| JMESPath 查询 | 灵活但需要额外依赖 | |

**User's choice:** 核心 getter 方法集（推荐）

### 索引文件位置

| Option | Description | Selected |
|--------|-------------|----------|
| 同目录，编译时生成 | index.json 在 knowledge_packs_compiled/ 中与 JSON 同级 | ✓ |
| 独立 index 目录 | 子目录分离 | |
| 内嵌在代码中 | Python 常量，最快但需重新编译 | |

**User's choice:** 同目录，编译时生成（推荐）

---

## 知识包扩展范围

### Internet/IT 扩展程度

| Option | Description | Selected |
|--------|-------------|----------|
| 达标 KNOW-04 | 扩展到 80+ 术语/15+ 场景/3+ 追问树 | ✓ |
| 适度扩展 | 50+ 术语/10 场景 | |
| 保持 36/5 不变 | 只做基础设施，内容留给阶段 7 | |

**User's choice:** 达标 KNOW-04（推荐）
**Notes:** 为阶段 5（生成器）准备足够的真实数据。

### 新场景覆盖方向

| Option | Description | Selected |
|--------|-------------|----------|
| 覆盖更多 IT 子领域 | 面试招聘、项目管理、运维部署、UI/UX、测试、架构、数据库、安全、性能、协作 | ✓ |
| 深化现有场景 | 5 个场景不变，增加子场景和变体 | |
| 混合策略 | 7 个新场景 + 3 个深度变体 | |

**User's choice:** 覆盖更多 IT 子领域（推荐）

---

## Claude's Discretion

- KnowledgePack 各 getter 方法具体参数签名和返回值类型
- index.json 的完整 JSON schema 字段
- LRU 缓存的实现方式（collections.OrderedDict 或自定义链表）
- KnowledgeManager.initialize() 的调用时机
- 追问树的运行时数据结构转换方式

## Deferred Ideas

- JMESPath 查询接口 — D-11 技术栈包含，但本阶段先用 dict + getter，后续需要时再引入
- 运行时知识包热更新 — v2 功能
- 用户自定义知识包编辑器 — v2 功能
- 其他 4 个行业包 — 阶段 7
