# Requirements: 智能提示词工坊 v4.0

**Defined:** 2026-06-03
**Core Value:** 让不懂写提示词的普通人，用最简短的语言，最快拿到能让AI真正干活的、有行业深度的提示词

## v1 Requirements

### 知识包体系 (KNOW)

- [x] **KNOW-01**: 知识包数据结构定义 — 设计完整的行业知识包 JSON Schema（术语表、场景、角色、KPI、流程、文档规范、追问树、痛点）
- [x] **KNOW-02**: YAML→JSON 编译管线 — 知识包用 YAML 编写，编译为 JSON 供运行时加载
- [x] **KNOW-03**: 懒加载机制 — 启动时仅加载索引(~5KB)，识别行业后按需加载完整知识包(~300KB)
- [x] **KNOW-04**: 互联网/IT 行业知识包 — 完成首个完整行业包（术语80+、场景15+、追问树3+）
- [ ] **KNOW-05**: 销售/零售行业知识包
- [ ] **KNOW-06**: 教育行业知识包
- [ ] **KNOW-07**: 金融行业知识包
- [ ] **KNOW-08**: 制造业知识包
- [x] **KNOW-09**: 知识包构建验证脚本 — 编译时自动校验知识包结构完整性

### 对话式需求挖掘 (CONV)

- [x] **CONV-01**: 状态机对话引擎 — 9 种会话状态（IDLE→ANALYZING→CONFIRMING→CLARIFYING→GENERATING→COMPLETE 等）
- [x] **CONV-02**: 意图分类器 v2 — 基于知识包索引的行业/任务识别，带置信度评分
- [x] **CONV-03**: 追问逻辑树遍历器 — JSON 定义的决策树，支持单选/多选/文本输入/确认四种节点类型
- [x] **CONV-04**: 3 问题硬限制 — 首轮最多问 3 个问题，之后立即生成草案
- [x] **CONV-05**: "我不知道"降级处理 — 3 级渐进简化（简化问题→更宽泛分类→示例引导）
- [x] **CONV-06**: 会话上下文管理 — 跨轮次追踪用户选择、已答问题、推导出的上下文

### 提示词生成 v2 (GEN)

- [ ] **GEN-01**: 意图驱动合成器 — 基于对话上下文+知识包组合提示词，替代模板填充
- [ ] **GEN-02**: 4 级知识注入 — 角色深度、质量标准、输出结构、反模式警告四个注入点
- [ ] **GEN-03**: 3 种策略升级 — 更新直给式/角色式/完整式三种生成策略，融入知识包内容
- [ ] **GEN-04**: 反模式过滤 — 自动检测并移除生成提示词中的虚假权威表述和刻板信息

### 用户界面 (UI)

- [ ] **UI-01**: 对话式交互界面 — 输入区→对话流气泡→结果展示，自然一问一答体验
- [ ] **UI-02**: "立即生成"逃生门 — 任何时候可跳过追问，直接生成初版提示词
- [ ] **UI-03**: 结果优化面板 — 生成后可进一步细化：追加要求、换风格、加限制
- [ ] **UI-04**: 知识包可见性 — 用户可查看当前行业知识包概览，了解工具覆盖范围

### 打包与分发 (PKG)

- [ ] **PKG-01**: --onedir 打包迁移 — 从 --onefile 迁移到 --onedir 模式以支持知识包增长
- [ ] **PKG-02**: 知识包压缩 — gzip 压缩行业知识包，按需解压加载
- [ ] **PKG-03**: 中文 Windows 兼容测试 — 验证非 ASCII 用户名路径、中文系统下的兼容性

### 质量与治理 (QA)

- [x] **QA-01**: 行业深度完成标准 — 每个行业包必须通过深度检查清单才能标记为完成
- [ ] **QA-02**: 提示词质量评估 — 建立评估机制，对比 v3.0 模板 vs v4.0 知识包生成的提示词质量
- [ ] **QA-03**: 受管制行业内容审查 — 金融/医疗等敏感行业的提示词内容合规检查

## v2 Requirements

- **KNOW-10**: 用户自定义知识包编辑器
- **CONV-07**: 深度追问模式（不限问题数，专家模式）
- **CONV-08**: 跨会话历史记忆
- **GEN-05**: 多语言提示词生成
- **UI-05**: 暗色主题支持
- **UI-06**: 提示词效果评分反馈机制
- **PKG-04**: NSIS 安装包（含桌面快捷方式、文件关联）
- **PKG-05**: 在线知识包更新机制

## Out of Scope

| Feature | Reason |
|---------|--------|
| 运行时间调用 LLM API | 离线的核心承诺不变 |
| Web/移动端版本 | 先做好 Windows 桌面体验 |
| 16 行业全覆盖 | v4.0 硬上限为 5 个行业，做深不做广 |
| 用户自定义知识包编辑器 | v2 功能，知识包结构稳定后再开放 |
| 多语言支持 | v4.0 专注中文 |
| 实时协作 | 非核心需求 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| KNOW-01 | Phase 1 | Complete |
| KNOW-02 | Phase 1 | Complete |
| KNOW-09 | Phase 1 | Complete |
| QA-01 | Phase 1 | Complete |
| KNOW-03 | Phase 2 | Complete |
| KNOW-04 | Phase 2 | Complete |
| CONV-06 | Phase 3 | Complete |
| CONV-01 | Phase 4 | Complete |
| CONV-02 | Phase 4 | Complete |
| CONV-03 | Phase 4 | Complete |
| CONV-04 | Phase 4 | Complete |
| CONV-05 | Phase 4 | Complete |
| GEN-01 | Phase 5 | Pending |
| GEN-02 | Phase 5 | Pending |
| GEN-03 | Phase 5 | Pending |
| GEN-04 | Phase 5 | Pending |
| QA-02 | Phase 5 | Pending |
| UI-01 | Phase 6 | Pending |
| UI-02 | Phase 6 | Pending |
| UI-03 | Phase 6 | Pending |
| UI-04 | Phase 6 | Pending |
| QA-03 | Phase 6 | Pending |
| KNOW-05 | Phase 7 | Pending |
| KNOW-06 | Phase 7 | Pending |
| KNOW-07 | Phase 7 | Pending |
| KNOW-08 | Phase 7 | Pending |
| PKG-01 | Phase 8 | Pending |
| PKG-02 | Phase 8 | Pending |
| PKG-03 | Phase 8 | Pending |

**Coverage:**

- v1 requirements: 29 total
- Mapped to phases: 29
- Unmapped: 0 ✓

---
*Requirements defined: 2026-06-03*
*Last updated: 2026-06-03 after roadmap creation*
