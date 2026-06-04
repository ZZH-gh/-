"""
分析引擎 - 智能解析用户输入，识别行业、任务类型、需求要点
完全离线运行，基于关键词权重匹配 + 模式识别
"""

import re
from .knowledge import (
    INDUSTRIES, TASK_TYPES, ROLES, STOP_WORDS,
    OUTPUT_FORMATS, TONE_KEYWORDS
)
from .knowledge_manager import knowledge_manager


class AnalysisEngine:
    """用户输入分析引擎"""

    def __init__(self):
        self.industry_scores = {}
        self.task_scores = {}
        self.extracted_info = {}

    def analyze(self, user_input: str, manual_industry: str = None):
        """
        分析用户输入，返回完整的分析结果
        Args:
            user_input: 用户输入的文本
            manual_industry: 手动指定的行业（可选）
        Returns:
            dict: 分析结果
        """
        # 预处理
        cleaned = self._clean_text(user_input)
        keywords = self._extract_keywords(cleaned)

        # 行业识别
        if manual_industry and manual_industry != "自动识别":
            best_industry_key = self._get_industry_key(manual_industry)
            best_industry_name = manual_industry
        else:
            best_industry_key, best_industry_name = self._identify_industry(cleaned, keywords)
            if not best_industry_key:
                best_industry_key = "通用"
                best_industry_name = "通用 / 其他"

        # 任务识别
        best_task = self._identify_task(cleaned, keywords, best_industry_key)

        # 需求提取
        requirements = self._extract_requirements(cleaned, keywords)

        # 语气/风格识别
        tone = self._identify_tone(cleaned, keywords)

        # 输出格式识别
        output_format = self._identify_output_format(cleaned, keywords)

        # 构建识别到的所有行业（用于展示）
        all_matched_industries = sorted(
            self.industry_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        # 构建识别到的所有任务（用于展示）
        all_matched_tasks = sorted(
            self.task_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        result = {
            "industry_key": best_industry_key,
            "industry_name": best_industry_name,
            "task_name": best_task["name"] if best_task else "通用任务",
            "task_key": best_task["key"] if best_task else "通用",
            "task_description": best_task.get("desc", "") if best_task else "",
            "requirements": requirements,
            "tone": tone,
            "output_format": output_format,
            "all_industries": all_matched_industries,
            "all_tasks": all_matched_tasks,
            "original_input": user_input,
            "cleaned_input": cleaned,
            "keywords": keywords,
        }

        self.extracted_info = result
        return result

    def _clean_text(self, text: str) -> str:
        """清洗文本：去标点、去停用词、标准化"""
        # 去除多余空格
        text = re.sub(r'\s+', ' ', text.strip())
        # 去除特殊字符（保留中文、英文、数字、基本标点）
        # 使用简单的字符过滤，避免正则表达式兼容性问题
        allowed = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                       '，。！？、：；""''（）【】《》-,. ')
        result = []
        for char in text:
            if '一' <= char <= '鿿' or char in allowed:
                result.append(char)
        return ''.join(result)

    def _extract_keywords(self, text: str) -> list:
        """提取关键词（按字符简单切分）"""
        # 去除停用词
        words = []
        # 尝试按字词切分
        for char in text:
            if '一' <= char <= '鿿':
                words.append(char)

        # 简单的二元词组
        bigrams = [text[i:i+2] for i in range(len(text)-1)
                   if '一' <= text[i] <= '鿿' and '一' <= text[i+1] <= '鿿']

        # 三元词组
        trigrams = [text[i:i+3] for i in range(len(text)-2)
                    if all('一' <= c <= '鿿' for c in text[i:i+3])]

        # 过滤停用词
        filtered_bigrams = [w for w in bigrams if w not in STOP_WORDS and len(w) >= 2]
        filtered_trigrams = [w for w in trigrams if w not in STOP_WORDS and len(w) >= 2]

        # 提取英文单词
        eng_words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

        return {
            "chars": words,
            "bigrams": filtered_bigrams,
            "trigrams": filtered_trigrams,
            "eng_words": eng_words,
            "raw": text
        }

    def _identify_industry(self, text: str, keywords: dict) -> tuple:
        """识别行业（通过 KnowledgeManager）

        Delegates to knowledge_manager.match_industry() which operates
        on the compiled index.json keywords instead of v3.0 knowledge.py.
        """
        matches = knowledge_manager.match_industry(text)

        if not matches:
            return "通用", "通用 / 其他"

        # Store all scores for UI display (consistent with analyze() usage)
        self.industry_scores = {m.industry_id: m.score for m in matches[:3]}

        best = matches[0]
        return best.industry_id, best.industry_name

    def _identify_task(self, text: str, keywords: dict, industry_key: str) -> dict:
        """识别任务类型"""
        scores = {}
        text_lower = text.lower()

        # 首先尝试匹配行业内的任务
        industry = INDUSTRIES.get(industry_key)
        if industry:
            for task_name, task_info in industry["templates"].items():
                score = 0
                for kw in task_info["task_keywords"]:
                    # 精确匹配（中文直接匹配，英文不区分大小写）
                    if kw in text:
                        score += 3
                    elif any(c.isascii() and c.isalpha() for c in kw) and kw.lower() in text_lower:
                        score += 3
                    # 二元词组匹配
                    for bg in keywords["bigrams"]:
                        if kw in bg or bg in kw:
                            score += 1
                if score > 0:
                    scores[task_name] = {
                        "score": score,
                        "name": task_name,
                        "key": task_name,
                        "desc": task_info["description"]
                    }

        # 然后匹配通用任务类型
        for task_key, task_info in TASK_TYPES.items():
            score = 0
            for kw in task_info["keywords"]:
                if kw in text:
                    score += 3
                elif any(c.isascii() and c.isalpha() for c in kw) and kw.lower() in text_lower:
                    score += 3
                for bg in keywords["bigrams"]:
                    if kw in bg or bg in kw:
                        score += 1
            if score > 0:
                if task_key not in scores or score > scores[task_key]["score"]:
                    scores[task_key] = {
                        "score": score,
                        "name": task_key,
                        "key": task_key,
                        "desc": task_info["prompt_focus"]
                    }

        self.task_scores = {k: v["score"] for k, v in scores.items()}

        if not scores:
            # 尝试从通用行业匹配
            fallback = self._fallback_task(text, keywords)
            return fallback

        best = max(scores.values(), key=lambda x: x["score"])
        return best

    def _fallback_task(self, text: str, keywords: dict) -> dict:
        """兜底的任务识别"""
        # 检查是否包含写作相关词
        writing_patterns = ["写", "撰写", "创作", "编写"]
        if any(p in text for p in writing_patterns):
            return {"score": 1, "name": "写作", "key": "写作", "desc": "写作任务"}

        # 检查是否包含分析相关词
        analysis_patterns = ["分析", "研究", "对比", "评估"]
        if any(p in text for p in analysis_patterns):
            return {"score": 1, "name": "分析", "key": "分析", "desc": "数据分析与研究"}

        return {"score": 1, "name": "通用任务", "key": "通用", "desc": "综合任务"}

    def _extract_requirements(self, text: str, keywords: dict) -> list:
        """提取关键需求点"""
        requirements = []

        # 提取目标
        goal_patterns = [
            r'(?:想要|需要|希望|要求|目的是|目标[是]?)(.{5,50})',
            r'(?:帮[我我们])(.{5,60})',
            r'(?:生成|制作|完成|实现|提供)(.{5,50})',
        ]
        for pattern in goal_patterns:
            matches = re.findall(pattern, text)
            for m in matches[:2]:
                m = m.strip()
                if len(m) > 5:
                    requirements.append(m)

        # 提取约束条件
        constraint_patterns = [
            r'(?:要求|需要|必须|要)(.{3,30})(?:格式|风格|方式)',
            r'(?:用|以|按照)(.{3,20})(?:格式|风格|形式|方式)',
        ]
        for pattern in constraint_patterns:
            matches = re.findall(pattern, text)
            for m in matches[:2]:
                m = m.strip()
                if len(m) > 2:
                    requirements.append(f"格式/风格要求：{m}")

        # 如果没有提取到
        if not requirements:
            requirements.append(text[:80] if len(text) > 80 else text)

        return requirements

    def _identify_tone(self, text: str, keywords: dict) -> str:
        """识别语气/风格"""
        scores = {}
        for tone, tone_kws in TONE_KEYWORDS.items():
            score = 0
            for kw in tone_kws:
                if kw in text:
                    score += 2
            if score > 0:
                scores[tone] = score

        if not scores:
            return "专业"  # 默认

        return max(scores, key=scores.get)

    def _identify_output_format(self, text: str, keywords: dict) -> dict:
        """识别期望的输出格式"""
        for fmt_name, fmt_info in OUTPUT_FORMATS.items():
            for kw in fmt_info["keywords"]:
                if kw in text:
                    return {"name": fmt_name, "format": fmt_info["format"]}

        return {"name": "文本", "format": "请以清晰的自然语言段落形式输出。"}

    def _get_industry_key(self, industry_name: str) -> str:
        """根据行业名称获取行业key"""
        for key, info in INDUSTRIES.items():
            if info["name"] == industry_name:
                return key
        return "通用"

    def get_industry_context(self, industry_key: str) -> str:
        """获取行业描述（用于生成提示词）"""
        industry = INDUSTRIES.get(industry_key, INDUSTRIES["通用"])
        return industry["name"]

    def get_role_info(self, role_key: str) -> dict:
        """获取角色信息"""
        return ROLES.get(role_key, ROLES["user"])


# 创建一个全局引擎实例
default_engine = AnalysisEngine()
