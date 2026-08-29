from branch_helper.sources import get_source
from branch_helper.sources.base import Issue


def print_issue(issue: Issue) -> None:
    print("----------------")
    print(issue.label())
    print(f"    branch: {issue.branch()}")
    task_branch = issue.task_branch()
    if task_branch is not None:
        print(f"    task branch: {task_branch}")
    commit_message = issue.commit_message()
    if commit_message is not None:
        print(f"    commit message: {commit_message}")
    note = issue.note()
    if note is not None:
        print(note)
    print("----------------")


def print_issues_for_profile(alias_name: str, profile: dict) -> None:
    source = get_source(profile, alias_name)
    for issue in source.fetch_issues():
        print_issue(issue)
