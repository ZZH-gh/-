# Roadmap: 智能提示词工坊 v4.0

## Overview

从 v3.0 的扁平关键词匹配和模板填充，升级为知识包驱动、对话式需求挖掘的深度提示词生成工具。8 个 MVP 阶段，每个阶段交付端到端可验证的用户能力：先打好知识包基础设施，依次构建知识层、上下文层、对话引擎、生成器，接上对话式 UI，再扩展行业覆盖，最后打包分发。

## Phases

- [ ] **Phase 1: Foundation** — 知识包 Schema + 构建管线 + 互联网/IT 行业知识包
- [ ] **Phase 2: Knowledge Layer** — Loader、Manager、懒加载机制
- [ ] **Phase 3: Context Layer** — 会话状态管理与上下文构建
- [ ] **Phase 4: Conversation Core** — 状态机引擎 + 意图分类器 + 追问树遍历器
- [ ] **Phase 5: Generation v2** — 意图驱动合成 + 4 级知识注入
- [ ] **Phase 6: UI** — 对话式交互界面 + AppController
- [ ] **Phase 7: Scale** — 剩余 4 个核心行业知识包
- [ ] **Phase 8: Packaging** — PyInstaller --onedir 打包 + 中文兼容测试

## Phase Details

### Phase 1: Foundation

**Goal**: 知识包数据结构定义完毕，编译管线可用，首个行业包可通过构建验证
**Mode**: mvp
**Depends on**: Nothing (first phase)
**Requirements**: KNOW-01, KNOW-02, KNOW-09, QA-01
**Success Criteria** (what must be TRUE):

  1. 行业知识包 JSON Schema 定义完整，涵盖术语、场景、角色、KPI、流程、文档规范、追问树、痛点 8 个维度
  2. YAML 源文件可通过编译脚本生成 JSON，编译时自动校验结构完整性
  3. 互联网/IT 行业知识包 V1 编写完成，通过深度检查清单（QA-01）
  4. 构建验证脚本在数据缺失或结构错误时给出明确错误提示

**Plans**: 2 plans
Plans:
**Wave 1**

- [ ] 01-01-PLAN.md — Schema + 编译管线 + 测试基础设施 + 最小桩知识包

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 01-02-PLAN.md — 互联网/IT 知识包 V1 完整内容 + QA-01 深度验证

### Phase 2: Knowledge Layer

**Goal**: 知识包可在运行时加载、索引、按需获取
**Mode**: mvp
**Depends on**: Phase 1
**Requirements**: KNOW-03, KNOW-04
**Success Criteria** (what must be TRUE):

  1. 启动时仅加载索引(~5KB)，识别行业后按需加载完整知识包(~300KB)
  2. 互联网/IT 行业知识包完成编写并通过深度检查（术语80+、场景15+、追问树3+）
  3. KnowledgeManager 提供行业匹配查询接口，返回置信度排名的行业列表
  4. KnowledgePack 提供 typed 访问方法（get_terms, get_workflows, get_follow_up_tree 等）

**Plans**: TBD

### Phase 3: Context Layer

**Goal**: 多轮对话的会话状态可被追踪和持久化
**Mode**: mvp
**Depends on**: Phase 2
**Requirements**: CONV-06
**Success Criteria** (what must be TRUE):

  1. 会话上下文记录用户选择、已答问题、推导出的上下文信息，跨轮次可追踪
  2. ConversationTurn 记录每个轮次的角色、内容、类型和时间戳
  3. ContextBuilder 能从原始上下文构建出供生成器使用的 GenerationContext
  4. SessionManager 线程安全，支持多会话隔离

**Plans**: TBD

### Phase 4: Conversation Core

**Goal**: 系统能像资深顾问一样反问补全信息，支撑有深度的多轮对话
**Mode**: mvp
**Depends on**: Phase 3
**Requirements**: CONV-01, CONV-02, CONV-03, CONV-04, CONV-05
**Success Criteria** (what must be TRUE):

  1. 用户输入后，系统自动进入分析-确认-追问流程，而非直接出结果
  2. 首轮最多问 3 个问题，之后立即生成草案（硬限制 CONV-04）
  3. 用户说"不知道"时，系统 3 级渐进简化（简化问题→更宽泛分类→示例引导）
  4. 追问决策树支持单选/多选/文本输入/确认四种节点类型，行业/任务感知
  5. 意图分类器返回置信度评分，低置信度自动进入澄清流程

**Plans**: TBD

### Phase 5: Generation v2

**Goal**: 生成有行业深度、自然、不模板化的提示词
**Mode**: mvp
**Depends on**: Phase 4
**Requirements**: GEN-01, GEN-02, GEN-03, GEN-04, QA-02
**Success Criteria** (what must be TRUE):

  1. 生成的提示词包含角色深度、质量标准、输出结构、反模式警告四个知识注入点（GEN-02）
  2. 直给式/角色式/完整式三种策略均融入知识包内容，而非纯模板填充（GEN-03）
  3. 生成的提示词中无虚假权威表述和刻板信息（反模式过滤生效，GEN-04）
  4. QA-02 评估显示 v4.0 生成质量显著优于 v3.0 模板式输出
  5. 生成基于对话上下文+知识包组合，而非 keyword-to-template 映射

**Plans**: TBD

### Phase 6: UI

**Goal**: 用户通过对话界面自然交互，随时可获取结果
**Mode**: mvp
**Depends on**: Phase 5
**Requirements**: UI-01, UI-02, UI-03, UI-04, QA-03
**Success Criteria** (what must be TRUE):

  1. 对话式交互界面呈现一问一答气泡流，输入区→对话流→结果展示自然过渡（UI-01）
  2. 任何时候用户可点"立即生成"跳过追问，直接获得初版提示词（UI-02）
  3. 生成后可进一步细化：追加要求、换风格、加限制（UI-03）
  4. 用户可查看当前行业知识包概览（UI-04）
  5. 金融/制造等敏感行业的提示词内容包含合规声明（QA-03）

**Plans**: TBD
**UI hint**: yes

### Phase 7: Scale

**Goal**: 4 个核心行业知识包完成深度建设
**Mode**: mvp
**Depends on**: Phase 2 (知识层基础设施), Phase 6 (UI 可展示所有行业)
**Requirements**: KNOW-05, KNOW-06, KNOW-07, KNOW-08
**Success Criteria** (what must be TRUE):

  1. 销售/零售行业知识包完成（术语60+、场景10+、追问树2+）
  2. 教育行业知识包完成（术语60+、场景10+、追问树2+）
  3. 金融行业知识包完成（术语60+、场景10+、追问树2+）
  4. 制造业行业知识包完成（术语60+、场景10+、追问树2+）
  5. 每个包通过 QA-01 深度检查清单

**Plans**: TBD

### Phase 8: Packaging

**Goal**: 最终产物为 <50MB 的单文件目录 exe，中文 Windows 双击即用
**Mode**: mvp
**Depends on**: Phase 7
**Requirements**: PKG-01, PKG-02, PKG-03
**Success Criteria** (what must be TRUE):

  1. PyInstaller 从 --onefile 迁移到 --onedir 模式，启动时间 < 3 秒（PKG-01）
  2. 行业知识包 gzip 压缩后内置到 exe，按需解压加载（PKG-02）
  3. 在中文 Windows 10/11 系统、含中文用户名的路径下正常启动和运行（PKG-03）
  4. 最终 exe 体积 < 50MB

**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 0/2 | Not started | - |
| 2. Knowledge Layer | 0/0 | Not started | - |
| 3. Context Layer | 0/0 | Not started | - |
| 4. Conversation Core | 0/0 | Not started | - |
| 5. Generation v2 | 0/0 | Not started | - |
| 6. UI | 0/0 | Not started | - |
| 7. Scale | 0/0 | Not started | - |
| 8. Packaging | 0/0 | Not started | - |

---

*Roadmap created: 2026-06-03*
