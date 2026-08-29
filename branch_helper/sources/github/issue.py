from branch_helper.slugify import slugify
from branch_helper.sources.base import Issue


class GitHubIssue(Issue):
    def __init__(self, data: dict):
        self.data = data

    def getNumber(self) -> int:
        return self.data.get("number")

    def getTitle(self) -> str:
        return self.data.get("title", "")

    def label(self) -> str:
        return f"Issue: #{self.getNumber()} {self.getTitle()}"

    def branch(self) -> str:
        return f"issues/{self.getNumber()}-{slugify(self.getTitle())}"

    def task_branch(self) -> str | None:
        return None

    def commit_message(self) -> str | None:
        return f"(#{self.getNumber()}) {self.getTitle()}"
