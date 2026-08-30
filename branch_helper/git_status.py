import subprocess
import sys

from branch_helper.worktree_entry import WorktreeEntry


def _run_git(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _parse_porcelain_line(line: str) -> list[WorktreeEntry]:
    if not line.strip():
        return []

    if line.startswith("?? "):
        path = line[3:].strip()
        return [
            WorktreeEntry(
                path=path,
                status_label="?",
                is_staged=False,
                kind="untracked",
            )
        ]

    if len(line) < 4:
        return []

    index_status = line[0]
    worktree_status = line[1]
    rest = line[3:].strip()
    if " -> " in rest:
        path = rest.split(" -> ", 1)[1].strip()
    else:
        path = rest

    entries: list[WorktreeEntry] = []
    if index_status != " ":
        entries.append(
            WorktreeEntry(
                path=path,
                status_label=index_status,
                is_staged=True,
                kind="staged",
            )
        )

    if worktree_status == "?":
        if index_status == " ":
            entries.append(
                WorktreeEntry(
                    path=path,
                    status_label="?",
                    is_staged=False,
                    kind="untracked",
                )
            )
    elif worktree_status != " ":
        entries.append(
            WorktreeEntry(
                path=path,
                status_label=worktree_status,
                is_staged=False,
                kind="unstaged",
            )
        )

    return entries


def list_worktree_entries() -> list[WorktreeEntry]:
    result = _run_git(["status", "--porcelain=v1"])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        print(f"Failed to read git status: {detail}", file=sys.stderr)
        return []

    entries: list[WorktreeEntry] = []
    for line in result.stdout.splitlines():
        entries.extend(_parse_porcelain_line(line))
    return entries


def stage_path(path: str) -> bool:
    result = _run_git(["add", "--", path])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        print(f"Failed to stage '{path}': {detail}", file=sys.stderr)
        return False
    return True


def unstage_path(path: str) -> bool:
    result = _run_git(["restore", "--staged", "--", path])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        print(f"Failed to unstage '{path}': {detail}", file=sys.stderr)
        return False
    return True


def toggle_staged(entry: WorktreeEntry) -> bool:
    if entry.is_staged:
        return unstage_path(entry.path)
    return stage_path(entry.path)
