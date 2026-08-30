import subprocess
import sys

from branch_helper.ensure_branch_result import EnsureBranchResult


def _run_git(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=check,
    )


def _step(message: str) -> None:
    print(message)


def is_git_repo() -> bool:
    result = _run_git(["rev-parse", "--show-toplevel"], check=False)
    return result.returncode == 0


def current_branch() -> str | None:
    result = _run_git(["branch", "--show-current"], check=False)
    if result.returncode != 0:
        return None
    branch = result.stdout.strip()
    return branch or None


def is_on_branch(name: str) -> bool:
    current = current_branch()
    if current is None:
        return False
    return current.casefold() == name.casefold()


def working_tree_dirty() -> bool:
    result = _run_git(["status", "--porcelain"], check=False)
    return bool(result.stdout.strip())


def stash_push(message: str) -> bool:
    _step(f"Stashing local changes ({message})…")
    result = _run_git(["stash", "push", "-u", "-m", message], check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        print(f"Failed to stash changes: {detail}", file=sys.stderr)
        return False
    return True


def stash_pop() -> bool:
    _step("Restoring stashed changes…")
    result = _run_git(["stash", "pop"], check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        print(
            f"Warning: failed to restore stashed changes: {detail}",
            file=sys.stderr,
        )
        return False
    return True


def _local_branch_names() -> list[str]:
    result = _run_git(
        ["for-each-ref", "--format=%(refname:short)", "refs/heads/"],
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _remote_branch_names() -> list[str]:
    result = _run_git(
        ["for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/"],
        check=False,
    )
    if result.returncode != 0:
        return []
    prefix = "origin/"
    names = []
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "origin/HEAD":
            continue
        if stripped.startswith(prefix):
            names.append(stripped[len(prefix) :])
    return names


def _find_branch_case_insensitive(name: str, branches: list[str]) -> str | None:
    target = name.casefold()
    for branch in branches:
        if branch.casefold() == target:
            return branch
    return None


def branch_exists(name: str) -> bool:
    if _local_branch_exists(name) or _remote_branch_exists(name):
        return True
    return (
        _find_branch_case_insensitive(name, _local_branch_names()) is not None
        or _find_branch_case_insensitive(name, _remote_branch_names()) is not None
    )


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


def _push_upstream(name: str) -> None:
    _step(f"Pushing '{name}' to origin and setting upstream…")
    result = _run_git(["push", "-u", "origin", name], check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        print(
            f"Warning: failed to push and set upstream for '{name}': {detail}",
            file=sys.stderr,
        )
        print(
            f"Run manually: git push -u origin {name!r}",
            file=sys.stderr,
        )


def _checkout_existing(name: str) -> None:
    checkout = _run_git(["checkout", name], check=False)
    if checkout.returncode != 0:
        _git_fail(checkout, f"Failed to checkout '{name}'.")


def _checkout_remote_tracking(name: str, remote_name: str) -> None:
    checkout = _run_git(["checkout", "-b", name, f"origin/{remote_name}"], check=False)
    if checkout.returncode != 0:
        _git_fail(checkout, f"Failed to checkout 'origin/{remote_name}'.")


def ensure_branch(name: str, parent_branch: str) -> EnsureBranchResult:
    if not is_git_repo():
        print("Not inside a git repository; skipping branch creation.", file=sys.stderr)
        return EnsureBranchResult(created=False, checked_out=False)

    _step("Fetching origin…")
    fetch = _run_git(["fetch", "origin"], check=False)
    if fetch.returncode != 0:
        print(
            f"Warning: git fetch origin failed: {fetch.stderr.strip()}",
            file=sys.stderr,
        )

    if _local_branch_exists(name):
        if is_on_branch(name):
            _step(f"Already on branch '{name}'.")
            return EnsureBranchResult(created=False, checked_out=False)
        _step(f"Branch '{name}' already exists locally — checking out.")
        _checkout_existing(name)
        return EnsureBranchResult(created=False, checked_out=True)

    local_match = _find_branch_case_insensitive(name, _local_branch_names())
    if local_match is not None:
        if is_on_branch(local_match):
            _step(
                f"Already on branch '{local_match}' (matches '{name}' ignoring case)."
            )
            return EnsureBranchResult(created=False, checked_out=False)
        _step(
            f"Branch '{local_match}' already exists locally "
            f"(matches '{name}' ignoring case) — checking out."
        )
        _checkout_existing(local_match)
        return EnsureBranchResult(created=False, checked_out=True)

    if _remote_branch_exists(name):
        _step(f"Branch 'origin/{name}' exists — checking out with tracking.")
        _checkout_remote_tracking(name, name)
        return EnsureBranchResult(created=False, checked_out=True)

    remote_match = _find_branch_case_insensitive(name, _remote_branch_names())
    if remote_match is not None:
        _step(
            f"Branch 'origin/{remote_match}' exists "
            f"(matches '{name}' ignoring case) — checking out with tracking."
        )
        _checkout_remote_tracking(remote_match, remote_match)
        return EnsureBranchResult(created=False, checked_out=True)

    _step(f"No branch '{name}' — will create from '{parent_branch}'.")

    if _remote_branch_exists(parent_branch):
        _step(f"Creating branch '{name}' from 'origin/{parent_branch}'.")
        create = _run_git(
            ["checkout", "--no-track", "-b", name, f"origin/{parent_branch}"],
            check=False,
        )
    elif _local_branch_exists(parent_branch):
        local_parent = _find_branch_case_insensitive(
            parent_branch, _local_branch_names()
        )
        parent_ref = local_parent or parent_branch
        _step(f"Creating branch '{name}' from local '{parent_ref}'.")
        create = _run_git(["checkout", "-b", name, parent_ref], check=False)
    else:
        print(
            f"Parent branch '{parent_branch}' not found locally or on origin.",
            file=sys.stderr,
        )
        sys.exit(1)

    if create.returncode != 0:
        _git_fail(create, f"Failed to create branch '{name}'.")

    _step(f"Created and checked out branch '{name}'.")
    _push_upstream(name)
    return EnsureBranchResult(created=True, checked_out=True)
