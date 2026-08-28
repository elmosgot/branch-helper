from branch_helper.github import GitHubIssue, get_github_issues
from branch_helper.jira import JiraEntity, get_jira_tasks
from branch_helper.linear import LinearIssue, get_linear_issues


def print_jira_issue(task: JiraEntity) -> None:
    issue_type = task.getType()
    print("----------------")
    print(f"{issue_type}: {task.getName()}")
    print(f"    branch: {task.getBranch()}")
    if issue_type in ["Subtaak", "Taak"]:
        print(f"    task branch: {task.getTaskBranch()}")
        print(f"    commit message: {task.message()}")
    else:
        print(f"Not a subtaak: {issue_type}")
    print("----------------")


def print_github_issue(task: GitHubIssue) -> None:
    print("----------------")
    print(f"Issue: {task.getName()}")
    print(f"    branch: {task.getBranch()}")
    print(f"    commit message: {task.message()}")
    print("----------------")


def print_linear_issue(task: LinearIssue) -> None:
    print("----------------")
    if task.hasParent():
        print(f"Sub-issue: {task.getName()}")
        print(f"    branch: {task.getBranch()}")
        print(f"    task branch: {task.getTaskBranch()}")
        print(f"    commit message: {task.message()}")
    else:
        print(f"Issue: {task.getName()}")
        print(f"    branch: {task.getBranch()}")
        print(f"    commit message: {task.message()}")
    print("----------------")


def print_jira_issues(profile: dict, alias: str) -> None:
    tasks = get_jira_tasks(profile, alias)
    for issue in tasks.get("issues", []):
        print_jira_issue(JiraEntity(issue))


def print_github_issues(profile: dict, alias: str) -> None:
    issues = get_github_issues(profile, alias)
    for issue in issues:
        print_github_issue(GitHubIssue(issue))


def print_linear_issues(profile: dict, alias: str) -> None:
    issues = get_linear_issues(profile, alias)
    for issue in issues:
        print_linear_issue(LinearIssue(issue))


def print_issues_for_profile(alias_name: str, profile: dict) -> None:
    source = profile["source"]
    if source == "github":
        print_github_issues(profile, alias_name)
    elif source == "linear":
        print_linear_issues(profile, alias_name)
    else:
        print_jira_issues(profile, alias_name)
