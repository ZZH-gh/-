"""
KnowledgePack — 运行时知识包包装类

提供 8 个 typed getter 方法，返回值均为 Python 原生类型（dict/list/None）。
零运行时依赖（仅使用 Python stdlib dict/list 操作）。
无数据验证——编译时已验证。
"""


class KnowledgePack:
    """Typed wrapper around a compiled knowledge pack JSON dict.

    Provides typed access to specific slices of the data.
    Returns native Python types only. No Pydantic, no validation.
    """

    def __init__(self, data: dict):
        self._data = data

    # ---- Meta ----

    def get_meta(self) -> dict:
        """Returns meta dict with id, name, icon, description, etc."""
        return self._data.get("meta", {})

    # ---- Terms ----

    def get_terms(self, category: str | None = None) -> list[dict]:
        """Returns all terms, optionally filtered by category."""
        terms = self._data.get("terms", [])
        if category:
            return [t for t in terms if t.get("category") == category]
        return terms

    # ---- Tasks ----

    def get_tasks(self) -> list[dict]:
        """Returns all task/scenario definitions."""
        return self._data.get("tasks", [])

    def get_task(self, task_name: str) -> dict | None:
        """Returns a single task by name, or None if not found."""
        for task in self._data.get("tasks", []):
            if task.get("name") == task_name:
                return task
        return None

    # ---- Roles ----

    def get_roles(self) -> list[dict]:
        """Returns all role definitions."""
        return self._data.get("roles", [])

    def get_role(self, role_name: str) -> dict | None:
        """Returns a single role by name, or None if not found."""
        for role in self._data.get("roles", []):
            if role.get("name") == role_name:
                return role
        return None

    # ---- Workflows ----

    def get_workflows(self, category: str | None = None) -> list[dict]:
        """Returns all workflows, optionally filtered by category."""
        wfs = self._data.get("workflows", [])
        if category:
            return [w for w in wfs if w.get("category") == category]
        return wfs

    def get_workflow(self, name: str) -> dict | None:
        """Returns a workflow by name, or None if not found."""
        for wf in self._data.get("workflows", []):
            if wf.get("name") == name:
                return wf
        return None

    # ---- Doc Templates ----

    def get_doc_templates(self, task_type: str | None = None) -> list[dict]:
        """Returns doc templates, optionally filtered by task_type."""
        docs = self._data.get("docs", [])
        if task_type:
            return [d for d in docs if d.get("task_type") == task_type]
        return docs

    def get_doc_template(self, template_name: str) -> dict | None:
        """Returns a doc template by name, or None if not found."""
        for doc in self._data.get("docs", []):
            if doc.get("name") == template_name:
                return doc
        return None

    # ---- Follow-up Trees ----

    def get_follow_up_tree(self, task_type: str) -> dict | None:
        """Returns a follow-up tree by its task_type identifier, or None."""
        for tree in self._data.get("follow_up_trees", []):
            if tree.get("task_type") == task_type:
                return tree
        return None

    # ---- Pain Points ----

    def get_pain_points(self) -> list[dict]:
        """Returns all industry pain points."""
        return self._data.get("pain_points", [])
