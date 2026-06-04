# Phase 7: Scale (4 Industry Knowledge Packs) - Research

**Researched:** 2026-06-04
**Domain:** Chinese-language industry knowledge pack authoring (YAML structured data)
**Confidence:** HIGH

## Summary

Phase 7 requires expanding 4 placeholder YAML knowledge packs (sales_retail, education, finance, manufacturing) from their current shell state (~3 terms, 2 tasks, 2 roles each) to full production-quality packs matching the `01-internet-it.yaml` standard (~80+ terms, 10-15+ tasks, 6-9 roles, 3-5 workflows, 6+ doc templates, 5-15 follow-up trees, 5-8 pain points). The existing `01-internet-it.yaml` (3419 lines) provides the authoritative structural template. The build pipeline (`build_packs.py`) performs runtime-Schema validation via Pydantic v2, and `tests/test_schema.py` covers Schema-level integration.

**Primary recommendation:** Use `01-internet-it.yaml` as the direct authoring template. Write each industry pack in full before compiling. There are no code changes required -- this phase is pure YAML content authoring plus build/verification.

### Key Gap Analysis

| Dimension | Template (internet-it) | Current Placeholders (each) | Target per KNOW-05~08 | Delta |
|-----------|----------------------|---------------------------|----------------------|-------|
| terms | ~93 | 3 | 60+ (QA says 60+, KNOW says 60+) | ~58-80 new terms |
| tasks | 15 | 2 | 10+ (QA says 10+, KNOW says 10+) | 8-13 new tasks |
| roles | 9 | 2 | ~5-8 (no min, but depth requires) | 3-6 new roles |
| workflows | 5 | 1 | 2-3+ (no formal min, but depth requires) | 2-4 new workflows |
| docs | 6 | 1 | 3-5+ (no formal min, but depth requires) | 3-5 new doc templates |
| follow_up_trees | 15 | 2 | 2+ (target 10-15 to match template) | 8-13 new trees |
| pain_points | 8 | 1 | 5+ (no formal min, but depth requires) | 4-7 new pain points |

**Key insight:** The requirement "terms 60+, scenarios 10+, follow-up trees 2+" from CONTEXT.md represents the KNOW-05~08 floor, not the target. The template demonstrates what "production quality" means. Each pack should aim for the template's level of depth (~60-100 terms, 10-15 tasks, 10+ trees) to avoid shallow coverage in QA review.

---

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** 4 packs simultaneously, not batched.
- **D-02:** Use `01-internet-it.yaml` as the template -- identical YAML structure and 8-dimension Schema.
- **D-03:** Finance covers credit, wealth management, insurance, securities, compliance -- include compliance disclaimers and risk warning content.
- **D-04:** Sales/retail covers retail stores, e-commerce, wholesale, customer management, sales process.
- **D-05:** Education covers K12 + vocational training, including curriculum design, student assessment, training system, teaching management.
- **D-06:** Manufacturing covers production management, quality control, supply chain, equipment maintenance.
- **D-07:** Each pack must pass Schema compilation via `build_packs.py`.
- **D-08:** Each pack must meet: 60+ terms, 10+ scenarios, 2+ follow-up trees.
- **D-09:** After each pack, run `python -m pytest tests/test_schema.py -x`.
- **D-10:** Filename format: `02-sales-retail.yaml`, `03-education.yaml`, `04-finance.yaml`, `05-manufacturing.yaml` in `prompt_tool/knowledge_packs/`.

### Claude's Discretion
- Specific scenarios, terms, tree structures per industry.
- Role KPI details and pain point definitions.
- Doc template specifics and workflow details.
- Tree depth and branch granularity.

### Deferred Ideas (OUT OF SCOPE)
- 16 industry full coverage (v4.0 hard limit is 5 core industries).
- User-customizable knowledge pack editor.
- Auto-building knowledge packs from web sources.

---

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| KNOW-05 | Sales/retail knowledge pack | Full content map for sales/retail provided below (60+ terms, 12 tasks, 6 roles, etc.) |
| KNOW-06 | Education knowledge pack | Full content map for education provided below (60+ terms, 12 tasks, 6 roles, etc.) |
| KNOW-07 | Finance knowledge pack | Full content map for finance provided below (65+ terms, 12 tasks, 7 roles, compliance notes) |
| KNOW-08 | Manufacturing knowledge pack | Full content map for manufacturing provided below (60+ terms, 11 tasks, 6 roles, etc.) |

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| YAML (PyYAML) | latest | Knowledge pack authoring format | Compile-time validation via `build_packs.py`. No runtime changes needed. |
| Pydantic v2 | schema v1.0 | Schema validation model | Built into `build_packs.py`, validates all fields at compile time |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | latest | Schema validation tests | After each pack write: `python -m pytest tests/test_schema.py -x` |

---

## Package Legitimacy Audit

> No external packages being installed in this phase. This phase is pure YAML content authoring. No npm, PyPI, or crate dependencies.

---

## Architecture Patterns

### 8-Dimension Schema Structure (from 01-internet-it.yaml)

Every knowledge pack follows this exact structure, top to bottom:

```yaml
meta:          # Pack metadata (id, name, version, description, icon)
terms:         # Term dictionary (term, category, definition, aliases, usage_context, related_terms)
tasks:         # Task/scenario definitions (name, description, typical_output, complexity, frequency, follow_up_tree)
roles:         # Role definitions (name, kpis[], pain_points[], common_tasks[], responsibilities[])
workflows:     # Process workflows (name, category, steps[], decision_points[], failure_modes[])
docs:          # Document templates (name, task_type, sections[], tone, common_mistakes[])
follow_up_trees:  # Follow-up decision trees (task_type, root_node_id, nodes{})
pain_points:   # Industry pain points (name, description, why_happens, who_feels_it, typical_phrases[], what_not_to_do)
```

### Follow-Up Tree Node Structure Pattern

Each tree node has this structure (from Schema):

```yaml
node_id: "q1"
question_text: "What question?"
question_type: "single_choice" | "multi_choice" | "text_input" | "confirm"
info_key: "context_key"     # stored in conversation context
depth: 1                     # 1-10
options:                     # for single_choice/multi_choice
  - value: "opt_a"
    label: "Option A"
children:                     # value -> next_node_id mapping
  opt_a: "q2"
  opt_b: "q2"
fallback_node_id: "q2"       # "I don't know" fallback
is_leaf: false                # leaf nodes have empty children and no fallback
```

**Tree depth convention from template:**
- Depth 1: Broadest categorization (3-4 options, single_choice)
- Depth 2: Narrowing focus (2-3 options or text_input)
- Depth 3-4: Collection of specific needs (multi_choice)
- Leaf nodes: Collect final preferences (multi_choice with output format options, or text_input for free text)

### Variable Naming Convention for Tree Node IDs

From template:
- PRD: `prd_q1`, `prd_q2_scope`, `prd_q3_mgmt`, etc.
- Code: `code_q1`, `code_q2_tech`, `code_q3_style`, etc.
- Data: `data_q1`, `data_q2_data`, `data_q3_dim`, etc.

Use industry prefix + sequential pattern.

### Role Structure Pattern

Each role from template has:
- 3 KPIs (name, description, benchmark string)
- 3-5 pain points (string list)
- 4-6 common_tasks (string list matching task names)
- 4-5 responsibilities (string list)

### Workflow Structure Pattern

Each workflow has:
- 5-8 steps (step number, name, owner, deliverables list)
- 1-2 decision_points (point, yes path, no path)
- 2-3 failure_modes (name, impact, prevention)

### Doc Template Structure Pattern

Each doc template has:
- 4-6 sections (title, prompt_hint)
- Tone string
- 3-4 common_mistakes

### Pain Point Structure

Each pain point has:
- name, description, why_happens, who_feels_it
- 3-5 typical_phrases (things users say)
- what_not_to_do (what to avoid in generation)

---

## Content Map: Sales/Retail (销售/零售)

**Current state:** 3 terms, 2 tasks, 2 roles, 1 workflow, 1 doc, 2 trees, 1 pain point
**Target state:** 60+ terms, 10+ tasks, 6+ roles, 3+ workflows, 5+ docs, 10+ trees, 5+ pain points

### Terms (target: 60+)

**Sales metrics (10):**
- 转化率 (Conversion Rate), 客单价 (Average Transaction Value), 复购率 (Repeat Purchase Rate), 客流量 (Customer Traffic), 连带率 (Attachment Rate), 成交率 (Close Rate), 客诉率 (Complaint Rate), 退货率 (Return Rate), 毛利率 (Gross Margin), 坪效 (Sales per Square Foot)

**E-commerce metrics (10):**
- GMV (Gross Merchandise Volume), ROI (Return on Investment), LTV (Customer Lifetime Value), CAC (Customer Acquisition Cost), 客件数 (Items per Transaction), 渗透率 (Penetration Rate), 购物车放弃率 (Cart Abandonment Rate), AOV (Average Order Value), 流量成本 (Traffic Cost), 点击率 (CTR)

**CRM terms (8):**
- RFM分析 (Recency/Frequency/Monetary), 线索评分 (Lead Scoring), 客户分群 (Customer Segmentation), 客户生命周期 (Customer Lifecycle), 沉默客户 (Dormant Customer), 流失预警 (Churn Warning), 精准营销 (Targeted Marketing), 私域流量 (Private Domain Traffic)

**Supply chain/retail ops (8):**
- 库存周转率 (Inventory Turnover), SCM (Supply Chain Management), 缺货率 (Stockout Rate), 动销率 (Sell-Through Rate), 库龄 (Inventory Age), 安全库存 (Safety Stock), 订货点 (Reorder Point), 供应链协同 (Supply Chain Collaboration)

**Marketing/promotion (8):**
- 促销ROI (Promotion ROI), 满减 (Spend-and-Save), 秒杀 (Flash Sale), 裂变营销 (Viral Marketing), KOL营销 (KOL Marketing), 内容营销 (Content Marketing), 会员体系 (Membership System), 积分体系 (Points System)

**Sales process (6):**
- 销售漏斗 (Sales Funnel), 商机管理 (Opportunity Management), 跟单 (Order Follow-up), 回款 (Payment Collection), 渠道管理 (Channel Management), 经销商管理 (Dealer Management)

**Retail operations (8):**
- 巡店 (Store Inspection), 排班 (Staff Scheduling), 陈列 (Visual Merchandising), 补货 (Replenishment), 盘点 (Inventory Count), 损耗率 (Shrinkage Rate), 收银效率 (Checkout Efficiency), 会员管理 (Member Management)

### Tasks (target: 10+)
1. **促销方案策划** (Promotion Planning) -- medium complexity, high frequency
2. **销售数据分析** (Sales Data Analysis) -- medium complexity, very high frequency
3. **客户分群策略** (Customer Segmentation) -- medium complexity, high frequency
4. **渠道运营优化** (Channel Optimization) -- medium complexity, medium frequency
5. **商品选品分析** (Product Selection Analysis) -- high complexity, high frequency
6. **店铺运营报告** (Store Operations Report) -- low complexity, high frequency
7. **电商详情页文案** (Product Page Copywriting) -- low complexity, very high frequency
8. **会员运营方案** (Member Operations Plan) -- medium complexity, medium frequency
9. **销售话术设计** (Sales Script Design) -- low complexity, high frequency
10. **供应链优化方案** (Supply Chain Optimization) -- high complexity, medium frequency
11. **年度销售计划** (Annual Sales Plan) -- medium complexity, low frequency
12. **竞品调研报告** (Competitive Research) -- medium complexity, medium frequency

### Roles (target: 6+)
1. **销售经理** -- KPIs: 销售额完成率, 回款率, 客户增长率
2. **电商运营** -- KPIs: GMV达成率, 转化率, 流量留存率
3. **客户成功经理** -- KPIs: 复购率, 客户满意度, 流失率
4. **品类采购经理** -- KPIs: 缺货率, 毛利率, 供应商准时率
5. **零售店长** -- KPIs: 坪效, 客单价, 损耗率
6. **市场/增长经理** -- KPIs: 获客成本(ROI), 活动ROI

### Follow-up Trees (target: 10+)
- **促销方案策划** tree: 促销类型(满减/秒杀/裂变/会员专享) -> 目标客群 -> 预算范围 -> 期望产出
- **销售数据分析** tree: 分析维度(客户/产品/渠道/时间) -> 数据范围 -> 分析深度 -> 产出格式
- **客户分群策略** tree: 分群目的(留存/激活/促活/交叉销售) -> 数据来源 -> 分群方法(RFM/行为/画像)
- **渠道运营优化** tree: 渠道类型(线上/线下/私域) -> 当前痛点 -> 优化方向 -> 产出需求
- **(plus ~6-8 more matching the tasks above)**

### Pain Points (target: 5+)
1. **客户流失严重** -- 新客获取成本高但老客留存率低，投入产出不成比例
2. **库存积压** -- 采需不匹配导致资金占用，季末大量折扣清仓
3. **渠道冲突** -- 线上线下价格不一致，经销商之间恶性竞争
4. **促销 ROI 不透明** -- 大促投入高但无法准确衡量各渠道效果
5. **客户数据孤岛** -- 各系统(CRM/ERP/电商平台)数据不互通，无法形成完整客户画像

---

## Content Map: Education (教育)

**Current state:** 3 terms, 2 tasks, 2 roles, 1 workflow, 1 doc, 2 trees, 1 pain point

### Terms (target: 60+)

**Teaching methodology (10):**
- 布鲁姆分类学 (Bloom's Taxonomy), 脚手架教学 (Scaffolding), 差异化教学 (Differentiated Instruction), 探究式学习 (Inquiry-Based Learning), 项目式学习 (Project-Based Learning), 合作学习 (Cooperative Learning), 翻转课堂 (Flipped Classroom), 形成性评估 (Formative Assessment), 终结性评估 (Summative Assessment), 教学反思 (Teaching Reflection)

**Assessment terms (8):**
- 信度 (Reliability), 效度 (Validity), 区分度 (Discrimination Index), 难度系数 (Difficulty Index), 标准化考试 (Standardized Test), 常模参照 (Norm-Referenced), 标准参照 (Criterion-Referenced), 诊断性评估 (Diagnostic Assessment)

**Curriculum design (8):**
- 课程纲要 (Syllabus), 学习目标 (Learning Objectives), 知识图谱 (Knowledge Graph), 核心素养 (Core Competencies), 跨学科整合 (Interdisciplinary Integration), 螺旋式课程 (Spiral Curriculum), 模块化课程 (Modular Curriculum), 学分制 (Credit System)

**K12 education (8):**
- 学情分析 (Student Learning Analysis), 学业水平 (Academic Level), 升学率 (Graduation Rate), 分层教学 (Level-Based Teaching), 培优补差 (Advanced/Remedial), 家校沟通 (Parent-School Communication), 班主任管理 (Homeroom Management), 减负 (Burden Reduction)

**Vocational training (8):**
- 胜任力模型 (Competency Model), 技能矩阵 (Skills Matrix), 学习路径 (Learning Path), 认证体系 (Certification System), 实训 (Practical Training), 岗位技能图谱 (Job Skills Map), 培训评估 (Training Evaluation), 柯氏四级评估 (Kirkpatrick Model)

**Teaching management (6):**
- 教研活动 (Teaching Research), 集体备课 (Collaborative Lesson Planning), 听评课 (Peer Observation), 教学督导 (Teaching Supervision), 教学质量评估 (Teaching Quality Assessment), 教师发展 (Teacher Development)

**Student affairs (6):**
- 选课指导 (Course Selection Guidance), 学业预警 (Academic Warning), 综合素质评价 (Comprehensive Quality Assessment), 心理辅导 (Psychological Counseling), 职业生涯规划 (Career Planning), 学籍管理 (Student Records Management)

### Tasks (target: 10+)
1. **教学设计方案** (Lesson Plan Design) -- medium complexity, very high frequency
2. **试卷编制分析** (Exam Paper Design & Analysis) -- medium complexity, high frequency
3. **学情分析报告** (Student Learning Analysis Report) -- medium complexity, high frequency
4. **培训课程体系搭建** (Training Curriculum Design) -- high complexity, medium frequency
5. **教学评价方案** (Teaching Evaluation Plan) -- medium complexity, medium frequency
6. **教研活动方案** (Teaching Research Activity Plan) -- low complexity, medium frequency
7. **学生发展指导方案** (Student Development Guidance) -- medium complexity, low frequency
8. **家校沟通方案** (Parent-School Communication) -- low complexity, medium frequency
9. **教师培训方案** (Teacher Training Plan) -- medium complexity, medium frequency
10. **课程思政设计** (Curriculum Ideological-Political Design) -- medium complexity, medium frequency
11. **招生宣传文案** (Recruitment Copywriting) -- low complexity, high frequency
12. **教学资源建设方案** (Teaching Resource Development) -- medium complexity, low frequency

### Roles (target: 6+)
1. **课程设计师** -- KPIs: 课程开发完成率, 学员满意度, 课程目标达成率
2. **教研组长** -- KPIs: 教研活动参与率, 教学质量提升率, 教师成长率
3. **培训经理** -- KPIs: 培训覆盖率, 培训通过率, 培训ROI
4. **教学主管** -- KPIs: 学生成绩提升率, 教师满意度, 教学事故率
5. **班主任/辅导员** -- KPIs: 学生出勤率, 违纪率, 家校沟通满意度
6. **学科教师** -- KPIs: 教学目标达成率, 作业批改及时率, 学生进步率

### Follow-up Trees (target: 10+)
- **教学设计方案** tree: 教学类型(K12/职培) -> 学科领域 -> 学生特征(基础/水平) -> 产出需求
- **试卷编制分析** tree: 考试类型(诊断/期中/期末/模拟) -> 考察目标 -> 题型要求 -> 难度设定
- **学情分析报告** tree: 分析对象(个人/班级/年级) -> 数据范围(成绩/行为/问卷) -> 分析维度 -> 报告格式
- **培训课程体系搭建** tree: 培训对象(新员工/骨干/管理) -> 能力缺口 -> 交付形式 -> 认证需求
- **(plus ~6-8 more)**

### Pain Points (target: 5+)
1. **学生个体差异大** -- 同一班级学生基础参差不齐，统一教学法难以兼顾
2. **培训效果难以量化** -- 培训后难以衡量实际能力提升，柯氏评估做到Level 3/4困难
3. **课程内容的时效性** -- 行业知识更新快，教材和课程内容跟不上实际需求
4. **教师工作负担重** -- 备课、批改、教研、家校沟通多任务并行，精力分散
5. **升学压力与素质教育矛盾** -- 应试要求和综合素养培养之间的平衡难以把握

---

## Content Map: Finance (金融)

**Current state:** 3 terms, 2 tasks, 2 roles, 1 workflow, 1 doc, 2 trees, 1 pain point

### Terms (target: 65+)

**Credit/banking (10):**
- 信贷 (Credit), 不良率 (NPL Ratio), 贷前审核 (Pre-Loan Review), 贷后管理 (Post-Loan Management), 风控 (Risk Control), 征信 (Credit Reporting), 抵押率 (LTV Ratio), 授信额度 (Credit Line), 利率 (Interest Rate), 还款计划 (Repayment Schedule)

**Wealth management (8):**
- 理财 (Wealth Management), 基金净值 (NAV), 年化收益 (Annualized Return), 资产配置 (Asset Allocation), 风险测评 (Risk Assessment), 浮动收益 (Floating Return), 保本收益 (Principal-Guaranteed Return), 净值型理财 (Net-Value Wealth Management)

**Insurance (8):**
- 精算 (Actuarial Science), 核保 (Underwriting), 理赔 (Claims), 保费 (Premium), 保额 (Sum Insured), 免赔额 (Deductible), 等待期 (Waiting Period), 续保 (Renewal)

**Securities/investment (10):**
- K线 (Candlestick Chart), PE (Price-to-Earnings Ratio), PS (Price-to-Sales Ratio), 技术分析 (Technical Analysis), 基本面分析 (Fundamental Analysis), 量化交易 (Quantitative Trading), 波动率 (Volatility), 回撤 (Drawdown), 止损 (Stop-Loss), 杠杆 (Leverage)

**Compliance/regulation (8):**
- 反洗钱 (Anti-Money Laundering / AML), 适当性管理 (Suitability Management), 信息披露 (Information Disclosure), 合规审查 (Compliance Review), CRS (Common Reporting Standard), 投资者保护 (Investor Protection), 监管评级 (Regulatory Rating), 内控 (Internal Control)

**Risk management (8):**
- 信用风险 (Credit Risk), 市场风险 (Market Risk), 操作风险 (Operational Risk), 流动性风险 (Liquidity Risk), 集中度风险 (Concentration Risk), 压力测试 (Stress Test), VaR (Value at Risk), 风险敞口 (Risk Exposure)

**Financial products (6):**
- 结构化产品 (Structured Products), 信托 (Trust), 私募 (Private Equity), 公募 (Public Fund), 保险资管 (Insurance Asset Management), 银行理财 (Bank Wealth Management)

### Tasks (target: 10+)
1. **投资分析报告** (Investment Analysis Report) -- high complexity, high frequency
2. **风险评估报告** (Risk Assessment Report) -- high complexity, high frequency
3. **贷前尽职调查** (Pre-Loan Due Diligence) -- high complexity, medium frequency
4. **保险理赔处理** (Insurance Claims Processing) -- medium complexity, high frequency
5. **理财产品设计方案** (Wealth Product Design) -- high complexity, medium frequency
6. **合规检查报告** (Compliance Review Report) -- medium complexity, high frequency
7. **反洗钱可疑交易分析** (AML Suspicious Transaction Analysis) -- high complexity, medium frequency
8. **客户适当性评估** (Client Suitability Assessment) -- medium complexity, high frequency
9. **资产配置方案** (Asset Allocation Plan) -- medium complexity, medium frequency
10. **财务尽调报告** (Financial Due Diligence Report) -- high complexity, low frequency
11. **监管报送材料** (Regulatory Filing Documents) -- medium complexity, medium frequency
12. **投资策略分析** (Investment Strategy Analysis) -- high complexity, medium frequency

### Roles (target: 7+)
1. **投资经理** -- KPIs: 投资回报率, 回撤控制, 组合夏普比率
2. **风控分析师** -- KPIs: 风险预警准确率, 不良率控制, 模型AUC
3. **信贷审批经理** -- KPIs: 审批时效, 不良率, 审批通过率控制
4. **保险理赔师** -- KPIs: 理赔时效, 理赔准确率, 客户满意度
5. **合规官** -- KPIs: 合规检查覆盖率, 整改完成率, 监管处罚次数
6. **理财顾问** -- KPIs: 客户资产规模, 客户留存率, 产品推荐匹配度
7. **反洗钱专员** -- KPIs: 可疑交易识别率, SAR报送及时率, 误报率

### Follow-up Trees (target: 10+)
- **投资分析报告** tree: 投资类型(股票/基金/固收/衍生品) -> 分析深度(基本面/技术/量化) -> 时间维度 -> 报告格式
- **风险评估报告** tree: 风险类型(信用/市场/操作/流动性) -> 风险等级 -> 评估方法 -> 产出需求
- **贷前尽职调查** tree: 客户类型(企业/个人) -> 贷款用途 -> 担保方式 -> 报告深度
- **保险理赔处理** tree: 险种类型(车险/健康/寿险/财产) -> 复杂程度 -> 理赔材料 -> 赔付金额区间
- **(plus ~6-8 more)**

### Pain Points (target: 5+)
1. **信息不对称** -- 借款方/投资方掌握的信息不对称，风险评估难以全面
2. **合规要求复杂** -- 多重监管要求交叉覆盖，合规成本高，政策变化频繁
3. **风险评估准确度** -- 模型依赖历史数据，极端市场条件下预测失效
4. **客户适当性管理难** -- 复杂金融产品与客户认知水平不匹配，销售适当性难以把控
5. **反洗钱合规压力** -- 可疑交易识别标准模糊，误报率高导致大量人工审核
6. **资产质量下行** -- 经济周期波动导致不良率上升，拨备覆盖率承压

### Compliance Note for Finance
- All prompts generated from finance pack must include risk warning language: "投资有风险，入市需谨慎" equivalent
- No absolute return promises should be generated
- "保本保收益" language must be avoided per regulatory requirements
- The follow-up trees should not guide users toward specific investment products

---

## Content Map: Manufacturing (制造业)

**Current state:** 3 terms, 2 tasks, 2 roles, 1 workflow, 1 doc, 2 trees, 1 pain point

### Terms (target: 60+)

**Production management (10):**
- OEE (Overall Equipment Effectiveness), 节拍 (Takt Time), 产能 (Production Capacity), 排产 (Production Scheduling), 工单 (Work Order), 在制品 (WIP), 交货期 (Lead Time), 瓶颈工序 (Bottleneck Process), 生产周期 (Cycle Time), 产能利用率 (Capacity Utilization)

**Quality control (10):**
- SPC (Statistical Process Control), 六西格玛 (Six Sigma), CPK (Process Capability Index), FMEA (Failure Mode and Effects Analysis), 8D报告 (8D Report), PDCA (Plan-Do-Check-Act), 因果图 (Fishbone Diagram), 柏拉图 (Pareto Chart), 直通率 (First Pass Yield), 不良率 (Defect Rate)

**Supply chain (8):**
- JIT (Just In Time), VMI (Vendor Managed Inventory), MOQ (Minimum Order Quantity), 供应链风险 (Supply Chain Risk), 供应商评估 (Supplier Evaluation), 采购计划 (Procurement Plan), 物流成本 (Logistics Cost), 交货准时率 (On-Time Delivery Rate)

**Equipment maintenance (8):**
- MTBF (Mean Time Between Failures), MTTR (Mean Time To Repair), TPM (Total Productive Maintenance), 预防性维护 (Preventive Maintenance), 预测性维护 (Predictive Maintenance), 故障率 (Failure Rate), 备件管理 (Spare Parts Management), 设备综合效率

**Lean manufacturing (8):**
- 精益生产 (Lean Manufacturing), 看板管理 (Kanban), 5S现场管理 (5S), 价值流图 (Value Stream Mapping), 持续改善 (Kaizen), 标准化作业 (Standardized Work), 拉动生产 (Pull Production), 单件流 (One-Piece Flow)

**Warehousing/logistics (6):**
- 仓储管理 (Warehouse Management), 库位管理 (Location Management), FIFO (First In First Out), WMS (Warehouse Management System), 拣货效率 (Picking Efficiency), 循环盘点 (Cycle Counting)

**Industry 4.0/automation (6):**
- MES (Manufacturing Execution System), SCADA (Supervisory Control And Data Acquisition), 数字孪生 (Digital Twin), IIoT (Industrial IoT), AGV (Automated Guided Vehicle), 柔性制造 (Flexible Manufacturing)

### Tasks (target: 11+)
1. **生产排程计划** (Production Scheduling Plan) -- high complexity, very high frequency
2. **质量分析报告** (Quality Analysis Report) -- medium complexity, high frequency
3. **供应链风险评估** (Supply Chain Risk Assessment) -- high complexity, medium frequency
4. **设备维护计划** (Equipment Maintenance Plan) -- medium complexity, high frequency
5. **产能评估报告** (Capacity Assessment Report) -- medium complexity, medium frequency
6. **精益改善方案** (Lean Improvement Plan) -- high complexity, medium frequency
7. **供应商评估报告** (Supplier Evaluation Report) -- medium complexity, medium frequency
8. **生产成本分析** (Production Cost Analysis) -- medium complexity, high frequency
9. **标准作业指导书** (Standard Work Instruction) -- low complexity, high frequency
10. **工艺改进方案** (Process Improvement Plan) -- high complexity, medium frequency
11. **新产品导入方案** (New Product Introduction Plan) -- high complexity, low frequency

### Roles (target: 6+)
1. **生产主管** -- KPIs: 产量达成率, 计划完成率, 停工时间
2. **质量工程师** -- KPIs: 不良率, CPK达标率, 客诉次数
3. **供应链经理** -- KPIs: 交货准时率, 库存周转率, 采购成本控制率
4. **设备维护工程师** -- KPIs: MTBF, MTTR, 计划维护完成率
5. **工艺工程师** -- KPIs: 良率提升率, 工艺稳定性CPK, 工艺文件完整率
6. **仓库/物流主管** -- KPIs: 库存准确率, 发货及时率, 仓储成本

### Follow-up Trees (target: 10+)
- **生产排程计划** tree: 生产类型(批量/订单/MTS/MTO) -> 排产维度(设备/人力/物料) -> 时间范围 -> 产出需求
- **质量分析报告** tree: 质量问题类型(来料/过程/成品/客诉) -> 分析方法(SPC/8D/FMEA) -> 数据范围 -> 报告深度
- **供应链风险评估** tree: 风险类型(供应商/物流/价格/合规) -> 评估范围 -> 评估方法 -> 产出需求
- **设备维护计划** tree: 设备类型(关键/一般) -> 维护策略(预防/预测/事后) -> 备件情况 -> 时间周期
- **(plus ~6-7 more)**

### Pain Points (target: 5+)
1. **设备故障停机** -- 突发故障导致产线停摆，计划外停工损失大，备件响应不及时
2. **来料质量不稳定** -- 不同批次供应商质量波动大，IQC抽检难以覆盖所有风险
3. **需求波动大** -- 客户订单变化频繁，产能规划困难，淡旺季不均
4. **工艺标准不统一** -- 多产线同产品但工艺参数不一致，导致良率差异大
5. **信息孤岛** -- MES/ERP/WMS各系统间数据不互通，生产现场数据靠手工记录

---

## Common Pitfalls

### Pitfall 1: Shallow Term Definitions
**What goes wrong:** Terms defined in 2-3 words with no usage context or aliases.
**Why it happens:** Speed pressure -- the planner wants to hit "60+ terms" quickly.
**How to avoid:** Each term requires: `term`, `category`, `definition` (15-30 words), `aliases` (1-3), `usage_context` (who uses it when), `related_terms` (2-3 cross-references). Template average: ~6 lines per term.
**Warning signs:** `definition` is shorter than 15 Chinese characters.

### Pitfall 2: Flat Follow-Up Trees
**What goes wrong:** Trees are only 2 levels deep (root -> leaf). Template has 3-5 levels.
**Why it happens:** The D-08 minimum is "2+ trees", so authors stop at 2.
**How to avoid:** Each tree should have depth 3-4 with multiple branching paths. Leaf nodes should collect output format preferences, not end with "anything else?".
**Warning signs:** `depth` values in nodes only go to 2, or option labels end with the same 2 options in every tree.

### Pitfall 3: Overlapping Terms Across Packs
**What goes wrong:** Terms like "转化率" or "ROI" appear in multiple packs with identical definitions.
**Why it happens:** These are cross-industry terms that belong to each industry context.
**How to avoid:** Maintain industry-specific context even for shared terms. "转化率" in sales/retail is about purchase conversion; in finance it's about investment-to-cash conversion. Differentiate by `usage_context` and `related_terms`.

### Pitfall 4: Schema Violations from Omitted Fields
**What goes wrong:** `build_packs.py` fails because `is_leaf` is missing, node_id has invalid chars, or children mappings reference non-existent nodes.
**Why it happens:** YAML is verbose and copy-paste errors are common across 10+ trees.
**How to avoid:** After each pack, run `build_packs.py` immediately. The validator catches cycles, self-refs, missing root nodes, and type errors. Also run `pytest tests/test_schema.py -x` for unit-level coverage.

### Pitfall 5: Duplicate node_id Across Trees
**What goes wrong:** Two follow_up_trees in the same file use `n1` as root_node_id.
**Why it happens:** The template uses sequential IDs per tree (prd_q1, code_q1) but copy-paste authors use the same shorthand `n1` across trees.
**How to avoid:** Use unique prefix per tree: `sales_q1`, `data_q1`, `cust_q1`, etc. The Pydantic validator does NOT check for duplicate node_id across trees.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (stdlib, no external test framework) |
| Config file | Not detected -- pytest uses defaults |
| Quick run command | `python -m pytest tests/test_schema.py -x` |
| Full suite command | `python build_packs.py` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| KNOW-05 | sales_retail.yaml compiles | Build | `python build_packs.py` | YAML exists |
| KNOW-06 | education.yaml compiles | Build | `python build_packs.py` | YAML exists |
| KNOW-07 | finance.yaml compiles | Build | `python build_packs.py` | YAML exists |
| KNOW-08 | manufacturing.yaml compiles | Build | `python build_packs.py` | YAML exists |
| KNOW-05~08 | Schema integrity | Unit | `pytest tests/test_schema.py -x` | test_schema.py ✅ |
| KNOW-05~08 | Term count >= 60 | Manual/code review | Build output reports count | N/A |
| KNOW-05~08 | Task count >= 10 | Manual/code review | Build output reports count | N/A |
| KNOW-05~08 | Tree count >= 2 | Manual/code review | Build output reports count | N/A |

### Sampling Rate
- **Per task commit:** `python build_packs.py` (compiles ALL packs, catches schema and cycle errors)
- **Per wave merge:** `python build_packs.py && pytest tests/test_schema.py -x`
- **Phase gate:** All 4 packs pass build + schema + content review before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] No dedicated test for minimum term/scenario/tree counts. Need a content-level assertion (e.g., `assert len(pack.terms) >= 60`) that the planner should add in their plan.
- [ ] No test for cross-tree duplicate node_id validation. This is not caught by `build_packs.py` and may need a manual review step.

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No auth in knowledge pack content |
| V3 Session Management | no | No sessions in static data |
| V4 Access Control | no | No access control in static data |
| V5 Input Validation | no | Knowledge packs are static YAML, not user input |
| V6 Cryptography | no | No crypto operations on knowledge pack data |

### Finance-Specific Content Compliance

| Concern | Standard Mitigation |
|---------|-------------------|
| Absolute return promises | No "保本保收益" language in finance terms, tasks, or generated prompts |
| Investment risk warnings | Every investment-related task should reference risk warning phrasing |
| Regulatory compliance | Finance follow-up trees must not guide toward specific investment products or give investment advice |
| AML/KYC references | Anti-money laundering terms must be accurate and reference regulatory standards |
| Personal data handling | Customer suitability tasks should reference data privacy requirements |

---

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **Term count insufficient** (below 60) | KNOW-05~08 failure | MEDIUM | Full term maps provided above; count as you go |
| **Schema validation failure** | Build failure, blocks pipeline | LOW | Run `build_packs.py` after each pack; fix immediately |
| **Follow-up trees too shallow** | Poor user experience, QA failure | MEDIUM | Follow template depth (3-4 levels); detailed patterns provided above |
| **Cross-industry content mixing** | Incorrect context for terms | LOW | Use `usage_context` and `related_terms` to differentiate |
| **Finance compliance issues** | Regulatory risk if prompts give financial advice | LOW | Include risk disclaimers; avoid absolute return language; no investment recommendations |
| **File too large/editor performance** | YAML files may reach 2000-3000 lines each | MEDIUM | Use YAML-aware editor; break into sections with comments |
| **Duplicate node_id across trees** | Conversation engine may misroute | MEDIUM | Use unique prefix per tree; add manual review step |

---

## Code Examples

### Complete Follow-Up Tree Pattern (from template, adapted)

```yaml
# Follow-up tree for education: curriculum design
- task_type: "教学设计方案"
  root_node_id: "edu_cur_q1"
  nodes:
    edu_cur_q1:
      node_id: "edu_cur_q1"
      question_text: "教学对象是什么阶段？"
      question_type: "single_choice"
      info_key: "edu_level"
      depth: 1
      options:
        - value: "primary"
          label: "小学阶段（K1-K6，基础知识和学习习惯培养）"
        - value: "secondary"
          label: "中学阶段（K7-K12，应试与综合素质并重）"
        - value: "vocational"
          label: "职业培训（成人教育和技能提升）"
      children:
        primary: "edu_cur_q2_subject"
        secondary: "edu_cur_q2_subject"
        vocational: "edu_cur_q2_vocational"
      fallback_node_id: "edu_cur_q2_subject"
      is_leaf: false

    edu_cur_q2_subject:
      node_id: "edu_cur_q2_subject"
      question_text: "涉及什么学科或领域？"
      question_type: "text_input"
      info_key: "edu_subject"
      depth: 2
      options: []
      children:
        _any: "edu_cur_q3_diff"
      fallback_node_id: "edu_cur_q3_diff"
      is_leaf: false

    edu_cur_q3_diff:
      node_id: "edu_cur_q3_diff"
      question_text: "学生的基础水平如何？"
      question_type: "single_choice"
      info_key: "edu_diff_level"
      depth: 3
      options:
        - value: "weak"
          label: "基础薄弱（需要从核心概念讲解开始）"
        - value: "average"
          label: "中等水平（常规教学进度，需巩固练习）"
        - value: "advanced"
          label: "基础良好（需要拔高和拓展性内容）"
      children:
        weak: "edu_cur_q4_output"
        average: "edu_cur_q4_output"
        advanced: "edu_cur_q4_output"
      fallback_node_id: "edu_cur_q4_output"
      is_leaf: false

    edu_cur_q4_output:
      node_id: "edu_cur_q4_output"
      question_text: "期望的产出物包含什么？"
      question_type: "multi_choice"
      info_key: "edu_cur_output"
      depth: 4
      options:
        - value: "plan"
          label: "完整教学设计方案（目标+流程+评估）"
        - value: "activities"
          label: "课堂活动设计（互动环节和教学游戏）"
        - value: "assessment"
          label: "评估方案（形成性和终结性评估）"
        - value: "materials"
          label: "教学材料（讲义、课件、练习）"
      children: {}
      fallback_node_id: null
      is_leaf: true

    edu_cur_q2_vocational:
      node_id: "edu_cur_q2_vocational"
      question_text: "培训的对象是什么人群？"
      question_type: "single_choice"
      info_key: "edu_trainee"
      depth: 2
      options:
        - value: "new_hire"
          label: "新员工入职培训"
        - value: "junior"
          label: "基层员工技能提升"
        - value: "manager"
          label: "管理层能力发展"
        - value: "cert"
          label: "职业资格认证培训"
      children:
        new_hire: "edu_cur_q4_output"
        junior: "edu_cur_q4_output"
        manager: "edu_cur_q4_output"
        cert: "edu_cur_q4_output"
      fallback_node_id: "edu_cur_q4_output"
      is_leaf: false
```

### Term Definition Pattern

```yaml
- term: "OEE"
  category: "生产管理"
  definition: "设备综合效率（Overall Equipment Effectiveness），衡量设备利用率的综合性指标，由可用率×性能率×良品率三要素相乘得出。"
  aliases: ["设备综合效率", "Overall Equipment Effectiveness"]
  usage_context: "生产主管和精益工程师用于评估设备运行效率，识别六大损失（故障、换模、停机、降速、不良、启动损失）"
  related_terms: ["MTBF", "产能", "TPM"]
```

### Role Pattern

```yaml
- name: "信贷审批经理"
  kpis:
    - name: "审批时效"
      description: "从提交到完成审批的平均工作日数"
      benchmark: "< 3个工作日"
    - name: "不良率"
      description: "审批通过的贷款中发生不良的比例"
      benchmark: "< 2%"
    - name: "审批通过率控制"
      description: "审批通过率与风险偏好的匹配度"
      benchmark: "60-75%"
  pain_points:
    - "企业财务报表真实性难以核实，信息不对称严重"
    - "审批流程长，客户催促压力大"
    - "多头授信和隐形负债难以发现"
  common_tasks:
    - "贷前尽职调查"
    - "风险评估报告"
    - "合规检查报告"
  responsibilities:
    - "负责信贷业务的风险评估和授信审批"
    - "审核贷款申请材料的真实性和完整性"
    - "控制授信风险在可接受范围内"
    - "跟踪贷后风险状况，及时预警"
```

### Workflow Pattern

```yaml
- name: "质量管控流程"
  category: "质量管理"
  steps:
    - step: 1
      name: "来料检验"
      owner: "IQC质检员"
      deliverables:
        - "来料检验报告"
    - step: 2
      name: "过程检验"
      owner: "IPQC质检员"
      deliverables:
        - "过程巡检记录"
    - step: 3
      name: "成品检验"
      owner: "OQC质检员"
      deliverables:
        - "成品检验报告"
    - step: 4
      name: "不合格处理"
      owner: "质量工程师"
      deliverables:
        - "不合格品处理单"
        - "8D改善报告"
    - step: 5
      name: "纠正预防"
      owner: "质量工程师"
      deliverables:
        - "改善行动计划"
  decision_points:
    - point: "来料检验是否合格？"
      yes: "进入仓库或生产线"
      no: "退回供应商或MRB评审"
    - point: "不合格原因是否已根除？"
      yes: "关闭问题并归档"
      no: "启动FMEA重新评估"
  failure_modes:
    - name: "来料抽检漏检"
      impact: "批量不良流入产线，导致停线和返工"
      prevention: "提升抽检比例，对关键物料实施全检"
    - name: "过程检验频次不足"
      impact: "不良品大量产生后才被发现，浪费材料和工时"
      prevention: "基于CPK动态调整检验频次"
```

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The 4 existing YAML placeholders are from Phase 1 scaffolding and have no real content | Header | LOW -- confirmed by reading the files |
| A2 | `build_packs.py` is the authoritative validation and no code changes to it are needed | Validation | LOW -- schema is stable per CONTEXT.md |
| A3 | KnowledgeManager auto-discovers new packs (no code change needed) | Integration | LOW -- confirmed by CONTEXT.md code_context |
| A4 | Finance industry compliance requires risk disclaimers | Content | MEDIUM -- verify exact regulatory requirements |
| A5 | `meta` `icon` field uses emoji characters | Template | LOW -- confirmed in both template and schema |
| A6 | The industry-specific terms and roles I recommend are appropriate for Chinese-language knowledge packs | Content maps | LOW -- based on training knowledge, needs human verification |

---

## Open Questions

1. **What is the "follow_up_tree" field's exact matching mechanism?**
   - What we know: Each `tasks[].follow_up_tree` references a `follow_up_trees[].task_type` value.
   - What's unclear: Whether the match is by exact string or fuzzy. The template uses exact matching in both fields.
   - Recommendation: Use exact string match (as template does). `tasks[].follow_up_tree` == `follow_up_trees[].task_type`.

2. **Should `related_terms` reference terms within the same pack or across packs?**
   - What we know: Template references are all within the same pack (internet-it terms refer to other internet-it terms).
   - What's unclear: Whether cross-pack references work at all (e.g., finance referencing a term that also exists in sales).
   - Recommendation: Keep all `related_terms` within the same pack for consistency.

3. **What is the emoji icon convention for new packs?**
   - What we know: Template uses `icon: "💻"`, placeholders use `💰`, `📚`, `🛒`, `⚙️`.
   - What's unclear: Whether there's a registry of icons or just free choice.
   - Recommendation: Use existing placeholder icons (`🛒`, `📚`, `💰`, `⚙️`) -- they are already set.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Running build_packs.py | yes | 3.14.4 | -- |
| PyYAML (yaml) | build_packs.py YAML parsing | yes | installed | -- |
| Pydantic v2 | build_packs.py Schema validation | yes | installed | -- |
| pytest | test_schema.py | yes | installed | -- |
| `01-internet-it.yaml` | Authoring template | yes | 3421 lines | -- |
| `build_packs.py` | Compilation | yes | v1.0 | -- |

**Missing dependencies with no fallback:** None
**Missing dependencies with fallback:** None

---

## Sources

### Primary (HIGH confidence)
- `prompt_tool/knowledge_packs/01-internet-it.yaml` -- Complete reference template (93 terms, 15 tasks, 9 roles, 5 workflows, 6 docs, 15 trees, 8 pain points)
- `prompt_tool/knowledge_packs/_schema.yaml` -- Schema definition with field specifications
- `build_packs.py` -- Build script, Pydantic v2 validation models
- `tests/test_schema.py` -- Schema unit tests
- `prompt_tool/knowledge_packs/sales_retail.yaml`, `education.yaml`, `finance.yaml`, `manufacturing.yaml` -- Current placeholder files (verified content state)

### Secondary (MEDIUM confidence)
- `.planning/phases/07-scale/07-CONTEXT.md` -- User decisions and phase boundary
- `.planning/REQUIREMENTS.md` -- KNOW-05~08 requirement definitions

---

## Metadata

**Confidence breakdown:**
- Standard stack (template/schema): HIGH -- verified by reading all source files
- Content maps per industry: MEDIUM to LOW -- based on training knowledge; AI-generated term suggestions need human verification for accuracy and completeness
- Pitfalls: HIGH -- based on document structure analysis
- Architecture patterns: HIGH -- extracted directly from template code

**Research date:** 2026-06-04
**Valid until:** 2026-07-04 (30 days -- stable YAML schema, no fast-moving dependencies)
