from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class TrialIdentity(Base):
    __tablename__ = "trial_identities"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True)
    domain = Column(String(255), nullable=True, index=True)
    pixel_id = Column(String(64), nullable=True, index=True)
    email = Column(String(255), nullable=True)
    source = Column(String(32), nullable=False, default="signup")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
