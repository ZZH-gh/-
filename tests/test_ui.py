"""
AppController 单元测试 — 生命周期与并发防护
"""
import pytest
from prompt_tool.app_controller import AppController
from prompt_tool.conversation_engine import ConversationState


class TestAppControllerLifecycle:
    """AppController 基本生命周期测试"""

    def setup_method(self):
        """Clear session state between tests."""
        from prompt_tool.session_manager import session_manager
        session_manager._active_session = None

    def test_init_state_idle_no_session(self):
        """Test 1: 初始化后 state 为 IDLE，无活跃会话"""
        controller = AppController()
        assert controller.state == ConversationState.IDLE
        from prompt_tool.session_manager import session_manager
        session_manager._active_session = None
        assert not session_manager.has_active_session()

    def test_start_session_changes_state(self):
        """Test 2: start_session 后 state 不为 IDLE"""
        controller = AppController()
        controller.process_input("帮我写一个电商PRD")
        import time
        time.sleep(0.5)
        assert controller.state != ConversationState.IDLE

    def test_reset_returns_to_idle(self):
        """Test 3: reset() 后引擎回到 IDLE，_is_generating 为 False"""
        controller = AppController()
        controller.process_input("帮我写一个电商PRD")
        import time
        time.sleep(0.5)
        controller.reset()
        assert controller.state == ConversationState.IDLE
        assert controller._is_generating == False

    def test_concurrency_guard(self):
        """Test 4: 并发防护：_is_generating=True 时 process_input 被忽略"""
        calls = []
        controller = AppController(
            on_question=lambda d: calls.append("q"),
            on_state_change=lambda d: calls.append("s"),
        )
        controller._is_generating = True
        controller.process_input("测试输入")
        assert len(calls) == 0

    def test_generate_complete_returns_prompts(self):
        """Test 5: generate_complete() 返回含三个策略键的 dict"""
        controller = AppController()
        controller._engine.start("帮我写一个电商平台PRD")
        import time
        time.sleep(0.3)
        if controller._engine.state == ConversationState.CONFIRMING:
            controller._engine.handle_confirmation(True)
        result = controller.generate_complete()
        assert isinstance(result, dict)
        prompts = result.get("prompts", {})
        assert "direct" in prompts
        assert "roleplay" in prompts
        assert "detailed" in prompts


class TestAppControllerThreadSafety:
    """并发防护验证"""

    def setup_method(self):
        from prompt_tool.session_manager import session_manager
        session_manager._active_session = None

    def test_is_generating_blocks_skip(self):
        """_is_generating=True 时 skip_and_generate 被忽略"""
        calls = []
        controller = AppController(
            on_results=lambda d: calls.append("r"),
            on_error=lambda d: calls.append("e"),
        )
        controller._is_generating = True
        controller.skip_and_generate()
        assert len(calls) == 0
