import subprocess
import sys


def _run_git(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=check,
    )


def is_git_repo() -> bool:
    result = _run_git(["rev-parse", "--show-toplevel"], check=False)
    return result.returncode == 0


def branch_exists(name: str) -> bool:
    return _local_branch_exists(name) or _remote_branch_exists(name)


def _local_branch_exists(name: str) -> bool:
    return (
        _run_git(
            ["show-ref", "--verify", "--quiet", f"refs/heads/{name}"],
            check=False,
        ).returncode
        == 0
    )


def _remote_branch_exists(name: str) -> bool:
    return (
        _run_git(
            ["show-ref", "--verify", "--quiet", f"refs/remotes/origin/{name}"],
            check=False,
        ).returncode
        == 0
    )


def _git_fail(result: subprocess.CompletedProcess, message: str) -> None:
    detail = result.stderr.strip() or result.stdout.strip()
    if detail:
        print(detail, file=sys.stderr)
    print(message, file=sys.stderr)
    sys.exit(result.returncode or 1)


def ensure_branch(name: str, base_branch: str) -> None:
    if not is_git_repo():
        print("Not inside a git repository; skipping branch creation.", file=sys.stderr)
        return

    fetch = _run_git(["fetch", "origin"], check=False)
    if fetch.returncode != 0:
        print(
            f"Warning: git fetch origin failed: {fetch.stderr.strip()}",
            file=sys.stderr,
        )

    if _local_branch_exists(name):
        print(f"Checking out existing branch '{name}'.")
        checkout = _run_git(["checkout", name], check=False)
        if checkout.returncode != 0:
            _git_fail(checkout, f"Failed to checkout '{name}'.")
        return

    if _remote_branch_exists(name):
        print(f"Checking out remote branch 'origin/{name}'.")
        checkout = _run_git(["checkout", "-b", name, f"origin/{name}"], check=False)
        if checkout.returncode != 0:
            _git_fail(checkout, f"Failed to checkout 'origin/{name}'.")
        return

    if _remote_branch_exists(base_branch):
        print(f"Creating branch '{name}' from 'origin/{base_branch}'.")
        create = _run_git(
            ["checkout", "-b", name, f"origin/{base_branch}"],
            check=False,
        )
    elif _local_branch_exists(base_branch):
        print(f"Creating branch '{name}' from local '{base_branch}'.")
        create = _run_git(["checkout", "-b", name, base_branch], check=False)
    else:
        print(
            f"Base branch '{base_branch}' not found locally or on origin.",
            file=sys.stderr,
        )
        sys.exit(1)

    if create.returncode != 0:
        _git_fail(create, f"Failed to create branch '{name}'.")

    print(f"Created and checked out branch '{name}'.")
