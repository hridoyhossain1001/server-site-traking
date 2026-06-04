from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.sql import func

from app.database import Base


class SiteBinding(Base):
    __tablename__ = "site_bindings"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    site_host = Column(String(255), nullable=False, index=True)
    root_domain = Column(String(255), nullable=False, index=True)
    installation_id = Column(String(128), nullable=True, index=True)
    status = Column(String(32), nullable=False, default="active", index=True)
    source = Column(String(32), nullable=False, default="plugin_connect")
    connected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_event_at = Column(DateTime(timezone=True), nullable=True, index=True)
    released_at = Column(DateTime(timezone=True), nullable=True, index=True)
    released_by = Column(String(128), nullable=True)
    release_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_site_bindings_root_status", "root_domain", "status"),
        Index("ix_site_bindings_site_status", "site_host", "status"),
        Index("ix_site_bindings_client_status", "client_id", "status"),
        Index(
            "uq_site_bindings_active_root_domain",
            "root_domain",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
    )
