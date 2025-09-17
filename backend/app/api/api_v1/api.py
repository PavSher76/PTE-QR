"""
API v1 router configuration
"""

from fastapi import APIRouter
from app.api.api_v1.endpoints import (
    documents,
    qrcodes,
    admin,
    health,
    frontend,
    auth,
    pdf,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(qrcodes.router, prefix="/qrcodes", tags=["qrcodes"])
api_router.include_router(pdf.router, prefix="/pdf", tags=["pdf"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(frontend.router, tags=["frontend"])
