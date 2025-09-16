"""
Audit log database models
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class AuditActionEnum(str, enum.Enum):
    """Audit action enumeration"""
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    QR_GENERATE = "QR_GENERATE"
    QR_VERIFY = "QR_VERIFY"
    DOCUMENT_STATUS = "DOCUMENT_STATUS"
    PDF_STAMP = "PDF_STAMP"


class AuditLog(Base):
    """Audit log model"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(Enum(AuditActionEnum), nullable=False)
    
    # Request info
    resource_type = Column(String(100), nullable=True)  # document, qr_code, user, etc.
    resource_id = Column(String(255), nullable=True)  # ID of the resource
    endpoint = Column(String(255), nullable=True)  # API endpoint
    method = Column(String(10), nullable=True)  # HTTP method
    client_ip = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Request/Response data
    request_data = Column(JSON, nullable=True)  # Request payload
    response_status = Column(Integer, nullable=True)  # HTTP status code
    response_data = Column(JSON, nullable=True)  # Response data (limited)
    
    # Additional context
    details = Column(Text, nullable=True)  # Additional details
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")