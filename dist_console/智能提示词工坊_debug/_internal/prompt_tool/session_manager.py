"""
会话状态管理器 — 追踪多轮对话的会话历史、已确认信息、推导上下文

SessionManager 管理单活跃会话（D-04），支持：
- 创建/新建会话
- 记录每轮对话（ConversationTurn）
- 累积确认信息（行业、任务）
- 提取信息（语气、角色等）
- 线程安全的深拷贝快照（D-06：主线程写，后台线程读）
"""

import time
import uuid
from copy import deepcopy
from typing import NamedTuple


class ConversationTurn(NamedTuple):
    """单轮对话记录（D-01）

    Fields:
        role: "user" | "system"
        content: 对话文本
        turn_type: "question" | "answer" | "confirm" | "info"
        timestamp: time.time() 时间戳

    NamedTuple 保证不可变——轮次记录后不能修改，只能追加。
    """
    role: str
    content: str
    turn_type: str
    timestamp: float


class SessionState:
    """活跃会话的完整状态（D-02）

    字段：
        session_id: uuid4 格式的唯一会话标识
        created_at: 会话创建时间（time.time()）
        turns: 对话轮次列表（ConversationTurn 追加）
        confirmed_industry: 已确认的行业 ID 引用（D-03：存 ID，不存快照）
        confirmed_task: 已确认的任务类型 key
        extracted_info: 累积的提取信息（snake_case key → str value）
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = time.time()
        self.turns: list[ConversationTurn] = []
        self.confirmed_industry: str | None = None
        self.confirmed_task: str | None = None
        self.extracted_info: dict[str, str] = {}

    def to_snapshot(self) -> "SessionState":
        """返回独立深拷贝快照——线程安全机制（D-06）"""
        return deepcopy(self)


class SessionManager:
    """会话管理器——单活跃会话模式（D-04）

    使用方式：
        session_manager = SessionManager()  # 或 import 模块级单例
        session_manager.create_session()
        session_manager.add_turn("system", "...", "question")
        session_manager.get_session_snapshot()  # 后台线程安全读取
    """

    def __init__(self):
        self._active_session: SessionState | None = None
        self._initialized = False

    def initialize(self) -> None:
        """初始化会话管理器（目前为 no-op，保留给未来的持久化 I/O）"""
        self._initialized = True

    # === 会话生命周期 ===

    def create_session(self) -> str:
        """创建新会话，返回 uuid4 session_id。替换已有会话（D-04 单会话模式）。"""
        session_id = str(uuid.uuid4())
        self._active_session = SessionState(session_id)
        return session_id

    def new_session(self) -> str:
        """丢弃旧会话，创建新会话（D-04）"""
        return self.create_session()

    def has_active_session(self) -> bool:
        """是否存在活跃会话"""
        return self._active_session is not None

    # === 线程安全访问（D-06） ===

    def get_active_session(self) -> SessionState | None:
        """返回活跃会话的实时引用。

        ⚠ 仅供主线程使用。后台线程请使用 get_session_snapshot()。
        """
        return self._active_session

    def get_session_snapshot(self) -> SessionState | None:
        """返回独立深拷贝快照。

        ✅ 安全用于后台线程读取。修改快照不影响活跃会话。
        无活跃会话时返回 None。
        """
        if self._active_session is None:
            return None
        return self._active_session.to_snapshot()

    # === 轮次记录 ===

    def add_turn(self, role: str, content: str, turn_type: str) -> None:
        """追加一轮对话记录到活跃会话。

        Raises:
            RuntimeError: 无活跃会话时调用。
        """
        if self._active_session is None:
            raise RuntimeError("No active session. Call create_session() first.")
        turn = ConversationTurn(
            role=role,
            content=content,
            turn_type=turn_type,
            timestamp=time.time(),
        )
        self._active_session.turns.append(turn)

    # === 确认信息更新 ===

    def update_confirmed_industry(self, industry_id: str) -> None:
        """设置已确认的行业 ID 引用（D-03）"""
        if self._active_session is None:
            raise RuntimeError("No active session. Call create_session() first.")
        self._active_session.confirmed_industry = industry_id

    def update_confirmed_task(self, task_key: str) -> None:
        """设置已确认的任务类型 key"""
        if self._active_session is None:
            raise RuntimeError("No active session. Call create_session() first.")
        self._active_session.confirmed_task = task_key

    # === 累积信息提取 ===

    def update_extracted_info(self, key: str, value: str) -> None:
        """累积提取信息。调用方应确保 key 使用 snake_case 命名，value 为字符串。

        Raises:
            RuntimeError: 无活跃会话时调用。
        """
        if self._active_session is None:
            raise RuntimeError("No active session. Call create_session() first.")
        self._active_session.extracted_info[key] = value

    # === 查询方法 ===

    def get_turn_count(self) -> int:
        """返回当前会话的轮次数。无会话时返回 0。"""
        if self._active_session is None:
            return 0
        return len(self._active_session.turns)

    def get_elapsed_seconds(self) -> float:
        """返回会话创建至今的秒数。无会话时返回 0.0。"""
        if self._active_session is None:
            return 0.0
        return time.time() - self._active_session.created_at


# 模块级单例（D-10：与 knowledge_manager.py 模式一致）
session_manager = SessionManager()
