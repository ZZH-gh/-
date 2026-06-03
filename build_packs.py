#!/usr/bin/env python3
"""
build_packs.py — Compile YAML knowledge packs to validated JSON.

Usage:
    python build_packs.py              # Compile all packs

Exit code: 0 on success, 1 on any validation failure.
This script runs at build time (inside build.bat) and in CI.
"""

import json
import sys
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator
from enum import Enum


# ============================================================
# Enums
# ============================================================

class QuestionType(str, Enum):
    SINGLE_CHOICE = "single_choice"
    MULTI_CHOICE = "multi_choice"
    TEXT_INPUT = "text_input"
    CONFIRM = "confirm"


class ComplexityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ============================================================
# Meta
# ============================================================

class PackMeta(BaseModel):
    id: str = Field(..., pattern=r"^[a-z][a-z_]*$")
    name: str = Field(..., min_length=1, max_length=50)
    version: str = Field(default="1.0.0")
    schema_version: str = Field(default="1.0")
    description: str = Field(default="")
    last_updated: str = Field(default="")
    icon: str = Field(default="")


# ============================================================
# Terms
# ============================================================

class Term(BaseModel):
    term: str = Field(..., min_length=1)
    category: str = Field(default="")
    definition: str = Field(..., min_length=1)
    aliases: list[str] = Field(default_factory=list)
    usage_context: str = Field(default="")
    related_terms: list[str] = Field(default_factory=list)


# ============================================================
# Tasks
# ============================================================

class Task(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    typical_output: str = Field(default="")
    complexity: ComplexityLevel = Field(default=ComplexityLevel.MEDIUM)
    frequency: str = Field(default="medium")
    follow_up_tree: str = Field(default="")


# ============================================================
# Follow-Up Trees
# ============================================================

class Option(BaseModel):
    value: str = Field(..., min_length=1)
    label: str = Field(..., min_length=1)


class QuestionNode(BaseModel):
    node_id: str = Field(..., pattern=r"^[a-z][a-z0-9_]*$")
    question_text: str = Field(..., min_length=1)
    question_type: QuestionType = Field(default=QuestionType.SINGLE_CHOICE)
    info_key: str = Field(default="")
    depth: int = Field(default=1, ge=1, le=10)
    options: list[Option] = Field(default_factory=list)
    children: dict[str, str] = Field(default_factory=dict)
    fallback_node_id: Optional[str] = None
    is_leaf: bool = Field(default=False)

    @field_validator("children")
    @classmethod
    def validate_children_no_self_ref(cls, v, info):
        """children 不应引用自身 node_id."""
        node_id = info.data.get("node_id")
        if node_id and node_id in v.values():
            raise ValueError(f"Node '{node_id}' references itself in children")
        return v


class FollowUpTree(BaseModel):
    task_type: str = Field(..., min_length=1)
    root_node_id: str = Field(..., min_length=1)
    nodes: dict[str, QuestionNode]

    @field_validator("nodes")
    @classmethod
    def validate_root_exists(cls, v, info):
        """root_node_id 必须存在于 nodes dict 中."""
        root_id = info.data.get("root_node_id")
        if root_id and root_id not in v:
            raise ValueError(f"root_node_id '{root_id}' not found in nodes")
        return v


# ============================================================
# Workflows
# ============================================================

class WorkflowStep(BaseModel):
    step: int = Field(..., ge=1)
    name: str = Field(..., min_length=1)
    owner: str = Field(default="")
    deliverables: list[str] = Field(default_factory=list)


class DecisionPoint(BaseModel):
    point: str = Field(..., min_length=1)
    yes: str = Field(default="")
    no: str = Field(default="")


class FailureMode(BaseModel):
    name: str = Field(..., min_length=1)
    impact: str = Field(default="")
    prevention: str = Field(default="")


class Workflow(BaseModel):
    name: str = Field(..., min_length=1)
    category: str = Field(default="")
    steps: list[WorkflowStep] = Field(default_factory=list)
    decision_points: list[DecisionPoint] = Field(default_factory=list)
    failure_modes: list[FailureMode] = Field(default_factory=list)


# ============================================================
# Roles
# ============================================================

class KPI(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(default="")
    benchmark: str = Field(default="")


class Role(BaseModel):
    name: str = Field(..., min_length=1)
    kpis: list[KPI] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    common_tasks: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)


# ============================================================
# Docs
# ============================================================

class DocSection(BaseModel):
    title: str = Field(..., min_length=1)
    prompt_hint: str = Field(default="")


class DocTemplate(BaseModel):
    name: str = Field(..., min_length=1)
    task_type: str = Field(default="")
    sections: list[DocSection] = Field(default_factory=list)
    tone: str = Field(default="")
    common_mistakes: list[str] = Field(default_factory=list)


# ============================================================
# Pain Points
# ============================================================

class PainPoint(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(default="")
    why_happens: str = Field(default="")
    who_feels_it: str = Field(default="")
    typical_phrases: list[str] = Field(default_factory=list)
    what_not_to_do: str = Field(default="")


# ============================================================
# Top-Level Pack
# ============================================================

class KnowledgePack(BaseModel):
    meta: PackMeta
    terms: list[Term] = Field(default_factory=list)
    tasks: list[Task] = Field(default_factory=list)
    roles: list[Role] = Field(default_factory=list)
    workflows: list[Workflow] = Field(default_factory=list)
    docs: list[DocTemplate] = Field(default_factory=list)
    follow_up_trees: list[FollowUpTree] = Field(default_factory=list)
    pain_points: list[PainPoint] = Field(default_factory=list)


# ============================================================
# Compilation
# ============================================================

def compile_pack(yaml_path: Path, output_dir: Path) -> dict:
    """Parse one YAML file, validate, write JSON. Returns stats dict.

    Args:
        yaml_path: Path to the YAML source file.
        output_dir: Directory to write compiled JSON to.

    Returns:
        dict with keys: pack_id, terms, tasks, trees

    Raises:
        FileNotFoundError: If yaml_path does not exist.
        yaml.YAMLError: If YAML parsing fails.
        ValidationError: If data does not match schema.
        ValueError: If file is empty or cycle detected.
    """
    # 步骤 1: 解析 YAML
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        raise
    except yaml.YAMLError as e:
        print(f"  YAML 解析错误 ({yaml_path.name}): {e}")
        raise

    # 步骤 2: 检查空文件
    if data is None:
        raise ValueError(f"{yaml_path.name} 是空文件")

    # 步骤 3: Pydantic 验证
    try:
        pack = KnowledgePack(**data)
    except ValidationError as e:
        print(f"  Schema 验证失败 ({yaml_path.name}):")
        for error in e.errors():
            loc = " -> ".join(str(l) for l in error["loc"])
            print(f"    {loc}: {error['msg']}")
        raise

    # 步骤 4: 追问树环检测
    for tree in pack.follow_up_trees:
        _check_tree_cycles(tree)

    # 步骤 5: 输出 JSON
    output_path = output_dir / f"{pack.meta.id}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(pack.model_dump(), f, ensure_ascii=False, indent=2)

    return {
        "pack_id": pack.meta.id,
        "terms": len(pack.terms),
        "tasks": len(pack.tasks),
        "trees": len(pack.follow_up_trees),
    }


def _check_tree_cycles(tree) -> None:
    """DFS cycle detection for follow-up tree node references.

    Uses per-path tracking to distinguish DAG merges (paths converging to
    the same node) from true cycles (child pointing back to an ancestor
    on the same DFS path).

    Args:
        tree: A FollowUpTree instance to validate.

    Raises:
        ValueError: If a cycle or missing node reference is found.
    """
    visited = set()      # fully explored nodes
    in_stack = set()     # nodes on the current DFS path

    def _dfs(node_id: str) -> None:
        if node_id in in_stack:
            raise ValueError(
                f"循环引用: tree '{tree.task_type}' node '{node_id}'"
            )
        if node_id in visited:
            return  # already fully explored, no cycle here

        node = tree.nodes.get(node_id)
        if node is None:
            raise ValueError(
                f"引用不存在的节点: tree '{tree.task_type}' node '{node_id}'"
            )

        in_stack.add(node_id)
        for child_id in node.children.values():
            _dfs(child_id)
        in_stack.remove(node_id)
        visited.add(node_id)

    _dfs(tree.root_node_id)


def _generate_index(output_dir: Path) -> dict:
    """从所有已编译的 JSON 包中生成 index.json。

    Args:
        output_dir: 编译产物输出目录（包含 *.json 文件）。

    Returns:
        生成的 index dict（同时写入 output_dir/index.json）。
    """
    index = {}
    for json_path in sorted(output_dir.glob("*.json")):
        if json_path.name == "index.json":
            continue
        with open(json_path, "r", encoding="utf-8") as f:
            pack = json.load(f)

        meta = pack.get("meta", {})
        pack_id = meta.get("id", json_path.stem)

        # 收集关键词：term 名 + aliases + task 名（不含 related_terms，防索引膨胀）
        keywords = []
        for term in pack.get("terms", []):
            t = term.get("term", "")
            if t:
                keywords.append(t)
            keywords.extend(term.get("aliases", []))
        for task in pack.get("tasks", []):
            t = task.get("name", "")
            if t:
                keywords.append(t)

        keywords = sorted(set(k for k in keywords if k))

        index[pack_id] = {
            "id": pack_id,
            "name": meta.get("name", pack_id),
            "icon": meta.get("icon", ""),
            "description": meta.get("description", ""),
            "keywords": keywords,
            "pack_file": json_path.name,
            "stats": {
                "term_count": len(pack.get("terms", [])),
                "scenario_count": len(pack.get("tasks", [])),
                "tree_count": len(pack.get("follow_up_trees", [])),
                "role_count": len(pack.get("roles", [])),
                "workflow_count": len(pack.get("workflows", [])),
            },
        }

    index_path = output_dir / "index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"  Generated index.json with {len(index)} industry entries")
    return index


def main():
    """CLI entry point: compile all knowledge packs in the source directory.

    Exit code: 0 on success, 1 on any validation failure.
    """
    project_root = Path(__file__).parent.resolve()
    source_dir = project_root / "prompt_tool" / "knowledge_packs"
    output_dir = project_root / "prompt_tool" / "knowledge_packs_compiled"

    if not source_dir.exists():
        print(f"Error: 源目录不存在: {source_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    yaml_files = sorted(source_dir.glob("*.yaml"))
    yaml_files = [f for f in yaml_files if not f.name.startswith("_")]

    if not yaml_files:
        print("Warning: No YAML knowledge pack files found")
        print(f"  (looked in: {source_dir})")
        sys.exit(0)

    print(f"Found {len(yaml_files)} knowledge pack(s)")
    print(f"Output: {output_dir}\n")

    errors = []
    for yaml_file in yaml_files:
        try:
            stats = compile_pack(yaml_file, output_dir)
            print(f"  OK  {yaml_file.name} "
                  f"({stats['terms']} terms, {stats['tasks']} tasks, "
                  f"{stats['trees']} trees)")
        except (yaml.YAMLError, ValidationError, ValueError) as e:
            errors.append((yaml_file.name, str(e)))
            print(f"  FAIL {yaml_file.name}: {e}")

    print("\n" + "=" * 50)
    print(f"Results: {len(yaml_files) - len(errors)} succeeded, "
          f"{len(errors)} failed")

    if errors:
        print(f"\n{'=' * 50}")
        print("FAILED PACKS:")
        for name, msg in errors:
            print(f"  {name}")
            for line in msg.split("\n"):
                print(f"    {line}")
        sys.exit(1)

    # 所有包编译成功后生成 index.json
    _generate_index(output_dir)
    print("All packs compiled successfully.")


if __name__ == "__main__":
    main()
