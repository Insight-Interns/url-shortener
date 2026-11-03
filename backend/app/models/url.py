import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class URLMapping(Base):
    __tablename__ = "url_mappings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    short_code = Column(String(30), unique=True, nullable=False, index=True)
    original_url = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    creator = relationship("User", back_populates="urls")
    click_events = relationship("ClickEvent", back_populates="url_mapping", cascade="all, delete-orphan")

