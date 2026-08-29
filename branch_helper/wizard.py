import sys

from branch_helper.config import (
    get_effective_default,
    read_local_default,
    resolve_profile,
)
from branch_helper.git_ops import ensure_branch
from branch_helper.output import print_issue
from branch_helper.sources import get_source
from branch_helper.sources.base import Issue


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


def prompt_yes_no(message: str, *, default: bool = True) -> bool:
    suffix = "Y/n" if default else "y/N"
    while True:
        raw = input(f"{message} [{suffix}]: ").strip().lower()
        if not raw:
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
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


def maybe_create_branch(selected: Issue, profile: dict) -> None:
    branch_name = selected.task_branch() or selected.branch()
    base_branch = profile.get("base_branch")
    if not base_branch:
        print(
            "Cannot create branch: alias needs 'base_branch' in config.",
            file=sys.stderr,
        )
        return

    if not prompt_yes_no(
        f"Create/checkout branch '{branch_name}' from '{base_branch}'?"
    ):
        return

    ensure_branch(branch_name, base_branch)


def finish_issue(selected: Issue, profile: dict) -> None:
    print_issue(selected)
    maybe_create_branch(selected, profile)


def run_wizard(config: dict) -> None:
    alias_name, profile = select_wizard_profile(config)
    source = get_source(profile, alias_name)
    items = source.fetch_issues()

    if not items:
        print(f"No assigned issues found for '{alias_name}'.")
        return

    if len(items) == 1:
        finish_issue(items[0], profile)
        return

    issue_labels = [item.label() for item in items]
    issue_index = prompt_choice("Select issue:", issue_labels)
    finish_issue(items[issue_index], profile)
