from branch_helper.slugify import slugify
from branch_helper.sources.base import Issue


class Entity:
    def __init__(self, data: dict):
        self.data = data
        self.fields = {} if data["fields"] is None else data["fields"]

    def getId(self) -> str:
        return self.data.get("key")

    def getField(self, key, default=None) -> str | None:
        field = self.fields.get(key)

        return default if field is None else field

    def getName(self) -> str:
        return f"{self.getId()} {self.getField('summary')}"

    def getType(self) -> str:
        issue_type = self.getField("issuetype")
        return f"{issue_type['name']}"


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
        return f"{base.getId()}-{slugify(title)}"

    def task_branch(self) -> str | None:
        if self.entity.getType() not in ["Subtaak", "Taak"]:
            return None
        if self.parent is None:
            return "no-parent"
        title = self.entity.getField("summary")
        return f"{self.parent.getId()}-{self.entity.getId()}-{slugify(title)}"

    def commit_message(self) -> str | None:
        if self.entity.getType() not in ["Subtaak", "Taak"]:
            return None
        return f"({self.entity.getId()}) {self.entity.getField('summary')}"

    def note(self) -> str | None:
        issue_type = self.entity.getType()
        if issue_type in ["Subtaak", "Taak"]:
            return None
        return f"Not a subtaak: {issue_type}"
