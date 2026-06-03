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
        "roles": [],
        "workflows": [],
        "docs": [],
        "follow_up_trees": [],
        "pain_points": [],
    }


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
