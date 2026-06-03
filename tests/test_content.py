"""
QA-01 内容质量深度检查 — 验证互联网/IT 知识包编译产物的完整性和质量

本文件包含 12 项检查，覆盖包级维度和场景级追问树质量标准：
- 包级检查（4 项）：8 维度存在性、数量阈值、版本一致性、UTF-8 中文编码
- 场景级检查（8 项）：遍历 5 棵追问树，逐棵验证节点数、分支逻辑、fallback、
  叶子节点、引用完整性、任务关联性、变体覆盖

运行方式: python -m pytest tests/test_content.py -x --tb=short
"""

import json
import re
from pathlib import Path

import pytest

# 编译产物路径（相对于 tests/ 目录的父目录）
COMPILED_PATH = (
    Path(__file__).resolve().parent.parent
    / "prompt_tool"
    / "knowledge_packs_compiled"
    / "internet_it.json"
)

# 所有 8 个顶层维度
ALL_DIMENSIONS = [
    "meta",
    "terms",
    "tasks",
    "roles",
    "workflows",
    "docs",
    "follow_up_trees",
    "pain_points",
]

# 数量阈值
THRESHOLDS = {
    "terms": 30,
    "tasks": 5,
    "roles": 4,
    "workflows": 2,
    "docs": 3,
    "pain_points": 5,
    "follow_up_trees": 5,  # 精确数量
}

# 场景级变体检查定义
VARIANT_CHECKS = {
    "prd_writing": {
        "description": "PRD撰写至少一条路径区分研发团队 vs 管理层",
        "check": lambda tree: _has_children_keys(tree, ["dev_team", "management"]),
    },
    "code_generation": {
        "description": "代码生成至少一条路径区分 API vs 前端",
        "check": lambda tree: _has_children_keys(tree, ["api", "frontend"]),
    },
    "data_analysis": {
        "description": "数据分析至少一条路径区分不同分析类型（children 键数 >= 3）",
        "check": lambda tree: _has_children_key_count(tree, 3),
    },
    "tech_doc": {
        "description": "技术文档至少一条路径区分不同文档类型（children 键数 >= 3）",
        "check": lambda tree: _has_children_key_count(tree, 3),
    },
    "work_summary": {
        "description": "工作总结至少一条路径区分角色或业绩（children 键数 >= 2）",
        "check": lambda tree: _has_children_key_count(tree, 2),
    },
}


# ============================================================
# 辅助函数
# ============================================================

@pytest.fixture(scope="module")
def pack_data():
    """加载编译后的 JSON 数据，供所有测试共享"""
    if not COMPILED_PATH.exists():
        pytest.fail(f"编译产物不存在: {COMPILED_PATH}。请先运行 python build_packs.py")
    with open(COMPILED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _has_children_keys(tree: dict, keys: list[str]) -> bool:
    """检查树中是否有节点的 children dict 包含所有指定 keys"""
    for node in tree["nodes"].values():
        children = node.get("children", {})
        if all(k in children for k in keys):
            return True
    return False


def _has_children_key_count(tree: dict, min_keys: int) -> bool:
    """检查树中是否有节点的 children dict 键数 >= min_keys"""
    for node in tree["nodes"].values():
        children = node.get("children", {})
        if len(children) >= min_keys:
            return True
    return False


# ============================================================
# 包级检查（4 项）
# ============================================================

class TestPackLevelChecks:
    """包级完整性检查"""

    def test_all_8_dimensions_present(self, pack_data):
        """Test 1: 断言 JSON 顶层包含全部 8 个维度键"""
        missing = [k for k in ALL_DIMENSIONS if k not in pack_data]
        assert not missing, f"缺少顶层维度键: {missing}"

    def test_content_thresholds(self, pack_data):
        """Test 2: 断言各维度数量达到最低阈值"""
        for dim, threshold in THRESHOLDS.items():
            actual = len(pack_data[dim])
            if dim == "follow_up_trees":
                assert actual == threshold, (
                    f"follow_up_trees 数量应为 {threshold}，实际为 {actual}"
                )
            else:
                assert actual >= threshold, (
                    f"{dim} 数量 {actual} 低于最低阈值 {threshold}"
                )

    def test_version_consistency(self, pack_data):
        """Test 3: 断言版本号格式正确"""
        meta = pack_data["meta"]
        assert re.match(r"^\d+\.\d+\.\d+$", meta["version"]), (
            f"版本号格式无效: {meta['version']}（应为 X.Y.Z）"
        )
        assert meta["schema_version"] == "1.0", (
            f"schema_version 应为 '1.0'，实际为 {meta['schema_version']}"
        )

    def test_json_valid_utf8_chinese(self, pack_data):
        """Test 4: 断言 JSON 文件中无 \\uXXXX 转义序列

        读取原始 JSON 文本后检查是否存在 \\u 后跟四位十六进制数的模式。
        如果中文内容被 ensure_ascii=True 转义，将出现 \\uXXXX 序列。
        """
        raw_text = json.dumps(pack_data, ensure_ascii=True)
        # 用 ensure_ascii=True 重新序列化后应该有转义序列（这是确认检查方法正确性）
        # 但实际文件必须用 ensure_ascii=False 存储
        raw_text_preserved = COMPILED_PATH.read_text(encoding="utf-8")
        escaped = re.search(r"\\u[0-9a-fA-F]{4}", raw_text_preserved)
        assert not escaped, (
            "编译产物中包含 \\uXXXX 转义序列，"
            "表明 json.dump() 时未使用 ensure_ascii=False"
        )


# ============================================================
# 场景级检查（8 项—遍历 5 棵 follow_up_trees）
# ============================================================

class TestFollowUpTreeChecks:
    """追问树场景级质量检查"""

    def _get_trees(self, pack_data) -> list[dict]:
        """获取全部 5 棵追问树"""
        return pack_data["follow_up_trees"]

    def test_each_tree_node_count_range(self, pack_data):
        """Test 5: 断言每棵树节点数在 5-8 范围内"""
        for tree in self._get_trees(pack_data):
            n = len(tree["nodes"])
            task_type = tree["task_type"]
            assert 5 <= n <= 8, (
                f"Tree '{task_type}' 有 {n} 个节点，预期 5-8 个"
            )

    def test_each_tree_has_branching(self, pack_data):
        """Test 6: 断言每棵树至少 2 个节点的 children 有 >= 2 个条目"""
        for tree in self._get_trees(pack_data):
            task_type = tree["task_type"]
            branch_count = sum(
                1 for node in tree["nodes"].values()
                if len(node.get("children", {})) >= 2
            )
            assert branch_count >= 2, (
                f"Tree '{task_type}' 只有 {branch_count} 个分支节点（>=2 children），"
                f"预期至少 2 个"
            )

    def test_each_tree_has_fallback(self, pack_data):
        """Test 7: 断言每棵树至少 2 个节点的 fallback_node_id 不为 null"""
        for tree in self._get_trees(pack_data):
            task_type = tree["task_type"]
            fallback_count = sum(
                1 for node in tree["nodes"].values()
                if node.get("fallback_node_id") is not None
            )
            assert fallback_count >= 2, (
                f"Tree '{task_type}' 只有 {fallback_count} 个 fallback 节点，"
                f"预期至少 2 个"
            )

    def test_each_tree_has_leaf(self, pack_data):
        """Test 8: 断言每棵树至少 1 个节点的 is_leaf == true"""
        for tree in self._get_trees(pack_data):
            task_type = tree["task_type"]
            leaf_count = sum(
                1 for node in tree["nodes"].values()
                if node.get("is_leaf") is True
            )
            assert leaf_count >= 1, (
                f"Tree '{task_type}' 没有叶子节点（is_leaf: true），预期至少 1 个"
            )

    def test_each_tree_root_exists(self, pack_data):
        """Test 9: 断言每棵树的 root_node_id 对应的 node 存在于 nodes dict 中"""
        for tree in self._get_trees(pack_data):
            root_id = tree["root_node_id"]
            assert root_id in tree["nodes"], (
                f"Tree '{tree['task_type']}' 的 root_node_id '{root_id}' "
                f"不存在于 nodes dict 中"
            )

    def test_all_children_references_valid(self, pack_data):
        """Test 10: 断言所有 children 引用的目标 node_id 在 nodes dict 中存在

        遍历每棵树的所有节点，检查每个 children 条目指向的 node_id
        是否确实存在于 nodes dict 中。
        """
        for tree in self._get_trees(pack_data):
            task_type = tree["task_type"]
            nodes = tree["nodes"]
            for node_id, node in nodes.items():
                for option_key, child_id in node.get("children", {}).items():
                    assert child_id in nodes, (
                        f"Tree '{task_type}' node '{node_id}' "
                        f"children['{option_key}'] 引用不存在的节点 '{child_id}'"
                    )

    def test_each_tree_task_type_matches(self, pack_data):
        """Test 11: 断言每棵树的 task_type 与 tasks 列表中的 follow_up_tree 引用匹配"""
        tasks = pack_data["tasks"]
        task_tree_refs = {t.get("follow_up_tree") for t in tasks}
        for tree in self._get_trees(pack_data):
            task_type = tree["task_type"]
            assert task_type in task_tree_refs, (
                f"Tree task_type '{task_type}' 在 tasks 列表中未找到对应的 "
                f"follow_up_tree 引用。已注册的引用: {task_tree_refs}"
            )

    def test_each_tree_has_variant_coverage(self, pack_data):
        """Test 12: 断言每棵树覆盖 D-06 要求的关键变体分支"""
        trees_by_type = {t["task_type"]: t for t in self._get_trees(pack_data)}
        for task_type, check_def in VARIANT_CHECKS.items():
            assert task_type in trees_by_type, (
                f"缺少场景 '{task_type}' 对应的追问树"
            )
            tree = trees_by_type[task_type]
            assert check_def["check"](tree), (
                f"Tree '{task_type}' 变体检查失败: {check_def['description']}"
            )
