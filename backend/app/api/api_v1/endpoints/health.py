"""
Health check endpoints
"""

import time

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.cache_service import cache_service
from app.services.enovia_service import enovia_service
from app.services.metrics_service import metrics_service

logger = structlog.get_logger()
router = APIRouter()


@router.get("/")
async def health_check(db: Session = Depends(get_db)):
    """
    Comprehensive health check for all services
    """
    logger.info("Starting health check")
    start_time = time.time()
    status = "healthy"
    checks = {}

    # Check database
    try:
        logger.info("Checking database connection")
        from sqlalchemy import text

        db.execute(text("SELECT 1"))
        checks["database"] = "healthy"
        logger.info("Database check passed")
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
        status = "unhealthy"
        logger.error("Database check failed", error=str(e))

    # Check Redis cache
    try:
        logger.info("Checking Redis cache connection")
        cache_health = await cache_service.health_check()
        checks["cache"] = cache_health["status"]
        if cache_health["status"] != "healthy":
            status = "unhealthy"
        logger.info("Cache check completed", status=cache_health["status"])
    except Exception as e:
        checks["cache"] = f"unhealthy: {str(e)}"
        status = "unhealthy"
        logger.error("Cache check failed", error=str(e))

    # Check ENOVIA
    try:
        logger.info("Checking ENOVIA connection")
        enovia_health = await enovia_service.health_check()
        checks["enovia"] = enovia_health["enovia"]
        if enovia_health["enovia"] != "healthy":
            status = "degraded"  # ENOVIA is optional
        logger.info("ENOVIA check completed", status=enovia_health["enovia"])
    except Exception as e:
        checks["enovia"] = f"unhealthy: {str(e)}"
        status = "degraded"
        logger.warning("ENOVIA check failed", error=str(e))

    duration = time.time() - start_time
    logger.info(
        "Health check completed", status=status, duration=duration, checks=checks
    )

    return {
        "status": status,
        "timestamp": time.time(),
        "database": checks.get("database", "unknown"),
        "redis": checks.get("cache", "unknown"),
        "enovia": checks.get("enovia", "unknown"),
    }


@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint
    """
    try:
        from fastapi.responses import Response

        metrics_data = metrics_service.get_metrics_prometheus()
        return Response(
            content=metrics_data, media_type="text/plain; version=0.0.4; charset=utf-8"
        )
    except Exception as e:
        logger.error("Failed to get metrics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get metrics")


@router.get("/metrics/json")
async def metrics_json():
    """
    Metrics in JSON format
    """
    try:
        metrics_data = metrics_service.get_metrics_dict()
        return {"registry": metrics_data, "timestamp": time.time()}
    except Exception as e:
        logger.error("Failed to get metrics JSON", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get metrics")


@router.get("/status")
async def detailed_status(db: Session = Depends(get_db)):
    """
    Detailed system status with metrics
    """
    try:
        # Get health metrics
        health_metrics = metrics_service.get_health_metrics()

        # Get cache health
        cache_health = await cache_service.health_check()

        # Get ENOVIA health
        enovia_health = await enovia_service.health_check()

        # Get database info
        try:
            from sqlalchemy import text

            db.execute(text("SELECT 1"))
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"

        return {
            "status": "healthy",
            "timestamp": time.time(),
            "system": {
                "cpu_percent": health_metrics["cpu_usage_percent"],
                "memory_percent": health_metrics["memory_usage_percent"],
                "disk_percent": health_metrics["disk_usage_percent"],
                "uptime_seconds": health_metrics["uptime_seconds"],
            },
            "application": {
                "total_requests": health_metrics["total_requests"],
                "total_qr_codes": health_metrics["total_qr_codes"],
            },
            "cache": cache_health,
            "enovia": enovia_health,
        }

    except Exception as e:
        logger.error("Failed to get detailed status", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get system status")
