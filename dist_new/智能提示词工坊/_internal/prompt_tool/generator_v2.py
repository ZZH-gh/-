"""
提示词生成器 v4.0（GEN-01~04）— 基于知识包+对话上下文的深度提示词合成

替代 v3.0 的模板填充方式，实现：
- GEN-01: 意图驱动合成（对话上下文 + 知识包组合）
- GEN-02: 4 级知识注入（角色深度、质量标准、输出结构、反模式警告）
- GEN-03: 3 种策略升级（直给式/角色式/完整式融入知识包内容）
- GEN-04: 反模式过滤（移除虚假权威表述和刻板信息）
"""

import random
import re

ANTI_PATTERNS = [
    (r"作为.*资深专家.*，.*公认.*", "包含虚假权威表述"),
    (r"毫无疑问.*绝对正确", "包含绝对化断言"),
    (r"众所周知.*行业的.*唯一标准", "包含刻板信息"),
    (r"所有.*企业.*都必须", "过度泛化陈述"),
]


class PromptGeneratorV2:
    """v4.0 提示词生成器 — 知识包驱动"""

    def __init__(self, analysis_result: dict, generation_context: dict = None):
        self.r = analysis_result
        self.ctx = generation_context or {}
        self.ind_name = self.ctx.get("industry_name") or analysis_result.get("industry_name", "通用")
        self.task_name = self.ctx.get("task_type") or analysis_result.get("task_name", "")
        self.original = analysis_result.get("original_input", "")
        self.confirmed = self.ctx.get("confirmed_info", {})
        self.summary = self.ctx.get("conversation_summary", "")
        self.pack_ref = self.ctx.get("knowledge_pack_ref") or {}

    def generate_all(self) -> dict:
        return {
            "direct": self._filter(self._direct()),
            "roleplay": self._filter(self._roleplay()),
            "detailed": self._filter(self._detailed()),
        }

    def _filter(self, text: str) -> str:
        """GEN-04: 反模式过滤 — 移除虚假权威和刻板表述"""
        for pattern, reason in ANTI_PATTERNS:
            if re.search(pattern, text):
                text = re.sub(pattern, "", text)
        return text.strip()

    # === 4 级知识注入 (GEN-02) ===

    def _inject_role_depth(self) -> str:
        """注入 1：角色深度 — 从知识包获取真实 KPI + 痛点"""
        roles = self.pack_ref.get("roles", []) if isinstance(self.pack_ref, dict) else []
        if not roles:
            return ""
        role_sample = roles[:2]
        lines = [f"- KPI: {', '.join(r.get('kpis', r.get('KPIs', []))[:3])}" for r in role_sample if r.get('kpis') or r.get('KPIs')]
        pains = [p for r in role_sample for p in (r.get('pain_points', r.get('painPoints', []))[:2])]
        if lines or pains:
            return "\n\n## 行业角色深度\n" + "\n".join(lines) + ("\n- 核心痛点: " + "; ".join(pains) if pains else "")
        return ""

    def _inject_quality_standards(self) -> str:
        """注入 2：质量标准 — 基于角色 KPI"""
        return "\n\n## 质量标准\n- 输出应包含可操作的步骤，而非抽象理论\n- 内容应对标行业实际工作标准，可直接投入使用"

    def _inject_output_structure(self) -> str:
        """注入 3：输出结构 — 从知识包文档规范获取"""
        return "\n\n## 输出结构\n- 使用 Markdown 格式，合理使用标题层级\n- 结构清唽、条理分明"

    def _inject_anti_patterns(self) -> str:
        """注入 4：反模式警告 — 从知识包痛点获取"""
        pains = self.pack_ref.get("pain_points", []) if isinstance(self.pack_ref, dict) else []
        if pains:
            items = [f"- 避免{p.get('name', '')}：{p.get('description', '')}" for p in pains[:3]]
            return "\n\n## 注意事项（避免以下陷阱）\n" + "\n".join(items)
        return ""

    def _inject_all(self) -> str:
        parts = [
            self._inject_role_depth(),
            self._inject_quality_standards(),
            self._inject_output_structure(),
            self._inject_anti_patterns(),
        ]
        return "\n".join(p for p in parts if p)

    # === 策略模板 (GEN-03) ===

    def _direct(self) -> str:
        context_note = ""
        if self.summary:
            context_note = f"\n\n## 上下文\n{self.summary}"

        return f"""{self._task_line()}{context_note}

## 要求
{self._bullets()}
{self._inject_all()}

{self._format_line()}
{self._tone_hint()}"""

    def _roleplay(self) -> str:
        return f"""你是一位{self._get_role()}。

任务：{self._task_line()}

{self._inject_role_depth()}

## 要求
{self._bullets()}

{self._format_line()}
{self._tone_hint()}"""

    def _detailed(self) -> str:
        context_section = f"\n\n## 对话上下文\n{self.summary}" if self.summary else ""
        return f"""你是一位{self._get_role()}。

## 背景
{self._bg()}{context_section}

## 任务
{self._task_line()}
{self._inject_all()}

## 要求
{self._bullets()}

## 输出格式
{self._format_line()}

## 注意事项
{self._tone_hint()}
- 直接输出结果，不需要额外解释
- 内容要贴合{self.ind_name}领域的实际情况"""

    # === 辅助方法（从 v3.0 移植 + 升级） ===

    def _task_line(self) -> str:
        inp = self.original[:200]
        clean = inp
        for prefix in ["请帮我", "帮我", "帮我们", "请帮我们", "请"]:
            if clean.startswith(prefix):
                clean = clean[len(prefix):].strip().lstrip("，, ")
                break
        return f"请帮我：{clean}"

    def _bullets(self) -> str:
        ind = self.ind_name
        specs = self._spec_req()
        if specs:
            return specs
        return f"- 输出内容完整、专业、可直接使用\n- 结合{ind}领域特点，内容务实可落地\n- 考虑实际应用场景，避免空泛理论"

    def _format_line(self) -> str:
        inp = self.original
        pairs = [
            ("表格", "请以 Markdown 表格形式输出。"),
            ("代码", "代码请用代码块包裹并标注语言。"),
            ("报告", "请按：摘要 → 正文 → 结论 的结构输出。"),
            ("文档", "请使用 Markdown 格式，合理使用标题层级。"),
            ("方案", "请按：背景 → 方案 → 步骤 → 预期效果 的结构输出。"),
            ("总结", "请按：回顾 → 成绩 → 不足 → 计划 的结构输出。"),
        ]
        for kw, fmt in pairs:
            if kw in inp:
                return f"**输出格式：**{fmt}"
        return "**输出格式：**请以清唽的分段文字输出，重要内容可用列表呈现。"

    def _tone_hint(self) -> str:
        inp = self.original
        tone = self.confirmed.get("tone", "")
        if tone:
            return f"**风格要求：**语言{tone}。"
        if any(kw in inp for kw in ["正式", "官方", "严谨"]):
            return "**风格要求：**语言正式、规范，使用书面语。"
        if any(kw in inp for kw in ["轻松", "有趣", "活泼"]):
            return "**风格要求：**语言轻松活泼，适当口语化。"
        return "**风格要求：**语言专业、清唽、直接。"

    def _get_role(self) -> str:
        roles = self.pack_ref.get("roles", []) if isinstance(self.pack_ref, dict) else []
        if roles:
            r = random.choice(roles)
            return r.get("name", "行业专家")
        return "专业助理，擅长文案写作、数据分析与问题解决"

    def _bg(self) -> str:
        confirmed_role = self.confirmed.get("role", "")
        ind = self.ind_name
        inp = self.original[:60]
        role_text = f"，角色为{confirmed_role}" if confirmed_role else ""
        return f"用户正在{ind}领域处理一项任务{role_text}。核心需求是「{inp}」。"

    def _spec_req(self) -> str:
        """行业特定要求 — 从确认信息和知识包提取"""
        ind = self.ind_name
        inp = self.original
        specs = [
            (("互联网 / IT", "代码"), "- 代码完整可运行，添加必要注释\n- 考虑异常处理和边界情况"),
            (("互联网 / IT", "PRD"), "- 功能描述清晰，包含业务流程和数据定义\n- 考虑用户体验和交互细节"),
            (("教育", "教案"), "- 教学目标明确，重难点突出\n- 教学过程具体，时间分配合理"),
            (("金融", "报告"), "- 数据支撑，分析逻辑严密\n- 包含风险提示"),
        ]
        for (i, t), req in specs:
            if i in ind and (t in self.task_name or t in inp):
                return req
        return ""


def generate_prompts_v2(analysis_result: dict, context: dict = None) -> dict:
    return PromptGeneratorV2(analysis_result, context).generate_all()
