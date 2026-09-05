from branch_helper.branch_mode import BranchMode
from branch_helper.sources import get_source
from branch_helper.sources.issue import Issue


def print_issue(
    issue: Issue,
    *,
    branch_mode: BranchMode | None = None,
    mode_stored: bool = False,
) -> None:
    print("----------------")
    print(issue.label())
    print(f"    branch: {issue.branch()}")
    task_branch = issue.task_branch()
    if task_branch is not None and branch_mode is not None:
        mode_label = "story branch" if branch_mode == "story" else "task branch"
        stored_suffix = " (stored)" if mode_stored else ""
        print(f"    branching mode: {mode_label}{stored_suffix}")
        checkout_target = issue.branch() if branch_mode == "story" else task_branch
        print(f"    checkout target: {checkout_target}")
    elif task_branch is not None:
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
