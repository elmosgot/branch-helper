from branch_helper.sources.base import Issue, IssueSource
from branch_helper.sources.github.client import get_github_issues
from branch_helper.sources.github.issue import GitHubIssue


class GitHubSource(IssueSource):
    def __init__(self, profile: dict, alias: str):
        self.profile = profile
        self.alias = alias

    def fetch_issues(self) -> list[Issue]:
        return [
            GitHubIssue(issue) for issue in get_github_issues(self.profile, self.alias)
        ]
