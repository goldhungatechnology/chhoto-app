class AuthCacheKeys:
    """
    collection of auth cache keys
    """

    @staticmethod
    def get_user_session_key(session_uuid: str) -> str:
        """
        get user session key
        """
        return f"auth:user_session:{session_uuid}"

    @staticmethod
    def get_user_cache_key(user_id: int) -> str:
        """
        get user cache key
        """
        return f"auth:user:{user_id}"

    @staticmethod
    def get_user_last_seen_key(user_id: int) -> str:
        """
        get user last seen key
        """
        return f"auth:user:{user_id}:last_seen"
