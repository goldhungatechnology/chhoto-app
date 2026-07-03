from src.modules.auth.infrastructure.session.user_session_reader_impl import (
    UserSessionReaderImpl,
    get_user_session_reader_impl,
)
from src.modules.auth.infrastructure.user.user_reader_impl import (
    UserReaderImpl,
    get_user_reader_impl,
)


def get_session_reader(session) -> UserSessionReaderImpl:
    """
    Factory that builds a UserSessionReaderImpl bound to the given
    request-scoped AsyncSession.
    """
    return get_user_session_reader_impl(session)


def get_user_reader(session) -> UserReaderImpl:
    """
    Factory that builds a UserReaderImpl bound to the given request-scoped
    AsyncSession.
    """
    return get_user_reader_impl(session)
