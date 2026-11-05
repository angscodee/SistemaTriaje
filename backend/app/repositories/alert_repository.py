"""Alert repository"""

from datetime import datetime
from typing import Optional
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.alert import Alert
from app.models.enrichment import EnrichmentData
from app.models.triage import TriageResult


class AlertRepository:
    """Repository for alert operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_alerts(
        self,
        skip: int = 0,
        limit: int = 100,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        source: Optional[str] = None,
        src_ip: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> tuple[list[Alert], int]:
        """Get alerts with filters and pagination"""
        query = select(Alert)

        # Apply filters
        if severity:
            query = query.where(Alert.severity_original == severity)
        if status:
            query = query.where(Alert.status == status)
        if source:
            query = query.where(Alert.source == source)
        if src_ip:
            query = query.where(Alert.src_ip == src_ip)
        if date_from:
            query = query.where(Alert.received_at >= date_from)
        if date_to:
            query = query.where(Alert.received_at <= date_to)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and order
        query = query.order_by(desc(Alert.received_at)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        alerts = result.scalars().all()

        return list(alerts), total

    async def get_alert_by_id(self, alert_id: int) -> Optional[Alert]:
        """Get alert by ID with enrichment and triage"""
        query = (
            select(Alert)
            .where(Alert.id == alert_id)
            .options(selectinload(Alert.enrichment_data), selectinload(Alert.triage_result))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_alert(self, alert_data: dict) -> Alert:
        """Create new alert"""
        alert = Alert(**alert_data)
        self.db.add(alert)
        await self.db.flush()
        await self.db.refresh(alert)
        return alert

    async def update_alert(self, alert_id: int, **kwargs) -> Optional[Alert]:
        """Update alert"""
        query = select(Alert).where(Alert.id == alert_id)
        result = await self.db.execute(query)
        alert = result.scalar_one_or_none()

        if not alert:
            return None

        for key, value in kwargs.items():
            setattr(alert, key, value)

        await self.db.flush()
        await self.db.refresh(alert)
        return alert
