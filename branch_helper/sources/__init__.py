from branch_helper.sources.base import IssueSource
from branch_helper.sources.github import GitHubSource
from branch_helper.sources.jira import JiraSource
from branch_helper.sources.linear import LinearSource


def get_source(profile: dict, alias: str) -> IssueSource:
    source = profile["source"]
    if source == "github":
        return GitHubSource(profile, alias)
    if source == "jira":
        return JiraSource(profile, alias)
    if source == "linear":
        return LinearSource(profile, alias)
    raise ValueError(f"Unsupported source '{source}'")
