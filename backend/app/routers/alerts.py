"""Alerts router"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.alert_repository import AlertRepository
from app.schemas.alert import AlertDetail, AlertIngest, AlertListResponse, AlertOut, AlertUpdate
from app.services.alert_service import AlertService

router = APIRouter()


def get_alert_service(db: AsyncSession = Depends(get_db)) -> AlertService:
    """Dependency to get alert service"""
    return AlertService(AlertRepository(db))


@router.get("/alerts", response_model=AlertListResponse)
async def get_alerts(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Elementos por página"),
    severity: Optional[str] = Query(None, description="Filtrar por severidad"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    source: Optional[str] = Query(None, description="Filtrar por fuente"),
    src_ip: Optional[str] = Query(None, description="Filtrar por IP origen"),
    date_from: Optional[datetime] = Query(None, description="Fecha desde"),
    date_to: Optional[datetime] = Query(None, description="Fecha hasta"),
    alert_service: AlertService = Depends(get_alert_service),
) -> AlertListResponse:
    """Get alerts with filters and pagination"""
    skip = (page - 1) * page_size

    alerts, total = await alert_service.get_alerts(
        skip=skip,
        limit=page_size,
        severity=severity,
        status=status,
        source=source,
        src_ip=src_ip,
        date_from=date_from,
        date_to=date_to,
    )

    pages = (total + page_size - 1) // page_size if total > 0 else 0

    return AlertListResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        items=[AlertOut.model_validate(alert) for alert in alerts],
    )


@router.get("/alerts/{alert_id}", response_model=AlertDetail)
async def get_alert_detail(
    alert_id: int,
    alert_service: AlertService = Depends(get_alert_service),
) -> AlertDetail:
    """Get alert detail with enrichment and triage"""
    alert = await alert_service.get_alert_detail(alert_id)

    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerta no encontrada")

    # Build enrichment list
    enrichment = [
        {
            "provider": e.provider,
            "indicator": e.indicator,
            "result": e.result,
            "score": e.score,
            "fetched_at": e.fetched_at,
        }
        for e in alert.enrichment_data
    ]

    # Build triage dict
    triage = None
    if alert.triage_result:
        t = alert.triage_result
        triage = {
            "severity": t.severity,
            "verdict": t.verdict,
            "confidence": t.confidence,
            "summary": t.summary,
            "recommended_actions": t.recommended_actions,
            "mitre_techniques": t.mitre_techniques,
            "indicators": t.indicators,
            "enrichment": t.enrichment,
            "llm_model": t.llm_model,
            "latency_ms": t.latency_ms,
            "created_at": t.created_at,
        }

    return AlertDetail(
        id=alert.id,
        external_id=alert.external_id,
        source=alert.source,
        rule_id=alert.rule_id,
        rule_description=alert.rule_description,
        raw_payload=alert.raw_payload,
        normalized=alert.normalized,
        src_ip=alert.src_ip,
        dst_ip=alert.dst_ip,
        agent_name=alert.agent_name,
        severity_original=alert.severity_original,
        fingerprint=alert.fingerprint,
        status=alert.status,
        received_at=alert.received_at,
        triaged_at=alert.triaged_at,
        enrichment=enrichment,
        triage=triage,
    )


@router.patch("/alerts/{alert_id}", response_model=AlertOut)
async def update_alert(
    alert_id: int,
    update: AlertUpdate,
    alert_service: AlertService = Depends(get_alert_service),
) -> AlertOut:
    """Update alert status with justification"""
    alert = await alert_service.update_alert_status(alert_id, update.status, update.justification)

    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerta no encontrada")

    return AlertOut.model_validate(alert)


@router.post("/alerts/ingest", response_model=AlertOut, status_code=status.HTTP_201_CREATED)
async def ingest_alert(
    alert_data: AlertIngest,
    alert_service: AlertService = Depends(get_alert_service),
) -> AlertOut:
    """Ingest alert from n8n (requires service API key)"""
    # TODO: Add API key validation
    alert = await alert_service.ingest_alert(alert_data.model_dump())
    return AlertOut.model_validate(alert)
