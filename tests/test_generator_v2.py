"""
PromptGeneratorV2 单元测试 — 知识注入、反模式过滤、策略生成
"""
import pytest
from prompt_tool.generator_v2 import PromptGeneratorV2, generate_prompts_v2


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


class TestAntiPatternFilter:
    """GEN-04 反模式过滤测试"""

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
