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

    def story_issue(self) -> "Issue":
        """Story branch owner: self for stories, parent for tasks."""
        return self
