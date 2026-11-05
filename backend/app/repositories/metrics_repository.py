"""Metrics repository"""

from datetime import datetime
from typing import List, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.triage import TriageResult


class MetricsRepository:
    """Repository for metrics queries"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_total_alerts(self) -> int:
        """Get total number of alerts"""
        result = await self.db.execute(select(func.count(Alert.id)))
        return result.scalar() or 0

    async def get_critical_open_alerts(self) -> int:
        """Get count of critical open alerts"""
        result = await self.db.execute(
            select(func.count(Alert.id)).where(
                Alert.severity_original == "alta", Alert.status.in_(["pendiente", "en_triaje", "triada"])
            )
        )
        return result.scalar() or 0

    async def get_mttt_seconds(self) -> float:
        """Get Mean Time To Triage in seconds"""
        result = await self.db.execute(
            select(func.avg(func.extract("epoch", Alert.triaged_at - Alert.received_at))).where(
                Alert.triaged_at.is_not(None)
            )
        )
        avg_seconds = result.scalar()
        return float(avg_seconds) if avg_seconds else 0.0

    async def get_false_positive_rate(self) -> float:
        """Get false positive rate"""
        total_result = await self.db.execute(select(func.count(TriageResult.id)))
        total = total_result.scalar() or 0

        if total == 0:
            return 0.0

        fp_result = await self.db.execute(
            select(func.count(TriageResult.id)).where(TriageResult.verdict == "falso_positivo")
        )
        fp_count = fp_result.scalar() or 0

        return (fp_count / total) * 100

    async def get_time_series(self, date_from: datetime) -> List[Tuple[str, int, int, int]]:
        """Get alerts by severity per day"""
        query = (
            select(
                func.date(Alert.received_at).label("date"),
                func.count().filter(Alert.severity_original == "alta").label("alta"),
                func.count().filter(Alert.severity_original == "media").label("media"),
                func.count().filter(Alert.severity_original == "baja").label("baja"),
            )
            .where(Alert.received_at >= date_from)
            .group_by(func.date(Alert.received_at))
            .order_by(func.date(Alert.received_at))
        )

        result = await self.db.execute(query)
        return result.all()

    async def get_top_sources(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get top source IPs"""
        query = (
            select(Alert.src_ip, func.count(Alert.id).label("count"))
            .where(Alert.src_ip.is_not(None))
            .group_by(Alert.src_ip)
            .order_by(func.count(Alert.id).desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return result.all()

    async def get_top_rules(self, limit: int = 10) -> List[Tuple[str, str, int]]:
        """Get top triggered rules"""
        query = (
            select(Alert.rule_id, Alert.rule_description, func.count(Alert.id).label("count"))
            .group_by(Alert.rule_id, Alert.rule_description)
            .order_by(func.count(Alert.id).desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return result.all()
