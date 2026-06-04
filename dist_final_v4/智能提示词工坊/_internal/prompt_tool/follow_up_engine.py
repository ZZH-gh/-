"""
追问引擎（CONV-03）— 知识包追问决策树遍历器

支持 4 种节点类型（single_choice, multi_choice, text_input, confirm），
3 问题硬限制（CONV-04），3 级降级处理（CONV-05）。
"""

RANK_DEGRADATION = ["simplify", "broader", "examples"]

SIMPLIFIED_QUESTIONS = {
    "single_choice": "请从以下选项中选择一个：",
    "multi_choice": "可以选择多个：",
    "text_input": "请简单描述一下：",
    "confirm": "请确认以上信息是否正确？",
}

EXAMPLE_PROMPTS = {
    "single_choice": '例如选"技术方案"或"产品规划"都可以',
    "multi_choice": "可以多选，例如同时需要技术方案和成本分析",
    "text_input": '例如：需要支持1000并发用户',
    "confirm": '回答"是"或"不是"即可',
}


class FollowUpEngine:
    """追问决策树遍历器"""

    MAX_QUESTIONS = 3  # CONV-04: 硬限制

    def __init__(self, pack, task_type: str):
        """初始化追问引擎。

        Args:
            pack: KnowledgePack 实例（含 get_follow_up_tree()）
            task_type: 当前任务类型 key，用于选择对应的追问树
        """
        self.pack = pack
        self.task_type = task_type
        self.question_count = 0
        self._degradation_level = 0
        self._per_node_degradation: dict[str, int] = {}
        self._current_node_id: str | None = None
        self._answers: list[dict] = []

        # 加载追问树
        tree = None
        if pack:
            try:
                tree = pack.get_follow_up_tree(task_type)
            except Exception:
                tree = None

        if tree and isinstance(tree, dict) and tree.get("nodes"):
            self.tree = tree
            self._current_node_id = tree.get("root_node_id")
            self._nodes = tree.get("nodes", {})
        else:
            self.tree = None
            self._current_node_id = None
            self._nodes = {}

    def has_more_questions(self) -> bool:
        """是否还有更多追问（受 CONV-04 3问题限制）。"""
        if self.question_count >= self.MAX_QUESTIONS:
            return False
        if self._current_node_id is None:
            return False
        node = self._nodes.get(self._current_node_id)
        return node is not None and not node.get("is_leaf", False)

    def is_degraded(self) -> bool:
        """是否已进入降级模式（需要澄清）。"""
        return self._degradation_level > 0

    def get_clarify_prompt(self) -> str:
        """获取降级澄清引导文本。"""
        prompts = {
            1: "我换个方式问：",
            2: "没关系，让我从更宽的角度来了解：",
            3: "我来举个例子帮您理解这个问题：",
        }
        return prompts.get(self._degradation_level, "能再多说一点吗？")

    def next_question(self) -> dict | None:
        """返回下一个追问节点。无更多追问时返回 None。"""
        if self.question_count >= self.MAX_QUESTIONS:
            return None

        node_id = self._current_node_id
        if node_id is None:
            return None

        node = self._nodes.get(node_id)
        if node is None:
            return None

        self.question_count += 1
        degradation = self._per_node_degradation.get(node_id, 0)
        question = self._build_question(node, degradation)

        return {
            "node_id": node_id,
            "question_text": question,
            "question_type": node.get("question_type", "text_input"),
            "options": node.get("options", []),
            "degradation_level": degradation,
        }

    def handle_answer(self, answer: str):
        """处理用户对当前追问的回答，前进到下一节点。"""
        node_id = self._current_node_id
        node = self._nodes.get(node_id, {}) if node_id else {}
        qtype = node.get("question_type", "text_input")

        self._answers.append({
            "node_id": node_id,
            "question_type": qtype,
            "answer": answer,
        })

        # 根据节点类型确定下一节点
        if qtype == "single_choice" and node.get("children"):
            next_id = node["children"].get(answer)
            if next_id:
                self._current_node_id = next_id
                return

        if qtype == "confirm":
            is_yes = answer.strip().lower() in ("是", "yes", "对", "确认", "ok", "y")
            if is_yes and node.get("children"):
                children = node.get("children", {})
                next_id = children.get("_yes") or children.get("yes") or next(iter(children.values()), None)
                if next_id:
                    self._current_node_id = next_id
                    return

        # 通用前进：取第一个子节点
        children = node.get("children", {})
        if children:
            self._current_node_id = next(iter(children.values()))
        elif node.get("fallback_node_id"):
            self._current_node_id = node.get("fallback_node_id")
        else:
            self._current_node_id = None

    def handle_dont_know(self) -> dict:
        """处理"我不知道"（CONV-05 3级降级）。"""
        node_id = self._current_node_id
        if node_id:
            current_level = self._per_node_degradation.get(node_id, 0)
            if current_level < len(RANK_DEGRADATION):
                self._per_node_degradation[node_id] = current_level + 1
                self._degradation_level = current_level + 1
            else:
                # 完全降级：跳过此节点
                node = self._nodes.get(node_id, {})
                if node.get("fallback_node_id"):
                    self._current_node_id = node["fallback_node_id"]
                else:
                    self._current_node_id = None
                self._per_node_degradation[node_id] = 0

        fully_degraded = (self._current_node_id is None or self.question_count >= self.MAX_QUESTIONS)
        return {"fully_degraded": fully_degraded}

    def _build_question(self, node: dict, degradation: int) -> str:
        """根据降级等级构建问题文本。"""
        if degradation <= 0:
            return node.get("question_text", node.get("question", ""))

        if degradation >= 3:
            base = EXAMPLE_PROMPTS.get(node.get("question_type", "text_input"), "")
            return f"{base}\n\n{node.get('question_text', node.get('question', ''))}"

        if degradation == 2:
            return f"大致来说，" + node.get("question_text", node.get("question", ""))

        return SIMPLIFIED_QUESTIONS.get(
            node.get("question_type", "text_input"),
            node.get("question_text", node.get("question", "")),
        )
