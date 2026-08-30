from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LocalSettings:
    path: Path
    alias: str | None = None
    base_branch: str | None = None
