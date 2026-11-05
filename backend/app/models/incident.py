"""Incident model"""

from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    alert_id = Column(BigInteger, ForeignKey("alerts.id", ondelete="SET NULL"), index=True)
    title = Column(String(500), nullable=False)
    severity = Column(String(20), nullable=False, index=True)  # alta | media | baja
    status = Column(
        String(20), nullable=False, default="abierto", index=True
    )  # abierto | en_progreso | resuelto | cerrado
    ticket_system = Column(String(50))  # osticket | redmine
    ticket_id = Column(String(100))
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime)

    # Relationships
    alert = relationship("Alert", back_populates="incidents")

    __table_args__ = (Index("idx_incident_status_severity", "status", "severity"),)
