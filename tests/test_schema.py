"""
Schema 模型单元测试 — 验证 Pydantic v2 模型的行为
"""

import pytest
from pydantic import ValidationError

from build_packs import (
    KnowledgePack,
    PackMeta,
    Term,
    Task,
    QuestionNode,
    FollowUpTree,
    QuestionType,
    ComplexityLevel,
)


class TestValidPack:
    """Test 1: 合法数据通过验证"""

    def test_valid_pack(self):
        """构造一个仅含 meta 必填字段的最小合法 KnowledgePack dict，验证通过"""
        data = {
            "meta": {
                "id": "test_pack",
                "name": "测试知识包",
            },
            "terms": [],
            "tasks": [],
            "roles": [],
            "workflows": [],
            "docs": [],
            "follow_up_trees": [],
            "pain_points": [],
        }
        pack = KnowledgePack(**data)
        assert pack.meta.id == "test_pack"
        assert pack.meta.name == "测试知识包"
        assert len(pack.terms) == 0
        assert len(pack.tasks) == 0


class TestMissingRequiredField:
    """Test 2: 缺失必填字段拒绝"""

    def test_missing_meta_id(self):
        """构造缺少 meta.id 的 dict，验证抛出 ValidationError"""
        data = {
            "meta": {
                "name": "测试知识包",
            },
            "terms": [],
        }
        with pytest.raises(ValidationError) as excinfo:
            KnowledgePack(**data)
        errors = excinfo.value.errors()
        # 验证错误信息包含字段路径
        error_locs = [" -> ".join(str(l) for l in e["loc"]) for e in errors]
        assert any("meta" in loc and "id" in loc for loc in error_locs)

    def test_missing_term_definition(self):
        """构造缺少 term.definition 的 dict，验证抛出 ValidationError"""
        data = {
            "meta": {"id": "test", "name": "Test"},
            "terms": [
                {"term": "PRD"},  # missing definition
            ],
        }
        with pytest.raises(ValidationError):
            KnowledgePack(**data)

    def test_missing_task_name(self):
        """构造缺少 task.name 的 dict，验证抛出 ValidationError"""
        data = {
            "meta": {"id": "test", "name": "Test"},
            "tasks": [
                {"description": "Some task"},  # missing name
            ],
        }
        with pytest.raises(ValidationError):
            KnowledgePack(**data)


class TestInvalidType:
    """Test 3: 字段类型错误拒绝"""

    def test_invalid_type(self):
        """构造 terms[0].term 为整数类型的 dict，验证抛出 ValidationError"""
        data = {
            "meta": {"id": "test", "name": "Test"},
            "terms": [
                {"term": 12345, "definition": "A test term"},  # term should be str
            ],
        }
        with pytest.raises(ValidationError):
            KnowledgePack(**data)

    def test_invalid_complexity(self):
        """构造不存在的复杂度枚举值，验证抛出 ValidationError"""
        data = {
            "meta": {"id": "test", "name": "Test"},
            "tasks": [
                {"name": "TestTask", "description": "A test", "complexity": "ultra"},
            ],
        }
        with pytest.raises(ValidationError):
            KnowledgePack(**data)


class TestFollowUpTreeNoSelfRef:
    """Test 4: follow-up tree 自引用拒绝"""

    def test_follow_up_tree_no_self_ref(self):
        """构造 children 映射指向自身 node_id 的 follow-up tree，验证拒绝"""
        data = {
            "meta": {"id": "test", "name": "Test"},
            "follow_up_trees": [
                {
                    "task_type": "测试场景",
                    "root_node_id": "q1",
                    "nodes": {
                        "q1": {
                            "node_id": "q1",
                            "question_text": "这是一个问题?",
                            "children": {"yes": "q1"},  # self-reference
                        }
                    },
                }
            ],
        }
        with pytest.raises(ValidationError):
            KnowledgePack(**data)


class TestFollowUpTreeRootExists:
    """Test 5: follow-up tree root_node_id 必须存在于 nodes 中"""

    def test_follow_up_tree_root_exists(self):
        """构造 root_node_id 指向不存在的节点的 tree，验证拒绝"""
        data = {
            "meta": {"id": "test", "name": "Test"},
            "follow_up_trees": [
                {
                    "task_type": "测试场景",
                    "root_node_id": "nonexistent_root",
                    "nodes": {
                        "q1": {
                            "node_id": "q1",
                            "question_text": "这是一个问题?",
                        }
                    },
                }
            ],
        }
        with pytest.raises(ValidationError):
            KnowledgePack(**data)
