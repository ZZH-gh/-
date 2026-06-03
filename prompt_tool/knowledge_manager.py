"""
Knowledge Manager — 运行时知识包加载器和行业匹配器

模块级单例: from prompt_tool.knowledge_manager import knowledge_manager

架构:
  - initialize() 在应用启动时调用一次（由 app.py 调用）
  - 仅加载 index.json (~5KB) 到内存
  - match_industry() 对用户输入进行关键词权重打分
  - load_pack() 懒加载完整 JSON，通过 LRU-2 (OrderedDict) 缓存
  - 编译产物缺失时静默 fallback 到 v3.0 knowledge.py
"""

import json
import sys
from collections import OrderedDict
from pathlib import Path
from typing import NamedTuple


class IndustryMatch(NamedTuple):
    """行业匹配结果"""
    industry_id: str
    industry_name: str
    score: float


class KnowledgeManager:
    """Singleton runtime manager for knowledge pack lifecycle."""

    def __init__(self):
        self._index: dict[str, dict] = {}
        self._cache: OrderedDict[str, "KnowledgePack"] = OrderedDict()
        self._max_cache_size = 2
        self._initialized = False
        self._fallback_active = False
        self._compiled_dir: Path | None = None

    def initialize(self) -> None:
        """Load index.json. Call once at app startup before mainloop."""
        self._compiled_dir = self._resolve_compiled_dir()
        index_path = self._compiled_dir / "index.json"

        try:
            with open(index_path, "r", encoding="utf-8") as f:
                self._index = json.load(f)
            self._initialized = True
        except (FileNotFoundError, json.JSONDecodeError):
            self._fallback_active = True
            self._build_fallback_index()

    def match_industry(self, user_input: str) -> list[IndustryMatch]:
        """Return confidence-ranked list of matching industries.

        Uses keyword weight scoring:
        - Exact keyword match in input: +3.0
        - Case-insensitive keyword match: +2.0
        """
        if not self._initialized and not self._fallback_active:
            return []

        if len(user_input.strip()) < 2:
            return []

        text_lower = user_input.lower()
        results: list[IndustryMatch] = []

        for industry_id, entry in self._index.items():
            score = 0.0
            for kw in entry.get("keywords", []):
                if not kw:
                    continue
                kw_lower = kw.lower()
                if kw in user_input:
                    score += 3.0
                elif kw_lower in text_lower:
                    score += 2.0

            if score > 0:
                results.append(IndustryMatch(
                    industry_id=industry_id,
                    industry_name=entry.get("name", industry_id),
                    score=score,
                ))

        results.sort(key=lambda m: m.score, reverse=True)
        return results

    def get_index(self) -> dict:
        """Return raw index dict (for debug/UI display)."""
        return self._index

    def load_pack(self, industry_id: str) -> "KnowledgePack":
        """Load a knowledge pack. Uses LRU-2 cache."""
        from .knowledge_pack import KnowledgePack  # local import to avoid cycle

        # Cache hit
        if industry_id in self._cache:
            self._cache.move_to_end(industry_id)
            return self._cache[industry_id]

        # Cache miss -- load from disk
        pack = self._load_from_disk(industry_id)

        # Evict oldest if at capacity
        if len(self._cache) >= self._max_cache_size:
            self._cache.popitem(last=False)

        self._cache[industry_id] = pack
        return pack

    def get_loaded_industry_ids(self) -> list[str]:
        """Return industry IDs currently in cache."""
        return list(self._cache.keys())

    def is_fallback_active(self) -> bool:
        """Return whether fallback mode is active."""
        return self._fallback_active

    # ---- Internal ----

    def _resolve_compiled_dir(self) -> Path:
        """Return path to knowledge_packs_compiled/ in any runtime context."""
        if getattr(sys, "frozen", False):
            base = Path(sys._MEIPASS)
        else:
            base = Path(__file__).parent
        return base / "knowledge_packs_compiled"

    def _load_from_disk(self, industry_id: str) -> "KnowledgePack":
        """Load JSON from disk. Fallback to knowledge.py on failure."""
        from .knowledge_pack import KnowledgePack

        pack_path = self._compiled_dir / f"{industry_id}.json"
        try:
            with open(pack_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return KnowledgePack(data)
        except (FileNotFoundError, json.JSONDecodeError):
            self._fallback_active = True
            return self._build_fallback_pack(industry_id)

    def _build_fallback_index(self) -> None:
        """Build a minimal index from v3.0 knowledge.py INDUSTRIES."""
        from .knowledge import INDUSTRIES

        for key, industry in INDUSTRIES.items():
            keywords = list(industry.get("keywords", []))
            templates = industry.get("templates", {})
            self._index[key] = {
                "id": key,
                "name": industry.get("name", key),
                "icon": industry.get("icon", ""),
                "description": "",
                "keywords": keywords,
                "pack_file": "",
                "stats": {
                    "term_count": 0,
                    "scenario_count": len(templates),
                    "tree_count": 0,
                    "role_count": 0,
                    "workflow_count": 0,
                },
            }

    def _build_fallback_pack(self, industry_id: str) -> "KnowledgePack":
        """Build a KnowledgePack-compatible wrapper from v3.0 data."""
        from .knowledge_pack import KnowledgePack

        industry = {}
        try:
            from .knowledge import INDUSTRIES
            industry = INDUSTRIES.get(industry_id, {})
        except ImportError:
            pass

        data = {
            "meta": {
                "id": industry_id,
                "name": industry.get("name", industry_id),
                "icon": industry.get("icon", ""),
                "description": "",
                "version": "3.0",
                "schema_version": "1.0",
            },
            "terms": [],
            "tasks": [
                {
                    "name": task_name,
                    "description": task_info.get("description", ""),
                    "typical_output": "",
                    "complexity": "medium",
                    "frequency": "medium",
                    "follow_up_tree": "",
                }
                for task_name, task_info in industry.get("templates", {}).items()
            ],
            "roles": [],
            "workflows": [],
            "docs": [],
            "follow_up_trees": [],
            "pain_points": [],
        }
        return KnowledgePack(data)


# Module-level singleton
knowledge_manager = KnowledgeManager()
