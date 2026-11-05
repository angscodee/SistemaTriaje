"""EnrichmentData model"""

from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class EnrichmentData(Base):
    __tablename__ = "enrichment_data"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    alert_id = Column(BigInteger, ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)  # virustotal | abuseipdb | geoip
    indicator = Column(String(255), nullable=False, index=True)
    result = Column(JSONB, nullable=False)
    score = Column(Float)  # Normalized score if applicable
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    alert = relationship("Alert", back_populates="enrichment_data")

    __table_args__ = (Index("idx_enrichment_alert_provider", "alert_id", "provider"),)
