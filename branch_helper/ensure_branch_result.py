from dataclasses import dataclass


@dataclass(frozen=True)
class EnsureBranchResult:
    created: bool
    checked_out: bool
