"""
SessionManager 单元测试 — 测试会话创建、轮次记录、确认更新、信息提取、快照隔离、生命周期
"""

import pytest
from prompt_tool.session_manager import SessionManager, ConversationTurn, SessionState


class TestConversationTurn:
    """ConversationTurn NamedTuple 结构和不可变性测试"""

    def test_turn_structure(self):
        """验证 ConversationTurn 的 4 个字段和 NamedTuple 不可变性"""
        turn = ConversationTurn(
            role="system",
            content="你需要什么帮助？",
            turn_type="question",
            timestamp=1234567890.0,
        )
        assert turn.role == "system"
        assert turn.content == "你需要什么帮助？"
        assert turn.turn_type == "question"
        assert turn.timestamp == 1234567890.0

        # NamedTuple 不可变性
        with pytest.raises(AttributeError):
            turn.content = "modified"


class TestSessionManager:
    """SessionManager 会话生命周期测试"""

    def test_create_session(self, session_manager_instance):
        """create_session() 返回 uuid4 格式的 session_id，初始化状态正确"""
        sm = session_manager_instance
        session_id = sm.create_session()

        assert isinstance(session_id, str)
        assert len(session_id) == 36  # uuid4 标准长度
        assert sm.has_active_session() is True
        assert sm.get_turn_count() == 0
        assert sm.get_elapsed_seconds() > 0

    def test_add_turn(self, session_manager_instance):
        """add_turn() 追加 ConversationTurn 并增加轮次计数"""
        sm = session_manager_instance
        sm.create_session()
        sm.add_turn("system", "你想做什么类型的分析？", "question")

        assert sm.get_turn_count() == 1
        session = sm.get_active_session()
        turn = session.turns[0]
        assert turn.role == "system"
        assert turn.content == "你想做什么类型的分析？"
        assert turn.turn_type == "question"
        assert isinstance(turn.timestamp, float)

    def test_update_confirmed(self, session_manager_instance):
        """update_confirmed_industry/task 设置活跃会话的确认字段"""
        sm = session_manager_instance
        sm.create_session()

        sm.update_confirmed_industry("internet_it")
        sm.update_confirmed_task("prd_writing")

        session = sm.get_active_session()
        assert session.confirmed_industry == "internet_it"
        assert session.confirmed_task == "prd_writing"

    def test_extracted_info(self, session_manager_instance):
        """update_extracted_info 累积键值对，可跨多次调用追加"""
        sm = session_manager_instance
        sm.create_session()

        sm.update_extracted_info("tone", "正式")
        sm.update_extracted_info("role", "产品经理")

        session = sm.get_active_session()
        assert session.extracted_info == {"tone": "正式", "role": "产品经理"}

    def test_new_session(self, session_manager_instance):
        """new_session() 丢弃旧会话，创建新会话（D-04 单会话模式）"""
        sm = session_manager_instance

        id1 = sm.create_session()
        sm.add_turn("user", "旧会话的消息", "answer")

        id2 = sm.new_session()

        assert id2 != id1
        assert sm.get_turn_count() == 0  # 新会话无轮次

    def test_snapshot_independence(self, session_manager_instance):
        """get_session_snapshot() 返回独立深拷贝，修改不影响原会话（D-06）"""
        sm = session_manager_instance
        sm.create_session()
        sm.add_turn("system", "测试消息", "info")
        sm.update_extracted_info("key", "original")

        snapshot = sm.get_session_snapshot()
        assert snapshot is not None

        # 修改快照
        snapshot.turns.append(ConversationTurn("evil", "bad", "question", 0.0))
        snapshot.extracted_info["key"] = "mutation"

        # 原会话不变
        original = sm.get_active_session()
        assert sm.get_turn_count() == 1
        assert original.extracted_info["key"] == "original"

    def test_add_turn_no_session(self, session_manager_instance):
        """无活跃会话时 add_turn() 抛出 RuntimeError"""
        sm = session_manager_instance
        with pytest.raises(RuntimeError, match="No active session"):
            sm.add_turn("user", "hello", "answer")

    def test_update_no_session(self, session_manager_instance):
        """无活跃会话时 update_confirmed_industry() 抛出 RuntimeError"""
        sm = session_manager_instance
        with pytest.raises(RuntimeError):
            sm.update_confirmed_industry("internet_it")

    def test_has_active_session_false_initially(self, session_manager_instance):
        """初始化后未创建会话时 has_active_session() 返回 False"""
        sm = session_manager_instance
        assert sm.has_active_session() is False
        assert sm.get_active_session() is None
        assert sm.get_session_snapshot() is None

    def test_full_lifecycle(self):
        """端到端生命周期：创建→3轮→确认→提取→快照→新建→验证隔离"""
        sm = SessionManager()

        # 创建
        sid = sm.create_session()
        assert sm.has_active_session()

        # 3 轮对话
        sm.add_turn("system", "你属于哪个行业？", "question")
        sm.add_turn("user", "我是后端开发工程师", "answer")
        sm.add_turn("system", "已确认角色：后端开发工程师", "confirm")

        # 确认行业 & 任务
        sm.update_confirmed_industry("internet_it")
        sm.update_confirmed_task("code_generation")

        # 提取信息
        sm.update_extracted_info("role", "后端工程师")
        sm.update_extracted_info("language", "Python")

        # 快照
        snapshot = sm.get_session_snapshot()
        assert snapshot.confirmed_industry == "internet_it"
        assert snapshot.confirmed_task == "code_generation"
        assert len(snapshot.turns) == 3
        assert snapshot.extracted_info["role"] == "后端工程师"

        # 新建会话
        new_sid = sm.new_session()
        assert new_sid != sid
        assert sm.get_turn_count() == 0
        assert sm.get_active_session().confirmed_industry is None

        # 快照仍保留旧数据
        assert snapshot.confirmed_industry == "internet_it"
