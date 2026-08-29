from branch_helper.sources.base import Issue, IssueSource
from branch_helper.sources.linear.client import get_linear_issues
from branch_helper.sources.linear.issue import LinearIssue


class LinearSource(IssueSource):
    def __init__(self, profile: dict, alias: str):
        self.profile = profile
        self.alias = alias

    def fetch_issues(self) -> list[Issue]:
        return [
            LinearIssue(issue) for issue in get_linear_issues(self.profile, self.alias)
        ]
