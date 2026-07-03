class VisitorCacheKeys:
    """
    Collection of Redis key builders for visitor real-time presence.
    """

    # Per-organization presence keys live under a common prefix so they can be
    # enumerated with a single SCAN pattern for the agent dashboard.
    _PRESENCE_PREFIX = "visitor:presence"
    _SESSION_INDEX_PREFIX = "visitor:session_index"

    @classmethod
    def presence_key(cls, organization_id: int, visitor_id: int) -> str:
        """presence:{org}:{visitor}"""
        return f"{cls._PRESENCE_PREFIX}:{organization_id}:{visitor_id}"

    @classmethod
    def presence_scan_pattern(cls, organization_id: int) -> str:
        """Glob matching every presence key for an organization."""
        return f"{cls._PRESENCE_PREFIX}:{organization_id}:*"

    @classmethod
    def session_index_key(cls, session_uuid: str) -> str:
        """session_index:{session_uuid} -> {org_id, visitor_id}"""
        return f"{cls._SESSION_INDEX_PREFIX}:{session_uuid}"
