from datetime import datetime
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class ClickEvent(Base):
    __tablename__ = "click_events"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    url_mapping_id = Column(String(36), ForeignKey("url_mappings.id", ondelete="CASCADE"), nullable=False, index=True)
    clicked_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    ip_hash = Column(String(64), nullable=True, index=True)
    user_agent = Column(String(512), nullable=True)
    referrer = Column(String(2048), nullable=True)
    country_code = Column(String(2), nullable=True)
    device_type = Column(String(32), nullable=True)

    # Relationship back to url mapping
    url_mapping = relationship("URLMapping", back_populates="click_events")
