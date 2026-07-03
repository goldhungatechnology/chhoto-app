from .adapter.dramatiq.dramatiq_background_task_manager import (
    DramatiqBackgroundTaskManager,
)

bgtask = DramatiqBackgroundTaskManager()

__all__ = ["bgtask"]
