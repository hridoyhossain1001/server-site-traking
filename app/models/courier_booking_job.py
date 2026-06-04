from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from app.database import Base


class CourierBookingJob(Base):
    """Durable courier provider booking request processed outside web requests."""

    __tablename__ = "courier_booking_jobs"
    __table_args__ = (
        UniqueConstraint("courier_order_id", name="uq_courier_booking_job_order"),
        Index("ix_courier_booking_jobs_claim", "status", "next_attempt_at", "created_at"),
        Index("ix_courier_booking_jobs_client_status", "client_id", "status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    pending_event_id = Column(Integer, ForeignKey("pending_events.id", ondelete="SET NULL"), nullable=True, index=True)
    courier_order_id = Column(Integer, ForeignKey("courier_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    request_payload = Column(JSON, nullable=False)
    status = Column(String(32), nullable=False, default="queued", index=True)
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=8)
    locked_at = Column(DateTime(timezone=True), nullable=True)
    locked_by = Column(String(255), nullable=True)
    next_attempt_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
