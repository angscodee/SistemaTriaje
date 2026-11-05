"""TriageResult model"""

from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class TriageResult(Base):
    __tablename__ = "triage_results"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    alert_id = Column(BigInteger, ForeignKey("alerts.id", ondelete="CASCADE"), unique=True, nullable=False)
    severity = Column(String(20), nullable=False, index=True)  # alta | media | baja
    verdict = Column(
        String(30), nullable=False, index=True
    )  # verdadero_positivo | falso_positivo | requiere_revision
    confidence = Column(Float, nullable=False)  # 0.0 - 1.0
    summary = Column(Text, nullable=False)
    recommended_actions = Column(JSONB, nullable=False)
    mitre_techniques = Column(JSONB, nullable=False)
    indicators = Column(JSONB, nullable=False)
    enrichment = Column(JSONB, nullable=False)
    llm_model = Column(String(100), nullable=False)  # ollama:llama3 | openai:gpt-4 | fallback_rules
    latency_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    alert = relationship("Alert", back_populates="triage_result")

    __table_args__ = (Index("idx_triage_severity_verdict", "severity", "verdict"),)
