"""Alert service"""

import hashlib
from datetime import datetime
from typing import Optional

from app.repositories.alert_repository import AlertRepository


class AlertService:
    """Service for alert business logic"""

    def __init__(self, alert_repo: AlertRepository):
        self.alert_repo = alert_repo

    def calculate_fingerprint(
        self, source: str, rule_id: str, src_ip: Optional[str], dst_ip: Optional[str], timestamp: datetime
    ) -> str:
        """Calculate fingerprint for deduplication (rounded to minute)"""
        ts_rounded = timestamp.replace(second=0, microsecond=0)
        fingerprint_str = f"{source}:{rule_id}:{src_ip}:{dst_ip}:{ts_rounded}"
        return hashlib.md5(fingerprint_str.encode()).hexdigest()

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
    ):
        """Get alerts with filters"""
        return await self.alert_repo.get_alerts(
            skip=skip,
            limit=limit,
            severity=severity,
            status=status,
            source=source,
            src_ip=src_ip,
            date_from=date_from,
            date_to=date_to,
        )

    async def get_alert_detail(self, alert_id: int):
        """Get alert detail with enrichment and triage"""
        return await self.alert_repo.get_alert_by_id(alert_id)

    async def update_alert_status(self, alert_id: int, status: str, justification: str):
        """Update alert status with justification"""
        return await self.alert_repo.update_alert(alert_id, status=status)

    async def ingest_alert(self, alert_data: dict):
        """Ingest new alert from n8n"""
        # Calculate fingerprint
        fingerprint = self.calculate_fingerprint(
            source=alert_data["source"],
            rule_id=alert_data["rule_id"],
            src_ip=alert_data.get("src_ip"),
            dst_ip=alert_data.get("dst_ip"),
            timestamp=datetime.utcnow(),
        )

        alert_data["fingerprint"] = fingerprint
        alert_data["status"] = "pendiente"
        alert_data["received_at"] = datetime.utcnow()

        return await self.alert_repo.create_alert(alert_data)
