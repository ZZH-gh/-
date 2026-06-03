"""
KnowledgeManager 单元测试 — 验证 initialize/match_industry/load_pack/LRU 缓存/fallback

RED phase: ImportError expected (KnowledgeManager module does not exist yet).
"""

import json

import pytest

from prompt_tool.knowledge_manager import KnowledgeManager, IndustryMatch


class TestKnowledgeManager:
    """KnowledgeManager 单元测试 (10 个)"""

    @pytest.fixture
    def manager(self):
        """返回一个干净的 KnowledgeManager 实例（未初始化）"""
        return KnowledgeManager()

    @pytest.fixture
    def manager_with_index(self, manager, temp_compiled_dir, monkeypatch):
        """返回一个已初始化的 KnowledgeManager（指向 temp_compiled_dir）"""
        monkeypatch.setattr(manager, "_resolve_compiled_dir", lambda: temp_compiled_dir)
        manager.initialize()
        return manager

    def test_initialize_with_valid_index(self, manager_with_index):
        """Test 16: initialize() 后 _initialized=True, _fallback_active=False"""
        assert manager_with_index._initialized is True
        assert manager_with_index._fallback_active is False

    def test_match_industry_ranked(self, manager_with_index):
        """Test 17: match_industry('帮我写一个PRD文档') 返回排名列表"""
        matches = manager_with_index.match_industry("帮我写一个PRD文档")
        assert len(matches) >= 1
        # internet_it should rank first (PRD is a keyword)
        assert matches[0].industry_id == "internet_it"
        assert matches[0].score > 0
        assert isinstance(matches[0], IndustryMatch)

    def test_match_industry_empty_input(self, manager_with_index):
        """Test 18: match_industry('') 和 match_industry('  ') 返回 []"""
        assert manager_with_index.match_industry("") == []
        assert manager_with_index.match_industry("  ") == []

    def test_match_industry_no_match(self, manager_with_index):
        """Test 19: match_industry('xyz123不存在') 返回 []"""
        matches = manager_with_index.match_industry("xyz123不存在")
        assert matches == []

    def test_load_pack_success(self, manager_with_index):
        """Test 20: load_pack('test_industry') 返回 KnowledgePack 实例"""
        pack = manager_with_index.load_pack("test_industry")
        from prompt_tool.knowledge_pack import KnowledgePack
        assert isinstance(pack, KnowledgePack)
        assert pack.get_meta()["id"] == "test_industry"

    def test_lru_cache_eviction(self, manager_with_index):
        """Test 21: 加载 3 个不同 pack，get_loaded_industry_ids() 返回 2 个"""
        # Load 3 different packs (only internet_it and test_industry exist on disk)
        # First load test_industry
        manager_with_index.load_pack("test_industry")
        assert len(manager_with_index.get_loaded_industry_ids()) == 1

        # Second load internet_it
        manager_with_index.load_pack("internet_it")
        assert len(manager_with_index.get_loaded_industry_ids()) == 2

        # Third load test_industry again — cache is full, only 2 entries
        manager_with_index.load_pack("test_industry")
        loaded = manager_with_index.get_loaded_industry_ids()
        assert len(loaded) == 2
        # test_industry should be the most recent (moved to end)
        assert loaded[-1] == "test_industry"

    def test_lru_cache_hit(self, manager_with_index):
        """Test 22: 加载 A → B → A，第二次加载 A 返回缓存实例（A 未被驱逐）"""
        # Load A
        pack_a1 = manager_with_index.load_pack("test_industry")
        # Load B
        manager_with_index.load_pack("internet_it")
        # Load A again — should be cache hit
        pack_a2 = manager_with_index.load_pack("test_industry")
        assert pack_a1 is pack_a2  # same instance (cached)

    def test_fallback_on_missing_index(self, manager, tmp_path, monkeypatch):
        """Test 23: compiled_dir 无 index.json，initialize() 后 fallback 激活"""
        empty_dir = tmp_path / "empty_compiled"
        empty_dir.mkdir()
        monkeypatch.setattr(manager, "_resolve_compiled_dir", lambda: empty_dir)

        manager.initialize()
        assert manager._fallback_active is True
        assert manager.is_fallback_active() is True
        # Should have fallback index from knowledge.py
        assert len(manager.get_index()) > 0

    def test_fallback_on_missing_pack(self, manager_with_index):
        """Test 24: load_pack('missing') fallback 返回 KnowledgePack（不抛异常）"""
        from prompt_tool.knowledge_pack import KnowledgePack

        pack = manager_with_index.load_pack("missing")
        assert isinstance(pack, KnowledgePack)
        # Fallback pack should have empty terms/tasks but still be a valid KnowledgePack
        assert pack.get_terms() == []

    def test_initialize_not_called(self, manager):
        """Test 25: 未初始化时 match_industry('test') 返回 []"""
        matches = manager.match_industry("test")
        assert matches == []
