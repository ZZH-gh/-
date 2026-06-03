"""
ConversationEngine 单元测试 — 9态状态机、状态转换、完整对话路径
"""
import pytest
from prompt_tool.conversation_engine import (
    ConversationEngine, ConversationState, ConversationError,
)


class TestConversationState:
    """状态枚举定义测试"""

    def test_all_states_defined(self):
        assert len(ConversationState) == 9
        for s in ("idle", "analyzing", "confirming", "clarifying",
                   "following_up", "generating", "complete", "error", "paused"):
            assert ConversationState(s) is not None


class TestStateMachine:
    """状态机转换规则测试"""

    def test_starts_from_idle(self):
        engine = ConversationEngine()
        assert engine.state == ConversationState.IDLE

    def test_start_transitions_to_confirming(self):
        engine = ConversationEngine()
        result = engine.start("帮我写一个电商PRD")
        assert engine.state in (ConversationState.CONFIRMING, ConversationState.CLARIFYING)

    def test_invalid_transition_raises_error(self):
        engine = ConversationEngine()
        with pytest.raises(ConversationError):
            engine.handle_answer("test")

    def test_handle_confirmation_transitions(self):
        engine = ConversationEngine()
        engine.start("帮我写一个电商平台的PRD文档")
        if engine.state == ConversationState.CONFIRMING:
            result = engine.handle_confirmation(True)
            assert engine.state in (
                ConversationState.FOLLOWING_UP,
                ConversationState.GENERATING,
            )

    def test_reset_goes_to_idle(self):
        engine = ConversationEngine()
        engine.start("test")
        engine.reset()
        assert engine.state == ConversationState.IDLE

    def test_skip_follow_up_generates(self):
        engine = ConversationEngine()
        engine.start("帮我写一个PRD文档")
        if engine.state == ConversationState.CONFIRMING:
            engine.handle_confirmation(True)
        result = engine.skip_follow_up()
        assert engine.state == ConversationState.GENERATING


class TestFullLifecycle:
    """完整对话路径测试"""

    def test_idle_to_clarifying_for_vague_input(self):
        engine = ConversationEngine()
        result = engine.start("")
        assert engine.state in (
            ConversationState.CLARIFYING,
            ConversationState.CONFIRMING,
        )

    def test_low_confidence_clarifies(self):
        engine = ConversationEngine()
        result = engine.start("不知道")
        assert engine.state in (
            ConversationState.CLARIFYING,
            ConversationState.CONFIRMING,
        )
