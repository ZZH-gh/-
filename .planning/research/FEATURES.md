# Feature Landscape: Industry Knowledge Packs for Prompt Generation

**Domain:** Offline industry knowledge packs for deep, nuanced prompt generation
**Researched:** 2026-06-03
**Confidence:** MEDIUM (synthesized from training knowledge; web verification was unavailable)

---

## Knowledge Dimension Model

An industry knowledge pack needs **8 content dimensions** to enable truly deep prompt generation. Each dimension answers a specific question that arises during prompt construction.

```
KNOWLEDGE PACK STRUCTURE
==========================
1. Industry Fundamentals    ─ What is this industry? (scope, boundaries, core concepts)
2. Terminology Dictionary   ─ What do words mean? (terms by level & context)
3. Common Task Scenarios    ─ What do users want to do? (10-15 high-frequency tasks)
4. Role Knowledge           ─ Who is the user? (jobs, KPIs, orgs, responsibilities)
5. Document Standards       ─ What does the output look like? (formats, templates, expectations)
6. Core Processes           ─ How does work flow? (steps, decision points, approvals)
7. Pain Points & Pitfalls   ─ What goes wrong? (gotchas, sensitive topics, landmines)
8. 追问逻辑树               ─ What should we ask next? (question trees by task)
```

---

## Dimension 1: Industry Fundamentals

**Purpose:** Let the AI understand the industry's nature, boundaries, and operating logic so it doesn't generate content that feels wrong for that world.

### What Each Pack Needs

| Sub-dimension | Description | Example (互联网/IT) | Example (制造业) |
|---------------|-------------|---------------------|-------------------|
| Scope definition | What's included and what's not | Software dev, but not hardware mfg | Discrete/process mfg, not logistics-only |
| Core business model | How value is created and captured | SaaS, ad-based, transaction fee | B2B contract mfg, OEM/ODM |
| Value chain | Key players upstream to downstream | User > DAU > feature > iteration | Raw material > process > QC > delivery |
| Industry lifecycle | Maturity stage | Mature but fast-moving | Stable with Industry 4.0 shifts |
| Key constraints | What limits the industry | Time-to-market, tech debt | Cost/unit, yield rate, safety regs |
| Typical org structure | How companies are organized | BU-based, squads, tribes | Factory + HQ + R&D + Supply Chain |
| Regulatory environment | What rules apply | Data privacy (PIPL), copyright | ISO9001, 安全生产, GB standards |

---

## Dimension 2: Terminology Dictionary

**Purpose:** Ensure generated prompts use industry-correct vocabulary, not generic language. This is the most visible sign of "depth" -- a prompt that sounds like an insider vs. an outsider.

### Three-Level Structure

```
Level 1: Industry-Wide Terms ─ understood by anyone in the industry
Level 2: Role-Specific Terms  ─ only used by certain job functions
Level 3: Scenario-Level Terms ─ only relevant in specific task contexts
```

### Example Extract: 互联网/IT

| Term | Level | Definition | Usage Context | Common Mistake |
|------|-------|------------|---------------|----------------|
| DAU/MAU | L1 | Daily/Monthly Active Users | Growth metrics, product health | Confusing with registered users |
| PRD | L2 | Product Requirements Document | PM role | Treating as technical spec |
| 埋点 | L2 | Event tracking/analytics instrumentation | Data team, PM | Not considering data schema design |
| 灰度发布 | L3 | Canary release / phased rollout | Deployment scenario | Skipping rollback plan |
| 技术债 | L1 | Technical debt | Any engineering discussion | Treating as purely negative |
| OKR | L1 | Objectives and Key Results | Goal setting | Making OKR = KPI |
| 迭代 | L1 | Sprint/iteration | Agile development | Skipping retrospective |
| 复盘 | L1 | Post-mortem / retrospective | After any milestone | Becoming blame session |

### Example Extract: 金融

| Term | Level | Definition | Usage Context | Common Mistake |
|------|-------|------------|---------------|----------------|
| 风控 | L1 | Risk control | Any financial operation | Treating as only credit risk |
| 合规 | L1 | Compliance | Regulatory operations | Over-relying on checklists |
| 非标 | L2 | Non-standard assets | Wealth management | Misunderstanding liquidity risk |
| 精算 | L2 | Actuarial science | Insurance product design | Confusing with accounting |
| 回测 | L3 | Backtesting | Quantitative strategy | Overfitting without out-of-sample |
| KYC | L1 | Know Your Customer | Account opening, compliance | One-time check vs continuous monitoring |

---

## Dimension 3: Common Task Scenarios

**Purpose:** Map the 10-15 highest-frequency tasks users actually need prompts for in each industry. This defines the "surface area" of what the tool can help with.

### 互联网/IT (15 tasks)

| # | Task | Typical User Query | Complexity | Frequency |
|----|------|--------------------|------------|-----------|
| 1 | 代码生成/实现功能 | "帮我写一个Python函数实现..." | Med | Very High |
| 2 | 代码优化/重构 | "这段代码太乱了，帮我重构一下" | Med | High |
| 3 | Bug调试/排查 | "这个接口报500错误，帮我看看哪里有问题" | Med | Very High |
| 4 | 技术方案设计 | "设计一个消息推送系统的技术方案" | High | High |
| 5 | 代码审查(Code Review) | "帮我看一下这段代码有什么问题" | Med | High |
| 6 | 需求分析/PRD | "帮我写一个登录功能的产品需求文档" | Med | High |
| 7 | API接口文档 | "帮我写这个REST API的接口文档" | Low | High |
| 8 | 测试用例编写 | "给这个支付功能写测试用例" | Low | High |
| 9 | 系统架构设计 | "设计一个高并发秒杀系统的架构" | High | Med |
| 10 | 项目复盘/总结 | "写一个Sprint复盘总结" | Med | Med |
| 11 | 数据看板/SQL | "写一个用户留存分析的SQL查询" | Med | Med |
| 12 | 技术分享/PPT大纲 | "准备一次关于微服务架构的技术分享大纲" | Med | Med |
| 13 | DevOps/部署文档 | "写一份Docker部署指南" | Low | Med |
| 14 | 产品功能介绍/文案 | "帮我写新功能发布公告" | Low | Med |
| 15 | 面试题/技术面试 | "出几道考察系统设计能力的面试题" | High | Low |

### 销售/零售 (14 tasks)

| # | Task | Typical User Query | Complexity | Frequency |
|----|------|--------------------|------------|-----------|
| 1 | 商品详情页文案 | "帮我写一款护手霜的电商详情页文案" | Low | Very High |
| 2 | 营销活动方案 | "设计618大促的活动方案" | High | High |
| 3 | 客服话术 | "客户说商品有瑕疵要退货，怎么回复" | Low | Very High |
| 4 | 直播脚本 | "写一场带货直播的完整脚本" | High | High |
| 5 | 运营数据分析 | "分析上周店铺的销售数据" | Med | High |
| 6 | 品牌文案/Slogan | "给我的新品牌想一句slogan" | Low | High |
| 7 | 社群运营方案 | "设计一个私域社群7天转化SOP" | Med | Med |
| 8 | 选品分析 | "帮我在这个类目下做一个选品建议" | High | Med |
| 9 | 促销活动设计 | "设计满减+赠品的促销方案" | Med | High |
| 10 | 竞品分析报告 | "对比我和竞品A的用户体验差异" | Med | Med |
| 11 | 会员体系设计 | "设计一个会员等级制度" | High | Med |
| 12 | 直播复盘 | "总结这场直播的数据表现和改进点" | Med | High |
| 13 | 售后流程SOP | "写一份标准售后处理流程" | Low | Med |
| 14 | 培训手册 | "写一份新员工产品知识培训手册" | Med | Low |

### 教育 (13 tasks)

| # | Task | Typical User Query | Complexity | Frequency |
|----|------|--------------------|------------|-----------|
| 1 | 教案编写 | "写一份《红楼梦》第一课时的教案" | High | Very High |
| 2 | 试题/试卷生成 | "出10道关于三角函数的测试题" | Med | Very High |
| 3 | 知识点讲解方案 | "用生动的方式讲解光合作用" | Med | High |
| 4 | 学生评语/评估 | "给一个成绩进步但纪律一般的初中生写评语" | Low | Very High |
| 5 | 课程大纲设计 | "设计一学期Python编程入门课的大纲" | High | High |
| 6 | 教学反思 | "写一份公开课后的教学反思" | Med | Med |
| 7 | 家长沟通话术 | "怎么跟家长沟通孩子成绩下滑的问题" | Low | High |
| 8 | 教研报告 | "写一份关于分层教学效果的教研报告" | High | Med |
| 9 | 班会/活动方案 | "设计一次关于校园霸凌的主题班会" | Med | Med |
| 10 | 升学指导材料 | "帮高三学生写一份志愿填报指导意见" | High | Med |
| 11 | 家校沟通通知 | "写一份寒假安全注意事项通知" | Low | High |
| 12 | 分层教学方案 | "设计一个班级内分层教学的实施计划" | High | Med |
| 13 | 微课/视频脚本 | "写一个5分钟微课的讲解脚本" | Med | High |

### 金融 (14 tasks)

| # | Task | Typical User Query | Complexity | Frequency |
|----|------|--------------------|------------|-----------|
| 1 | 分析/研究报告 | "写一份新能源行业投资分析报告" | High | High |
| 2 | 投资策略建议 | "手头有50万闲钱，请给我一个资产配置建议" | Med | Very High |
| 3 | 风险评估报告 | "对这笔信贷申请做风险分析" | High | High |
| 4 | 合规文档/制度 | "写一份反洗钱内部管理制度" | High | Med |
| 5 | 金融客服话术 | "客户投诉理财产品亏损，怎么安抚" | Med | Very High |
| 6 | 理财产品说明 | "写一款理财产品的通俗说明页" | Low | High |
| 7 | 保险方案设计 | "35岁上班族，设计一套保险方案" | Med | High |
| 8 | 尽职调查报告 | "写一份拟投资企业的尽调报告" | High | Med |
| 9 | 财务分析 | "分析这家公司的三大财务报表" | High | High |
| 10 | 监管报送材料 | "写一份向银保监会的季度报告" | High | Med |
| 11 | 金融知识科普 | "用通俗的话解释什么是通胀" | Low | High |
| 12 | 信贷审批意见 | "写一份贷款审批意见" | Med | High |
| 13 | 业务制度/流程 | "写一份对公账户开立操作规程" | Med | Med |
| 14 | 会议发言/致辞 | "写一份年终答谢酒会的行长致辞" | Low | Med |

### 制造业 (14 tasks)

| # | Task | Typical User Query | Complexity | Frequency |
|----|------|--------------------|------------|-----------|
| 1 | SOP/作业指导书 | "写一份CNC机床操作SOP" | Med | Very High |
| 2 | 工艺文件/工艺卡 | "写一份注塑成型工艺参数表" | High | High |
| 3 | 质量报告/8D报告 | "写一份产品不良的8D改善报告" | High | High |
| 4 | 设备维护/保养计划 | "写一份冲压机月度保养计划" | Med | High |
| 5 | 生产计划/排程 | "根据订单制定下周生产排程" | Med | High |
| 6 | 安全培训材料 | "写一份车间安全操作培训材料" | Low | High |
| 7 | 改善提案/合理化建议 | "写一份关于降低不良率的改善提案" | High | Med |
| 8 | 流程优化方案 | "分析产线瓶颈并提出优化方案" | High | Med |
| 9 | 供应商评估报告 | "对新供应商A进行资质评估" | Med | Med |
| 10 | 产品说明书 | "写一款家用电器的产品说明书" | Low | Med |
| 11 | 检验规范/标准 | "写一份来料检验规范(IQC)" | Med | High |
| 12 | 培训教材 | "写一份新员工上岗培训教材" | Med | Med |
| 13 | 5S管理方案 | "设计车间5S管理制度" | Med | High |
| 14 | 成本分析报告 | "分析A产品BOM成本并提出降本方案" | High | Med |

---

## Dimension 4: Role Knowledge

**Purpose:** Let the AI understand who the user IS, so it can generate prompts that match their perspective, vocabulary, and concerns. A PM and an Engineer in the same industry want very different outputs.

### Role Knowledge Structure Per Industry

```
For each common role, capture:
- Role name (Chinese, English)
- Core responsibility
- Typical KPIs / how they get evaluated
- Common deliverables they produce
- Who they report to
- Typical pain points
- Things they care about that others don't
- Things they DON'T care about (to avoid mis-prioritizing)
```

### Example: 互联网/IT Role Map

| Role | KPIs | Reports To | Key Deliverables | Cares About | Doesn't Care |
|------|------|------------|------------------|-------------|--------------|
| 前端工程师 | 页面加载速度、兼容性、bug率 | 技术组长/架构师 | 前端代码、组件库 | 交互体验、性能 | 后端架构、数据模型 |
| 后端工程师 | 接口响应时间、系统可用性、QPS | 技术负责人 | API、服务代码 | 稳定性、扩展性 | UI细节、动效 |
| 产品经理(PM) | 功能上线率、用户满意度、业务目标达成 | 产品总监 | PRD、原型、需求文档 | 用户价值、业务目标 | 实现细节、具体语法 |
| 测试工程师(QA) | 测试覆盖率、漏测率 | 测试经理 | 测试用例、测试报告 | 边界情况、异常处理 | 功能逻辑、业务价值 |
| 运维(DevOps) | 系统可用性(99.9%)、故障恢复时间 | 技术总监 | 部署脚本、监控报警 | 自动化、可观测性 | 新功能开发 |
| 数据分析师 | 数据准确率、分析报告使用率 | 数据总监 | 分析报告、看板、埋点方案 | 数据质量、洞察深度 | 功能实现、部署方式 |
| UI/UX设计师 | 设计满意度、可用性测试得分 | 设计总监 | 设计稿、设计组件 | 视觉一致性、用户体验 | 后端API、性能 |

### Example: 金融 Role Map

| Role | KPIs | Reports To | Key Deliverables | Cares About | Doesn't Care |
|------|------|------------|------------------|-------------|--------------|
| 客户经理 | 存款规模、产品渗透率、客户满意度 | 支行行长 | 客户服务、产品推荐 | 客户关系、业绩 | 系统实现、后台流程 |
| 风控经理 | 不良率、风险覆盖率 | 风险总监 | 风险评估报告、风控策略 | 逾期率、合规性 | 销售线索、客户满意 |
| 合规官 | 监管处罚次数、合规检查通过率 | 合规负责人 | 合规制度、检查报告 | 监管要求、政策变化 | 业务增长、产品创新 |
| 投资顾问 | 客户收益率、AUM规模 | 投顾总监 | 投资建议、资产配置方案 | 市场判断、客户回报 | 柜面操作、系统流程 |
| 精算师 | 产品定价合理性、准备金充足率 | 精算负责人 | 精算模型、定价报告 | 数据模型、死亡率/发病率 | 客户服务、市场营销 |

---

## Dimension 5: Document Standards

**Purpose:** Each industry has standard document templates and formats. Users often need help producing these. The AI needs to know what a "good" version looks like.

### What Each Pack Needs

For each common document type, store:

| Information | Example (8D Report - 制造业) |
|-------------|------------------------------|
| Document name | 8D改善报告 (Eight Disciplines) |
| Purpose | 系统性地解决根本原因，防止再发 |
| Standard sections | D1-团队组建, D2-问题描述, D3-临时措施, D4-根本原因分析, D5-永久措施, D6-实施验证, D7-预防措施, D8-团队表彰 |
| Expected length | 3-5页，含数据图表 |
| Tone | 严谨、数据驱动、避免推卸责任 |
| Common mistakes | 跳过根本原因分析直接写措施，没有验证数据 |
| Good example snippet | "问题描述：2024年3月5日，A产品批次#240305在最终检验中发现划痕比例8.2%（基线0.5%），影响订单#20240301交付..." |
| Bad example | "产品有质量问题，我们改进了工艺" |

### Document Coverage Per Industry

| Industry | Key Document Types |
|----------|-------------------|
| 互联网/IT | PRD, API文档, 技术方案, 设计文档, 测试用例, 部署手册, 复盘报告, 技术白皮书 |
| 销售/零售 | 详情页, 活动方案, 客服话术, 直播脚本, 运营报告, 竞品分析, 品牌手册 |
| 教育 | 教案, 试卷, 教学反思, 教研报告, 班会记录, 家长信, 课程大纲 |
| 金融 | 投资分析报告, 风控报告, 尽调报告, 合规制度, 理财说明, 授信审批, 监管报送 |
| 制造业 | SOP, 工艺文件, 8D报告, 设备保养计划, 检验规范, 安全手册, 改善提案 |

---

## Dimension 6: Core Processes

**Purpose:** Many user requests involve describing or following a process. The AI needs to know the standard industry process to generate accurate prompts.

### Process Knowledge Structure Per Industry

```
Process name
Trigger (what starts it)
Steps (numbered, with owner per step)
Decision points (branch conditions)
Handoffs (work moves from role A to role B)
Artifacts (what's produced at each step)
Approval gates
Common failure modes
Cycle time / urgency
```

### Example: 互联网/IT -- 功能上线流程 (Feature Release)

```
Trigger: PRD评审通过
Step 1: 技术方案设计 (后端TL) → Artifact: 技术设计文档
Step 2: 技术评审 (全体开发) → Gate: 技术方案签字
Step 3: 编码实现 (开发) → Artifact: 代码PR
Step 4: Code Review (Lead/高级工程师) → Gate: Review通过
Step 5: 开发自测 (开发) → Artifact: 自测报告
Step 6: QA测试 (测试工程师) → Artifact: 测试报告, bug list
Step 7: 灰度发布 (DevOps) → Artifact: 灰度报告
  Decision: 灰度数据达标? → Yes: 全量  |  No: 回滚或修bug
Step 8: 全量上线 (DevOps)
Step 9: 线上监控 (全员) → 观察期: 24-48小时
Step 10: 上线复盘 (全员) → Artifact: 复盘文档

Common failure: 跳过灰度直接全量, 上线后监控不足, 没有回滚预案
Cycle time: 小型功能2-3天, 大型功能2-4周
```

### Example: 制造业 -- 质量问题处理流程

```
Trigger: 产线发现不良 or 客户投诉
Step 1: 不良品隔离 (产线/QC) → 物理隔离、标识
Step 2: 初步分析 (QC工程师) → What: 不良率、不良类型
Step 3: 启动8D流程 (质量经理) → Gate: 是否需要成立8D小组?
Step 4: 临时措施 (生产+质量) → 筛选、返工、替换
Step 5: 根本原因分析 (8D小组) → 鱼骨图+5Why
  Decision: 根本原因确定? → Yes: D5 | No: 继续分析
Step 6: 永久纠正措施 (工程/工艺) → Gate: 措施验证
Step 7: 实施跟踪 (质量) → 监控措施效果30天
Step 8: 标准化 (文档控制) → 更新SOP、FMEA、控制计划

Common failure: 临时措施变成永久措施, 根本原因停留在表面
```

---

## Dimension 7: Pain Points & Pitfalls

**Purpose:** Let the AI anticipate what could go wrong and pre-emptively address it in generated prompts. This is what separates "sounds good in theory" from "actually works in practice."

### Pain Point Structure

```
Pain point name
Description
Why it happens
Who feels it most
How users talk about it (typical phrases)
What NOT to do
What actually helps
```

### Examples Per Industry

#### 互联网/IT

| Pain Point | Description | How Users Talk About It | What NOT to Do |
|-----------|-------------|------------------------|----------------|
| 需求频繁变更 | PM不断改需求导致开发返工 | "需求又变了", "改改改" | 生成的技术方案假设需求锁定 |
| 技术债累积 | 短期快糙猛，长期改不动 | "烂代码", "历史遗留问题" | 写代码时不考虑现有风格 |
| 上线事故 | 部署导致线上出问题 | "炸了", "回滚!" | 建议的方案不包含回滚预案 |
| 沟通断层 | 产品-开发-测试信息不同步 | "没人通知我改了" | 输出忽略同步机制 |
| 加班文化 | 长期高强度工作 | "996", "上线加班" | 生成的计划不考虑合理工时 |

#### 销售/零售

| Pain Point | Description | How Users Talk About It | What NOT to Do |
|-----------|-------------|------------------------|----------------|
| 流量成本高 | 获客越来越贵 | "流量见顶了", "买量太贵" | 只建议投钱买量不谈转化优化 |
| 价格战 | 同行比价导致利润薄 | "不降价卖不动" | 方案只教降价不教价值塑造 |
| 退货率 | 售后退货率高 | "退货退疯了" | 只管卖不管售后引导 |
| 库存积压 | 货进多了卖不掉 | "压货了" | 建议大量囤货 |
| 主播流失 | 达人/主播做起来就走 | "养好了就跑了" | 方案过度依赖个人IP |

#### 教育

| Pain Point | Description | How Users Talk About It | What NOT to Do |
|-----------|-------------|------------------------|----------------|
| 两极分化 | 班里成绩差距太大 | "教快的跟不上，教慢的吃不饱" | 写一套教案适合所有人 |
| 家校矛盾 | 家长不配合或过度干预 | "家长太难搞了" | 对抗性沟通话术 |
| 职业倦怠 | 老师累，重复劳动多 | "事情太多做不完" | 建议增加工作量 |
| 应试压力 | 分数导向限制创新教学 | "不考这些，讲了也没用" | 完全脱离考试大纲的创新 |
| 学生心理 | 心理问题增多但不知道怎么处理 | "这个学生不对劲" | 提供未经验证的心理建议 |

#### 金融

| Pain Point | Description | How Users Talk About It | What NOT to Do |
|-----------|-------------|------------------------|----------------|
| 合规压力 | 监管趋严，动辄被罚 | "合规越来越严了" | 建议打擦边球 |
| 客户亏损投诉 | 市场不好客户亏钱闹事 | "客户要上门了" | 推卸责任或过度承诺 |
| KPI压力 | 业绩指标层层加码 | "指标太高完不成" | 方案只谈理想不谈落地 |
| 信任危机 | 金融产品销售信任门槛高 | "客户说都是骗人的" | 使用销售话术而非事实 |
| 信息不对称 | 员工对产品理解不深 | "这个产品我自己都搞不懂" | 建议推销不理解的产品 |

#### 制造业

| Pain Point | Description | How Users Talk About It | What NOT to Do |
|-----------|-------------|------------------------|----------------|
| 良率不达标 | 良品率长期在目标线以下 | "良率上不去" | 只谈改善不谈原因分析 |
| 设备故障 | 突发停机影响生产 | "机器又坏了" | 维护计划不包含预防性维修 |
| 人员流动 | 熟练工流失严重 | "人走了没人会干" | 方案不包含知识传承 |
| 成本压力 | 原材料涨价，利润压缩 | "成本快顶不住了" | 只建议降本不考虑质量风险 |
| 交期延误 | 总是不能按时交付 | "又延期了，客户在催" | 只压缩工期不考虑可行性 |

---

## Dimension 8: 追问逻辑树 (Question Trees)

**Purpose:** A structured, deterministic question flow that clarifies the user's real need step by step. This is NOT random Q&A -- each question has a purpose, and the next question depends on the answer.

### Design Principles

1. **Breadth-first at shallow levels** -- confirm the basics (industry, role, task)
2. **Depth-first at deeper levels** -- drill into specifics of the current path
3. **Progressive disclosure** -- don't ask everything upfront; ask as needed
4. **Answer-sensitive branching** -- next question depends on previous answer
5. **Saturation detection** -- stop asking when you have enough to generate a deep prompt
6. **Minimum viable questions** -- 3-5 questions for a simple task, 6-10 for complex

### Example Tree 1: 写年终总结

```
Level 0: 主要意图
  Q: 您要写的是什么类型的总结?
  A1: 年终工作总结 → 继续
  A2: 项目复盘总结 → 跳转到项目复盘树
  A3: 个人述职报告 → 跳转到述职树

Level 1: 行业与岗位定位
  Q: 您所在的行业和具体岗位是什么?
  A: [互联网/IT, 产品经理]
  → 加载行业知识包中的"年终总结"分支
  → 检索互联网产品经理的考核维度

Level 2: 汇报对象与场景
  Q: 这份总结是写给谁看的? 什么场合?
  A1: 直属上级 (1对1沟通) → 侧重数据+问题
  A2: 部门会议 (PPT展示) → 侧重成果可视化+团队贡献
  A3: 全公司/CEO → 侧重战略价值+业务影响
  A4: 自己留存 → 侧重反思+成长
  → 用户选A3

Level 3: 业绩维度 (因角色而异)
  Q: 今年最值得说的3个核心成果是什么? 有数据吗?
  A: DAU从2.3万增长到3.8万; 交付了3个核心功能; 团队从5人扩展到8人
  → 提取量化指标: DAU +65%, 交付3个功能, 团队扩到8人
  → 检测是否缺失: ROI? 用户满意度? 营收影响?
  → 追问需要的数据缺失项

Level 3b: (如果数据不足)
  Q: 您提到DAU增长, 这个增长对公司营收有直接影响吗? (估算提升比例)
  A: 转化率从2.1%提升到2.8%

Level 4: 困难与挑战
  Q: 今年遇到的最大困难是什么? 怎么克服的?
  A: 一个核心功能延期了2周, 因为技术方案推倒重来
  → 存储: 延期原因, 解决方案, 学到的经验
  → 标记: "延期需要正面呈现"

Level 5: 内容策略
  Q: 对于延期2周那个项目, 你希望正面呈现还是轻描淡写?
  A1: 正面呈现 → 强调"为了质量主动调整"
  A2: 轻描淡写 → 归入"经验教训"部分

Level 6: 格式偏好
  Q: 长度和格式有要求吗?
  A1: 1页A4 + bullet points + 关键数据突出
  A2: 详细报告 + 表格 + 附录
  → 用户选A1
  → 知识包输出格式模板: "互联网PM年终总结(1页简报)"

Level 7: 明年规划
  Q: 明年工作的重点方向是哪几个?
  A: AI+行业解决方案, 出海准备
  → 注入明年方向到规划部分

=== SATURATION REACHED (8 questions answered) ===
→ 生成完整 prompt (见Dimension 9示例)
```

### Example Tree 2: 写营销方案 (销售/零售)

```
Level 0: 场景确认
  Q: 您要做的是什么类型的营销?
  A1: 大促活动 (618/双11) → Level 1
  A2: 新品上市 → Level 1 (走新品分支)
  A3: 日常推广 → Level 1 (走留存/转化分支)
  A4: 品牌活动 → Level 1 (走品牌分支)

Level 1: 渠道与平台
  Q: 主要在哪个平台做? 线上还是线下?
  A1: 淘宝/天猫 → Level 2a
  A2: 抖音/快手 → Level 2b
  A3: 线下门店 → Level 2c
  A4: 全渠道 → Level 2d

Level 2a (淘宝): 店铺现状
  Q: 目前店铺的层级(星级/钻级/冠级)和月GMV大概多少?
  A: 4钻, 月GMV 15万

Level 3a: 预算与目标
  Q: 这次活动的预算和GMV目标大概是多少?
  A: 预算2万, 目标GMV 50万
  → (检测: ROI要求25倍, 纯投流可能不够 → 需要复购+客单价提升)

Level 4: 具体玩法
  Q: 历史活动效果最好的玩法是什么?
  A: 满减效果最好, 满200减30
  → 建议: 满减+赠品+会员专属价组合

Level 5: 货品策略
  Q: 活动的主力款和引流款分别是哪些产品?
  A1: 有明确区分 → Level 6
  A2: 不清楚 → 建议"选品策略"分支
  → 用户选A1

Level 6: 执行时间线
  Q: 活动筹备期多久? 预热期和爆发期怎么分配?
  A: 2周筹备, 3天预热, 3天爆发

=== SATURATION REACHED ===
```

### Example Tree 3: 写教案 (教育)

```
Level 0: 基本信息
  Q: 您要准备哪个学科、哪个年级的教案?
  A: 小学五年级语文

Level 1: 具体课题
  Q: 哪一课或哪个知识点?
  A: 《草船借箭》第一课时

Level 2: 教学类型
  Q: 这堂课是? (新授课/复习课/公开课/研讨课)
  A: 公开课
  → 自动标记: 需要更精细的教学环节设计, 含课堂互动

Level 3: 学生基础
  Q: 这个班的学生基础怎么样? 对三国背景了解吗?
  A: 成绩中等, 大部分只知道诸葛亮是军师
  → 自动标记: 需要背景导入环节

Level 4: 课时长度
  Q: 一节课多长时间?
  A: 40分钟

Level 5: 教学难点
  Q: 这篇课文学生最容易卡在哪?
  A1: 文言文理解 → 侧重字词解释策略
  A2: 人物关系 → 侧重故事逻辑+角色分析
  A3: 借箭的计谋 → 侧重战略思维引导
  → 用户选A3
  → 知识包检索: 小学语文"计谋类课文"教学策略

Level 6: 评估方式
  Q: 课后有作业或小测吗?
  A1: 有 → 加入作业设计环节
  A2: 公开课不布置作业 → 去掉作业环节

Level 7: 教学策略偏好
  Q: 您倾向的教学风格是?
  A1: 讲授为主 → 传统教案结构
  A2: 互动探究 → 更多小组讨论环节
  A3: 情境表演 → 含角色扮演环节
  → 用户选A2
  → 知识包检索: 互动探究式语文教案模板

=== SATURATION REACHED ===
```

### Example Tree 4: 写投资分析报告 (金融)

```
Level 0: 分析对象
  Q: 您要分析哪只股票/哪个行业/哪家公司的投资价值?
  A: 新能源行业

Level 1: 报告用途
  Q: 这份报告是给谁看的?
  A1: 内部投委会 (投资决策用) → 侧重估值+风险
  A2: 给客户看 (投顾建议) → 侧重机会+通俗化
  A3: 自己研究 (学习参考) → 侧重框架+全面
  → 用户选A1

Level 2: 时间框架
  Q: 投资期限和策略定位是?
  A: 中长期(1-3年), 价值投资

Level 3: 分析深度
  Q: 需要包含哪些分析模块?
  A1: 宏观分析+行业分析+公司分析+估值+风险
  A2: 仅行业分析+公司分析
  → 用户选A1

Level 4: 行业细分
  Q: 新能源中具体关注哪个细分领域?
  A1: 光伏
  A2: 锂电
  A3: 风电
  A4: 储能 → 用户选A4
  → 知识包检索: 储能行业关键指标、政策环境、主要玩家

Level 5: 数据来源
  Q: 有已有的财务数据或行业数据吗? 还是需要假设数据并用框架?
  A: 有基本财报数据, 需要补充行业对标数据

=== SATURATION REACHED ===
```

### Question Saturation Heuristics

The system should stop asking questions when:

1. **Task is simple** (e.g., "写一段商品描述") -- 3 questions max
2. **User has given enough data** -- enough to populate 80%+ of the prompt template
3. **User shows fatigue** -- answers become shorter, faster, less detailed
4. **Critical path resolved** -- the core unknown variables are answered
5. **User explicitly says "就按这个来" or similar**

Rule of thumb: Never ask more than 10 questions for any single session. For 80% of tasks, 3-5 questions suffice.

---

## Dimension 9: Cross-Industry Handling (Special Dimension)

**Purpose:** Handle scenarios where a user's identity spans multiple industries (e.g., "互联网公司销售总监" crosses IT and Sales).

### Approach

```
Cross-Industry Detection → Priority Resolution → Mixed Knowledge Application
```

### Priority Rules

When a user mentions elements from multiple industries, apply this priority:

```
1. TASK drives the primary industry
   "写一份互联网产品的销售方案"
   → Task = 销售方案 → Primary = 销售/零售
   → Secondary = 互联网/IT (for product knowledge)

2. ROLE drives the role knowledge
   "我是互联网公司的HR总监"
   → Primary industry = 人力资源
   → Secondary = 互联网/IT (for context knowledge about tech companies)

3. Explicit mention of both
   "要用互联网思维改造传统制造业流程"
   → Left-bias: whichever industry is listed FIRST takes priority
   → But: 追问确认用户意图
```

### Cross-Industry Knowledge Map

| Primary \ Secondary | 互联网/IT | 销售/零售 | 教育 | 金融 | 制造业 |
|--------------------|-----------|-----------|------|------|--------|
| **互联网/IT** | -- | 电商技术、SaaS销售 | 在线教育技术 | FinTech、支付 | 工业互联网、MES |
| **销售/零售** | 电商运营、私域流量 | -- | 营销培训 | 消费金融、保险销售 | 零售供应链 |
| **教育** | 教育信息化、在线课程 | 教育电商 | -- | 教育金融(学费贷) | 职教、产教融合 |
| **金融** | 金融科技、量化 | 消费金融、支付 | 金融知识科普 | -- | 供应链金融 |
| **制造业** | 工业互联网、智能制造 | 品牌出海 | 安全生产培训 | 供应链金融 | -- |

### Example Cross-Industry Prompt Flow

```
User: "我是互联网公司的销售总监, 需要写一份销售培训手册"

System detects:
- Industry: 互联网/IT (from "互联网公司")
- Role: 销售总监
- Task: 写销售培训手册 (from "销售培训手册")
- Cross-industry flag: YES

追问逻辑树 (Modified):
Q1: 您主要销售的是哪种类型的产品?
A: SaaS产品, 年费制

Q2: 目标客户是?(ToB/ToC)
A: ToB, 中小企业为主

Q3: 销售模式是?
A: 电销+面销结合

→ 系统融合知识包:
Primary: 销售/零售 (销售培训、销售方法论、CRM、转化漏斗)
Secondary: 互联网/IT (SaaS产品特性、技术交流技巧)
→ 生成的prompt会包含"SaaS产品的价值主张如何传递给中小企业决策者"
```

---

## Dimension 10: Prompt Depth Examples

### Example 1: 年终总结 (互联网产品经理)

**浅层 (template-generated):**
```
请帮我写一份2024年终总结。我是一名产品经理。

内容包括：
1. 工作成果
2. 遇到的问题
3. 明年计划
字数控制在1000字左右。
```
**Why it fails:** 没有角色深度，AI会编造数据，结构通用无亮点，末尾可能是"提高用户满意度"之类空话。

---

**深层 (knowledge pack + dialog):**
```
你是一位拥有15年经验的产品管理导师，尤其擅长B2B SaaS产品领域。请帮我撰写一份面向CEO汇报的年终总结。

【我的背景】
- 岗位：B2B SaaS平台高级产品经理
- 汇报对象：CEO（关注营收和战略方向，不看细节）
- 今年负责：3个核心功能上线 + 1个P0级大客户项目交付

【关键数据】
- DAU: 2.3万 → 3.8万 (+65%)，其中Q3新功能贡献35%增量
- NPS: 42 → 68（用户满意度大幅提升）
- 功能交付：3个全部按时上线，1个P0项目延期2周（技术方案重构）
- 团队：从5人扩展到8人（新增2后端、1前端）
- 续费率：从88%提升到93%

【汇报策略】
- 延期2周的项目不要写成"延期"，要呈现为"为了保障质量主动调整时间线，获得客户理解并追加了二期预算"
- CEO看重营收影响和战略卡位，不要写技术细节
- 突出个人从"执行者"到"团队管理者"的成长转变

【格式要求】
- 篇幅：1页A4纸（约800字）
- 格式：标题 + 要点化呈现（每点1-2句话+数据）
- 语气：专业自信，不张扬也不谦虚过度
- 结构：
  1. 年度核心成果（每条用STAR法则: Situation-Task-Action-Result）
  2. 个人突破（重点讲从带项目到带团队的转变）
  3. 挑战与反思（坦诚但有建设性）
  4. 明年规划（聚焦AI+行业解决方案，出海准备）
- 关键数据高亮：*DAU增长65%*、*NPS提升26个点*、*续费率93%*
- 不使用"取得了显著成绩" "做出了突出贡献"等空话
- 每个成果必须附带可验证的量化数据

请按上述要求生成完整的年度总结内容。
```

### Example 2: 生产质量改善报告 (制造业)

**浅层 (template-generated):**
```
请帮我写一份产品质量改善报告。最近产品不良率偏高，需要分析原因并提出改进措施。
```
**Why it fails:** 没有具体数据，AI会写"加强质量意识培训""严格执行检验标准"等万能结论，缺乏行业特定的分析框架（鱼骨图、5Why、FMEA）。

---

**深层 (knowledge pack + dialog):**
```
你是一位资深质量工程师，熟悉汽车行业IATF 16949质量体系和QC七大手法。请以8D报告格式撰写一份质量改善报告。

【背景】
- 产品：A系列注塑外壳（PC+ABS材料）
- 问题：表面缩痕（sink mark），不良率8.2%（基线目标0.5%）
- 发现时间：2024年3月5日，最终检验环节
- 涉及批次：#240305-240307，共3批次

【已做的分析】
- 鱼骨图分析初步结论：主要怀疑方向是"工艺参数设置"（保压压力不足、保压时间不够）
- 数据对比：缩痕集中在进胶口远端，与模流分析结果一致
- 已采取的临时措施：全检挑选+增加10秒保压时间（不良率降至3.1%）

【报告要求】
- 严格按8D格式（D1-D8），每部分需要具体内容而非套话
- D4（根本原因分析）必须使用5Why法，至少分析到3层原因
- 改善措施必须具体到参数级别（如"保压压力从80MPa调整到95MPa"）
- 验证数据必须包含改善前后的SPC控制图对比
- 语气：专业客观，不推诿责任，体现"问题导向、持续改进"的制造业文化
- 用词注意：使用"根本原因"而非"罪魁祸首"，使用"纠正措施"而非"整改"
- 包含时间节点和责任人，体现项目管理思维
```

### Example 3: 商品详情页 (销售/零售)

**浅层 (template-generated):**
```
帮我写一段商品详情页文案。产品是护手霜，主要成分是乳木果油，保湿效果好。
```
**Why it fails:** 无用户画像，无竞品差异点，无购买理由排序，无信任背书。

---

**深层 (knowledge pack + dialog):**
```
你是一位顶级电商文案策划，尤其擅长美妆个护品类，写过多个月销万单的爆款详情页。请为这款护手霜撰写天猫详情页文案。

【产品信息】
- 品名：xx乳木果护手霜
- 核心卖点：30%乳木果油含量（行业平均10-15%），德国进口原料
- 价格带：89元/50ml（中高端定位）
- 目标人群：25-35岁都市女性，有护手习惯，对手部保养有要求
- 竞品对比：同类产品均价59元，但我们含量是竞品的2-3倍

【详情页结构要求】
按以下顺序组织，每个板块200字以内：
1. 主标题（吸引注意，突出"30%乳木果油"这个最大差异点）
2. 痛点共鸣（"试了无数护手霜，洗完手又打回原形？"）
3. 成分背书（德国进口乳木果油 + 第三方检测报告）
4. 使用场景（办公桌、包里、床头柜各放一支）
5. 用户证言（模拟2-3条真实感评价）
6. 价格锚点（对比一次手部护理的价格，体现性价比）
7. 信任保障（假一赔十、7天无理由）

【文案策略】
- 避免"殿堂级""神仙级"等淘宝禁用词
- 每30字出现一次核心关键词"乳木果油"
- 多用对比，突出"30%"这个数字
- 不要堆砌成分，要讲每个成分对用户的好处
- 末尾加CTA（立即购买、限时优惠）
- 加入30%乳木果油和普通15%产品的质地对比描述

请写出能从首屏抓住用户、一直看完到底的完整详情页文案。
```

---

## Cross-Industry Mapping Table (Dimension 9 Detail)

To handle "互联网公司销售总监" style cross-industry cases systematically:

| User Identity | Primary Pack | Secondary Pack | What to Pull From Secondary |
|--------------|-------------|----------------|---------------------------|
| 互联网公司+销售 | 销售/零售 | 互联网/IT | SaaS产品知识、技术术语、online sales funnel |
| 互联网公司+HR | 人力资源 | 互联网/IT | 技术岗位招聘画像、技术团队绩效 |
| 互联网公司+财务 | 金融 | 互联网/IT | SAAS财务模型、技术投资评估 |
| 互联网公司+教育 | 教育 | 互联网/IT | 教育信息化工具、在线教学平台 |
| 制造业+销售 | 销售/零售 | 制造业 | 工业品销售特点、B2B采购决策流程 |
| 制造业+财务 | 金融 | 制造业 | 成本核算、BOM表、固定资产管理 |
| 金融+销售 | 销售/零售 | 金融 | 金融产品合规要求、KYC、投资者适当性 |
| 教育+IT | 互联网/IT | 教育 | 教育行业术语、教学法理论 |
| 零售+物流 | 物流/供应链 | 销售/零售 | 电商配送要求、仓配一体化 |

---

## Knowledge Pack Content Size Estimates

| Dimension | Estimated Entries/Pack | Storage |
|-----------|----------------------|---------|
| Industry Fundamentals | 15-20 facts | ~5KB JSON |
| Terminology Dictionary | 80-120 terms with metadata | ~30KB JSON |
| Common Task Scenarios | 13-15 tasks, each with metadata | ~15KB JSON |
| Role Knowledge | 6-10 roles, each with 8-12 fields | ~20KB JSON |
| Document Standards | 10-15 doc types, each with templates | ~40KB JSON |
| Core Processes | 5-8 processes, structured | ~25KB JSON |
| Pain Points & Pitfalls | 8-12 pain points | ~15KB JSON |
| 追问逻辑树 | 10-15 question trees, variable depth | ~50KB JSON |
| Cross-Industry Mappings | 12-15 cross mappings | ~5KB JSON |
| **Total per industry** | | **~200KB JSON** |

All 5 deep industries: ~1MB total. Easily fits in a 50MB exe.

---

## MVP Recommendation

### Round 1 (Build for 2 weeks per industry)

1. **All 5 industries**: Terminology Dictionary + Common Task Scenarios (10-12 tasks each)
   - This gives immediate improvement over flat keywords
   - Enables basic追问 for industry-specific terms
2. **优先**: 追问逻辑树 for the top 3 tasks per industry
   - Most visible impact on user experience
   - Covers 60%+ of user sessions

### Round 2 (Add depth for 2 weeks)

3. **All 5 industries**: Role Knowledge + Document Standards
   - Makes prompts feel personalized
   - Handles "写给谁看" dimension
4. **优先**: Pain Points & Pitfalls
   - Prevents embarrassing AI-generated content

### Round 3 (Polish for 1 week)

5. **All 5 industries**: Core Processes + Cross-Industry Mappings
   - Enables process-aware prompts
   - Handles boundary cases

### Defer

- **Full 追问逻辑树 for ALL tasks**: Too much upfront investment. Build top-3 per industry, then expand based on usage data.
- **User-customizable knowledge packs**: Out of scope for v4.0. Build authoring tool for ourselves first.

---

## Feature Dependencies

```
Terminology Dictionary → Common Task Scenarios (scenarios reference terms)
Common Task Scenarios → 追问逻辑树 (trees are per-task)
Role Knowledge → Document Standards (documents vary by role)
Terminology + Roles + Scenarios → Pain Points (requires all three to identify accurately)
All of the above → Cross-Industry Handling (requires all dimensions from both industries)
```

---

## Key Design Decisions

| Decision | Option Chosen | Why |
|----------|--------------|-----|
| Knowledge pack format | Structured JSON, not free-text | Offline parsing, deterministic access |
| 追问逻辑树 depth | Max 10 questions, 3-5 typical | User fatigue threshold; diminishing returns after 5 |
| Cross-industry resolution | Task-priority model | User intent (task) best determines primary context |
| Document templates | Structural guide, not fill-in-blank | Avoids template feel; AI fills content |
| Pain point integration | Pre-emptive injection into prompt | Catches issues before AI makes them |
| Term levels | 3 levels (industry/role/scenario) | Avoids cramming all terms at same priority |

---

## Sources

- **Training data:** Language model training data (2024-2025) on Chinese industry practices, prompt engineering methodologies, AI prompt generation patterns
- **Confidence:** MEDIUM -- all content synthesized from training knowledge without current web verification
- **Verification needed for production:** Each industry's task frequencies, specific KPIs, and role definitions should be validated by domain experts or industry-specific documentation before production use
