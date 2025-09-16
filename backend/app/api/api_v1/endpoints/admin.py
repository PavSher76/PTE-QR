"""
Admin endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import structlog
import time

from app.core.database import get_db
from app.services.metrics_service import metrics_service
from app.services.cache_service import cache_service
from app.models.user import User, UserRole
from app.models.document import Document, DocumentRevision, DocumentStatus
from app.models.qr_code import QRCode

router = APIRouter()
logger = structlog.get_logger()


@router.get("/stats")
async def get_system_stats(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get system statistics
    """
    start_time = time.time()
    
    try:
        # Get document statistics
        total_documents = db.query(func.count(Document.id)).scalar() or 0
        total_revisions = db.query(func.count(DocumentRevision.id)).scalar() or 0
        total_status_checks = db.query(func.count(DocumentStatus.id)).scalar() or 0
        
        # Get QR code statistics
        total_qr_codes = db.query(func.count(QRCode.id)).scalar() or 0
        
        # Get user statistics
        total_users = db.query(func.count(User.id)).scalar() or 0
        active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
        
        # Get recent activity
        recent_status_checks = db.query(DocumentStatus).order_by(desc(DocumentStatus.checked_at)).limit(10).all()
        
        # Get cache statistics
        cache_health = await cache_service.health_check()
        
        # Get system metrics
        system_metrics = metrics_service.get_health_metrics()
        
        duration = time.time() - start_time
        metrics_service.record_api_request("GET", "/admin/stats", 200, duration)
        
        return {
            "documents": {
                "total": total_documents,
                "revisions": total_revisions,
                "status_checks": total_status_checks
            },
            "qr_codes": {
                "total": total_qr_codes
            },
            "users": {
                "total": total_users,
                "active": active_users
            },
            "system": {
                "uptime_seconds": system_metrics["uptime_seconds"],
                "total_requests": system_metrics["total_requests"],
                "cpu_usage_percent": system_metrics["cpu_usage_percent"],
                "memory_usage_percent": system_metrics["memory_usage_percent"],
                "disk_usage_percent": system_metrics["disk_usage_percent"]
            },
            "cache": cache_health,
            "recent_activity": [
                {
                    "type": "status_check",
                    "doc_uid": check.revision.document.doc_uid,
                    "revision": check.revision.revision,
                    "page": check.page,
                    "is_actual": check.is_actual,
                    "checked_at": check.checked_at.isoformat() if check.checked_at else None
                }
                for check in recent_status_checks
            ]
        }
        
    except Exception as e:
        duration = time.time() - start_time
        metrics_service.record_api_request("GET", "/admin/stats", 500, duration)
        
        logger.error("Failed to get system stats", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/users")
async def get_users(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all users with pagination
    """
    start_time = time.time()
    
    try:
        # Get users with pagination
        users = db.query(User).offset(skip).limit(limit).all()
        total_users = db.query(func.count(User.id)).scalar() or 0
        
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "roles": [role.name for role in user.roles],
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None
            })
        
        duration = time.time() - start_time
        metrics_service.record_api_request("GET", "/admin/users", 200, duration)
        
        return {
            "users": user_list,
            "total": total_users,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        duration = time.time() - start_time
        metrics_service.record_api_request("GET", "/admin/users", 500, duration)
        
        logger.error("Failed to get users", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get specific user by ID
    """
    start_time = time.time()
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        duration = time.time() - start_time
        metrics_service.record_api_request("GET", f"/admin/users/{user_id}", 200, duration)
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": [role.name for role in user.roles],
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
        
    except HTTPException:
        duration = time.time() - start_time
        metrics_service.record_api_request("GET", f"/admin/users/{user_id}", 404, duration)
        raise
    except Exception as e:
        duration = time.time() - start_time
        metrics_service.record_api_request("GET", f"/admin/users/{user_id}", 500, duration)
        
        logger.error("Failed to get user", user_id=user_id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Activate user account
    """
    start_time = time.time()
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.is_active = True
        db.commit()
        
        duration = time.time() - start_time
        metrics_service.record_api_request("PUT", f"/admin/users/{user_id}/activate", 200, duration)
        
        logger.info("User activated", user_id=user_id, username=user.username)
        
        return {"message": "User activated successfully"}
        
    except HTTPException:
        duration = time.time() - start_time
        metrics_service.record_api_request("PUT", f"/admin/users/{user_id}/activate", 404, duration)
        raise
    except Exception as e:
        duration = time.time() - start_time
        metrics_service.record_api_request("PUT", f"/admin/users/{user_id}/activate", 500, duration)
        
        logger.error("Failed to activate user", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Deactivate user account
    """
    start_time = time.time()
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.is_active = False
        db.commit()
        
        duration = time.time() - start_time
        metrics_service.record_api_request("PUT", f"/admin/users/{user_id}/deactivate", 200, duration)
        
        logger.info("User deactivated", user_id=user_id, username=user.username)
        
        return {"message": "User deactivated successfully"}
        
    except HTTPException:
        duration = time.time() - start_time
        metrics_service.record_api_request("PUT", f"/admin/users/{user_id}/deactivate", 404, duration)
        raise
    except Exception as e:
        duration = time.time() - start_time
        metrics_service.record_api_request("PUT", f"/admin/users/{user_id}/deactivate", 500, duration)
        
        logger.error("Failed to deactivate user", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/cache")
async def clear_cache(
    request: Request,
    pattern: str = "*"
):
    """
    Clear cache
    """
    start_time = time.time()
    
    try:
        deleted_count = await cache_service.clear_pattern(pattern)
        
        duration = time.time() - start_time
        metrics_service.record_api_request("DELETE", "/admin/cache", 200, duration)
        
        logger.info("Cache cleared", pattern=pattern, deleted_count=deleted_count)
        
        return {
            "message": "Cache cleared successfully",
            "deleted_keys": deleted_count,
            "pattern": pattern
        }
        
    except Exception as e:
        duration = time.time() - start_time
        metrics_service.record_api_request("DELETE", "/admin/cache", 500, duration)
        
        logger.error("Failed to clear cache", pattern=pattern, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")