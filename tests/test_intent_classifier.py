"""
IntentClassifier 单元测试 — 置信度评分、行业匹配、任务识别
"""
import pytest
from prompt_tool.intent_classifier import IntentClassifier


class TestIntentClassifier:
    """行业和任务分类测试"""

    def setup_method(self):
        self.classifier = IntentClassifier()

    def test_classify_it_industry_prd(self):
        result = self.classifier.classify("帮我写一个电商PRD")
        assert "industry_id" in result
        assert "industry_name" in result
        assert "industry_confidence" in result
        assert "task_key" in result
        assert "task_name" in result
        assert "needs_clarification" in result
        assert "matched_industries" in result
        assert "matched_tasks" in result

    def test_empty_input_needs_clarification(self):
        result = self.classifier.classify("")
        assert result["needs_clarification"] is True

    def test_unrelated_input_low_confidence(self):
        result = self.classifier.classify("今天天气真好")
        assert result["industry_confidence"] < 0.5 or result["needs_clarification"] is True

    def test_all_fields_populated(self):
        result = self.classifier.classify("帮我写代码")
        for field in ("industry_id", "industry_name", "industry_confidence",
                       "task_key", "task_name", "task_confidence",
                       "matched_industries", "matched_tasks", "needs_clarification"):
            assert field in result

    def test_confidence_normalized(self):
        result = self.classifier.classify("PRD 产品需求文档 技术方案")
        assert 0.0 <= result["industry_confidence"] <= 1.0
        assert 0.0 <= result["task_confidence"] <= 1.0
