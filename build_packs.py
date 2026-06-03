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
from pydantic import BaseModel, Field, field_validator
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
    pass  # Task 2 will implement


def _check_tree_cycles(tree) -> None:
    """BFS check for circular node references in a follow-up tree.

    Args:
        tree: A FollowUpTree instance to validate.

    Raises:
        ValueError: If a cycle or missing node reference is found.
    """
    pass  # Task 2 will implement


def main():
    """CLI entry point: compile all knowledge packs in the source directory.

    Exit code: 0 on success, 1 on any validation failure.
    """
    pass  # Task 2 will implement


if __name__ == "__main__":
    main()
