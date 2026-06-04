---
phase: 07-scale
plan: 03
type: execute
subsystem: knowledge-pack
tags: [knowledge-pack, finance, content-authoring, compliance]
requires: [07-01, 07-02]
provides: [04-finance.yaml, finance-compiled-json]
affects: [build_packs.py, knowledge_packs_compiled/finance.json, .planning/REQUIREMENTS.md]
tech-stack:
  added: []
  patterns: ["Compliance-first YAML content structure with risk warnings embedded at term/task/doc level"]
key-files:
  created: ["prompt_tool/knowledge_packs/04-finance.yaml"]
  modified: []
  deleted: ["prompt_tool/knowledge_packs/finance.yaml"]
decisions:
  - "Removed old finance.yaml stub (3 terms, 2 tasks) to prevent compiled JSON collision - 04-finance.yaml uses the same meta.id 'finance'"
metrics:
  duration: "~25 minutes"
  completed: "2026-06-04"
---

# Phase 7 Plan 3: Finance Knowledge Pack Summary

Complete finance industry knowledge pack (04-finance.yaml) with 69 terms, 12 task scenarios, 12 follow-up trees, 7 roles, 3 workflows, 5 doc templates, and 6 pain points covering credit, wealth management, insurance, securities, and compliance per D-03. All investment-related content embeds risk warnings and compliance safeguards.

## Results

| Dimension | Count | Requirements |
|-----------|-------|-------------|
| terms | 69 (7 groups) | >= 65 |
| tasks | 12 | >= 10 |
| roles | 7 | >= 7 |
| workflows | 3 | >= 3 |
| docs | 5 | >= 5 |
| follow_up_trees | 12 | >= 10 |
| pain_points | 6 | >= 5 |
| Total lines | 2317 | >= 2000 |

**All verification checks:**
- KnowledgePack Pydantic validation: PASS
- build_packs.py compile: PASS (0 failures across 5 packs)
- Compliance audit (prohibited absolute-return language): PASS (0 real violations)
- Risk warning language present in investment-related content: PASS
- No specific investment product guidance in follow-up trees: PASS

## Structure Overview

### Terms (69 across 8 categories)
- Credit/banking (10): 信贷, 不良率(NPL Ratio), 贷前审核, 贷后管理, 风控, 征信, 抵押率(LTV), 授信额度, 利率, 还款计划
- Wealth management (9): 理财, 基金净值(NAV), 年化收益, 资产配置, 风险测评, 浮动收益, 保本收益, 净值型理财, 业绩比较基准
- Insurance (9): 精算, 核保, 理赔, 保费, 保额, 免赔额, 等待期, 续保, 保险责任
- Securities/investment (11): K线, PE(市盈率), PS(市销率), 技术分析, 基本面分析, 量化交易, 波动率, 回撤, 止损, 杠杆, 衍生品
- Compliance/regulation (9): 反洗钱(AML), 适当性管理, 信息披露, 合规审查, CRS, 投资者保护, 监管评级, 内控, 金融消费者权益
- Risk management (9): 信用风险, 市场风险, 操作风险, 流动性风险, 集中度风险, 压力测试, VaR, 风险敞口, 拨备覆盖率
- Financial products (7): 结构化产品, 信托, 私募, 公募, 保险资管, 银行理财, FOF
- Data metrics (5): IRR, DPI, 夏普比率, PB(市净率), 久期

### Tasks (12)
1. 投资分析报告 → investment_analysis_report
2. 风险评估报告 → risk_assessment_report
3. 贷前尽职调查 → pre_loan_due_diligence
4. 保险理赔处理 → insurance_claims_processing
5. 理财产品设计方案 → wealth_product_design
6. 合规检查报告 → compliance_review_report
7. 反洗钱可疑交易分析 → aml_suspicious_transaction
8. 客户适当性评估 → client_suitability_assess
9. 资产配置方案 → asset_allocation_plan
10. 财务尽调报告 → financial_due_diligence
11. 监管报送材料 → regulatory_filing_docs
12. 投资策略分析 → investment_strategy_analysis

### Roles (7)
投资经理, 风控分析师, 信贷审批经理, 保险理赔师, 合规官, 理财顾问, 反洗钱专员

### Workflows (3)
投资决策全流程 (7 steps, 2 decision points, 3 failure modes), 信贷审批全流程 (9 steps, 2 decision points, 3 failure modes), 合规审查全流程 (7 steps, 2 decision points, 3 failure modes)

### Follow-up Trees (12)
All at depth 3-4, branching on task-relevant dimensions (type/risk level/term/output). Node IDs use namespace prefixes (inv_, risk_, loan_, claim_, wp_, comp_, aml_, suit_, alloc_, fdd_, reg_, strat_).

### Pain Points (6)
信息不对称, 合规要求复杂, 风险评估准确度, 客户适当性管理难, 反洗钱合规压力, 资产质量下行

## Compliance Safeguards (per D-03)
- Zero occurrences of absolute-return promises as affirmations
- 保本收益 term definition: explains prohibition under 资管新规, not a guarantee
- All investment tasks: "风险提示和免责声明" in typical_output
- 理财产品设计方案: "不构成投资建议，业绩基准不代表实际收益"
- 资产配置方案: "基于风险测评结果，不推荐具体产品"
- 投资策略分析: "包含风险收益特征分析和压力测试情景"
- Investment-related roles: compliance responsibilities embedded
- Follow-up trees: use risk level categories and product TYPE descriptions, not specific product names
- Pain point what_not_to_do entries: reference compliance risks

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2] Removed old finance.yaml stub to prevent compiled JSON collision**
- **Found during:** Task 2 build verification
- **Issue:** Old `finance.yaml` stub (3 terms, 2 tasks) has the same `meta.id: finance` as the new `04-finance.yaml`, causing the compiled `finance.json` to be overwritten
- **Fix:** Deleted old stub file (backed up as safeguard, then removed)
- **Files modified:** `prompt_tool/knowledge_packs/finance.yaml` (deleted)
- **Commit:** e1445a7

## Self-Check

- [x] `prompt_tool/knowledge_packs/04-finance.yaml` exists with 8 dimensions
- [x] Terms: 69 >= 60
- [x] Tasks: 12 >= 10
- [x] Follow-up trees: 12 >= 2
- [x] Roles: 7 >= 7
- [x] Workflows: 3 >= 3
- [x] Docs: 5 >= 5
- [x] Pain points: 6 >= 5
- [x] build_packs.py exits 0
- [x] Compliance audit: 0 real violations
- [x] Risk warning language present in investment content
- [x] No specific investment product guidance in follow-up trees
- [x] Total lines: 2317 >= 2000
- [x] Compiled JSON at `prompt_tool/knowledge_packs_compiled/finance.json`: confirmed 69 terms, 12 tasks, 12 trees
