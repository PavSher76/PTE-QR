"""
Audit and logging related database models
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class AuditActionEnum(str, enum.Enum):
    """Audit action enumeration"""
    QR_SCAN = "qr_scan"
    QR_GENERATE = "qr_generate"
    DOCUMENT_VIEW = "document_view"
    STATUS_CHECK = "status_check"
    LOGIN = "login"
    LOGOUT = "logout"
    ADMIN_ACTION = "admin_action"


class AuditLog(Base):
    """Audit log model"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Action details
    action = Column(Enum(AuditActionEnum), nullable=False)
    resource_type = Column(String(50), nullable=True)  # document, qr_code, user
    resource_id = Column(String(255), nullable=True)
    
    # Request details
    client_ip = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(255), nullable=True)
    
    # Additional data
    details = Column(Text, nullable=True)  # JSON with additional context
    result = Column(String(20), nullable=True)  # success, failure, error
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
