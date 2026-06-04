"""
PromptGeneratorV2 单元测试 — 知识注入、反模式过滤、策略生成
"""
import pytest
from prompt_tool.generator import PromptGeneratorV2, generate_prompts_v2


class TestGeneratorV2:
    """v4.0 生成器测试"""

    ANALYSIS = {
        "industry_key": "internet_it",
        "industry_name": "互联网 / IT",
        "task_name": "PRD撰写",
        "original_input": "帮我写一个电商PRD",
    }
    CONTEXT = {
        "industry_id": "internet_it",
        "industry_name": "互联网 / IT",
        "task_type": "PRD撰写",
        "confirmed_info": {"tone": "专业", "role": "产品经理"},
        "conversation_summary": "[用户] 需要电商PRD\n[系统] 已确认行业和任务",
        "knowledge_pack_ref": None,
    }

    def test_generates_three_strategies(self):
        gen = PromptGeneratorV2(self.ANALYSIS, self.CONTEXT)
        result = gen.generate_all()
        assert "direct" in result
        assert "roleplay" in result
        assert "detailed" in result
        assert len(result["direct"]) > 0
        assert len(result["roleplay"]) > 0
        assert len(result["detailed"]) > 0

    def test_direct_contains_requirements(self):
        gen = PromptGeneratorV2(self.ANALYSIS, self.CONTEXT)
        result = gen.generate_all()
        assert "要求" in result["direct"] or "请帮我" in result["direct"]

    def test_roleplay_has_role(self):
        gen = PromptGeneratorV2(self.ANALYSIS, self.CONTEXT)
        result = gen.generate_all()
        assert "你是" in result["roleplay"] or "一位" in result["roleplay"]

    def test_detailed_has_structure(self):
        gen = PromptGeneratorV2(self.ANALYSIS, self.CONTEXT)
        result = gen.generate_all()
        assert "输出格式" in result["detailed"] or "##" in result["detailed"]

    def test_anti_pattern_filter_removes_fake_authority(self):
        gen = PromptGeneratorV2(self.ANALYSIS, self.CONTEXT)
        # Directly test filter
        text = "作为全球资深专家，这是公认的正确做法"
        filtered = gen._filter(text)
        assert "公认" not in filtered or len(filtered) < len(text)

    def test_context_injection(self):
        gen = PromptGeneratorV2(self.ANALYSIS, self.CONTEXT)
        result = gen.generate_all()
        # At least one strategy should contain conversation context or injected knowledge
        combined = result["direct"] + result["roleplay"] + result["detailed"]
        assert len(combined) > 200  # Substantial output

    def test_empty_context_works(self):
        gen = PromptGeneratorV2(self.ANALYSIS, {})
        result = gen.generate_all()
        assert "direct" in result
        assert len(result["direct"]) > 0

    def test_factory_function(self):
        result = generate_prompts_v2(self.ANALYSIS, self.CONTEXT)
        assert "direct" in result

    # ---- GEN-02: 4-Level injection point tests (with KnowledgePack data) ----

    def test_role_depth_injection_contains_kpis(self, fully_loaded_pack):
        """Detailed output contains KPI-related content from pack roles."""
        gen = PromptGeneratorV2(self.ANALYSIS, self.CONTEXT)
        gen._pack = fully_loaded_pack
        gen._task_knowledge = gen._select_task_knowledge()
        result = gen.generate_all()
        assert "完整度" in result["detailed"] or "KPI" in result["detailed"] or "迭代效率" in result["detailed"]

    def test_output_structure_injection_has_sections(self, fully_loaded_pack):
        """Detailed output contains doc template section titles."""
        gen = PromptGeneratorV2(self.ANALYSIS, self.CONTEXT)
        gen._pack = fully_loaded_pack
        gen._task_knowledge = gen._select_task_knowledge()
        result = gen.generate_all()
        assert "背景与目标" in result["detailed"] or "功能范围" in result["detailed"]

    def test_anti_pattern_injection_has_warnings(self, fully_loaded_pack):
        """Detailed output contains pain point warnings (inject 4)."""
        gen = PromptGeneratorV2(self.ANALYSIS, self.CONTEXT)
        gen._pack = fully_loaded_pack
        gen._task_knowledge = gen._select_task_knowledge()
        result = gen.generate_all()
        assert "避免以下陷阱" in result["detailed"] or "注意事项" in result["detailed"]

    def test_quality_injection_in_direct(self, fully_loaded_pack):
        """Direct output contains quality standards content."""
        gen = PromptGeneratorV2(self.ANALYSIS, self.CONTEXT)
        gen._pack = fully_loaded_pack
        gen._task_knowledge = gen._select_task_knowledge()
        result = gen.generate_all()
        assert "可操作" in result["direct"] or "行业实际工作标准" in result["direct"]


class TestAntiPatternFilter:
    """GEN-04 反模式过滤测试"""

    # ---- RED Phase: These tests fail because _build_anti_pattern_rules
    #       and _filter do not exist on generator.py's PromptGeneratorV2 yet.
    #       They will pass after GREEN implementation. ----

    def test_build_anti_pattern_rules_returns_list(self):
        gen = PromptGeneratorV2({"industry_name": "通用", "task_name": "", "original_input": "test"}, {})
        rules = gen._build_anti_pattern_rules()
        assert isinstance(rules, list)
        assert len(rules) > 0

    def test_filters_authority_claim(self):
        gen = PromptGeneratorV2({"industry_name": "通用", "task_name": "", "original_input": "test"}, {})
        text = "作为全球资深专家，这是公认的正确做法。"
        filtered = gen._filter(text)
        assert "公认的正确做法" not in filtered

    def test_filters_absolute_statements(self):
        gen = PromptGeneratorV2({"industry_name": "通用", "task_name": "", "original_input": "test"}, {})
        text = "毫无疑问这是绝对正确的方案。"
        filtered = gen._filter(text)
        assert "毫无疑问" not in filtered

    def test_preserves_normal_content(self):
        gen = PromptGeneratorV2({"industry_name": "通用", "task_name": "", "original_input": "test"}, {})
        text = "请根据行业最佳实践，输出一份PRD文档。"
        filtered = gen._filter(text)
        assert filtered == text  # Normal content unchanged

    def test_filter_regex_supplements_without_pack(self):
        gen = PromptGeneratorV2({"industry_name": "通用", "task_name": "", "original_input": "test"}, {})
        text = "作为行业顶尖专家，这是公认的最佳方案。"
        filtered = gen._filter(text)
        assert len(filtered) < len(text)

    # ---- GEN-04: Pain point driven filter tests (D-15, D-18) ----

    def test_anti_pattern_filter_uses_pain_points(self, fully_loaded_pack):
        """_build_anti_pattern_rules() includes pain_point rules from pack data."""
        gen = PromptGeneratorV2(TestGeneratorV2.ANALYSIS, TestGeneratorV2.CONTEXT)
        gen._pack = fully_loaded_pack
        gen._anti_pattern_rules = None
        rules = gen._build_anti_pattern_rules()
        pain_rules = [r for r in rules if r["type"] == "pain_point"]
        assert len(pain_rules) >= 1, f"Expected pain_point rules, got: {[r['type'] for r in rules]}"
        # Verify trigger_phrases from fixture data
        phrase_found = any(
            "需求不会变了" in r.get("trigger_phrases", []) or "就这些需求" in r.get("trigger_phrases", [])
            for r in pain_rules
        )
        assert phrase_found, "Pain point rules should contain fixture trigger_phrases"

    def test_anti_pattern_filter_handles_pain_point_phrase(self, fully_loaded_pack):
        """_filter() replaces a typical_phrase from pack with a warning."""
        gen = PromptGeneratorV2(TestGeneratorV2.ANALYSIS, TestGeneratorV2.CONTEXT)
        gen._pack = fully_loaded_pack
        gen._anti_pattern_rules = None
        text = "项目经理说需求不会变了，让我们开始开发。"
        filtered = gen._filter(text)
        assert "需求不会变了" not in filtered
        assert "注意" in filtered

    def test_pack_has_no_hardcoded_ANTI_PATTERNS(self):
        """generator.py should NOT have a module-level ANTI_PATTERNS constant."""
        import prompt_tool.generator as gen_mod
        assert not hasattr(gen_mod, "ANTI_PATTERNS"), "ANTI_PATTERNS constant should not exist in generator.py"


class TestComplianceDisclaimer:
    """QA-03: 金融/制造行业提示词包含合规声明"""

    ANALYSIS_FINANCE = {
        "industry_key": "金融",
        "industry_name": "金融",
        "task_name": "投资分析报告",
        "original_input": "帮我分析投资组合",
    }
    ANALYSIS_MANUFACTURING = {
        "industry_key": "制造",
        "industry_name": "制造",
        "task_name": "工艺流程优化",
        "original_input": "帮我优化生产线工艺流程",
    }
    ANALYSIS_INTERNET = {
        "industry_key": "internet_it",
        "industry_name": "互联网 / IT",
        "task_name": "PRD撰写",
        "original_input": "帮我写一个电商PRD",
    }

    CONTEXT_FINANCE = {
        "industry_id": "finance",
        "industry_name": "金融",
        "task_type": "投资分析报告",
        "confirmed_info": {},
        "conversation_summary": "",
    }
    CONTEXT_MANUFACTURING = {
        "industry_id": "manufacturing",
        "industry_name": "制造",
        "task_type": "工艺流程优化",
        "confirmed_info": {},
        "conversation_summary": "",
    }
    CONTEXT_INTERNET = {
        "industry_id": "internet_it",
        "industry_name": "互联网 / IT",
        "task_type": "PRD撰写",
        "confirmed_info": {},
        "conversation_summary": "",
    }

    def _make_gen(self, analysis, context):
        gen = PromptGeneratorV2(analysis, context)
        gen._task_knowledge = {}
        gen._anti_pattern_rules = []
        return gen

    def test_finance_prompts_contain_compliance(self):
        """industry_id='finance' 时，所有三个策略包含合规关键字"""
        gen = self._make_gen(self.ANALYSIS_FINANCE, self.CONTEXT_FINANCE)
        result = gen.generate_all()
        for strategy_name, text in result.items():
            assert any(kw in text for kw in ["合规声明", "风险提示", "不构成"]), \
                f"Finance {strategy_name} missing compliance keywords"

    def test_manufacturing_prompts_contain_compliance(self):
        """industry_id='manufacturing' 时，所有三个策略包含合规关键字"""
        gen = self._make_gen(self.ANALYSIS_MANUFACTURING, self.CONTEXT_MANUFACTURING)
        result = gen.generate_all()
        for strategy_name, text in result.items():
            assert any(kw in text for kw in ["合规", "安全规范", "国标"]), \
                f"Manufacturing {strategy_name} missing compliance keywords"

    def test_non_sensitive_industry_no_crash(self):
        """industry_id='internet_it' 时，generate_all() 正常返回不崩溃"""
        gen = self._make_gen(self.ANALYSIS_INTERNET, self.CONTEXT_INTERNET)
        result = gen.generate_all()
        assert "direct" in result
        assert "roleplay" in result
        assert "detailed" in result

    def test_compliance_contains_disclaimer_phrases(self):
        """合规声明内容包含免责条款文字"""
        gen = self._make_gen(self.ANALYSIS_FINANCE, self.CONTEXT_FINANCE)
        result = gen.generate_all()
        combined = result["direct"] + result["roleplay"] + result["detailed"]
        assert "不构成投资建议" in combined or "以国家/行业标准为最终依据" in combined
