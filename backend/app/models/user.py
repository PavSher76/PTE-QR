"""
User and authentication related database models
"""

import enum
import uuid

from app.core.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import CHAR, TypeDecorator


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


class UserRoleEnum(str, enum.Enum):
    """User role enumeration"""

    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"


# Association table for many-to-many relationship
user_roles_association = Table(
    "user_user_roles",
    Base.metadata,
    Column("user_id", GUID(), ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("user_roles.id"), primary_key=True),
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
    users = relationship(
        "User", secondary=user_roles_association, back_populates="roles"
    )


class User(Base):
    """User model"""

    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
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
    roles = relationship(
        "UserRole", secondary=user_roles_association, back_populates="users"
    )
    # qr_generations = relationship("QRCodeGeneration", back_populates="user")
    # qr_codes = relationship("QRCode", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
