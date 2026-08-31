import sys

from branch_helper.config import (
    CONFIG_PATH,
    get_effective_default,
    read_local_default,
    resolve_base_branch,
    resolve_profile,
)
from branch_helper.git_ops import (
    branch_exists,
    create_commit,
    current_branch,
    ensure_branch,
    has_staged_changes,
    is_on_branch,
    stash_pop,
    stash_push,
    update_branch,
    working_tree_dirty,
)
from branch_helper.output import print_issue
from branch_helper.sources import get_source
from branch_helper.sources.issue import Issue
from branch_helper.staging_screen import run_staging_screen


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


def select_wizard_profile(config: dict, alias: str | None = None) -> tuple[str, dict]:
    if alias:
        return resolve_profile(config, alias)

    local_default = read_local_default()
    aliases = config.get("aliases", {})

    if local_default and local_default[0] in aliases:
        return resolve_profile(config, None)

    alias_labels, alias_entries = build_alias_options(config)

    if len(alias_entries) == 1:
        return alias_entries[0]

    alias_index = prompt_choice("Select project:", alias_labels)
    return alias_entries[alias_index]


def print_missing_base_branch_error(alias_name: str) -> None:
    print("Cannot create branch: no base_branch configured.", file=sys.stderr)
    print("", file=sys.stderr)
    print(f"Set it in {CONFIG_PATH}:", file=sys.stderr)
    print("  aliases:", file=sys.stderr)
    print(f"    {alias_name}:", file=sys.stderr)
    print("      base_branch: master", file=sys.stderr)
    print("", file=sys.stderr)
    print("Or in .branch-helper-default (repo root):", file=sys.stderr)
    print(f"  {alias_name}", file=sys.stderr)
    print("  base_branch: master", file=sys.stderr)


def _branch_targets(selected: Issue, base_branch: str) -> tuple[str, str, str | None]:
    story_branch = selected.branch()
    task_branch = selected.task_branch()
    if task_branch:
        return task_branch, story_branch, story_branch
    return story_branch, base_branch, None


def _needs_branch_switch(target: str) -> bool:
    return not is_on_branch(target)


def _maybe_stash_before_switch(target: str) -> bool:
    if not _needs_branch_switch(target):
        print("Working tree has changes but already on target branch; not stashing.")
        return False
    if not working_tree_dirty():
        print("Working tree clean.")
        return False
    if not prompt_yes_no(
        "Working tree has uncommitted changes. Stash before switching?"
    ):
        print("Proceeding without stash.")
        return False
    return stash_push(f"branch-helper: checkout {target}")


def _ensure_issue_branch(
    selected: Issue,
    base_branch: str,
) -> None:
    target, parent, story_branch = _branch_targets(selected, base_branch)

    if story_branch is not None and not branch_exists(target):
        print(f"Ensuring story branch '{story_branch}' exists…")
        ensure_branch(story_branch, base_branch)
        print(f"Ensuring task branch '{target}' from story branch…")
        ensure_branch(target, story_branch)
    else:
        ensure_branch(target, parent)


def _issue_branch_refs(
    selected: Issue, profile: dict, alias_name: str
) -> tuple[str, str]:
    base_branch = resolve_base_branch(profile)
    if not base_branch:
        print_missing_base_branch_error(alias_name)
        sys.exit(1)
    target, parent, _story = _branch_targets(selected, base_branch)
    return target, parent


def _require_on_target_branch(
    selected: Issue, profile: dict, alias_name: str
) -> tuple[str, str]:
    target, parent = _issue_branch_refs(selected, profile, alias_name)
    if not is_on_branch(target):
        current = current_branch() or "(unknown)"
        print(
            f"Not on the issue branch '{target}' (currently on '{current}').",
            file=sys.stderr,
        )
        print(
            "Run 'branch-helper' first to create or checkout the branch.",
            file=sys.stderr,
        )
        sys.exit(1)
    return target, parent


def maybe_create_branch(selected: Issue, profile: dict, alias_name: str) -> None:
    base_branch = resolve_base_branch(profile)
    if not base_branch:
        print_missing_base_branch_error(alias_name)
        return

    target, parent, _story = _branch_targets(selected, base_branch)

    if is_on_branch(target):
        print(f"Already on the correct branch '{target}'.")
        return

    if not prompt_yes_no(f"Create/checkout branch '{target}' from '{parent}'?"):
        return

    stashed = _maybe_stash_before_switch(target)
    try:
        _ensure_issue_branch(selected, base_branch)
    finally:
        if stashed:
            stash_pop()


def maybe_commit_after_staging(selected: Issue) -> None:
    subject = selected.commit_message()
    if subject is None:
        print("No commit message for this issue type; skipping commit.")
        return

    if not has_staged_changes():
        print("No staged files; skipping commit.")
        return

    print(f"Commit subject: {subject}")
    extra = input("Extra message (optional): ").strip()
    message = subject if not extra else f"{subject}\n\n{extra}"

    if create_commit(message):
        print("Commit created.")


def _maybe_stash_before_update(branch: str) -> bool:
    if not working_tree_dirty():
        return False
    if not prompt_yes_no(
        "Working tree has uncommitted changes. Stash before updating?"
    ):
        print("Proceeding without stash.")
        return False
    return stash_push(f"branch-helper: update {branch}")


def maybe_update_branch(selected: Issue, profile: dict, alias_name: str) -> None:
    _target, parent = _require_on_target_branch(selected, profile, alias_name)
    current = current_branch()
    if current is None:
        print("Could not determine current branch.", file=sys.stderr)
        sys.exit(1)
    stashed = _maybe_stash_before_update(current)
    try:
        update_branch(current, parent)
    finally:
        if stashed:
            stash_pop()


def finish_issue(selected: Issue, profile: dict, alias_name: str, mode: str) -> None:
    print_issue(selected)
    if mode == "branch":
        maybe_create_branch(selected, profile, alias_name)
    elif mode == "commit":
        _require_on_target_branch(selected, profile, alias_name)
        if run_staging_screen(selected):
            maybe_commit_after_staging(selected)
    elif mode == "update":
        maybe_update_branch(selected, profile, alias_name)


def run_wizard(config: dict, *, mode: str = "branch", alias: str | None = None) -> None:
    alias_name, profile = select_wizard_profile(config, alias)
    source = get_source(profile, alias_name)
    items = source.fetch_issues()

    if not items:
        print(f"No assigned issues found for '{alias_name}'.")
        return

    if len(items) == 1:
        finish_issue(items[0], profile, alias_name, mode)
        return

    issue_labels = [item.label() for item in items]
    issue_index = prompt_choice("Select issue:", issue_labels)
    finish_issue(items[issue_index], profile, alias_name, mode)
