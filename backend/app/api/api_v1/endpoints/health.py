"""
Health check endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db, get_redis
from app.models.schemas import HealthResponse
from app.services.enovia_service import enovia_service
import time

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check(
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
):
    """
    Comprehensive health check for all services
    """
    status = "healthy"
    checks = {}
    
    # Check database
    try:
        db.execute("SELECT 1")
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
        status = "unhealthy"
    
    # Check Redis
    try:
        redis.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"
        status = "unhealthy"
    
    # Check ENOVIA (optional)
    try:
        enovia_health = await enovia_service.health_check()
        checks["enovia"] = enovia_health.get("enovia", "unhealthy")
    except Exception as e:
        checks["enovia"] = f"unhealthy: {str(e)}"
    
    return HealthResponse(
        status=status,
        timestamp=time.time(),
        **checks
    )


@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint
    """
    from app.core.metrics import metrics_collector
    from fastapi.responses import Response
    
    try:
        metrics_data = metrics_collector.get_metrics()
        return Response(
            content=metrics_data,
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )
    except Exception as e:
        logger.error("Failed to get metrics", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get metrics")


@router.get("/metrics/json")
async def metrics_json():
    """
    Metrics in JSON format
    """
    from app.core.metrics import metrics_collector
    
    try:
        metrics_dict = metrics_collector.get_metrics_dict()
        return metrics_dict
    except Exception as e:
        logger.error("Failed to get metrics JSON", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get metrics")


@router.get("/status")
async def detailed_status():
    """
    Detailed system status with metrics
    """
    from app.core.metrics import metrics_collector
    from app.core.cache import cache_manager
    from app.services.enovia_service import enovia_service
    import psutil
    import time
    
    try:
        # System metrics
        system_info = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
        
        # Application metrics
        app_metrics = metrics_collector.get_metrics_dict()
        
        # Cache health
        cache_health = await cache_manager.health_check()
        
        # ENOVIA health
        enovia_health = await enovia_service.health_check()
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "system": system_info,
            "application": app_metrics,
            "cache": cache_health,
            "enovia": enovia_health
        }
        
    except Exception as e:
        logger.error("Failed to get detailed status", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get system status")
