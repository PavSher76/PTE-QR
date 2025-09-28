"""
API v1 router configuration
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    admin,
    auth,
    documents,
    frontend,
    health,
    normocontrol,
    pdf,
    pdf_upload,
    qrcodes,
    settings,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(qrcodes.router, prefix="/qrcodes", tags=["qrcodes"])
api_router.include_router(pdf.router, prefix="/pdf", tags=["pdf"])
api_router.include_router(pdf_upload.router, prefix="/pdf", tags=["pdf-upload"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(normocontrol.router, prefix="/normocontrol", tags=["normocontrol"])
api_router.include_router(frontend.router, tags=["frontend"])
