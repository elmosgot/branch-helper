import subprocess
from typing import Literal

BranchMode = Literal["story", "task"]

_CONFIG_KEY = "branch-helper-mode"


def _config_key(story_branch: str) -> str:
    return f"branch.{story_branch}.{_CONFIG_KEY}"


def get_branch_mode(story_branch: str) -> BranchMode | None:
    result = subprocess.run(
        ["git", "config", "--get", _config_key(story_branch)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    if value in ("story", "task"):
        return value
    return None


def set_branch_mode(story_branch: str, mode: BranchMode) -> None:
    subprocess.run(
        ["git", "config", _config_key(story_branch), mode],
        check=True,
    )


def _prompt_branch_mode(story_branch: str, task_branch: str) -> BranchMode:
    options = [
        f"Task branch — {task_branch} (separate branch per task)",
        (
            f"Story branch — {story_branch} "
            "(work on story branch, task commit message)"
        ),
    ]
    print("Branching mode for this story:")
    for index, label in enumerate(options, start=1):
        print(f"  {index}. {label}")
    while True:
        raw = input(f"Choose [1-{len(options)}]: ").strip()
        if raw.isdigit():
            choice = int(raw)
            if choice == 1:
                return "task"
            if choice == 2:
                return "story"
        print("Invalid choice, try again.")


def resolve_branch_mode(
    story_branch: str,
    task_branch: str,
) -> tuple[BranchMode, bool]:
    stored = get_branch_mode(story_branch)
    if stored is not None:
        return stored, True

    mode = _prompt_branch_mode(story_branch, task_branch)
    set_branch_mode(story_branch, mode)
    return mode, False
