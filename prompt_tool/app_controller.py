"""
AppController — UI 事件与 ConversationEngine 的中介编排器

职责：
  - 封装 ConversationEngine 生命周期（启动、追问、生成、重置）
  - 管理后台线程，通过回调向 UI 报告状态变更
  - 并发防护：_is_generating 标志防止重复调用

回调约定（由 UI 层用 self.root.after 包装以确保线程安全）：
  on_state_change(data: dict) — 引擎状态变更（行业确认等）
  on_question(data: dict) — 引擎发出追问/澄清
  on_results(data: dict) — 生成完成，包含 prompts
  on_error(data: dict) — 引擎出错
"""

import threading

from .conversation_engine import ConversationEngine, ConversationState


class AppController:
    """编排器：中介 UI 事件与 ConversationEngine 的调用"""

    def __init__(self, on_state_change=None, on_question=None,
                 on_results=None, on_error=None):
        self._engine = ConversationEngine()
        self._is_generating = False
        self._callbacks = {
            "on_state_change": on_state_change or (lambda d: None),
            "on_question": on_question or (lambda d: None),
            "on_results": on_results or (lambda d: None),
            "on_error": on_error or (lambda d: None),
        }

    @property
    def state(self):
        """当前引擎状态"""
        return self._engine.state

    # ================================================================
    # 公共 API
    # ================================================================

    def process_input(self, user_input: str) -> None:
        """统一入口：根据引擎状态路由到正确处理器

        - IDLE → engine.start() (首次输入，自动解析)
        - CONFIRMING → engine.handle_confirmation(True) (自动确认)
        - CLARIFYING → engine.handle_clarify_response() (澄清回复)
        - FOLLOWING_UP → engine.handle_answer() (追问回答)
        - 其他状态 → 忽略
        """
        if self._is_generating:
            return
        self._is_generating = True

        if self._engine.state == ConversationState.IDLE:
            threading.Thread(target=self._do_start,
                             args=(user_input,), daemon=True).start()
        elif self._engine.state == ConversationState.CONFIRMING:
            threading.Thread(target=self._do_confirm, daemon=True).start()
        elif self._engine.state == ConversationState.CLARIFYING:
            threading.Thread(target=self._do_clarify,
                             args=(user_input,), daemon=True).start()
        elif self._engine.state == ConversationState.FOLLOWING_UP:
            threading.Thread(target=self._do_answer,
                             args=(user_input,), daemon=True).start()
        else:
            self._is_generating = False

    def skip_and_generate(self) -> None:
        """跳过追问，直接生成（逃生门）

        后台线程调用 engine.skip_follow_up() + engine.generate_complete()
        """
        if self._is_generating:
            return
        self._is_generating = True
        threading.Thread(target=self._do_skip_and_generate,
                         daemon=True).start()

    def generate_complete(self) -> dict:
        """同步调用引擎生成（用于初始快速生成路径）

        Returns:
            engine.generate_complete() 返回的完整 dict:
            {"state": "complete", "action": "display_results",
             "prompts": {"direct": ..., "roleplay": ..., "detailed": ...}}
        """
        result = self._engine.generate_complete()
        return result

    def reset(self) -> None:
        """重置引擎和生成状态"""
        self._engine.reset()
        self._is_generating = False

    # ================================================================
    # 内部后台方法（在 daemon 线程中运行）
    # ================================================================

    def _do_start(self, user_input: str):
        """首次输入：engine.start() + 根据结果自动路由"""
        try:
            result = self._engine.start(user_input)
            self._handle_start_result(result)
        except Exception as e:
            self._call_callbacks("on_error", {"error": str(e)})
            self._is_generating = False

    def _handle_start_result(self, result: dict):
        """处理 engine.start() 的结果并自动继续流程"""
        if result.get("needs_clarification"):
            # 低置信度 → 通过 on_question 回调让 UI 显示澄清提示
            self._call_callbacks("on_question", {
                "action": "clarify",
                "question_text": result.get("message", "能再说详细一点吗？"),
                "question_type": "text_input",
                "question_number": 0,
                "max_questions": 1,
            })
            self._is_generating = False
        else:
            # 高置信度 → 自动确认，进入追问流
            next_result = self._engine.handle_confirmation(True)
            self._dispatch_action(next_result)

    def _do_confirm(self):
        """自动确认行业/任务识别"""
        try:
            result = self._engine.handle_confirmation(True)
            self._dispatch_action(result)
        except Exception as e:
            self._call_callbacks("on_error", {"error": str(e)})
            self._is_generating = False

    def _do_clarify(self, answer: str):
        """处理用户的澄清回复"""
        try:
            result = self._engine.handle_clarify_response(answer)
            # handle_clarify_response 内部会重走 start 流程
            self._handle_start_result(result)
        except Exception as e:
            self._call_callbacks("on_error", {"error": str(e)})
            self._is_generating = False

    def _do_answer(self, answer: str):
        """处理用户对追问的回答"""
        try:
            result = self._engine.handle_answer(answer)
            self._dispatch_action(result)
        except Exception as e:
            self._call_callbacks("on_error", {"error": str(e)})
            self._is_generating = False

    def _do_skip_and_generate(self):
        """逃生门：跳过追问直接生成"""
        try:
            self._engine.skip_follow_up()
            result = self._engine.generate_complete()
            self._call_callbacks("on_results", result)
        except Exception as e:
            self._call_callbacks("on_error", {"error": str(e)})
        finally:
            self._is_generating = False

    def _dispatch_action(self, result: dict):
        """根据引擎返回的 action 分发到对应回调"""
        action = result.get("action")

        if action == "follow_up":
            # 引擎发出追问 → 通知 UI 显示
            self._call_callbacks("on_question", result)
            self._is_generating = False
        elif action == "generate":
            # 所有追问已完成 → 执行生成
            try:
                gen_result = self._engine.generate_complete()
                self._call_callbacks("on_results", gen_result)
            except Exception as e:
                self._call_callbacks("on_error", {"error": str(e)})
            finally:
                self._is_generating = False
        elif action == "clarify":
            self._call_callbacks("on_question", result)
            self._is_generating = False
        elif action == "reanalyze":
            self._call_callbacks("on_state_change", result)
            self._is_generating = False
        elif result.get("state") == "confirming":
            self._call_callbacks("on_state_change", result)
            self._is_generating = False
        else:
            self._call_callbacks("on_state_change", result)
            self._is_generating = False

    # ================================================================
    # 回调辅助
    # ================================================================

    def _call_callbacks(self, name: str, data: dict):
        """调用回调（同步 — UI 层负责 root.after 包装）

        Caller 负责确保已释放 _is_generating 标志。
        """
        cb = self._callbacks.get(name)
        if cb:
            cb(data)
