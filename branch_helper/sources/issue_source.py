from abc import ABC, abstractmethod

from branch_helper.sources.issue import Issue


class IssueSource(ABC):
    @abstractmethod
    def fetch_issues(self) -> list[Issue]:
        """Fetch assigned open work and map to Issue instances."""
