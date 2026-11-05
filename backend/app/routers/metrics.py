"""Metrics router"""

from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.metrics_repository import MetricsRepository
from app.schemas.metrics import MetricsSummary, TimeSeriesData, TopItem
from app.services.metrics_service import MetricsService

router = APIRouter()


def get_metrics_service(db: AsyncSession = Depends(get_db)) -> MetricsService:
    """Dependency to get metrics service"""
    return MetricsService(MetricsRepository(db))


@router.get("/metrics/summary", response_model=MetricsSummary)
async def get_summary(
    metrics_service: MetricsService = Depends(get_metrics_service),
) -> MetricsSummary:
    """Get summary metrics (KPIs)"""
    return await metrics_service.get_summary()


@router.get("/metrics/time-series", response_model=List[TimeSeriesData])
async def get_time_series(
    days: int = Query(7, ge=1, le=90, description="Días de histórico"),
    metrics_service: MetricsService = Depends(get_metrics_service),
) -> List[TimeSeriesData]:
    """Get time series data (alerts by severity per day)"""
    date_from = datetime.utcnow() - timedelta(days=days)
    return await metrics_service.get_time_series(date_from)


@router.get("/metrics/top-sources", response_model=List[TopItem])
async def get_top_sources(
    limit: int = Query(10, ge=1, le=50, description="Número de resultados"),
    metrics_service: MetricsService = Depends(get_metrics_service),
) -> List[TopItem]:
    """Get top source IPs"""
    return await metrics_service.get_top_sources(limit)


@router.get("/metrics/top-rules", response_model=List[TopItem])
async def get_top_rules(
    limit: int = Query(10, ge=1, le=50, description="Número de resultados"),
    metrics_service: MetricsService = Depends(get_metrics_service),
) -> List[TopItem]:
    """Get top triggered rules"""
    return await metrics_service.get_top_rules(limit)
