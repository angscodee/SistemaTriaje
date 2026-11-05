"""AuditLog model - Immutable audit trail"""

from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ts = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), index=True)  # Can be NULL for system actions
    role = Column(String(50))
    action = Column(String(100), nullable=False, index=True)
    resource = Column(String(100), nullable=False, index=True)
    method = Column(String(10))  # GET, POST, PUT, DELETE, etc.
    path = Column(String(500))
    status_code = Column(Integer, index=True)
    ip = Column(String(45))
    user_agent = Column(Text)
    request_id = Column(UUID(as_uuid=True), index=True)
    details = Column(JSONB)  # Additional context (before/after for changes, etc.)
    prev_hash = Column(String(64))  # Hash of previous record (blockchain-style)
    hash = Column(String(64), nullable=False)  # SHA-256 hash of this record

    __table_args__ = (
        Index("idx_audit_user_action", "user_id", "action"),
        Index("idx_audit_ts_action", "ts", "action"),
    )
