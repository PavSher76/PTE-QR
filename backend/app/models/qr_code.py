"""
QR Code related database models
"""

import enum
import uuid

from sqlalchemy import (
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
from sqlalchemy.types import CHAR, TypeDecorator

from app.core.database import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), storing as stringified hex values.
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


class QRCodeFormatEnum(str, enum.Enum):
    """QR Code format enumeration"""

    PNG = "PNG"
    SVG = "SVG"
    PDF = "PDF"


class QRCodeStyleEnum(str, enum.Enum):
    """QR Code style enumeration"""

    BLACK = "BLACK"
    INVERTED = "INVERTED"
    WITH_LABEL = "WITH_LABEL"


class QRCode(Base):
    """QR Code model"""

    __tablename__ = "qr_codes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(GUID(), ForeignKey("documents.id"), nullable=False)
    doc_uid = Column(String(100), nullable=False)
    revision = Column(String(20), nullable=False)
    page = Column(Integer, nullable=False)
    qr_data = Column(Text, nullable=False)
    hmac_signature = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(GUID(), ForeignKey("users.id"), nullable=True)

    # Relationships
    document = relationship("Document", back_populates="qr_codes")


class QRCodeGeneration(Base):
    """QR Code generation log"""

    __tablename__ = "qr_code_generations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    doc_uid = Column(String(100), nullable=False)
    revision = Column(String(20), nullable=False)
    pages = Column(Text, nullable=False)  # JSON array of page numbers
    style = Column(Enum(QRCodeStyleEnum), nullable=False)
    dpi = Column(Integer, default=300)
    mode = Column(String(50), default="qr-only")

    # Request info
    client_ip = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Response info
    qr_codes_count = Column(Integer, nullable=False)
    total_size_bytes = Column(Integer, nullable=True)

    # Timestamps
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    # user = relationship("User", back_populates="qr_generations")
