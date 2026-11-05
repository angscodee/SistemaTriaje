"""Alert schemas"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AlertOut(BaseModel):
    """Alert output schema"""

    id: int
    external_id: str
    source: str
    rule_id: str
    rule_description: Optional[str]
    src_ip: Optional[str]
    dst_ip: Optional[str]
    agent_name: Optional[str]
    severity_original: str
    status: str
    received_at: datetime
    triaged_at: Optional[datetime]

    class Config:
        from_attributes = True


class AlertDetail(BaseModel):
    """Alert detail with enrichment and triage"""

    id: int
    external_id: str
    source: str
    rule_id: str
    rule_description: Optional[str]
    raw_payload: dict
    normalized: dict
    src_ip: Optional[str]
    dst_ip: Optional[str]
    agent_name: Optional[str]
    severity_original: str
    fingerprint: str
    status: str
    received_at: datetime
    triaged_at: Optional[datetime]
    enrichment: list[dict] = Field(default_factory=list)
    triage: Optional[dict] = None

    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    """Alert update schema"""

    status: Optional[str] = None
    justification: str = Field(..., min_length=10, description="Justificación del cambio (mínimo 10 caracteres)")


class AlertIngest(BaseModel):
    """Alert ingestion schema (for n8n)"""

    external_id: str
    source: str
    rule_id: str
    rule_description: Optional[str]
    raw_payload: dict
    normalized: dict
    src_ip: Optional[str]
    dst_ip: Optional[str]
    agent_name: Optional[str]
    severity_original: str


class AlertListResponse(BaseModel):
    """Alert list response with pagination"""

    total: int
    page: int
    page_size: int
    pages: int
    items: list[AlertOut]
