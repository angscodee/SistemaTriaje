"""Alert model"""

from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    external_id = Column(String(255), unique=True, nullable=False, index=True)
    source = Column(String(50), nullable=False, index=True)  # wazuh | opnsense
    rule_id = Column(String(100), nullable=False, index=True)
    rule_description = Column(Text)
    raw_payload = Column(JSONB, nullable=False)
    normalized = Column(JSONB, nullable=False)
    src_ip = Column(String(45), index=True)  # IPv4 or IPv6
    dst_ip = Column(String(45), index=True)
    agent_name = Column(String(255))
    severity_original = Column(String(20), index=True)
    fingerprint = Column(String(64), nullable=False, index=True)  # For deduplication
    status = Column(
        String(20),
        nullable=False,
        default="pendiente",
        index=True,
    )  # pendiente | en_triaje | triada | descartada | escalada
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    triaged_at = Column(DateTime)

    # Relationships
    enrichment_data = relationship("EnrichmentData", back_populates="alert", cascade="all, delete-orphan")
    triage_result = relationship("TriageResult", back_populates="alert", uselist=False)
    incidents = relationship("Incident", back_populates="alert")

    __table_args__ = (
        Index("idx_alert_fingerprint_time", "fingerprint", "received_at"),
        Index("idx_alert_status_severity", "status", "severity_original"),
    )
