"""
Pydantic schemas for API requests and responses
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models.document import DocumentStatusEnum, EnoviaStateEnum
from app.models.qr_code import QRCodeFormatEnum, QRCodeStyleEnum
from app.models.user import UserRoleEnum
from pydantic import BaseModel, Field


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration"""

    class Config:
        from_attributes = True


# Document schemas
class DocumentBase(BaseSchema):
    doc_uid: str = Field(..., description="ENOVIA DocumentID")
    title: str = Field(..., description="Document title")
    number: Optional[str] = Field(None, description="Document number")
    enovia_id: Optional[str] = Field(None, description="ENOVIA internal ID")


class DocumentCreate(DocumentBase):
    pass


class Document(DocumentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# Status response schema
class StatusResponse(BaseSchema):
    doc_uid: str
    revision: str
    page: int
    business_status: DocumentStatusEnum
    enovia_state: EnoviaStateEnum
    is_actual: bool
    released_at: Optional[datetime] = None
    superseded_by: Optional[str] = None
    links: Dict[str, Optional[str]] = Field(default_factory=dict)


# QR Code schemas
class QRCodeRequest(BaseSchema):
    doc_uid: str = Field(..., description="Document UID")
    revision: str = Field(..., description="Revision")
    pages: List[int] = Field(..., description="List of page numbers", min_items=1)
    style: QRCodeStyleEnum = Field(
        default=QRCodeStyleEnum.BLACK, description="QR style"
    )
    dpi: int = Field(default=300, ge=96, le=1200, description="DPI for QR generation")
    mode: str = Field(
        default="images", description="Generation mode: images or pdf-stamp"
    )


class QRCodeItem(BaseSchema):
    page: int
    format: QRCodeFormatEnum
    data_base64: str = Field(..., description="Base64 encoded QR code data")
    url: str = Field(..., description="URL encoded in QR code")


class QRCodeResponse(BaseSchema):
    doc_uid: str
    revision: str
    items: List[QRCodeItem]


# Status mapping schemas
class StatusMappingItem(BaseSchema):
    business_status: DocumentStatusEnum
    color: str = Field(..., description="Display color (hex code)")
    action_label: str = Field(..., description="Action button label")


class StatusMapping(BaseSchema):
    __root__: Dict[str, StatusMappingItem]


# User schemas
class UserBase(BaseSchema):
    username: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, description="Full name")
    role: UserRoleEnum = Field(default=UserRoleEnum.USER)


class UserCreate(UserBase):
    password: Optional[str] = Field(
        None, min_length=8, description="Password for local auth"
    )


class UserUpdate(BaseSchema):
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRoleEnum] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


# Authentication schemas
class Token(BaseSchema):
    access_token: str
    token_type: str = "bearer"


class TokenResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    user: User


class TokenData(BaseSchema):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[UserRoleEnum] = None


class UserResponse(BaseSchema):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: UserRoleEnum
    is_active: bool


# Health check schema
class HealthResponse(BaseSchema):
    status: str
    timestamp: float
    database: Optional[str] = None
    redis: Optional[str] = None
    enovia: Optional[str] = None


# Error schemas
class ErrorResponse(BaseSchema):
    detail: str
    error_code: Optional[str] = None
    request_id: Optional[str] = None


# Audit log schemas
class AuditLogBase(BaseSchema):
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    result: Optional[str] = None


class AuditLog(AuditLogBase):
    id: int
    user_id: Optional[int] = None
    client_ip: Optional[str] = None
    created_at: datetime
