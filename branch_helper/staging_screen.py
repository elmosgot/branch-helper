import curses
import sys

from branch_helper.git_ops import current_branch, is_git_repo
from branch_helper.git_status import list_worktree_entries, toggle_staged
from branch_helper.sources.issue import Issue
from branch_helper.worktree_entry import WorktreeEntry

HEADER = "Stage files for commit  (↑/↓ move, Space toggle, Enter done)"
SEPARATOR = "─" * 60


def _format_row(entry: WorktreeEntry) -> str:
    check = "x" if entry.is_staged else " "
    return f"[{check}] {entry.status_label}  {entry.path}  {entry.display_suffix()}"


def _entry_key(entry: WorktreeEntry) -> tuple[str, bool]:
    return (entry.path, entry.is_staged)


def _find_index_by_key(
    entries: list[WorktreeEntry],
    selected_key: tuple[str, bool] | None,
) -> int:
    if selected_key is None or not entries:
        return 0
    for index, entry in enumerate(entries):
        if _entry_key(entry) == selected_key:
            return index
    path, _ = selected_key
    for index, entry in enumerate(entries):
        if entry.path == path:
            return index
    return 0


def _draw_screen(
    stdscr: curses.window,
    entries: list[WorktreeEntry],
    selected_index: int,
    issue: Issue,
) -> None:
    stdscr.erase()
    height, width = stdscr.getmaxyx()
    branch = current_branch() or "(detached or unknown)"
    stdscr.addnstr(0, 0, HEADER, width - 1)
    stdscr.addnstr(1, 0, f"Branch: {branch}", width - 1)
    stdscr.addnstr(2, 0, f"Task:   {issue.label()}", width - 1)
    stdscr.addnstr(3, 0, SEPARATOR, width - 1)

    if not entries:
        stdscr.addnstr(5, 0, "No changed files to stage.", width - 1)
        stdscr.refresh()
        return

    list_top = 4
    list_height = max(1, height - list_top - 1)
    page_start = (selected_index // list_height) * list_height
    for row_offset in range(list_height):
        entry_index = page_start + row_offset
        if entry_index >= len(entries):
            break
        entry = entries[entry_index]
        line = _format_row(entry)
        y = list_top + row_offset
        if entry_index == selected_index:
            stdscr.attron(curses.A_REVERSE)
            stdscr.addnstr(y, 0, line, width - 1)
            stdscr.attroff(curses.A_REVERSE)
        else:
            stdscr.addnstr(y, 0, line, width - 1)

    stdscr.refresh()


def _staging_main(stdscr: curses.window, issue: Issue) -> None:
    curses.curs_set(0)
    stdscr.keypad(True)

    selected_key: tuple[str, bool] | None = None
    while True:
        entries = list_worktree_entries()
        selected_index = _find_index_by_key(entries, selected_key)
        if entries:
            selected_key = _entry_key(entries[selected_index])

        _draw_screen(stdscr, entries, selected_index, issue)

        key = stdscr.getch()
        if key in (ord("\n"), ord("\r"), ord("q")):
            return

        if not entries:
            continue

        if key in (curses.KEY_UP, ord("k")):
            selected_index = (selected_index - 1) % len(entries)
            selected_key = _entry_key(entries[selected_index])
        elif key in (curses.KEY_DOWN, ord("j")):
            selected_index = (selected_index + 1) % len(entries)
            selected_key = _entry_key(entries[selected_index])
        elif key == ord(" "):
            entry = entries[selected_index]
            toggle_staged(entry)
            selected_key = _entry_key(entry)


def run_staging_screen(issue: Issue) -> None:
    if not is_git_repo():
        print("Not inside a git repository; skipping staging.", file=sys.stderr)
        return

    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print(
            "Staging screen requires an interactive terminal; skipping.",
            file=sys.stderr,
        )
        return

    try:
        curses.wrapper(lambda stdscr: _staging_main(stdscr, issue))
    except curses.error as error:
        print(f"Could not start staging screen: {error}", file=sys.stderr)
