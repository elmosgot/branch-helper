from branch_helper.slugify import slugify
from branch_helper.sources.issue import Issue
from branch_helper.sources.jira.entity import Entity


class JiraIssue(Issue):
    def __init__(self, data: dict):
        self.entity = Entity(data)
        parent = self.entity.getField("parent")
        self.parent = Entity(parent) if parent is not None else None

    def label(self) -> str:
        return f"{self.entity.getType()}: {self.entity.getName()}"

    def branch(self) -> str:
        base = self.parent if self.parent is not None else self.entity
        title = base.getField("summary")
        return f"feature/{base.getId()}-{slugify(title)}"

    def task_branch(self) -> str | None:
        if self.entity.getType() not in ["Subtaak", "Taak"]:
            return None
        if self.parent is None:
            return "no-parent"
        title = self.entity.getField("summary")
        return f"feature/{self.parent.getId()}-{self.entity.getId()}-{slugify(title)}"

    def commit_message(self) -> str | None:
        if self.entity.getType() not in ["Subtaak", "Taak"]:
            return None
        return f"{self.entity.getId()} {self.entity.getField('summary')}"

    def note(self) -> str | None:
        issue_type = self.entity.getType()
        if issue_type in ["Subtaak", "Taak"]:
            return None
        return f"Not a subtaak: {issue_type}"
