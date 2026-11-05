"""Metrics schemas"""

from pydantic import BaseModel


class MetricsSummary(BaseModel):
    """Summary metrics (KPIs)"""

    total_alerts: int
    critical_open_alerts: int
    mttt_minutes: float
    false_positive_rate: float


class TimeSeriesData(BaseModel):
    """Time series data point"""

    date: str
    alta: int
    media: int
    baja: int


class TopItem(BaseModel):
    """Top item (source IP or rule)"""

    name: str
    description: str | None = None
    count: int
