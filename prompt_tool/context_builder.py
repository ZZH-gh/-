"""
上下文构建器 — 从 SessionState 构建 Phase 5 生成器需要的 GenerationContext dict

Pure function，无副作用。接收 SessionState（或深拷贝快照），返回包含 6 个固定字段
的 dict（D-05）：industry_id, industry_name, task_type, confirmed_info,
conversation_summary, knowledge_pack_ref。

知识点数据通过 KnowledgeManager 按需查询（D-03：存 ID，不存快照）。
"""

from .knowledge_manager import knowledge_manager

# 对话摘要最大轮次数（Claude 裁量：按 RESEARCH.md 推荐）
CONVERSATION_SUMMARY_MAX_TURNS = 5


def build_generation_context(session) -> dict:
    """从 SessionState 构建 GenerationContext dict（D-05）

    Args:
        session: SessionState 实例（或 get_session_snapshot() 返回的深拷贝）

    Returns:
        dict，包含 6 个固定字段：
        - industry_id: str | None
        - industry_name: str
        - task_type: str | None
        - confirmed_info: dict[str, str]
        - conversation_summary: str
        - knowledge_pack_ref: dict | None
    """
    industry_id = session.confirmed_industry

    if industry_id:
        # D-03：通过 KnowledgeManager 按需查询，不存快照
        index = knowledge_manager.get_index()
        entry = index.get(industry_id, {})
        industry_name = entry.get("name", industry_id)

        knowledge_pack_ref = None
        try:
            pack = knowledge_manager.load_pack(industry_id)
            knowledge_pack_ref = pack.get_meta()
        except Exception:
            knowledge_pack_ref = {"id": industry_id, "name": industry_name}
    else:
        industry_name = "通用 / 其他"
        knowledge_pack_ref = None

    confirmed_info = dict(session.extracted_info)  # 浅拷贝
    conversation_summary = _build_summary(session.turns)
    task_type = session.confirmed_task

    return {
        "industry_id": industry_id,
        "industry_name": industry_name,
        "task_type": task_type,
        "confirmed_info": confirmed_info,
        "conversation_summary": conversation_summary,
        "knowledge_pack_ref": knowledge_pack_ref,
    }


def _build_summary(turns: list, max_turns: int = CONVERSATION_SUMMARY_MAX_TURNS) -> str:
    """构建最近 N 轮对话摘要

    每行格式：[用户] content 或 [系统] content，用换行符拼接。
    空列表返回空字符串。

    Args:
        turns: ConversationTurn 列表
        max_turns: 最大保留轮次数（默认 5）
    """
    if not turns:
        return ""

    recent = turns[-max_turns:] if len(turns) > max_turns else turns
    lines = []
    for turn in recent:
        label = "用户" if turn.role == "user" else "系统"
        lines.append(f"[{label}] {turn.content}")

    return "\n".join(lines)
