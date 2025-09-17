"""
Document-related database models
"""

import enum
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import CHAR, TypeDecorator

from app.core.database import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), storing as
    stringified hex values.
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            else:
                return value


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

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    doc_uid = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    document_type = Column(String(50), nullable=True)
    current_revision = Column(String(20), nullable=True)
    current_page = Column(Integer, nullable=True)
    business_status = Column(String(50), nullable=True)
    enovia_state = Column(String(50), nullable=True)
    is_actual = Column(Boolean, default=True)
    released_at = Column(DateTime(timezone=True), nullable=True)
    superseded_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(GUID(), ForeignKey("users.id"), nullable=True)
    updated_by = Column(GUID(), ForeignKey("users.id"), nullable=True)

    # Relationships
    qr_codes = relationship(
        "QRCode", back_populates="document", cascade="all, delete-orphan"
    )
