from branch_helper.sources.issue import Issue
from branch_helper.sources.issue_source import IssueSource
from branch_helper.sources.jira.client import get_jira_tasks
from branch_helper.sources.jira.issue import JiraIssue


class JiraSource(IssueSource):
    def __init__(self, profile: dict, alias: str):
        self.profile = profile
        self.alias = alias

    def fetch_issues(self) -> list[Issue]:
        tasks = get_jira_tasks(self.profile, self.alias)
        return [JiraIssue(issue) for issue in tasks.get("issues", [])]
