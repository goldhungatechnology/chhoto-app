from abc import ABC, abstractmethod


class TaskInterface(ABC):
    """
    Interface for a background task.
    """

    @abstractmethod
    def queue(self, *args, **kwargs):
        """Queue the task for execution."""

    @abstractmethod
    def queue_with_options(self, task_options: dict | None = None, *args, **kwargs):
        """Queue the task with broker/middleware options."""


class BackgroundTaskManagerInterface(ABC):
    """
    Interface for managing background tasks.
    """

    @abstractmethod
    def add_task(self, task_callable, *args, **kwargs) -> TaskInterface:
        """Add a background task to be executed."""

    @abstractmethod
    def list_tasks(self):
        """List all scheduled background tasks."""
