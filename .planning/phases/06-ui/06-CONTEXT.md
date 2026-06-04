# Phase 6: UI - Context

**Gathered:** 2026-06-04
**Status:** Ready for planning

<domain>
## Phase Boundary

将 v3.0 的单页输入→标签页展示界面改造为 v4.0 的对话式交互界面。提供自然的一问一答体验，支持"立即生成"逃生门、结果三卡对比展示、结果优化面板，以及知识包可见性和合规声明。

**本阶段交付：** 对话界面（问答卡片水平交替）、逃生门按钮、结果展示（三卡横向对比）、优化侧栏面板。
**本阶段不包含：** 知识包扩展（Phase 7）、打包改动（Phase 8）。

</domain>

<decisions>
## Implementation Decisions

### 整体布局架构
- **D-01:** 采用页面切换模式——v4.0 界面完全替换 v3.0 界面（保留 v3.0 代码但默认隐藏）。进入应用时显示对话界面，生成后切换到结果展示界面。
- **D-02:** 页面切换通过 customtkinter 的帧切换实现（grid_remove/pack_forget 切换不同 Frame），不依赖额外包。
- **D-03:** 结果展示界面采用三卡横向对比布局，三种策略同时可见，方便用户对比差异。
- **D-04:** 结果界面保留"返回对话"按钮，用户可以回到对话修改行业或补充信息。
- **D-05:** 底部始终保留"新对话"按钮，用户可随时重新开始。

### 对话交互样式
- **D-06:** 问答卡片水平交替排列——用户输入显示在左侧（紧凑型），系统回复显示在右侧（展开式，带结构化信息）。
- **D-07:** 追问环节采用底部输入框自由回答模式。系统追问显示为右侧卡片，用户在底部输入框输入答案后提交。
- **D-08:** 系统显示支持文本、选项按钮（单选/多选）、确认提示等多种消息类型。

### 逃生门
- **D-09:** "立即生成"按钮放在底部输入框旁边，用户随时可点击提交当前信息直接生成提示词（UI-02）。
- **D-10:** 点击逃生门后跳过剩余追问，使用当前已收集的信息调用 ConversationEngine.generate_complete()。

### 结果优化面板
- **D-11:** 在结果界面右侧固定一个优化侧栏面板，包含"追加要求"输入框、"换风格"下拉菜单、"加限制"多选框。
- **D-12:** 用户提交优化请求后，重新生成全部三张策略卡（重新走 ConversationEngine → PromptGeneratorV2 流程）。
- **D-13:** 优化面板默认展开，用户可收起以让三卡展示更宽。

### Claude's Discretion
- 对话界面的具体颜色方案和气泡样式细节
- 知识包可见性（UI-04）的具体展示方式——侧栏面板、模态框或可展开区域
- 合规声明（QA-03）的展示位置和触发条件
- 优化面板中"换风格"具体有哪些风格选项
- 三卡布局中每张卡的高度同步策略（同步滚动 vs 独立滚动）
- 对话消息的历史记录滚动行为

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 项目文档
- `.planning/ROADMAP.md` § Phase 6 — 阶段目标与成功标准
- `.planning/REQUIREMENTS.md` § UI-01~04, QA-03 — 需求定义
- `.planning/PROJECT.md` — 项目核心价值和约束

### 前置阶段关键文档
- `.planning/phases/04-conversation-core/04-01-SUMMARY.md` — ConversationEngine 接口
- `.planning/phases/05-generation-v2/05-CONTEXT.md` — PromptGeneratorV2 输出格式
- `.planning/phases/05-generation-v2/05-01-SUMMARY.md` — 生成器具体接口

### 现有代码（参考模式）
- `prompt_tool/app.py` — 重构目标，现有 PromptToolApp 类
- `prompt_tool/conversation_engine.py` — ConversationEngine 生成流程
- `prompt_tool/session_manager.py` — 会话管理

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `prompt_tool/app.py` — 现有单页布局（标题栏+输入区+信息条+策略标签+状态栏），Frame 切换可复用
- `prompt_tool/conversation_engine.py` — 提供完整的对话状态机和生成流程
- `prompt_tool/session_manager.py` — 追踪用户选择和已答问题

### Established Patterns
- customtkinter Frame + grid layout 构建 UI
- daemon thread + self.root.after() 异步结果处理
- `is_v4_flow` 标志分流 v3/v4 路径

### Integration Points
- `prompt_tool/app.py` — 新增 v4 对话界面 Frame 和结果展示 Frame，通过帧切换显示
- `prompt_tool/conversation_engine.py` — 对话界面调用 engine.start() → handle_answer() → generate_complete()
- Phase 4/5 生成的 ConversationEngine + PromptGeneratorV2 作为对话流程的后端驱动

</code_context>

<specifics>
## Specific Ideas

- 优化面板的"换风格"可包括：更简洁/更详细/更专业/更通俗四种风格切换
- 对话界面的输入框可包含发送按钮（▶），与"立即生成"按钮并列
- 三卡横向布局中，每张策略卡包含：标题+内容+Copied按钮+优化按钮
- 知识包可见性可以放在标题栏的一个"📚 知识包概览"按钮，点击弹出知识包内容面板

</specifics>

<deferred>
## Deferred Ideas

- 知识包可见性（UI-04）的具体展示方式——由规划者或 Claude 判断
- 合规声明（QA-03）——由规划者设计合规声明的触发条件和展示方式
- 暗色主题（v2 功能）
- 提示词效果评分反馈机制（v2 功能）

</deferred>

---

*Phase: 6-UI*
*Context gathered: 2026-06-04*
