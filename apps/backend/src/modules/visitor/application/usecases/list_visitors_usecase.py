from collections import defaultdict

import user_agents

from src.modules.visitor.domain.repositories.visitor_page_visit_repository import (
    IVisitorPageVisitRepository,
)
from src.modules.visitor.domain.repositories.visitor_repository import (
    IVisitorRepository,
)
from src.modules.visitor.domain.repositories.visitor_session_repository import (
    IVisitorSessionRepository,
)


class ListVisitorsUseCase:
    """
    Returns all registered visitors for an organization, read from the database,
    enriched with details from their latest session (current page, device, browser,
    IP, active duration, and visit count).
    """

    def __init__(
        self,
        visitor_repository: IVisitorRepository,
        visitor_session_repository: IVisitorSessionRepository,
        visitor_page_visit_repository: IVisitorPageVisitRepository,
    ):
        self.visitor_repository = visitor_repository
        self.visitor_session_repository = visitor_session_repository
        self.visitor_page_visit_repository = visitor_page_visit_repository

    async def execute(self, organization_id: int) -> list[dict]:
        """List all visitors for the organization, enriched with latest session data."""
        visitors = await self.visitor_repository.filter(organization_id=organization_id)
        if not visitors:
            return []

        visitor_ids = [visitor.id for visitor in visitors]

        all_sessions = await self.visitor_session_repository.filter(
            visitor_id__in=visitor_ids
        )

        sessions_by_visitor = defaultdict(list)
        for session in all_sessions:
            sessions_by_visitor[session.visitor_id].append(session)

        latest_sessions = {}
        for visitor_id, sessions in sessions_by_visitor.items():
            latest_session = (
                max(sessions, key=lambda session: session.started_at)
                if sessions
                else None
            )
            if latest_session:
                latest_sessions[visitor_id] = latest_session

        latest_session_ids = [session.id for session in latest_sessions.values()]

        page_visits_by_session = defaultdict(list)
        if latest_session_ids:
            all_page_visits = await self.visitor_page_visit_repository.filter(
                session_id__in=latest_session_ids
            )
            for visit in all_page_visits:
                page_visits_by_session[visit.session_id].append(visit)

        enriched_visitors = []
        for visitor in visitors:
            visitor_sessions = sessions_by_visitor.get(visitor.id, [])
            latest_session = latest_sessions.get(visitor.id)

            current_page = None
            device = None
            browser = None
            ip_address = None

            active_duration = sum(
                int((session.ended_at - session.started_at).total_seconds())
                for session in visitor_sessions
                if session.is_ended() and session.ended_at
            )

            if latest_session:
                ip_address = latest_session.ip_address
                device, browser = self._parse_user_agent(latest_session.user_agent)

                session_visits = page_visits_by_session.get(latest_session.id, [])
                if session_visits:
                    last_visit = max(session_visits, key=lambda pv: pv.entered_at)
                    current_page = last_visit.url

            enriched_visitors.append(
                {
                    "visitor": visitor,
                    "current_page": current_page,
                    "device": device,
                    "browser": browser,
                    "ip_address": ip_address,
                    "active_duration": max(0, active_duration),
                }
            )

        return enriched_visitors

    def _parse_user_agent(
        self, user_agent: str | None
    ) -> tuple[str | None, str | None]:
        """Parses user agent string to extract device and browser family info."""
        if not user_agent or user_agent == "unknown":
            return None, None
        try:
            ua = user_agents.parse(user_agent)
            device = ua.device.family
            browser = f"{ua.browser.family} {ua.browser.version_string}"
            return device, browser
        except Exception:
            return None, None
