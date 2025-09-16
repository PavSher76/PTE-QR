"""
User and authentication related database models
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRoleEnum(str, enum.Enum):
    """User role enumeration"""
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    
    # Authentication
    hashed_password = Column(String(255), nullable=True)  # For local auth
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # External auth
    external_id = Column(String(255), nullable=True, index=True)  # ENOVIA user ID
    external_provider = Column(String(50), nullable=True)  # enovia, saml, oidc
    
    # Role
    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.USER)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    status_checks = relationship("DocumentStatus", back_populates="user")
    qr_generations = relationship("QRCodeGeneration", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
