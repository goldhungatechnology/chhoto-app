import importlib
import pkgutil
from pathlib import Path

from src.shared.infrastructure.logger import logger
from src.shared.mediator.registry import registry


def auto_discover_listeners(modules_root: str = "src.modules") -> None:
    """
    Walk every sub-package under `modules_root` and import any module
    whose name ends with `_listener`.  The @listener decorator does the
    rest — no explicit importlib calls needed in create_app().
    """
    root_path = Path(modules_root.replace(".", "/"))
    if not root_path.exists():
        logger.warning("[ListenerRegistry] modules root %s not found", root_path)
        return

    for finder, module_name, _ in pkgutil.walk_packages(
        path=[str(root_path)],
        prefix=f"{modules_root}.",
        onerror=lambda name: logger.warning("Could not import %s", name),
    ):
        if module_name.endswith("_listener"):
            try:
                importlib.import_module(module_name)
                logger.warning("[ListenerRegistry] Imported %s", module_name)
            except Exception:
                logger.exception("[ListenerRegistry] Failed to import %s", module_name)

    registry.log_all()
