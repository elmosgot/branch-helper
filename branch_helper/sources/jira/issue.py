from branch_helper.slugify import slugify
from branch_helper.sources.issue import Issue
from branch_helper.sources.jira.entity import Entity


def _branch_prefix(issue_type: str) -> str:
    return "bug" if issue_type.casefold() == "bug" else "feature"


class JiraIssue(Issue):
    def __init__(self, data: dict):
        self.entity = Entity(data)
        parent = self.entity.getField("parent")
        self.parent = Entity(parent) if parent is not None else None

    def label(self) -> str:
        return f"{self.entity.getType()}: {self.entity.getName()}"

    def _resolve_branch_prefix(self) -> str:
        if _branch_prefix(self.entity.getType()) == "bug":
            return "bug"
        if self.parent is not None and _branch_prefix(self.parent.getType()) == "bug":
            return "bug"
        return "feature"

    def branch(self) -> str:
        if self.task_branch() is not None and self.parent is not None:
            base = self.parent
        else:
            base = self.entity
        title = base.getField("summary")
        prefix = self._resolve_branch_prefix()
        return f"{prefix}/{base.getId()}-{slugify(title)}"

    def task_branch(self) -> str | None:
        if self.entity.getType() not in ["Subtaak", "Taak"]:
            return None
        if self.parent is None:
            return "no-parent"
        title = self.entity.getField("summary")
        prefix = self._resolve_branch_prefix()
        return f"{prefix}/{self.parent.getId()}-{self.entity.getId()}-{slugify(title)}"

    def commit_message(self) -> str | None:
        if self.entity.getType() not in ["Subtaak", "Taak"]:
            return None
        return f"({self.entity.getId()}) {self.entity.getField('summary')}"

    def note(self) -> str | None:
        issue_type = self.entity.getType()
        if issue_type in ["Subtaak", "Taak"]:
            return None
        return f"Not a subtaak: {issue_type}"

    def story_issue(self) -> Issue:
        if self.task_branch() is not None and self.parent is not None:
            return JiraIssue(self.parent.data)
        return self
