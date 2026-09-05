from branch_helper.slugify import slugify
from branch_helper.sources.issue import Issue


class LinearIssue(Issue):
    def __init__(self, data: dict):
        self.data = data
        parent = data.get("parent")
        self.parent = LinearIssue(parent) if parent else None

    def getIdentifier(self) -> str:
        return self.data.get("identifier", "")

    def getTitle(self) -> str:
        return self.data.get("title", "")

    def hasParent(self) -> bool:
        return self.parent is not None

    def label(self) -> str:
        if self.hasParent():
            return f"Sub-issue: {self.getIdentifier()} {self.getTitle()}"
        return f"Issue: {self.getIdentifier()} {self.getTitle()}"

    def branch(self) -> str:
        if self.task_branch() is not None and self.hasParent():
            base = self.parent
        else:
            base = self
        return f"feature/{base.getIdentifier()}-{slugify(base.getTitle())}"

    def task_branch(self) -> str | None:
        if not self.hasParent():
            return None
        return (
            f"feature/{self.parent.getIdentifier()}-"
            f"{self.getIdentifier()}-{slugify(self.getTitle())}"
        )

    def commit_message(self) -> str | None:
        return f"({self.getIdentifier()}) {self.getTitle()}"

    def story_issue(self) -> Issue:
        if self.task_branch() is not None and self.hasParent():
            return self.parent
        return self
