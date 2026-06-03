"""
FollowUpEngine 单元测试 — 决策树遍历、3问题限制、降级处理
"""
import pytest
from prompt_tool.follow_up_engine import FollowUpEngine


class MockPack:
    """模拟 KnowledgePack"""
    def get_follow_up_tree(self, task_type):
        return {
            "task_type": task_type,
            "root_node_id": "n1",
            "nodes": {
                "n1": {
                    "node_id": "n1",
                    "question_type": "single_choice",
                    "question_text": "你写PRD的目标受众是谁？",
                    "options": ["研发团队", "管理层", "投资人"],
                    "children": {"研发团队": "n2", "管理层": "n3", "投资人": "n4"},
                    "is_leaf": False,
                    "fallback_node_id": "n2",
                },
                "n2": {
                    "node_id": "n2",
                    "question_type": "text_input",
                    "question_text": "项目的主要技术挑战是什么？",
                    "options": [],
                    "children": {},
                    "is_leaf": True,
                    "fallback_node_id": None,
                },
                "n3": {
                    "node_id": "n3",
                    "question_type": "multi_choice",
                    "question_text": "你关注哪些方面的决策？（可多选）",
                    "options": ["技术选型", "人员配置", "预算规划", "时间安排"],
                    "children": {},
                    "is_leaf": True,
                    "fallback_node_id": None,
                },
                "n4": {
                    "node_id": "n4",
                    "question_type": "confirm",
                    "question_text": "需要包含财务预测和ROI分析吗？",
                    "options": ["是", "否"],
                    "children": {"_yes": "n2"},
                    "is_leaf": False,
                    "fallback_node_id": "n2",
                },
            },
        }

    def get_tasks(self):
        return []


class TestFollowUpEngine:
    """追问引擎测试"""

    def setup_method(self):
        self.pack = MockPack()
        self.engine = FollowUpEngine(self.pack, "prd_writing")

    def test_has_more_questions_initially(self):
        assert self.engine.has_more_questions() is True

    def test_first_question_returns_dict(self):
        q = self.engine.next_question()
        assert q is not None
        assert "question_text" in q
        assert "question_type" in q
        assert "node_id" in q

    def test_max_three_questions(self):
        for i in range(3):
            q = self.engine.next_question()
            if q:
                self.engine.handle_answer("test answer")
        assert self.engine.has_more_questions() is False

    def test_handle_dont_know_triggers_degradation(self):
        self.engine.next_question()
        result = self.engine.handle_dont_know()
        assert isinstance(result, dict)
        assert "fully_degraded" in result

    def test_degradation_level_tracks(self):
        assert self.engine._degradation_level == 0
        self.engine.next_question()
        self.engine.handle_dont_know()
        assert self.engine.is_degraded() is True

    def test_question_count_increments(self):
        assert self.engine.question_count == 0
        self.engine.next_question()
        assert self.engine.question_count == 1

    def test_none_pack_handled(self):
        engine = FollowUpEngine(None, "unknown")
        assert engine.has_more_questions() is False
        assert engine.next_question() is None
