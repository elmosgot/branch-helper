import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

CONFIG_PATH = Path.home() / ".config" / "branch-helper" / "config.yml"
LOCAL_DEFAULT_FILE = ".branch-helper-default"


@dataclass(frozen=True)
class LocalSettings:
    path: Path
    alias: str | None = None
    base_branch: str | None = None


def find_local_default_file() -> Path | None:
    directory = Path.cwd().resolve()
    while True:
        candidate = directory / LOCAL_DEFAULT_FILE
        if candidate.is_file():
            return candidate
        if directory.parent == directory:
            return None
        directory = directory.parent


def _parse_key_value_line(line: str) -> tuple[str, str] | None:
    for separator in (":", "="):
        if separator not in line:
            continue
        key, _, value = line.partition(separator)
        key = key.strip()
        value = value.strip()
        if key and value:
            return key, value
    return None


def read_local_settings() -> LocalSettings | None:
    path = find_local_default_file()
    if path is None:
        return None

    alias: str | None = None
    base_branch: str | None = None

    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        parsed = _parse_key_value_line(stripped)
        if parsed:
            key, value = parsed
            if key == "base_branch":
                base_branch = value
            continue

        if alias is None:
            alias = stripped

    if alias is None and base_branch is None:
        return None

    return LocalSettings(path=path, alias=alias, base_branch=base_branch)


def read_local_default() -> tuple[str, Path] | None:
    settings = read_local_settings()
    if settings is None or settings.alias is None:
        return None
    return settings.alias, settings.path


def resolve_base_branch(profile: dict) -> str | None:
    settings = read_local_settings()
    if settings and settings.base_branch:
        return settings.base_branch
    value = profile.get("base_branch")
    if value:
        return str(value)
    return None


def get_effective_default(config: dict) -> str | None:
    local_default = read_local_default()
    if local_default:
        return local_default[0]
    return config.get("default")


def read_config() -> dict:
    if not CONFIG_PATH.is_file():
        print(f"Config not found: {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(CONFIG_PATH) as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as error:
            print(error, file=sys.stderr)
            sys.exit(1)

    return config or {}


def require_config_section(profile: dict, section: str, alias: str) -> dict:
    section_config = profile.get(section)
    if not section_config:
        print(
            f"Alias '{alias}' is missing '{section}' config block in {CONFIG_PATH}",
            file=sys.stderr,
        )
        sys.exit(1)

    return section_config


def resolve_profile(config: dict, alias_name: str | None) -> tuple[str, dict]:
    if not config.get("aliases"):
        if config.get("jira") or config.get("github"):
            print(
                "Config uses the old flat format. "
                "Migrate to aliases — see example.yml.",
                file=sys.stderr,
            )
        else:
            print(f"Missing 'aliases' section in {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)

    name = alias_name or get_effective_default(config)
    if not name:
        print(f"Missing 'default' alias in {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)

    aliases = config.get("aliases")
    if name not in aliases:
        local_default = read_local_default()
        if not alias_name and local_default and name == local_default[0]:
            print(
                f"Unknown alias '{name}' in {local_default[1]}. "
                "Use --list-aliases to see available profiles.",
                file=sys.stderr,
            )
        else:
            print(
                f"Unknown alias '{name}'. "
                "Use --list-aliases to see available profiles.",
                file=sys.stderr,
            )
        sys.exit(1)

    profile = aliases[name]
    source = profile.get("source")
    if source not in ("jira", "github", "linear"):
        print(
            f"Alias '{name}' has invalid source '{source}'. "
            "Must be 'jira', 'github', or 'linear'.",
            file=sys.stderr,
        )
        sys.exit(1)

    require_config_section(profile, source, name)

    return name, profile


def print_aliases(config: dict) -> None:
    aliases = config.get("aliases")
    if not aliases:
        print(f"No aliases configured in {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)

    effective_default = get_effective_default(config)
    for name, profile in aliases.items():
        source = profile.get("source", "?")
        suffix = "  (default)" if name == effective_default else ""
        print(f"{name}{suffix}  [{source}]")
