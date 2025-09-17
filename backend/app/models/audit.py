"""
Audit log database models
"""

import enum
import uuid

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


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
    __table_args__ = {"schema": "pte_qr"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    table_name = Column(String(100), nullable=False)
    record_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String(20), nullable=False)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    changed_by = Column(
        UUID(as_uuid=True), ForeignKey("pte_qr.users.id"), nullable=True
    )
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
