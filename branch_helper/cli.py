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
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = read_config()

    if args.list_aliases:
        print_aliases(config)
        return 0

    try:
        if args.alias:
            alias_name, profile = resolve_profile(config, args.alias)
            print_issues_for_profile(alias_name, profile)
            return 0

        if sys.stdin.isatty():
            run_wizard(config)
            return 0

        alias_name, profile = resolve_profile(config, None)
        print_issues_for_profile(alias_name, profile)
        return 0
    except KeyboardInterrupt:
        print("\nCancelled.")
        return 130
