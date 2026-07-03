from dataclasses import asdict, dataclass
import user_agents


def parse_user_agent(user_agent: str | None) -> tuple[str | None, str | None]:
    """Parse a user agent string to extract device and browser family."""
    if not user_agent or user_agent == "unknown":
        return None, None
    try:
        ua = user_agents.parse(user_agent)
        device = ua.device.family
        browser = f"{ua.browser.family} {ua.browser.version_string}"
        return device, browser
    except Exception:
        return None, None


@dataclass(frozen=True)
class VisitorPresence:
    """
    Immutable real-time presence snapshot for a visitor. This is the unit stored
    in Redis and pushed to agent dashboards. It deliberately carries only the
    public visitor uuid (never the internal numeric id is exposed to clients,
    though ``visitor_id`` is kept for server-side routing).
    """

    organization_id: int
    visitor_id: int
    visitor_uuid: str
    session_uuid: str
    status: str
    last_seen: str  # ISO-8601 timestamp
    page: str | None = None
    name: str | None = None
    email: str | None = None
    phone: str | None = None

    # Enriched fields for the frontend visitor list
    external_id: str | None = None
    visit_count: int = 1
    is_identified: bool = False
    device: str | None = None
    browser: str | None = None
    ip_address: str | None = None
    active_duration: int = 0

    def to_dict(self) -> dict:
        """Serialize to a plain dict (safe for JSON / cache storage)."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "VisitorPresence":
        """Rehydrate a presence snapshot from a stored dict."""
        return cls(
            organization_id=int(data["organization_id"]),
            visitor_id=int(data["visitor_id"]),
            visitor_uuid=data["visitor_uuid"],
            session_uuid=data["session_uuid"],
            status=data["status"],
            last_seen=data["last_seen"],
            page=data.get("page"),
            name=data.get("name"),
            email=data.get("email"),
            phone=data.get("phone"),
            external_id=data.get("external_id"),
            visit_count=data.get("visit_count", 1),
            is_identified=data.get("is_identified", False),
            device=data.get("device"),
            browser=data.get("browser"),
            ip_address=data.get("ip_address"),
            active_duration=data.get("active_duration", 0),
        )
