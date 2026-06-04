"""
方案生成器 - 生成【可直接扔给 AI 执行】的完整提示词
"""

import random
import re
from .knowledge import INDUSTRIES
from .knowledge_manager import knowledge_manager


class PromptGenerator:

    def __init__(self, analysis_result: dict):
        self.r = analysis_result
        self.industry_key = analysis_result["industry_key"]
        self.industry_name = analysis_result["industry_name"]
        self.task_name = analysis_result["task_name"]
        self.original_input = analysis_result["original_input"]

    def generate_all(self) -> dict:
        return {
            "direct":   self._direct(),
            "roleplay": self._roleplay(),
            "detailed": self._detailed(),
        }

    # ================================================================
    # 方案一：直给式  — 最短，直接说事
    # ================================================================
    def _direct(self) -> str:
        return f"""{self._task_line()}

要求：
{self._bullets()}

{self._format_line()}
{self._tone_hint()}"""

    # ================================================================
    # 方案二：角色式  — 给 AI 一个身份
    # ================================================================
    def _roleplay(self) -> str:
        return f"""你是一位{self._get_role()}。

任务：{self._task_line()}

要求：
{self._bullets()}

{self._format_line()}
{self._tone_hint()}"""

    # ================================================================
    # 方案三：完整式  — 含背景、约束、格式
    # ================================================================
    def _detailed(self) -> str:
        role = self._get_role()
        bg = self._bg()
        bullets = self._bullets()
        fmt = self._format_line()
        tone = self._tone_hint()
        extra = random.choice([
            "确保内容具有实操性，避免空泛理论",
            "合理组织内容结构，确保逻辑清晰",
            "如信息不足，基于行业常识合理补充",
            "输出内容对专业人士有实际参考价值",
        ])

        return f"""你是一位{role}。

## 背景
{bg}

## 任务
{self._task_line()}

## 要求
{bullets}

## 输出格式
{fmt}

## 注意事项
{tone}
- 直接输出结果，不需要额外解释
- 内容要贴合{self.industry_name}领域的实际情况
- {extra}"""

    # ================================================================
    # 任务行
    # ================================================================
    def _task_line(self) -> str:
        inp = self.original_input[:200]
        clean = inp
        for prefix in ["请帮我", "帮我", "帮我们", "请帮我们", "请"]:
            if clean.startswith(prefix):
                clean = clean[len(prefix):].strip().lstrip("，, ")
                break

        patterns = [
            (["做", "制作", "创建", "建立", "设计", "开发", "画"], "创建"),
            (["写", "撰写", "起草", "编写", "生成", "出一份"], "写"),
            (["分析", "研究", "调研", "诊断", "评估"], "分析"),
            (["总结", "汇总", "归纳", "提炼", "复盘"], "总结"),
            (["翻译", "译"], "翻译"),
            (["规划", "计划", "安排", "策划"], "规划"),
        ]

        for keywords, action in patterns:
            if any(kw in self.original_input for kw in keywords):
                clean2 = re.sub(
                    r'^(写一份|写一篇|写一个|写一段|写|做一个|做一张|做一份|做'
                    r'|创建一个|创建|分析|总结|翻译一下|翻译'
                    r'|设计一份|设计一个|设计|出一份|出一篇)\s*',
                    '', clean
                )
                mapping = {
                    "创建": f"请帮我创建一个{clean2}",
                    "写":   f"请帮我写一份{clean2}",
                    "分析": f"请帮我分析：{clean2}",
                    "总结": f"请帮我总结：{clean2}",
                    "翻译": f"请帮我翻译：{clean2}",
                    "规划": f"请帮我制定：{clean2}",
                }
                return mapping.get(action, f"请帮我：{clean2}")

        return f"请帮我：{clean}"

    # ================================================================
    # 要求列表
    # ================================================================
    def _bullets(self) -> str:
        inp = self.original_input[:200]
        ind = self.industry_name

        spec = self._spec_req()
        if spec:
            return spec

        task_bullets = {
            "写":     f"- 内容完整、结构清晰、语言专业\n- 结合{ind}行业特点，内容务实可落地",
            "分析":   f"- 数据驱动，逻辑严密，结论明确\n- 给出具体的改进建议和可落地方案",
            "做":     f"- 输出内容完整、可直接使用\n- 结合{ind}行业的最佳实践",
            "设计":   f"- 方案完整，包含核心功能和使用流程\n- 考虑实际可落地性和用户体验",
            "总结":   f"- 重点突出，条理清晰\n- 提炼核心观点和关键数据",
            "写代码": f"- 代码完整可运行，添加必要注释\n- 考虑异常处理和边界情况",
            "翻译":   f"- 翻译准确通顺，符合中文表达习惯\n- 专业术语精准",
        }
        for kw, b in task_bullets.items():
            if kw in self.task_name or kw in inp:
                return b

        return f"- 输出内容完整、专业、可直接使用\n- 结合{ind}领域特点，内容务实可落地"

    # ================================================================
    # 格式提示
    # ================================================================
    def _format_line(self) -> str:
        inp = self.original_input
        pairs = [
            ("表格", "请以 Markdown 表格形式输出。"),
            ("表", "请以表格形式输出，表头清晰，数据规整。"),
            ("excel", "请以表格形式输出，包含字段说明。"),
            ("图表", "请用表格或字符画形式呈现。"),
            ("代码", "代码请用代码块包裹并标注语言。"),
            ("报告", "请按：摘要 → 正文 → 结论与建议 的结构输出。"),
            ("文档", "请使用 Markdown 格式，合理使用标题层级。"),
            ("ppt", "请输出 PPT 大纲结构。"),
            ("邮件", "请按正式邮件格式输出。"),
            ("教案", "请按：教学目标 → 教学过程 → 教学反思 的结构输出。"),
            ("方案", "请按：背景 → 方案 → 步骤 → 预期效果 的结构输出。"),
            ("总结", "请按：回顾 → 成绩 → 不足 → 计划 的结构输出。"),
            ("合同", "请按正式合同格式输出，含必要条款。"),
            ("文章", "请包含标题、正文段落和结尾。"),
            ("新闻稿", "请按倒金字塔结构输出。"),
            ("推文", "请用吸引人的标题和简洁有力的正文。"),
            ("公众号", "请按公众号文章风格输出，有标题、导语、正文。"),
            ("菜单", "请按菜单格式输出，含菜品名、价格、说明。"),
            ("通讯录", "请以表格形式输出，包含所有字段。"),
        ]
        for kw, fmt in pairs:
            if kw in inp:
                return f"**输出格式：**{fmt}"
        return "**输出格式：**请以清晰的分段文字输出，重要内容可用列表呈现。"

    # ================================================================
    # 语气风格
    # ================================================================
    def _tone_hint(self) -> str:
        inp = self.original_input
        if any(kw in inp for kw in ["正式", "官方", "严谨", "规范"]):
            return "**风格要求：**语言正式、规范，使用书面语。"
        if any(kw in inp for kw in ["轻松", "有趣", "幽默", "活泼"]):
            return "**风格要求：**语言轻松活泼，适当口语化。"
        if any(kw in inp for kw in ["简洁", "简短", "精炼"]):
            return "**风格要求：**简洁精炼，去除冗余。"
        return "**风格要求：**语言专业、清晰、直接。"

    # ================================================================
    # 角色选择
    # ================================================================
    def _get_role(self) -> str:
        m = {
            "互联网_IT":       "资深互联网产品与技术专家",
            "教育":            "经验丰富的教育工作者",
            "医疗健康":        "专业的医疗健康领域专家",
            "金融":            "资深的金融行业专家",
            "制造":            "制造业高级工程师",
            "零售电商":        "资深的电商运营专家",
            "建筑房地产":      "建筑与房地产行业专家",
            "农业":            "农业技术专家",
            "物流供应链":      "物流与供应链管理专家",
            "餐饮酒店":        "餐饮酒店行业资深从业者",
            "法律":            "执业律师",
            "传媒广告":        "资深传媒与广告策划专家",
            "能源环保":        "能源环保领域专家",
            "人力资源":        "资深人力资源专家",
            "政府公共服务":    "政府机关公文写作专家",
            "通用":            "专业助理，擅长文案写作、数据分析与问题解决",
        }
        return m.get(self.industry_key, m["通用"])

    # ================================================================
    # 背景（详细式专用）
    # ================================================================
    def _bg(self) -> str:
        ind = self.industry_name
        task = self.task_name.replace("任务", "") if self.task_name.endswith("任务") else self.task_name
        inp = self.original_input[:60]
        return f"用户正在{ind}领域处理一项{task}任务，需要一份专业、可直接使用的内容。核心需求是「{inp}」。"

    # ================================================================
    # 行业特定要求
    # ================================================================
    def _spec_req(self) -> str:
        inp = self.original_input[:200]
        ind = self.industry_key
        specs = [
            (("互联网_IT", "代码"),
             "- 代码完整可运行，添加必要注释\n- 考虑异常处理和边界情况\n- 提供使用示例"),
            (("互联网_IT", "文档"),
             "- 结构清晰，涵盖背景、功能需求、技术方案\n- 可直接作为开发参考"),
            (("互联网_IT", "需求"),
             "- 功能描述清晰，包含业务流程和数据定义\n- 考虑用户体验和交互细节"),
            (("互联网_IT", "测试"),
             "- 覆盖正常流程和异常场景\n- 包含预期结果和验证方法"),
            (("教育", "教案"),
             "- 教学目标明确，重难点突出\n- 教学过程具体，时间分配合理"),
            (("教育", "试题"),
             "- 难度适中，覆盖核心知识点\n- 提供参考答案和评分标准"),
            (("金融", "报告"),
             "- 数据支撑，分析逻辑严密\n- 包含风险提示和免责声明"),
            (("零售电商", "营销"),
             "- 活动玩法具体，预算和预期ROI明确\n- 包含推广渠道和执行排期"),
            (("零售电商", "描述"),
             "- 突出卖点，包含规格参数\n- 语言有感染力，促进转化"),
            (("法律", "合同"),
             "- 条款完整，符合《民法典》相关规定\n- 包含双方权利义务、违约责任、争议解决"),
            (("传媒广告", "文案"),
             "- 创意突出，有传播性\n- 品牌调性一致"),
            (("政府公共服务", "公文"),
             "- 格式规范，符合公文写作标准\n- 语言严谨，政策表述准确"),
        ]
        for (i, t), req in specs:
            if i == ind and (t in self.task_name or t in inp):
                return req
        return ""


class PromptGeneratorV2:
    """v4.0 提示词生成器 — 知识包驱动的深度提示词合成（GEN-01~04）"""

    def __init__(self, analysis_result: dict, generation_context: dict = None):
        self.r = analysis_result
        self.ctx = generation_context or {}
        self.industry_id = self.ctx.get("industry_id") or analysis_result.get("industry_key")
        self.industry_name = self.ctx.get("industry_name") or analysis_result.get("industry_name", "通用")
        self.task_name = self.ctx.get("task_type") or analysis_result.get("task_name", "")
        self.original_input = analysis_result.get("original_input", "")
        self.confirmed = self.ctx.get("confirmed_info", {})
        self.summary = self.ctx.get("conversation_summary", "")

        # KEY FIX: Load KnowledgePack directly, not metadata from context_builder
        self._pack = None
        if self.industry_id:
            try:
                self._pack = knowledge_manager.load_pack(self.industry_id)
            except Exception:
                self._pack = None

        # Select task-relevant knowledge (cached, shared across 3 strategies)
        self._task_knowledge = self._select_task_knowledge()

        # Anti-pattern rules cache (built lazily by _filter)
        self._anti_pattern_rules = None

    # ================================================================
    # 知识选择（D-12：任务相关核心知识，不全量注入）
    # ================================================================

    def _select_task_knowledge(self) -> dict:
        """Select task-relevant slice of knowledge pack (D-12).

        Robust fallback chain: exact match -> fuzzy match -> first/default.
        """
        if self._pack is None:
            return {}

        # ---- 1. Task matching (D-12) with fuzzy fallback ----
        task = self._pack.get_task(self.task_name) if self.task_name else None
        if task is None and self.task_name:
            all_tasks = self._pack.get_tasks()
            task = next(
                (t for t in all_tasks
                 if self.task_name in t.get("name", "")
                 or t.get("name", "") in self.task_name),
                None
            )
            if task is None and all_tasks:
                task = all_tasks[0]

        # ---- 2. Doc template matching (D-09) with fallback ----
        docs_for_task = self._pack.get_doc_templates(self.task_name) if self.task_name else []
        doc_template = docs_for_task[0] if docs_for_task else None
        if doc_template is None and self.task_name:
            all_docs = self._pack.get_doc_templates()
            doc_template = next(
                (d for d in all_docs if d.get("task_type") == self.task_name),
                None
            )

        # ---- 3. Role matching (D-07): exact -> substring -> default ----
        roles = self._pack.get_roles()
        pain_points = self._pack.get_pain_points()
        task_role = None
        if roles and self.task_name:
            common_tasks_list = [r for r in roles if self.task_name in r.get("common_tasks", [])]
            task_role = common_tasks_list[0] if common_tasks_list else None
            if task_role is None:
                task_role = next(
                    (r for r in roles if any(
                        self.task_name in ct or ct in self.task_name
                        for ct in r.get("common_tasks", [])
                    )),
                    None
                )
            if task_role is None:
                task_role = roles[0]

        # ---- 4. Terms filtering (D-13): keywords -> category -> fallback ----
        all_terms = self._pack.get_terms()
        task_terms = []
        if task:
            task_kws = task.get("keywords", [])
            if task_kws:
                task_terms = [t for t in all_terms if t.get("term") in task_kws][:15]
        if not task_terms:
            task_cats = task.get("related_categories", []) if task else []
            if task_cats:
                for cat in task_cats:
                    cat_terms = [t for t in all_terms if t.get("category") == cat]
                    task_terms.extend(cat_terms)
                task_terms = task_terms[:15]
        if not task_terms:
            task_terms = all_terms[:10]

        return {
            "task": task,
            "doc_template": doc_template,
            "role": task_role,
            "role_kpis": task_role.get("kpis", [])[:3] if task_role else [],
            "role_pain_points": task_role.get("pain_points", [])[:2] if task_role else [],
            "pain_points": pain_points[:3] if pain_points else [],
            "terms": task_terms,
        }

    # ================================================================
    # 4 级知识注入（D-06 固定顺序）
    # ================================================================

    def _inject_role_depth(self) -> str:
        """Inject 1: Role depth with KPI + pain points (D-07, D-14)."""
        role = self._task_knowledge.get("role")
        if not role:
            return ""

        kpis = self._task_knowledge.get("role_kpis", [])
        pains = self._task_knowledge.get("role_pain_points", [])

        lines = [f"你是一位{role['name']}。"]
        if kpis:
            lines.append("职责：")
            for k in kpis:
                benchmark = k.get("benchmark", "N/A")
                lines.append(f"- {k['name']}: {k['description']} (基准: {benchmark})")
        if pains:
            lines.append(f"常见痛点：{'、'.join(pains)}")

        return "\n".join(lines)

    def _inject_quality_standards(self) -> str:
        """Inject 2: Quality standards — general + industry-specific (D-08).

        Always returns content (the only always-on injection point).
        """
        lines = ["## 质量标准"]
        lines.append("- 输出应包含可操作的具体步骤，而非抽象理论")
        lines.append("- 内容应对标行业实际工作标准，可直接投入使用")

        # Industry-specific quality from doc template common_mistakes
        doc = self._task_knowledge.get("doc_template")
        if doc:
            mistakes = doc.get("common_mistakes", [])
            if mistakes:
                for m in mistakes[:2]:
                    lines.append(f"- 避免{m}")

        return "\n".join(lines)

    def _inject_output_structure(self) -> str:
        """Inject 3: Output structure from doc template sections (D-09)."""
        doc = self._task_knowledge.get("doc_template")
        if not doc:
            return ""
        sections = doc.get("sections", [])
        if not sections:
            return ""

        lines = ["## 输出结构"]
        for s in sections:
            lines.append(f"- {s['title']}：{s.get('prompt_hint', '')}")
        return "\n".join(lines)

    def _inject_anti_patterns(self) -> str:
        """Inject 4: Anti-pattern warnings from pain points (D-10)."""
        pains = self._task_knowledge.get("pain_points", [])
        if not pains:
            return ""

        lines = ["## 注意事项（避免以下陷阱）"]
        for pp in pains[:3]:
            what_not_to = pp.get("what_not_to_do", "")
            fallback = pp.get("description", "")
            text = what_not_to if what_not_to else fallback
            lines.append(f"- 避免{pp['name']}：{text}")
        return "\n".join(lines)

    def _inject_all(self) -> str:
        """Concatenate all 4 injection points in D-06 fixed order."""
        parts = [
            self._inject_role_depth(),
            self._inject_quality_standards(),
            self._inject_output_structure(),
            self._inject_anti_patterns(),
        ]
        return "\n".join(p for p in parts if p)

    # ================================================================
    # 反模式过滤（GEN-04, D-15~D-18）
    # ================================================================

    def _build_anti_pattern_rules(self) -> list:
        """Build filter rules from knowledge pack pain points + regex supplements.

        PRIMARY layer (D-15, D-18): pain point typical_phrases from KnowledgePack.
        SECONDARY layer (D-16): regex patterns for false authority + stereotypes.
        """
        rules = []

        # PRIMARY: Pain point driven (D-15)
        if self._pack:
            for pp in self._pack.get_pain_points():
                typical_phrases = pp.get("typical_phrases", [])
                if typical_phrases:
                    rules.append({
                        "type": "pain_point",
                        "trigger_phrases": typical_phrases,
                        "description": pp.get("name", ""),
                        "replacement": f"[注意：避免{pp.get('name', '')}]",
                    })

        # SECONDARY: Regex supplements for false authority + stereotypes (D-16)
        rules.extend([
            {"type": "authority", "pattern": r"作为.*[资深|首席|全球].*专家", "replacement": ""},
            {"type": "authority", "pattern": r"行业(领先|标杆|顶尖|公认)", "replacement": ""},
            {"type": "authority", "pattern": r"业界(公认|领先|一流)", "replacement": ""},
            {"type": "authority", "pattern": r"国际(标准|一流|顶尖)", "replacement": ""},
            {"type": "stereotype", "pattern": r"毫无疑问.*(?:正确|有效|最佳)", "replacement": ""},
            {"type": "stereotype", "pattern": r"所有.*?(?:企业|公司|产品|行业).*?都(?:必须|应该|需要)", "replacement": ""},
            {"type": "stereotype", "pattern": r"唯一(?:正确|有效|可行).*?(?:方案|方法|方式)", "replacement": ""},
            {"type": "stereotype", "pattern": r"公认.*?(?:正确|做法|标准)", "replacement": ""},
        ])
        return rules

    def _filter(self, text: str) -> str:
        """GEN-04: Pain point driven + regex supplement anti-pattern filter (D-17).

        Applies all rules from _build_anti_pattern_rules():
        1. Pain point phrase triggers -> replace with warning notes
        2. Authority/stereotype regex patterns -> remove or replace violations
        """
        if self._anti_pattern_rules is None:
            self._anti_pattern_rules = self._build_anti_pattern_rules()

        for rule in self._anti_pattern_rules:
            if rule["type"] == "pain_point":
                for phrase in rule.get("trigger_phrases", []):
                    if phrase in text:
                        text = text.replace(phrase, rule["replacement"])
            else:
                text = re.sub(rule["pattern"], rule.get("replacement", ""), text)

        return text.strip()

    # ================================================================
    # 策略实现（Plan 02: 差异化注入深度）
    # ================================================================

    def _direct(self) -> str:
        """Strategy 1: Direct — minimal injection (1 point: quality standards)."""
        parts = [self._task_line()]

        # Conversation context note (only if summary is non-empty)
        if self.summary.strip():
            parts.append(f"\n## 背景\n{self.summary}")

        parts.append(f"\n## 要求\n{self._bullets()}")

        # Injection: quality standards only, concise (no heading, 1-2 lines)
        qs = self._inject_quality_standards()
        qs_lines = [l for l in qs.split('\n') if l and not l.startswith('##')]
        if qs_lines:
            parts.append("\n" + "\n".join(qs_lines[:2]))

        parts.append(f"\n{self._format_line()}")
        parts.append(f"\n{self._tone_hint()}")

        return "".join(parts)

    def _roleplay(self) -> str:
        """Strategy 2: Roleplay — role depth + task + quality (2 injection points)."""
        parts = []

        # Role preamble with depth (from _inject_role_depth)
        role_depth = self._inject_role_depth()
        if role_depth:
            parts.append(role_depth)
        else:
            # Fallback: role name + generic role context
            role_name = self._get_role()
            parts.append(f"你是一位{role_name}。请从{role_name}的专业角度出发，结合行业经验完成以下任务。")

        parts.append(f"\n## 任务\n{self._task_line()}")
        parts.append(f"\n## 要求\n{self._bullets()}")

        # Injection: quality standards (with full heading)
        qs = self._inject_quality_standards()
        if qs:
            parts.append(f"\n{qs}")

        parts.append(f"\n{self._format_line()}")
        parts.append(f"\n{self._tone_hint()}")

        return "".join(parts)

    def _detailed(self) -> str:
        """Strategy 3: Detailed — full knowledge injection (all 4 points)."""
        parts = [f"你是一位{self._get_role()}。"]

        parts.append(f"\n## 背景\n{self._bg()}")

        # Conversation context (if available)
        if self.summary.strip():
            parts.append(f"\n## 对话上下文\n{self.summary}")

        parts.append(f"\n## 任务\n{self._task_line()}")

        # All 4 injection points (D-06 order)
        parts.append(f"\n{self._inject_all()}")

        # Requirements: use _spec_req first if available
        spec = self._spec_req()
        if spec:
            parts.append(f"\n## 要求\n{spec}")
        else:
            parts.append(f"\n## 要求\n{self._bullets()}")

        parts.append(f"\n## 输出格式\n{self._format_line()}")

        # Warnings with extra tips
        extra = random.choice([
            "确保内容具有实操性，避免空泛理论",
            "合理组织内容结构，确保逻辑清晰",
            "如信息不足，基于行业常识合理补充",
            "输出内容对专业人士有实际参考价值",
        ])
        parts.append(
            f"\n## 注意事项\n{self._tone_hint()}"
            f"\n- 直接输出结果，不需要额外解释"
            f"\n- 内容要贴合{self.industry_name}领域的实际情况"
            f"\n- {extra}"
        )

        return "".join(parts)

    def generate_all(self) -> dict:
        """Generate all 3 strategy variants, each filtered through anti-pattern filter."""
        return {
            "direct": self._filter(self._direct()),
            "roleplay": self._filter(self._roleplay()),
            "detailed": self._filter(self._detailed()),
        }

    # ================================================================
    # 辅助方法（从 v3.0 PromptGenerator 移植 + 适配）
    # ================================================================

    def _task_line(self) -> str:
        inp = self.original_input[:200]
        clean = inp
        for prefix in ["请帮我", "帮我", "帮我们", "请帮我们", "请"]:
            if clean.startswith(prefix):
                clean = clean[len(prefix):].strip().lstrip("，, ")
                break

        patterns = [
            (["做", "制作", "创建", "建立", "设计", "开发", "画"], "创建"),
            (["写", "撰写", "起草", "编写", "生成", "出一份"], "写"),
            (["分析", "研究", "调研", "诊断", "评估"], "分析"),
            (["总结", "汇总", "归纳", "提炼", "复盘"], "总结"),
            (["翻译", "译"], "翻译"),
            (["规划", "计划", "安排", "策划"], "规划"),
        ]

        for keywords, action in patterns:
            if any(kw in self.original_input for kw in keywords):
                clean2 = re.sub(
                    r'^(写一份|写一篇|写一个|写一段|写|做一个|做一张|做一份|做'
                    r'|创建一个|创建|分析|总结|翻译一下|翻译'
                    r'|设计一份|设计一个|设计|出一份|出一篇)\s*',
                    '', clean
                )
                mapping = {
                    "创建": f"请帮我创建一个{clean2}",
                    "写":   f"请帮我写一份{clean2}",
                    "分析": f"请帮我分析：{clean2}",
                    "总结": f"请帮我总结：{clean2}",
                    "翻译": f"请帮我翻译：{clean2}",
                    "规划": f"请帮我制定：{clean2}",
                }
                return mapping.get(action, f"请帮我：{clean2}")

        return f"请帮我：{clean}"

    def _bullets(self) -> str:
        inp = self.original_input[:200]
        ind = self.industry_name

        spec = self._spec_req()
        if spec:
            return spec

        task_bullets = {
            "写":     f"- 内容完整、结构清晰、语言专业\n- 结合{ind}行业特点，内容务实可落地",
            "分析":   f"- 数据驱动，逻辑严密，结论明确\n- 给出具体的改进建议和可落地方案",
            "做":     f"- 输出内容完整、可直接使用\n- 结合{ind}行业的最佳实践",
            "设计":   f"- 方案完整，包含核心功能和使用流程\n- 考虑实际可落地性和用户体验",
            "总结":   f"- 重点突出，条理清晰\n- 提炼核心观点和关键数据",
            "写代码": f"- 代码完整可运行，添加必要注释\n- 考虑异常处理和边界情况",
            "翻译":   f"- 翻译准确通顺，符合中文表达习惯\n- 专业术语精准",
        }
        for kw, b in task_bullets.items():
            if kw in self.task_name or kw in inp:
                return b

        return f"- 输出内容完整、专业、可直接使用\n- 结合{ind}领域特点，内容务实可落地"

    def _format_line(self) -> str:
        inp = self.original_input
        pairs = [
            ("表格", "请以 Markdown 表格形式输出。"),
            ("表", "请以表格形式输出，表头清晰，数据规整。"),
            ("excel", "请以表格形式输出，包含字段说明。"),
            ("图表", "请用表格或字符画形式呈现。"),
            ("代码", "代码请用代码块包裹并标注语言。"),
            ("报告", "请按：摘要 → 正文 → 结论与建议 的结构输出。"),
            ("文档", "请使用 Markdown 格式，合理使用标题层级。"),
            ("ppt", "请输出 PPT 大纲结构。"),
            ("邮件", "请按正式邮件格式输出。"),
            ("教案", "请按：教学目标 → 教学过程 → 教学反思 的结构输出。"),
            ("方案", "请按：背景 → 方案 → 步骤 → 预期效果 的结构输出。"),
            ("总结", "请按：回顾 → 成绩 → 不足 → 计划 的结构输出。"),
            ("合同", "请按正式合同格式输出，含必要条款。"),
            ("文章", "请包含标题、正文段落和结尾。"),
            ("新闻稿", "请按倒金字塔结构输出。"),
            ("推文", "请用吸引人的标题和简洁有力的正文。"),
            ("公众号", "请按公众号文章风格输出，有标题、导语、正文。"),
            ("菜单", "请按菜单格式输出，含菜品名、价格、说明。"),
            ("通讯录", "请以表格形式输出，包含所有字段。"),
        ]
        for kw, fmt in pairs:
            if kw in inp:
                return f"**输出格式：**{fmt}"
        return "**输出格式：**请以清晰的分段文字输出，重要内容可用列表呈现。"

    def _tone_hint(self) -> str:
        inp = self.original_input
        tone = self.confirmed.get("tone", "")
        if tone:
            return f"**风格要求：**语言{tone}。"
        if any(kw in inp for kw in ["正式", "官方", "严谨", "规范"]):
            return "**风格要求：**语言正式、规范，使用书面语。"
        if any(kw in inp for kw in ["轻松", "有趣", "幽默", "活泼"]):
            return "**风格要求：**语言轻松活泼，适当口语化。"
        if any(kw in inp for kw in ["简洁", "简短", "精炼"]):
            return "**风格要求：**简洁精炼，去除冗余。"
        return "**风格要求：**语言专业、清晰、直接。"

    def _get_role(self) -> str:
        """Get role name — from _task_knowledge first, then v3.0 fallback."""
        role = self._task_knowledge.get("role")
        if role and role.get("name"):
            return role["name"]
        return self._get_role_v3()

    def _get_role_v3(self) -> str:
        """v3.0 fallback role mapping."""
        m = {
            "互联网_IT":       "资深互联网产品与技术专家",
            "教育":            "经验丰富的教育工作者",
            "医疗健康":        "专业的医疗健康领域专家",
            "金融":            "资深的金融行业专家",
            "制造":            "制造业高级工程师",
            "零售电商":        "资深的电商运营专家",
            "建筑房地产":      "建筑与房地产行业专家",
            "农业":            "农业技术专家",
            "物流供应链":      "物流与供应链管理专家",
            "餐饮酒店":        "餐饮酒店行业资深从业者",
            "法律":            "执业律师",
            "传媒广告":        "资深传媒与广告策划专家",
            "能源环保":        "能源环保领域专家",
            "人力资源":        "资深人力资源专家",
            "政府公共服务":    "政府机关公文写作专家",
            "通用":            "专业助理，擅长文案写作、数据分析与问题解决",
            "internet_it":     "资深互联网产品与技术专家",
            "education":       "经验丰富的教育工作者",
            "healthcare":      "专业的医疗健康领域专家",
            "finance":         "资深的金融行业专家",
            "manufacturing":   "制造业高级工程师",
            "retail_ecommerce":"资深的电商运营专家",
            "legal":           "执业律师",
            "education":       "经验丰富的教育工作者",
        }
        return m.get(self.industry_id, m.get(self.r.get("industry_key", ""), m["通用"]))

    def _bg(self) -> str:
        ind = self.industry_name
        task = self.task_name.replace("任务", "") if self.task_name.endswith("任务") else self.task_name
        inp = self.original_input[:60]
        confirmed_role = self.confirmed.get("role", "")
        role_text = f"，角色为{confirmed_role}" if confirmed_role else ""
        return f"用户正在{ind}领域处理一项{task}任务{role_text}。核心需求是「{inp}」。"

    def _spec_req(self) -> str:
        inp = self.original_input[:200]
        ind = self.industry_id
        specs = [
            (("互联网_IT", "代码"),
             "- 代码完整可运行，添加必要注释\n- 考虑异常处理和边界情况\n- 提供使用示例"),
            (("互联网_IT", "文档"),
             "- 结构清晰，涵盖背景、功能需求、技术方案\n- 可直接作为开发参考"),
            (("互联网_IT", "需求"),
             "- 功能描述清晰，包含业务流程和数据定义\n- 考虑用户体验和交互细节"),
            (("互联网_IT", "测试"),
             "- 覆盖正常流程和异常场景\n- 包含预期结果和验证方法"),
            (("互联网_IT", "PRD"),
             "- 功能描述清晰，包含业务流程和数据定义\n- 考虑用户体验和交互细节"),
            (("教育", "教案"),
             "- 教学目标明确，重难点突出\n- 教学过程具体，时间分配合理"),
            (("教育", "试题"),
             "- 难度适中，覆盖核心知识点\n- 提供参考答案和评分标准"),
            (("金融", "报告"),
             "- 数据支撑，分析逻辑严密\n- 包含风险提示和免责声明"),
            (("零售电商", "营销"),
             "- 活动玩法具体，预算和预期ROI明确\n- 包含推广渠道和执行排期"),
            (("零售电商", "描述"),
             "- 突出卖点，包含规格参数\n- 语言有感染力，促进转化"),
            (("法律", "合同"),
             "- 条款完整，符合《民法典》相关规定\n- 包含双方权利义务、违约责任、争议解决"),
            (("传媒广告", "文案"),
             "- 创意突出，有传播性\n- 品牌调性一致"),
            (("政府公共服务", "公文"),
             "- 格式规范，符合公文写作标准\n- 语言严谨，政策表述准确"),
        ]
        for (i, t), req in specs:
            if i == ind and (t in self.task_name or t in inp):
                return req
        return ""


# ================================================================
# 对外接口
# ================================================================
def generate_prompts(analysis_result: dict) -> dict:
    return PromptGenerator(analysis_result).generate_all()


def generate_prompts_v2(analysis_result: dict, context: dict = None) -> dict:
    return PromptGeneratorV2(analysis_result, context).generate_all()
