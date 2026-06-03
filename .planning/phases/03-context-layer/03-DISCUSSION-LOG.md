# Phase 3: Context Layer - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-03
**Phase:** 3-context-layer
**Areas discussed:** 会话数据模型

---

## 会话数据模型

### ConversationTurn / SessionState 结构

| Option | Description | Selected |
|--------|-------------|----------|
| 简洁模型 | ConversationTurn(role+content+turn_type+timestamp), SessionState(id+created_at+turns+confirmed_industry+confirmed_task+extracted_info) | ✓ |
| 丰富模型 | 增加 intent_classification、knowledge_pack_ref、context_summary | |
| 极简模型 | 只有 role+content+timestamp，无预设 turn_type | |

**User's choice:** 简洁模型（推荐）

### 知识包关联方式

| Option | Description | Selected |
|--------|-------------|----------|
| 引用方式 | SessionState 存 industry_id，生成器通过 KnowledgeManager 按需查 | ✓ |
| ID + 版本号快照 | 存储 ID + version，用于一致性校验 | |

**User's choice:** 引用方式（推荐）

### 会话生命周期

| Option | Description | Selected |
|--------|-------------|----------|
| 单会话 | 只管理一个活跃会话，new_session() 替换旧会话 | ✓ |
| 多会话预留 | 支持多会话隔离，为未来扩展 | |

**User's choice:** 单会话（推荐）

### ContextBuilder 输出格式

| Option | Description | Selected |
|--------|-------------|----------|
| dict 输出 | ContextBuilder.build() → dict，字段 industry_id/task_type/confirmed_info/conversation_summary | ✓ |
| dataclass 类型 | GenerationContext dataclass，类型安全但风格不一致 | |

**User's choice:** dict 输出（推荐）

### 线程安全机制

| Option | Description | Selected |
|--------|-------------|----------|
| 主线程写 + 后台读 | 不加锁，依赖 Python GIL，与 Phase 2 D-08 一致 | ✓ |
| 加锁保护 | threading.Lock 保护所有读写 | |

**User's choice:** 主线程写 + 后台读（推荐）

---

## Claude's Discretion

- conversation_summary 摘要算法（最近 N 轮拼接 vs 关键词提取）
- extracted_info 字典 key 的命名规范
- ContextBuilder 实现方式（独立类 vs SessionManager 方法）
- 会话 ID 生成方式（uuid4 vs 时间戳）
- SessionManager 模块组织（独立文件 vs 合并）
- new_session() 替换旧会话时的回调通知

## Deferred Ideas

- 会话磁盘持久化 — 后续增强
- 多会话切换 — v2 功能
- 会话导出/导入 — v2 功能
