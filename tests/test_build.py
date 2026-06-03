"""
编译管线集成测试 — 验证 build_packs.py 的 compile_pack() 行为
"""

import json
import os

import pytest
import yaml

from build_packs import compile_pack


class TestCompileValidYaml:
    """Test 6: 有效 YAML 编译成功"""

    def test_compile_valid_yaml(self, temp_yaml_file, temp_output_dir):
        """使用最小合法 YAML，调用 compile_pack()，验证返回 stats dict 且输出 JSON 文件存在"""
        yaml_content = """meta:
  id: "test_pack"
  name: "测试知识包"
  version: "1.0.0"
  schema_version: "1.0"
  description: "测试用知识包"
  last_updated: "2026-06-03"
  icon: ""

terms:
  - term: "API"
    category: "技术"
    definition: "应用程序编程接口"
    aliases: ["接口", "接口文档"]
    usage_context: "前后端通信"
    related_terms: ["REST", "SDK"]

tasks:
  - name: "API设计"
    description: "设计RESTful API接口"
    typical_output: "API设计文档"
    complexity: "medium"
    frequency: "high"

roles: []
workflows: []
docs: []
follow_up_trees: []
pain_points: []
"""
        yaml_path = temp_yaml_file(yaml_content, "test_pack.yaml")
        stats = compile_pack(yaml_path, temp_output_dir)

        # 验证返回的 stats dict
        assert isinstance(stats, dict)
        assert "pack_id" in stats
        assert stats["pack_id"] == "test_pack"
        assert "terms" in stats
        assert stats["terms"] == 1  # 1 term
        assert "tasks" in stats
        assert stats["tasks"] == 1  # 1 task

        # 验证输出 JSON 文件存在
        output_file = temp_output_dir / "test_pack.json"
        assert output_file.exists()


class TestCompileInvalidYamlFails:
    """Test 7: 无效 YAML 编译失败且报错"""

    def test_compile_invalid_yaml_fails(self, temp_yaml_file, temp_output_dir):
        """缺失 meta.id 的 YAML 调用 compile_pack()，验证抛出 ValidationError 且错误信息包含字段名"""
        yaml_content = """meta:
  name: "测试知识包"
  version: "1.0.0"
  schema_version: "1.0"
  description: "缺少 meta.id"
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
        yaml_path = temp_yaml_file(yaml_content, "invalid_pack.yaml")

        with pytest.raises(Exception) as excinfo:
            compile_pack(yaml_path, temp_output_dir)

        error_msg = str(excinfo.value)
        # 验证错误信息包含字段名（meta 或 id）
        assert any(field in error_msg for field in ["meta", "id", "field required"])


class TestChineseEncodingPreserved:
    """Test 8: 编译后 JSON 中文编码正确"""

    def test_chinese_encoding_preserved(self, temp_yaml_file, temp_output_dir):
        """编译包含中文术语的 YAML，验证输出 JSON 中中文以原始 UTF-8 形式存在"""
        yaml_content = """meta:
  id: "chinese_test"
  name: "中文测试包"
  version: "1.0.0"
  schema_version: "1.0"
  description: "测试中文编码"
  last_updated: "2026-06-03"
  icon: ""

terms:
  - term: "互联网"
    category: "技术"
    definition: "互联网技术"
    aliases: []
    usage_context: "通用"
    related_terms: []

tasks: []
roles: []
workflows: []
docs: []
follow_up_trees: []
pain_points: []
"""
        yaml_path = temp_yaml_file(yaml_content, "chinese_test.yaml")
        compile_pack(yaml_path, temp_output_dir)

        output_file = temp_output_dir / "chinese_test.json"
        assert output_file.exists()

        # 读取输出 JSON 并检查中文未被转义
        raw_content = output_file.read_text(encoding="utf-8")
        # 检查没有 \\u 转义序列（普通 u 不算转义，\\u 才是）
        # 在 Unicode 字符中，"互联网" 不应该被转义成 \\u互\\u联\\u网
        escaped_count = 0
        i = 0
        while i < len(raw_content) - 5:
            if raw_content[i:i+2] == "\\u":
                # 检查是否真的是 Unicode 转义序列
                try:
                    int(raw_content[i+2:i+6], 16)
                    escaped_count += 1
                    i += 6
                    continue
                except ValueError:
                    pass
            i += 1
        assert escaped_count == 0, f"Found {escaped_count} escaped Unicode sequences in output"


class TestEmptyYamlFails:
    """Test 9: 空 YAML 编译报错"""

    def test_empty_yaml_fails(self, temp_yaml_file, temp_output_dir):
        """编译空 YAML 文件，验证抛出 ValueError"""
        yaml_path = temp_yaml_file("", "empty.yaml")

        with pytest.raises(ValueError):
            compile_pack(yaml_path, temp_output_dir)


class TestNonexistentDirectoryHandled:
    """Test 10: 源目录不存在时优雅处理"""

    def test_nonexistent_directory_handled(self, temp_output_dir):
        """尝试编译不存在的目录中的文件，compile_pack 应抛出 FileNotFoundError"""
        nonexistent_path = "/nonexistent/path/test.yaml"

        with pytest.raises(FileNotFoundError):
            compile_pack(nonexistent_path, temp_output_dir)


# ============================================================
# Phase 2 — Index Generation Test (Test 26)
# ============================================================


class TestIndexGenerated:
    """验证 build_packs.py 的 _generate_index() 生成合法的 index.json"""

    def test_index_generated(self, temp_yaml_file, temp_output_dir, monkeypatch):
        """编译一个最小 pack，验证 index.json 生成且结构完整"""
        from build_packs import compile_pack, _generate_index

        yaml_content = """meta:
  id: "test_pack"
  name: "测试知识包"
  version: "1.0.0"
  schema_version: "1.0"
  description: "测试用知识包"
  last_updated: "2026-06-03"
  icon: ""

terms:
  - term: "API"
    category: "技术"
    definition: "应用程序编程接口"
    aliases: ["接口", "API接口"]
    usage_context: "前后端通信"
    related_terms: ["REST", "SDK"]

tasks:
  - name: "API设计"
    description: "设计RESTful API接口"
    typical_output: "API设计文档"
    complexity: "medium"
    frequency: "high"

roles: []
workflows: []
docs: []
follow_up_trees: []
pain_points: []
"""
        yaml_path = temp_yaml_file(yaml_content, "test_pack.yaml")
        compile_pack(yaml_path, temp_output_dir)

        # Generate index
        index = _generate_index(temp_output_dir)

        # Verify index structure
        assert isinstance(index, dict)
        assert "test_pack" in index
        entry = index["test_pack"]

        # Each entry must have id/name/icon/keywords/pack_file/stats
        assert entry["id"] == "test_pack"
        assert entry["name"] == "测试知识包"
        assert "keywords" in entry
        assert "pack_file" in entry
        assert entry["pack_file"] == "test_pack.json"
        assert "stats" in entry
        stats = entry["stats"]
        assert stats["term_count"] == 1
        assert stats["scenario_count"] == 1
        assert stats["tree_count"] == 0
        assert stats["role_count"] == 0
        assert stats["workflow_count"] == 0

        # Verify index.json was written to disk
        index_path = temp_output_dir / "index.json"
        assert index_path.exists()

        # Verify it can be loaded as valid JSON
        import json
        with open(index_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        assert "test_pack" in loaded
