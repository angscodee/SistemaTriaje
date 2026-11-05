"""Metrics service"""

from datetime import datetime
from typing import List

from app.repositories.metrics_repository import MetricsRepository
from app.schemas.metrics import MetricsSummary, TimeSeriesData, TopItem


class MetricsService:
    """Service for metrics business logic"""

    def __init__(self, metrics_repo: MetricsRepository):
        self.metrics_repo = metrics_repo

    async def get_summary(self) -> MetricsSummary:
        """Get summary metrics"""
        total_alerts = await self.metrics_repo.get_total_alerts()
        critical_open = await self.metrics_repo.get_critical_open_alerts()
        mttt_seconds = await self.metrics_repo.get_mttt_seconds()
        fp_rate = await self.metrics_repo.get_false_positive_rate()

        return MetricsSummary(
            total_alerts=total_alerts,
            critical_open_alerts=critical_open,
            mttt_minutes=mttt_seconds / 60.0 if mttt_seconds > 0 else 0.0,
            false_positive_rate=round(fp_rate, 2),
        )

    async def get_time_series(self, date_from: datetime) -> List[TimeSeriesData]:
        """Get time series data"""
        data = await self.metrics_repo.get_time_series(date_from)

        return [
            TimeSeriesData(
                date=str(row[0]),
                alta=row[1],
                media=row[2],
                baja=row[3],
            )
            for row in data
        ]

    async def get_top_sources(self, limit: int) -> List[TopItem]:
        """Get top source IPs"""
        data = await self.metrics_repo.get_top_sources(limit)

        return [TopItem(name=row[0], count=row[1]) for row in data]

    async def get_top_rules(self, limit: int) -> List[TopItem]:
        """Get top rules"""
        data = await self.metrics_repo.get_top_rules(limit)

        return [TopItem(name=row[0], description=row[1], count=row[2]) for row in data]
