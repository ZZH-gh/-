"""
意图分类器 v2（CONV-02）— 基于知识包索引的行业/任务识别，带置信度评分
"""

from .knowledge_manager import knowledge_manager
from .knowledge import TASK_TYPES, INDUSTRIES


class IntentClassifier:
    """行业/任务意图分类，返回归一化置信度评分。"""

    CONFIDENCE_THRESHOLD = 0.3  # 低于此值触发 needs_clarification

    def classify(self, user_input: str) -> dict:
        """对用户输入执行行业 + 任务分类，返回完整 IntentResult。

        Returns:
            dict with fields:
            - industry_id, industry_name, industry_confidence
            - task_key, task_name, task_confidence
            - matched_industries (top 3), matched_tasks (top 3)
            - needs_clarification (bool)
        """
        cleaned = user_input.strip()

        # 行业匹配（通过 KnowledgeManager）
        industries = knowledge_manager.match_industry(cleaned)
        if not industries:
            industries = self._fallback_industry_match(cleaned)

        top_industry = industries[0] if industries else None
        industry_id = top_industry.industry_id if top_industry else None
        industry_name = top_industry.industry_name if top_industry else "通用 / 其他"
        industry_confidence = self._normalize_score(top_industry.score, len(industries)) if top_industry else 0.0

        # 任务匹配
        task_result = self._match_task(cleaned, industry_id)
        task_key = task_result["key"]
        task_name = task_result["name"]
        task_confidence = task_result["confidence"]

        needs_clarification = (
            not cleaned
            or industry_confidence < self.CONFIDENCE_THRESHOLD
            or task_confidence < self.CONFIDENCE_THRESHOLD
        )

        return {
            "industry_id": industry_id,
            "industry_name": industry_name,
            "industry_confidence": round(industry_confidence, 2),
            "task_key": task_key,
            "task_name": task_name,
            "task_confidence": round(task_confidence, 2),
            "matched_industries": [
                {"id": m.industry_id, "name": m.industry_name, "score": round(self._normalize_score(m.score, len(industries)), 2)}
                for m in industries[:3]
            ],
            "matched_tasks": task_result.get("top", []),
            "needs_clarification": needs_clarification,
        }

    def _match_task(self, text: str, industry_id: str | None) -> dict:
        """在 TASK_TYPES + 知识包场景中进行关键词权重匹配。"""
        scores = {}
        lower = text.lower()

        for task_key, task_data in TASK_TYPES.items():
            task_name = task_key
            all_keywords = task_data.get("keywords", []) + [task_name]
            score = 0
            for kw in all_keywords:
                if kw.lower() in lower:
                    score += 3 if len(kw) > 2 else 1
            if score > 0:
                scores[task_key] = {"name": task_name, "score": score, "key": task_key}

        # 从知识包索引中补充场景关键词
        if industry_id:
            try:
                index = knowledge_manager.get_index()
                entry = index.get(industry_id, {})
                keyword_map = entry.get("keyword_task_map", {})
                for task_name, keywords in keyword_map.items():
                    s = sum(3 if kw.lower() in lower else 0 for kw in keywords)
                    if s > 0:
                        k = task_name.lower().replace(" ", "_")
                        if k not in scores or scores[k]["score"] < s:
                            scores[k] = {"name": task_name, "score": s, "key": k}
            except Exception:
                pass

        # 从知识包场景中补充
        if industry_id:
            try:
                pack = knowledge_manager.load_pack(industry_id)
                tasks = pack.get_tasks()
                for t in tasks:
                    name = t.get("name", "")
                    desc = t.get("description", "")
                    s = 0
                    if name in text:
                        s += 5
                    if desc and any(w in text for w in desc.split()):
                        s += 2
                    if s > 0:
                        k = name.lower().replace(" ", "_")
                        if k not in scores or scores[k]["score"] < s:
                            scores[k] = {"name": name, "score": s, "key": k}
            except Exception:
                pass

        sorted_tasks = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
        if sorted_tasks:
            max_score = max(t["score"] for t in sorted_tasks)
            confidence = min(max_score / 15.0, 1.0)
            top = sorted_tasks[0]
            return {
                "key": top["key"],
                "name": top["name"],
                "confidence": confidence,
                "top": [{"key": t["key"], "name": t["name"], "score": t["score"]} for t in sorted_tasks[:3]],
            }

        return {"key": None, "name": None, "confidence": 0.0, "top": []}

    def _normalize_score(self, raw_score: int, match_count: int) -> float:
        """将原始关键词得分归一化到 0.0-1.0。"""
        if raw_score <= 0:
            return 0.0
        normalized = min(raw_score / 20.0, 0.95)
        if match_count == 1 and raw_score > 8:
            normalized = min(normalized + 0.1, 0.95)
        return normalized

    def _fallback_industry_match(self, text: str) -> list:
        """当 KnowledgeManager 匹配失败时，回退到 v3.0 knowledge.py 匹配。"""
        from collections import namedtuple
        IndustryMatch = namedtuple("IndustryMatch", ["industry_id", "industry_name", "score"])
        results = []
        lower = text.lower()
        for key, data in INDUSTRIES.items():
            keywords = data.get("keywords", [])
            score = sum(3 if kw.lower() in lower else 0 for kw in keywords)
            if score > 0:
                results.append(IndustryMatch(industry_id=key, industry_name=data.get("name", key), score=score))
        results.sort(key=lambda x: x.score, reverse=True)
        return results
