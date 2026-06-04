from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class PluginConnectSession(Base):
    __tablename__ = "plugin_connect_sessions"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    site_url = Column(String(512), nullable=False)
    site_host = Column(String(255), nullable=False, index=True)
    return_url = Column(String(1024), nullable=False)
    state = Column(String(128), nullable=False)
    code_hash = Column(String(64), unique=True, nullable=False, index=True)
    code_challenge = Column(String(96), nullable=False)
    created_ip = Column(String(64), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    used_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
