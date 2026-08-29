from abc import ABC, abstractmethod


class Issue(ABC):
    @abstractmethod
    def label(self) -> str:
        """Selection and display name."""

    @abstractmethod
    def branch(self) -> str:
        """Story or main branch name."""

    @abstractmethod
    def task_branch(self) -> str | None:
        """Task branch name, or None when not applicable."""

    @abstractmethod
    def commit_message(self) -> str | None:
        """Suggested commit message, or None when not applicable."""

    def note(self) -> str | None:
        """Optional extra line (e.g. Jira non-task warning)."""
        return None


class IssueSource(ABC):
    @abstractmethod
    def fetch_issues(self) -> list[Issue]:
        """Fetch assigned open work and map to Issue instances."""
