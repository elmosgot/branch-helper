from dataclasses import dataclass


@dataclass(frozen=True)
class WorktreeEntry:
    path: str
    status_label: str
    is_staged: bool
    kind: str

    def display_suffix(self) -> str:
        return f"({self.kind})"
