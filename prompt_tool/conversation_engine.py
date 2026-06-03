"""
对话引擎 v4.0 — 9态状态机（CONV-01），编排 分析→确认→追问→生成 全流程
"""

from enum import Enum
from .intent_classifier import IntentClassifier
from .follow_up_engine import FollowUpEngine
from .session_manager import session_manager
from .context_builder import build_generation_context


class ConversationError(Exception):
    """非法状态转换"""
    pass


class ConversationState(str, Enum):
    IDLE = "idle"
    ANALYZING = "analyzing"
    CONFIRMING = "confirming"
    CLARIFYING = "clarifying"
    FOLLOWING_UP = "following_up"
    GENERATING = "generating"
    COMPLETE = "complete"
    ERROR = "error"
    PAUSED = "paused"


VALID_TRANSITIONS = {
    ConversationState.IDLE: {ConversationState.ANALYZING},
    ConversationState.ANALYZING: {ConversationState.CONFIRMING, ConversationState.CLARIFYING, ConversationState.ERROR},
    ConversationState.CONFIRMING: {ConversationState.FOLLOWING_UP, ConversationState.GENERATING, ConversationState.CLARIFYING, ConversationState.IDLE},
    ConversationState.CLARIFYING: {ConversationState.ANALYZING, ConversationState.CONFIRMING, ConversationState.GENERATING, ConversationState.ERROR},
    ConversationState.FOLLOWING_UP: {ConversationState.GENERATING, ConversationState.COMPLETE, ConversationState.ERROR},
    ConversationState.GENERATING: {ConversationState.COMPLETE, ConversationState.ERROR},
    ConversationState.COMPLETE: {ConversationState.IDLE, ConversationState.ANALYZING},
    ConversationState.ERROR: {ConversationState.IDLE, ConversationState.ANALYZING},
    ConversationState.PAUSED: {ConversationState.IDLE, ConversationState.FOLLOWING_UP, ConversationState.GENERATING},
}


class ConversationEngine:
    """9态对话引擎（CONV-01）"""

    def __init__(self):
        self.state = ConversationState.IDLE
        self._classifier = IntentClassifier()
        self._follow_up: FollowUpEngine | None = None
        self._last_analysis: dict = {}

    def _transition(self, to_state: ConversationState):
        if to_state not in VALID_TRANSITIONS.get(self.state, set()):
            raise ConversationError(
                f"非法状态转换: {self.state.value} -> {to_state.value}"
            )
        self.state = to_state

    def start(self, user_input: str) -> dict:
        """接收用户输入，执行分析-确认流程。返回 action dict 供 UI 消费。"""
        self._transition(ConversationState.ANALYZING)

        if not session_manager.has_active_session():
            session_manager.create_session()
        session_manager.add_turn("user", user_input, "answer")

        # Intent classification (CONV-02)
        result = self._classifier.classify(user_input)
        self._last_analysis = result

        if result["needs_clarification"]:
            self._transition(ConversationState.CLARIFYING)
            return {
                "state": self.state.value,
                "needs_clarification": True,
                "message": "能再说详细一点吗？比如你是什么角色，想做什么？",
            }

        session_manager.update_confirmed_industry(result["industry_id"])
        session_manager.update_confirmed_task(result["task_key"])
        self._transition(ConversationState.CONFIRMING)

        return {
            "state": self.state.value,
            "needs_clarification": False,
            "industry_id": result["industry_id"],
            "industry_name": result["industry_name"],
            "industry_confidence": result["industry_confidence"],
            "task_key": result["task_key"],
            "task_name": result["task_name"],
            "task_confidence": result["task_confidence"],
        }

    def handle_confirmation(self, confirmed: bool, corrected_industry: str = None, corrected_task: str = None) -> dict:
        """用户确认或纠正行业/任务识别结果。"""
        if confirmed:
            session_manager.add_turn("user", "确认", "confirm")
            self._transition(ConversationState.FOLLOWING_UP)

            pack = None
            try:
                from .knowledge_manager import knowledge_manager
                pack = knowledge_manager.load_pack(self._last_analysis.get("industry_id", ""))
            except Exception:
                pass

            self._follow_up = FollowUpEngine(
                pack=pack,
                task_type=self._last_analysis.get("task_key", ""),
            )
            return self._get_next_question()
        else:
            session_manager.add_turn("user", "需要修正", "answer")
            if corrected_industry:
                session_manager.update_confirmed_industry(corrected_industry)
            if corrected_task:
                session_manager.update_confirmed_task(corrected_task)
            self._transition(ConversationState.ANALYZING)
            return {
                "state": self.state.value,
                "action": "reanalyze",
                "message": "请重新描述你的需求",
            }

    def handle_answer(self, answer: str) -> dict:
        """处理用户对追问的回答。"""
        if self.state != ConversationState.FOLLOWING_UP or self._follow_up is None:
            raise ConversationError(f"当前状态 {self.state.value} 不支持回答追问")

        session_manager.add_turn("user", answer, "answer")
        self._follow_up.handle_answer(answer)

        if self._follow_up.is_degraded():
            self._transition(ConversationState.CLARIFYING)
            return {
                "state": self.state.value,
                "action": "clarify",
                "message": self._follow_up.get_clarify_prompt(),
            }

        if self._follow_up.has_more_questions():
            return self._get_next_question()
        else:
            self._transition(ConversationState.GENERATING)
            session = session_manager.get_active_session()
            return {
                "state": self.state.value,
                "action": "generate",
                "generation_context": build_generation_context(session) if session else {},
            }

    def handle_clarify_response(self, answer: str) -> dict:
        """处理 CLARIFYING 状态的用户响应。"""
        if self.state != ConversationState.CLARIFYING:
            raise ConversationError(f"当前状态 {self.state.value} 不支持澄清响应")

        session_manager.add_turn("user", answer, "answer")
        self._transition(ConversationState.ANALYZING)
        return self.start(answer)

    def handle_dont_know(self) -> dict:
        """处理"我不知道"（CONV-05 3级降级）。"""
        if self.state != ConversationState.FOLLOWING_UP or self._follow_up is None:
            raise ConversationError(f"当前状态 {self.state.value} 不支持降级")

        session_manager.add_turn("user", "不知道", "answer")
        result = self._follow_up.handle_dont_know()

        if result.get("fully_degraded"):
            self._transition(ConversationState.GENERATING)
            session = session_manager.get_active_session()
            return {
                "state": self.state.value,
                "action": "generate",
                "generation_context": build_generation_context(session) if session else {},
            }

        return self._get_next_question()

    def skip_follow_up(self) -> dict:
        """跳过追问，直接生成（CONV-04 逃生门）。从任何状态都可用。"""
        if session_manager.has_active_session():
            session_manager.add_turn("user", "直接生成", "confirm")
        # 强制跳转：允许从多种状态跳到 GENERATING
        if self.state not in (ConversationState.GENERATING, ConversationState.COMPLETE, ConversationState.IDLE):
            self.state = ConversationState.GENERATING
        session = session_manager.get_active_session()
        return {
            "state": self.state.value,
            "action": "generate",
            "generation_context": build_generation_context(session) if session else {},
        }

    def generate_complete(self) -> dict:
        """生成完成，回到完成状态。"""
        self._transition(ConversationState.COMPLETE)
        return {"state": self.state.value, "action": "display_results"}

    def reset(self):
        """重置引擎到 IDLE。"""
        self.state = ConversationState.IDLE
        self._follow_up = None
        self._last_analysis = {}

    # === private ===

    def _get_next_question(self) -> dict:
        """获取下一个追问，带 3 问题限制（CONV-04）。"""
        if self._follow_up is None:
            self._transition(ConversationState.GENERATING)
            session = session_manager.get_active_session()
            return {
                "state": self.state.value,
                "action": "generate",
                "generation_context": build_generation_context(session) if session else {},
            }

        result = self._follow_up.next_question()

        if result is None:
            self._transition(ConversationState.GENERATING)
            session = session_manager.get_active_session()
            return {
                "state": self.state.value,
                "action": "generate",
                "generation_context": build_generation_context(session) if session else {},
            }

        session_manager.add_turn("system", result["question_text"], "question")
        return {
            "state": self.state.value,
            "action": "follow_up",
            "question": result,
            "question_number": self._follow_up.question_count,
            "max_questions": self._follow_up.MAX_QUESTIONS,
        }
