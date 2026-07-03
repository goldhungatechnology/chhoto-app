import importlib

from src.shared.mediator.discover import auto_discover_listeners

# Load listeners so background tasks can dispatch events.
auto_discover_listeners("src.modules")

# Import background tasks so Dramatiq registers actors.
importlib.import_module("src.modules.auth.application.tasks.user_created_email_task")
importlib.import_module("src.modules.auth.application.tasks.forgot_password_email_task")
importlib.import_module(
    "src.modules.auth.application.tasks.resend_email_verification_task"
)

importlib.import_module(
    "src.modules.workforce.application.tasks.default_role_and_member_role_task"
)
