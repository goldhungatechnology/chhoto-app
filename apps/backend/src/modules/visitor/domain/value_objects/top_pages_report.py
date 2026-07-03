from collections import defaultdict
from dataclasses import dataclass
from src.modules.visitor.domain.entities.visitor_page_visit_entity import (
    VisitorPageVisitEntity,
)


@dataclass(frozen=True)
class TopPageMetric:
    """Value object representing page view metrics for a single page URL."""

    url: str
    count: int
    percentage: float


@dataclass(frozen=True)
class TopPagesReport:
    """Value object representing top pages report metrics."""

    total_visitors: int
    pages: list[TopPageMetric]

    @classmethod
    def generate(
        cls,
        page_visits: list[VisitorPageVisitEntity],
        total_visitors: int,
        limit: int = 5,
    ) -> "TopPagesReport":
        """Generate a TopPagesReport from page visits and total visitor count."""
        if total_visitors == 0:
            return cls(total_visitors=0, pages=[])

        url_visitors: dict[str, set[int]] = defaultdict(set)
        for visit in page_visits:
            if visit.url:
                url_visitors[visit.url].add(visit.visitor_id)

        pages = [
            TopPageMetric(
                url=url,
                count=len(visitor_ids),
                percentage=round((len(visitor_ids) / total_visitors) * 100, 1),
            )
            for url, visitor_ids in url_visitors.items()
        ]

        pages.sort(key=lambda page: (-page.count, page.url))

        return cls(
            total_visitors=total_visitors,
            pages=pages[:limit],
        )

    def to_dict(self) -> dict:
        """Convert the report to a plain serialized dictionary."""
        return {
            "total": self.total_visitors,
            "pages": [
                {
                    "url": metric.url,
                    "count": metric.count,
                    "percentage": metric.percentage,
                }
                for metric in self.pages
            ],
        }
