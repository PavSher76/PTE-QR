"""
QR Code related database models
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
import uuid


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
    __table_args__ = {"schema": "pte_qr"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(
        UUID(as_uuid=True), ForeignKey("pte_qr.documents.id"), nullable=False
    )
    doc_uid = Column(String(100), nullable=False)
    revision = Column(String(20), nullable=False)
    page = Column(Integer, nullable=False)
    qr_data = Column(Text, nullable=False)
    hmac_signature = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(
        UUID(as_uuid=True), ForeignKey("pte_qr.users.id"), nullable=True
    )

    # Relationships
    document = relationship("Document", back_populates="qr_codes")


class QRCodeGeneration(Base):
    """QR Code generation log"""

    __tablename__ = "qr_code_generations"
    __table_args__ = {"schema": "pte_qr"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("pte_qr.users.id"), nullable=True)
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
