"""
User and authentication related database models
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRoleEnum(str, enum.Enum):
    """User role enumeration"""
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"


# Association table for many-to-many relationship
user_roles_association = Table(
    'user_user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('user_roles.id'), primary_key=True)
)


class UserRole(Base):
    """User role model"""
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(Text, nullable=True)  # JSON string of permissions
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", secondary=user_roles_association, back_populates="roles")


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
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    roles = relationship("UserRole", secondary=user_roles_association, back_populates="users")
    status_checks = relationship("DocumentStatus", back_populates="user")
    # qr_generations = relationship("QRCodeGeneration", back_populates="user")
    # qr_codes = relationship("QRCode", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
