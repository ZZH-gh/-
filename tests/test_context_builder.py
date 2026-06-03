"""
ContextBuilder 单元测试 — 测试 build_generation_context 输出形状、空会话默认值、摘要生成
"""

import pytest
from prompt_tool.context_builder import build_generation_context


class TestContextBuilder:
    """build_generation_context 输出验证"""

    def test_build_output_shape(self, sample_session_with_turns):
        """build_generation_context 返回包含 6 个固定字段的 dict（D-05）"""
        session = sample_session_with_turns.get_active_session()
        context = build_generation_context(session)

        assert isinstance(context, dict)
        expected_keys = {
            "industry_id", "industry_name", "task_type",
            "confirmed_info", "conversation_summary", "knowledge_pack_ref",
        }
        assert set(context.keys()) == expected_keys

    def test_build_empty_session(self, session_manager_instance):
        """无 confirmed_industry 的会话返回安全默认值"""
        sm = session_manager_instance
        sm.create_session()
        session = sm.get_active_session()

        context = build_generation_context(session)

        assert context["industry_id"] is None
        assert context["industry_name"] == "通用 / 其他"
        assert context["task_type"] is None
        assert context["confirmed_info"] == {}
        assert context["conversation_summary"] == ""
        assert context["knowledge_pack_ref"] is None

    def test_conversation_summary(self, session_manager_instance):
        """_build_summary 仅包含最近 5 轮，每行前缀 [用户] 或 [系统]"""
        sm = session_manager_instance
        sm.create_session()

        # 添加 7 个轮次（超过 max_turns=5）
        turns_data = [
            ("system", "Q1", "question"),
            ("user", "A1", "answer"),
            ("system", "Q2", "question"),
            ("user", "A2", "answer"),
            ("system", "Q3", "question"),
            ("user", "A3", "answer"),
            ("system", "confirmed", "confirm"),
        ]
        for role, content, ttype in turns_data:
            sm.add_turn(role, content, ttype)

        session = sm.get_active_session()
        context = build_generation_context(session)
        summary = context["conversation_summary"]

        # 只包含最近 5 轮（第 3-7 轮）
        assert "[用户]" in summary
        assert "[系统]" in summary
        # 前 2 轮被截断，不在摘要中
        assert "Q1" not in summary
        assert "A1" not in summary
        # 后 5 轮在摘要中
        assert "Q3" in summary
        assert "A3" in summary
        assert "confirmed" in summary

    def test_conversation_summary_empty_turns(self, session_manager_instance):
        """零轮次会话的 conversation_summary 为空字符串"""
        sm = session_manager_instance
        sm.create_session()
        session = sm.get_active_session()

        context = build_generation_context(session)

        assert context["conversation_summary"] == ""
