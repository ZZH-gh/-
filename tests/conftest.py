"""
共享 Fixtures — 用于知识包编译管线的测试数据
"""

import pytest


@pytest.fixture
def valid_minimal_yaml() -> str:
    """返回一个最小合法知识包 dict 的 YAML 字符串（仅 meta + 空列表的其他 7 个维度）"""
    return """meta:
  id: "test_pack"
  name: "测试知识包"
  version: "1.0.0"
  schema_version: "1.0"
  description: "用于测试的最小知识包"
  last_updated: "2026-06-03"
  icon: ""

terms: []

tasks: []

roles: []

workflows: []

docs: []

follow_up_trees: []

pain_points: []
"""


@pytest.fixture
def invalid_missing_meta_yaml() -> str:
    """返回缺少 meta.id 的非法 YAML 字符串"""
    return """meta:
  name: "测试知识包"
  version: "1.0.0"
  schema_version: "1.0"
  description: "缺少 meta.id 的测试包"
  last_updated: "2026-06-03"
  icon: ""

terms: []

tasks: []
"""


@pytest.fixture
def temp_yaml_file(tmp_path):
    """工厂 fixture — 在 tmp_path 中写入指定内容的 .yaml 文件并返回 Path"""
    def _create(content: str, filename: str = "test_pack.yaml"):
        file_path = tmp_path / filename
        file_path.write_text(content, encoding="utf-8")
        return file_path
    return _create


@pytest.fixture
def temp_output_dir(tmp_path):
    """在 tmp_path 中创建并返回输出目录 Path"""
    output_dir = tmp_path / "compiled"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


# ============================================================
# Phase 2 Fixtures — Knowledge Pack Runtime Tests
# ============================================================


@pytest.fixture
def sample_pack_json() -> dict:
    """返回一个最小但完整的知识包 dict，结构与 internet_it.json 一致"""
    return {
        "meta": {
            "id": "test_industry",
            "name": "测试行业",
            "version": "1.0.0",
            "schema_version": "1.0",
            "description": "用于测试的行业知识包",
            "last_updated": "2026-06-03",
            "icon": "🔬",
        },
        "terms": [
            {
                "term": "PRD",
                "category": "产品文档",
                "definition": "产品需求文档",
                "aliases": ["产品需求文档", "需求文档"],
                "usage_context": "产品经理编写",
                "related_terms": ["BRD", "MRD"],
            },
            {
                "term": "API",
                "category": "研发流程",
                "definition": "应用程序编程接口",
                "aliases": ["接口", "API接口"],
                "usage_context": "前后端通信",
                "related_terms": ["REST", "微服务"],
            },
        ],
        "tasks": [
            {
                "name": "PRD撰写",
                "description": "撰写产品需求文档",
                "typical_output": "PRD文档",
                "complexity": "medium",
                "frequency": "very_high",
                "follow_up_tree": "prd_writing",
            },
            {
                "name": "代码生成",
                "description": "编写高质量代码",
                "typical_output": "源代码文件",
                "complexity": "high",
                "frequency": "very_high",
                "follow_up_tree": "code_generation",
            },
        ],
        "roles": [
            {
                "name": "产品经理",
                "common_tasks": ["PRD撰写", "需求分析"],
                "responsibilities": ["定义产品需求", "管理产品backlog", "协调跨团队沟通"],
                "kpis": [
                    {"name": "PRD完整度", "description": "需求文档覆盖核心功能与异常场景", "benchmark": "90%"},
                    {"name": "迭代效率", "description": "版本交付周期", "benchmark": "2周"},
                    {"name": "需求变更率", "description": "开发阶段的需求变更次数", "benchmark": "<3次/版本"},
                ],
                "pain_points": ["需求频繁变更", "跨团队沟通成本高"],
            },
            {
                "name": "技术架构师",
                "common_tasks": ["代码生成", "技术方案设计"],
                "responsibilities": ["系统架构设计", "技术选型", "代码评审"],
                "kpis": [
                    {"name": "系统可用性", "description": "服务正常运行时间", "benchmark": "99.9%"},
                ],
                "pain_points": ["技术债积累", "性能瓶颈"],
            },
        ],
        "workflows": [],
        "docs": [
            {
                "name": "PRD模板",
                "task_type": "PRD撰写",
                "sections": [
                    {"title": "背景与目标", "prompt_hint": "项目背景和业务目标"},
                    {"title": "功能范围", "prompt_hint": "核心功能列表与优先级"},
                    {"title": "非功能需求", "prompt_hint": "性能、安全、兼容性要求"},
                    {"title": "验收标准", "prompt_hint": "可量化的验收条件"},
                ],
                "tone": "专业、严谨",
                "common_mistakes": ["需求过于模糊", "缺少验收标准"],
            },
        ],
        "follow_up_trees": [],
        "pain_points": [
            {
                "name": "需求不明确",
                "description": "用户说不清楚自己要什么，导致反复修改",
                "why_happens": "用户缺乏领域专业知识",
                "who_feels_it": "产品经理、开发团队",
                "typical_phrases": ["需求不会变了", "就这些需求", "随便做做"],
                "what_not_to_do": "不要在需求不明确时直接开始编码",
            },
            {
                "name": "过度承诺",
                "description": "为了争取项目而承诺不切实际的交付时间",
                "why_happens": "竞争压力、销售导向",
                "who_feels_it": "开发团队",
                "typical_phrases": ["一周搞定", "很简单的", "和XX一样就行"],
                "what_not_to_do": "不要承诺无法在合理时间内完成的功能范围",
            },
        ],
    }


@pytest.fixture
def fully_loaded_pack(sample_pack_json):
    """Return a KnowledgePack instance with all fields (roles, docs, pain_points) populated."""
    from prompt_tool.knowledge_pack import KnowledgePack
    return KnowledgePack(sample_pack_json)


@pytest.fixture
def sample_index_json() -> dict:
    """返回一个合法的 index.json dict，包含 2 个行业条目"""
    return {
        "internet_it": {
            "id": "internet_it",
            "name": "互联网 / IT",
            "icon": "💻",
            "description": "互联网与IT行业知识包",
            "keywords": ["PRD", "代码", "API", "技术方案", "架构", "开发", "测试"],
            "pack_file": "internet_it.json",
            "stats": {
                "term_count": 36,
                "scenario_count": 5,
                "tree_count": 5,
                "role_count": 5,
                "workflow_count": 3,
            },
        },
        "financial": {
            "id": "financial",
            "name": "金融",
            "icon": "💰",
            "description": "金融行业知识包",
            "keywords": ["股票", "基金", "投资", "理财", "保险"],
            "pack_file": "financial.json",
            "stats": {
                "term_count": 0,
                "scenario_count": 0,
                "tree_count": 0,
                "role_count": 0,
                "workflow_count": 0,
            },
        },
    }


@pytest.fixture
def temp_compiled_dir(tmp_path, sample_index_json, sample_pack_json):
    """使用 tmp_path 创建临时目录，写入 index.json 和 test_industry.json，返回 Path"""
    compiled_dir = tmp_path / "knowledge_packs_compiled"
    compiled_dir.mkdir(parents=True, exist_ok=True)

    import json

    # Write index.json
    index_path = compiled_dir / "index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(sample_index_json, f, ensure_ascii=False, indent=2)

    # Write a test pack
    pack_path = compiled_dir / "test_industry.json"
    with open(pack_path, "w", encoding="utf-8") as f:
        json.dump(sample_pack_json, f, ensure_ascii=False, indent=2)

    return compiled_dir


# ============================================================
# Phase 3 Fixtures — Session State & Context Builder Tests
# ============================================================


@pytest.fixture
def session_manager_instance():
    """返回一个全新的 SessionManager 实例（非模块级单例），用于隔离测试"""
    from prompt_tool.session_manager import SessionManager
    return SessionManager()


@pytest.fixture
def sample_session_with_turns(session_manager_instance):
    """创建一个包含 3 个轮次、已确认行业/任务、已提取信息的会话"""
    sm = session_manager_instance
    sm.create_session()
    sm.add_turn("system", "你想写什么类型的PRD？", "question")
    sm.add_turn("user", "我需要一个电商平台的PRD", "answer")
    sm.add_turn("system", "好的，已确认：电商平台PRD", "confirm")
    sm.update_confirmed_industry("internet_it")
    sm.update_confirmed_task("prd_writing")
    sm.update_extracted_info("tone", "专业")
    return sm
