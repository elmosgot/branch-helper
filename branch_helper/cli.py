import argparse
import sys

from branch_helper.config import print_aliases, read_config, resolve_profile
from branch_helper.output import print_issues_for_profile
from branch_helper.wizard import run_wizard


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "List assigned issues and print suggested branch names and commit messages."
        )
    )
    parser.add_argument(
        "--alias",
        help="Named profile from config (overrides default)",
    )
    parser.add_argument(
        "--list-aliases",
        action="store_true",
        help="List configured aliases",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--commit",
        action="store_true",
        help="Stage and commit on the current issue branch (interactive wizard)",
    )
    mode_group.add_argument(
        "--update",
        action="store_true",
        help=("Fetch from origin and upmerge the parent branch (interactive wizard)"),
    )
    return parser.parse_args()


def _resolve_mode(args: argparse.Namespace) -> str:
    if args.commit:
        return "commit"
    if args.update:
        return "update"
    return "branch"


def main() -> int:
    args = parse_args()
    config = read_config()

    if args.list_aliases:
        print_aliases(config)
        return 0

    mode = _resolve_mode(args)

    try:
        if mode in ("commit", "update"):
            if not sys.stdin.isatty():
                print(
                    f"--{mode} requires an interactive terminal.",
                    file=sys.stderr,
                )
                return 1
            run_wizard(config, mode=mode, alias=args.alias)
            return 0

        if args.alias:
            alias_name, profile = resolve_profile(config, args.alias)
            print_issues_for_profile(alias_name, profile)
            return 0

        if sys.stdin.isatty():
            run_wizard(config, mode=mode)
            return 0

        alias_name, profile = resolve_profile(config, None)
        print_issues_for_profile(alias_name, profile)
        return 0
    except KeyboardInterrupt:
        print("\nCancelled.")
        return 130
