"""
Document-related database models
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class DocumentStatusEnum(str, enum.Enum):
    """Business status enumeration"""
    APPROVED_FOR_CONSTRUCTION = "APPROVED_FOR_CONSTRUCTION"
    ACCEPTED_BY_CUSTOMER = "ACCEPTED_BY_CUSTOMER"
    CHANGES_INTRODUCED_GET_NEW = "CHANGES_INTRODUCED_GET_NEW"
    IN_WORK = "IN_WORK"


class EnoviaStateEnum(str, enum.Enum):
    """ENOVIA state enumeration"""
    RELEASED = "Released"
    AFC = "AFC"
    ACCEPTED = "Accepted"
    APPROVED = "Approved"
    OBSOLETE = "Obsolete"
    SUPERSEDED = "Superseded"
    IN_WORK = "In Work"
    FROZEN = "Frozen"


class Document(Base):
    """Document model"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    doc_uid = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    number = Column(String(100), nullable=True)
    enovia_id = Column(String(255), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    revisions = relationship("DocumentRevision", back_populates="document", cascade="all, delete-orphan")
    qr_codes = relationship("QRCode", back_populates="document", cascade="all, delete-orphan")


class DocumentRevision(Base):
    """Document revision model"""
    __tablename__ = "document_revisions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    revision = Column(String(10), nullable=False)  # A, B, C or 1, 2, 3
    enovia_state = Column(Enum(EnoviaStateEnum), nullable=False)
    business_status = Column(Enum(DocumentStatusEnum), nullable=False)
    
    # Metadata
    released_at = Column(DateTime(timezone=True), nullable=True)
    superseded_by = Column(String(10), nullable=True)
    last_modified = Column(DateTime(timezone=True), nullable=True)
    
    # ENOVIA specific
    enovia_revision_id = Column(String(255), nullable=True)
    maturity_state = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="revisions")
    status_checks = relationship("DocumentStatus", back_populates="revision")
    
    # Unique constraint
    __table_args__ = (
        {"extend_existing": True}
    )


class DocumentStatus(Base):
    """Document status check log"""
    __tablename__ = "document_status_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    revision_id = Column(Integer, ForeignKey("document_revisions.id"), nullable=False)
    page = Column(Integer, nullable=False)
    
    # Request info
    client_ip = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Response info
    is_actual = Column(Boolean, nullable=False)
    business_status = Column(Enum(DocumentStatusEnum), nullable=False)
    enovia_state = Column(Enum(EnoviaStateEnum), nullable=False)
    
    # Timestamps
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    revision = relationship("DocumentRevision", back_populates="status_checks")
    user = relationship("User", back_populates="status_checks")
