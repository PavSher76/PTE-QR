"""
Document model
"""

import uuid
import enum
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class DocumentStatusEnum(str, enum.Enum):
    """Document status enumeration"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    RELEASED = "released"
    OBSOLETE = "obsolete"

class EnoviaStateEnum(str, enum.Enum):
    """ENOVIA state enumeration"""
    DRAFT = "Draft"
    IN_WORK = "In Work"
    RELEASED = "Released"
    OBSOLETE = "Obsolete"

class Document(Base):
    """
    Document model for storing document information
    """
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    enovia_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    document_type = Column(String(50), nullable=True)
    revision = Column(String(50), nullable=False)
    current_page = Column(Integer, nullable=True)
    business_status = Column(String(50), nullable=True)
    enovia_state = Column(String(50), nullable=True)
    is_actual = Column(Boolean, default=True, nullable=False)
    released_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    qr_codes = relationship("QRCode", back_populates="document", cascade="all, delete-orphan")
    creator = relationship("User", back_populates="created_documents")

    def __repr__(self):
        return f"<Document(id={self.id}, enovia_id={self.enovia_id}, revision={self.revision})>"