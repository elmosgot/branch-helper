from branch_helper.config import (
    get_effective_default,
    read_local_default,
    resolve_profile,
)
from branch_helper.github import fetch_github_entities
from branch_helper.jira import fetch_jira_entities
from branch_helper.linear import fetch_linear_entities
from branch_helper.output import (
    print_github_issue,
    print_jira_issue,
    print_linear_issue,
)


def prompt_choice(title: str, options: list[str]) -> int:
    print(title)
    for index, label in enumerate(options, start=1):
        print(f"  {index}. {label}")
    while True:
        raw = input(f"Choose [1-{len(options)}]: ").strip()
        if raw.isdigit():
            choice = int(raw)
            if 1 <= choice <= len(options):
                return choice - 1
        print("Invalid choice, try again.")


def build_alias_options(config: dict) -> tuple[list[str], list[tuple[str, dict]]]:
    aliases = config.get("aliases", {})
    effective_default = get_effective_default(config)
    entries = list(aliases.items())
    labels = []
    for name, profile in entries:
        source = profile.get("source", "?")
        suffix = "  (default)" if name == effective_default else ""
        labels.append(f"{name}  [{source}]{suffix}")
    return labels, entries


def select_wizard_profile(config: dict) -> tuple[str, dict]:
    local_default = read_local_default()
    aliases = config.get("aliases", {})

    if local_default and local_default[0] in aliases:
        return resolve_profile(config, None)

    alias_labels, alias_entries = build_alias_options(config)

    if len(alias_entries) == 1:
        return alias_entries[0]

    alias_index = prompt_choice("Select project:", alias_labels)
    return alias_entries[alias_index]


def linear_issue_label(item) -> str:
    if item.hasParent():
        return f"Sub-issue: {item.getName()}"
    return item.getName()


def run_wizard(config: dict) -> None:
    alias_name, profile = select_wizard_profile(config)
    source = profile["source"]

    if source == "github":
        items = fetch_github_entities(profile, alias_name)
        if not items:
            print(f"No assigned issues found for '{alias_name}'.")
            return

        if len(items) == 1:
            print_github_issue(items[0])
            return

        issue_labels = [item.getName() for item in items]
        issue_index = prompt_choice("Select issue:", issue_labels)
        print_github_issue(items[issue_index])
        return

    if source == "linear":
        items = fetch_linear_entities(profile, alias_name)
        if not items:
            print(f"No assigned issues found for '{alias_name}'.")
            return

        if len(items) == 1:
            print_linear_issue(items[0])
            return

        issue_labels = [linear_issue_label(item) for item in items]
        issue_index = prompt_choice("Select issue:", issue_labels)
        print_linear_issue(items[issue_index])
        return

    items = fetch_jira_entities(profile, alias_name)
    if not items:
        print(f"No assigned issues found for '{alias_name}'.")
        return

    if len(items) == 1:
        print_jira_issue(items[0])
        return

    issue_labels = [f"{item.getType()}: {item.getName()}" for item in items]
    issue_index = prompt_choice("Select issue:", issue_labels)
    print_jira_issue(items[issue_index])
