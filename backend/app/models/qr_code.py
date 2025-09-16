"""
QR Code related database models
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class QRCodeFormatEnum(str, enum.Enum):
    """QR Code format enumeration"""
    PNG = "png"
    SVG = "svg"
    PDF = "pdf"


class QRCodeStyleEnum(str, enum.Enum):
    """QR Code style enumeration"""
    BLACK = "black"
    INVERTED = "inverted"
    WITH_LABEL = "with_label"


class QRCode(Base):
    """QR Code model"""
    __tablename__ = "qr_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    page = Column(Integer, nullable=False)
    revision = Column(String(10), nullable=False)
    
    # QR Code data
    url = Column(Text, nullable=False)  # Full URL with signature
    signature = Column(String(255), nullable=False)  # HMAC signature
    timestamp = Column(Integer, nullable=False)  # Unix timestamp
    
    # Generation metadata
    format = Column(Enum(QRCodeFormatEnum), nullable=False)
    style = Column(Enum(QRCodeStyleEnum), nullable=False)
    dpi = Column(Integer, nullable=False, default=300)
    size_mm = Column(Integer, nullable=False, default=35)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="qr_codes")
    generation = relationship("QRCodeGeneration", back_populates="qr_codes")


class QRCodeGeneration(Base):
    """QR Code generation batch"""
    __tablename__ = "qr_code_generations"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    revision = Column(String(10), nullable=False)
    
    # Generation parameters
    pages = Column(Text, nullable=False)  # JSON array of page numbers
    style = Column(Enum(QRCodeStyleEnum), nullable=False)
    dpi = Column(Integer, nullable=False, default=300)
    mode = Column(String(20), nullable=False, default="images")  # images or pdf-stamp
    
    # Generation metadata
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    generation_reason = Column(String(255), nullable=True)
    
    # Status
    status = Column(String(20), nullable=False, default="completed")  # pending, completed, failed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    qr_codes = relationship("QRCode", back_populates="generation")
    user = relationship("User", back_populates="qr_generations")
