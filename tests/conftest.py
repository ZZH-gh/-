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
