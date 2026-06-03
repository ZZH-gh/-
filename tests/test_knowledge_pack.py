"""
KnowledgePack 单元测试 — 验证 8 个 typed getter 方法的行为

RED phase: ImportError expected (KnowledgePack module does not exist yet).
"""

import pytest

from prompt_tool.knowledge_pack import KnowledgePack


class TestKnowledgePack:
    """KnowledgePack getter 方法单元测试 (15 个)"""

    def test_get_meta(self):
        """Test 1: get_meta() 返回完整的 meta dict"""
        data = {"meta": {"id": "test", "name": "测试行业", "icon": "🔬"}}
        pack = KnowledgePack(data)
        meta = pack.get_meta()
        assert isinstance(meta, dict)
        assert meta["id"] == "test"
        assert meta["name"] == "测试行业"

    def test_get_terms_all(self):
        """Test 2: get_terms() 返回全部 terms"""
        data = {
            "meta": {"id": "test", "name": "Test"},
            "terms": [
                {"term": "PRD", "category": "产品文档", "definition": "产品需求文档"},
                {"term": "API", "category": "研发流程", "definition": "应用程序编程接口"},
            ],
        }
        pack = KnowledgePack(data)
        terms = pack.get_terms()
        assert isinstance(terms, list)
        assert len(terms) == 2

    def test_get_terms_by_category(self):
        """Test 3: get_terms(category='产品文档') 只返回 category 匹配的 term"""
        data = {
            "meta": {"id": "test", "name": "Test"},
            "terms": [
                {"term": "PRD", "category": "产品文档", "definition": "..."},
                {"term": "API", "category": "研发流程", "definition": "..."},
            ],
        }
        pack = KnowledgePack(data)
        terms = pack.get_terms(category="产品文档")
        assert len(terms) == 1
        assert terms[0]["term"] == "PRD"

    def test_get_terms_empty(self):
        """Test 4: 空数据 KnowledgePack({}).get_terms() 返回 []"""
        pack = KnowledgePack({})
        assert pack.get_terms() == []

    def test_get_task_found(self):
        """Test 5: get_task('PRD撰写') 返回对应的 task dict"""
        data = {
            "meta": {"id": "test", "name": "Test"},
            "tasks": [
                {"name": "PRD撰写", "description": "撰写产品需求文档"},
                {"name": "代码生成", "description": "编写高质量代码"},
            ],
        }
        pack = KnowledgePack(data)
        task = pack.get_task("PRD撰写")
        assert isinstance(task, dict)
        assert task["name"] == "PRD撰写"
        assert task["description"] == "撰写产品需求文档"

    def test_get_task_not_found(self):
        """Test 6: get_task('nonexistent') 返回 None"""
        data = {
            "meta": {"id": "test", "name": "Test"},
            "tasks": [{"name": "PRD撰写", "description": "..."}],
        }
        pack = KnowledgePack(data)
        assert pack.get_task("nonexistent") is None

    def test_get_roles(self):
        """Test 7: get_roles() 返回全部 role"""
        data = {
            "meta": {"id": "test", "name": "Test"},
            "roles": [
                {"name": "产品经理", "kpis": []},
                {"name": "前端工程师", "kpis": []},
            ],
        }
        pack = KnowledgePack(data)
        roles = pack.get_roles()
        assert isinstance(roles, list)
        assert len(roles) == 2

    def test_get_role(self):
        """Test 8: get_role('产品经理') 返回对应 role dict，不存在返回 None"""
        data = {
            "meta": {"id": "test", "name": "Test"},
            "roles": [
                {"name": "产品经理", "kpis": []},
                {"name": "前端工程师", "kpis": []},
            ],
        }
        pack = KnowledgePack(data)
        role = pack.get_role("产品经理")
        assert isinstance(role, dict)
        assert role["name"] == "产品经理"

        assert pack.get_role("不存在角色") is None

    def test_get_workflow(self):
        """Test 9: get_workflow('agile_dev') 返回对应 workflow dict，不存在返回 None"""
        data = {
            "meta": {"id": "test", "name": "Test"},
            "workflows": [
                {
                    "name": "agile_dev",
                    "category": "研发流程",
                    "steps": [{"step": 1, "name": "需求评审"}],
                }
            ],
        }
        pack = KnowledgePack(data)
        wf = pack.get_workflow("agile_dev")
        assert isinstance(wf, dict)
        assert wf["name"] == "agile_dev"

        assert pack.get_workflow("nonexistent") is None

    def test_get_workflows_by_category(self):
        """Test 10: get_workflows(category='研发流程') filter 有效"""
        data = {
            "meta": {"id": "test", "name": "Test"},
            "workflows": [
                {
                    "name": "功能上线流程",
                    "category": "研发流程",
                    "steps": [],
                },
                {
                    "name": "财务审批流程",
                    "category": "管理流程",
                    "steps": [],
                },
            ],
        }
        pack = KnowledgePack(data)
        wfs = pack.get_workflows(category="研发流程")
        assert len(wfs) == 1
        assert wfs[0]["name"] == "功能上线流程"

    def test_get_doc_template(self):
        """Test 11: get_doc_template('PRD模板') 返回 doc dict，不存在返回 None"""
        data = {
            "meta": {"id": "test", "name": "Test"},
            "docs": [
                {"name": "PRD模板", "task_type": "prd_writing", "sections": []},
                {"name": "技术方案模板", "task_type": "tech_doc", "sections": []},
            ],
        }
        pack = KnowledgePack(data)
        doc = pack.get_doc_template("PRD模板")
        assert isinstance(doc, dict)
        assert doc["name"] == "PRD模板"

        assert pack.get_doc_template("不存在模板") is None

    def test_get_doc_templates_by_task_type(self):
        """Test 12: get_doc_templates(task_type='prd_writing') filter 有效"""
        data = {
            "meta": {"id": "test", "name": "Test"},
            "docs": [
                {"name": "PRD模板", "task_type": "prd_writing", "sections": []},
                {"name": "技术方案模板", "task_type": "tech_doc", "sections": []},
            ],
        }
        pack = KnowledgePack(data)
        docs = pack.get_doc_templates(task_type="prd_writing")
        assert len(docs) == 1
        assert docs[0]["name"] == "PRD模板"

    def test_get_follow_up_tree(self):
        """Test 13: get_follow_up_tree('prd_writing') 返回 tree dict，不存在返回 None"""
        data = {
            "meta": {"id": "test", "name": "Test"},
            "follow_up_trees": [
                {
                    "task_type": "prd_writing",
                    "root_node_id": "q1",
                    "nodes": {"q1": {"node_id": "q1", "question_text": "?"}},
                }
            ],
        }
        pack = KnowledgePack(data)
        tree = pack.get_follow_up_tree("prd_writing")
        assert isinstance(tree, dict)
        assert tree["task_type"] == "prd_writing"

        assert pack.get_follow_up_tree("nonexistent") is None

    def test_get_pain_points(self):
        """Test 14: get_pain_points() 返回全部 pain_point"""
        data = {
            "meta": {"id": "test", "name": "Test"},
            "pain_points": [
                {"name": "需求频繁变更", "description": "需求变更导致计划被打乱"},
                {"name": "沟通偏差", "description": "跨团队沟通存在理解偏差"},
            ],
        }
        pack = KnowledgePack(data)
        points = pack.get_pain_points()
        assert isinstance(points, list)
        assert len(points) == 2

    def test_getter_return_types(self):
        """Test 15: 所有 getter 方法返回正确的 Python 原生类型"""
        data = {
            "meta": {"id": "test", "name": "Test"},
            "terms": [],
            "tasks": [],
            "roles": [],
            "workflows": [],
            "docs": [],
            "follow_up_trees": [],
            "pain_points": [],
        }
        pack = KnowledgePack(data)

        assert isinstance(pack.get_meta(), dict)
        assert isinstance(pack.get_terms(), list)
        assert pack.get_task("不存在") is None
        assert isinstance(pack.get_tasks(), list)
        assert isinstance(pack.get_roles(), list)
        assert pack.get_role("不存在") is None
        assert isinstance(pack.get_workflows(), list)
        assert pack.get_workflow("不存在") is None
        assert pack.get_doc_template("不存在") is None
        assert isinstance(pack.get_doc_templates(), list)
        assert pack.get_follow_up_tree("不存在") is None
        assert isinstance(pack.get_pain_points(), list)
