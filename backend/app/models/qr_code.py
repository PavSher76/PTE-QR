"""
QR Code model
"""

import uuid
import enum
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class QRCodeFormatEnum(str, enum.Enum):
    """QR Code format enumeration"""
    PNG = "png"
    SVG = "svg"
    PDF = "pdf"

class QRCodeStyleEnum(str, enum.Enum):
    """QR Code style enumeration"""
    STANDARD = "standard"
    ROUNDED = "rounded"
    SQUARE = "square"
    BLACK = "black"

class QRCode(Base):
    """
    QR Code model for storing QR code information
    """
    __tablename__ = "qr_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    enovia_id = Column(String(100), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    revision = Column(String(50), nullable=False)
    page_number = Column(Integer, nullable=False)
    qr_data = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    document = relationship("Document", back_populates="qr_codes")
    creator = relationship("User", back_populates="created_qr_codes")

    def __repr__(self):
        return f"<QRCode(id={self.id}, enovia_id={self.enovia_id}, page={self.page_number})>"