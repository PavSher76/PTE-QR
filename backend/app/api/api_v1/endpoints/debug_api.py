"""
API для системы отладки и мониторинга
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import time
from datetime import datetime, timedelta

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.core.logging import DebugLogger
from app.models.user import User
from app.utils.debug_system import debug_system, DebugLevel

router = APIRouter()
logger = structlog.get_logger()
debug_logger = DebugLogger(__name__)


@router.get("/events", 
            summary="Get debug events",
            description="Get debug events with optional filtering")
async def get_debug_events(
    component: Optional[str] = Query(None, description="Filter by component"),
    level: Optional[str] = Query(None, description="Filter by level (trace, debug, info, warning, error, critical)"),
    since: Optional[float] = Query(None, description="Filter events since timestamp"),
    limit: int = Query(100, description="Maximum number of events to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение событий отладки
    """
    try:
        debug_logger.info("Getting debug events", 
                         user_id=str(current_user.id),
                         component=component,
                         level=level,
                         since=since,
                         limit=limit)
        
        # Парсим уровень
        debug_level = None
        if level:
            try:
                debug_level = DebugLevel(level.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid level: {level}")
        
        # Получаем события
        events = debug_system.get_events(
            component=component,
            level=debug_level,
            since=since,
            limit=limit
        )
        
        return {
            "success": True,
            "events": events,
            "count": len(events),
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        debug_logger.error("Failed to get debug events", 
                         error=str(e), user_id=str(current_user.id))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get debug events: {str(e)}"
        )


@router.get("/metrics", 
            summary="Get performance metrics",
            description="Get performance metrics with optional filtering")
async def get_performance_metrics(
    operation_name: Optional[str] = Query(None, description="Filter by operation name"),
    since: Optional[float] = Query(None, description="Filter metrics since timestamp"),
    limit: int = Query(100, description="Maximum number of metrics to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение метрик производительности
    """
    try:
        debug_logger.info("Getting performance metrics", 
                         user_id=str(current_user.id),
                         operation_name=operation_name,
                         since=since,
                         limit=limit)
        
        # Получаем метрики
        metrics = debug_system.get_metrics(
            operation_name=operation_name,
            since=since,
            limit=limit
        )
        
        return {
            "success": True,
            "metrics": metrics,
            "count": len(metrics),
            "timestamp": time.time()
        }
        
    except Exception as e:
        debug_logger.error("Failed to get performance metrics", 
                         error=str(e), user_id=str(current_user.id))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance metrics: {str(e)}"
        )


@router.get("/statistics", 
            summary="Get debug system statistics",
            description="Get comprehensive statistics about the debug system")
async def get_debug_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение статистики системы отладки
    """
    try:
        debug_logger.info("Getting debug system statistics", user_id=str(current_user.id))
        
        # Получаем статистику
        stats = debug_system.get_statistics()
        
        return {
            "success": True,
            "statistics": stats,
            "timestamp": time.time()
        }
        
    except Exception as e:
        debug_logger.error("Failed to get debug statistics", 
                         error=str(e), user_id=str(current_user.id))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get debug statistics: {str(e)}"
        )


@router.get("/health", 
            summary="Check debug system health",
            description="Check the health status of the debug system")
async def check_debug_system_health(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Проверка состояния системы отладки
    """
    try:
        debug_logger.info("Checking debug system health", user_id=str(current_user.id))
        
        stats = debug_system.get_statistics()
        
        # Определяем статус здоровья
        health_status = "healthy"
        issues = []
        
        # Проверяем количество событий
        total_events = stats["events"]["total"]
        if total_events > 50000:
            health_status = "warning"
            issues.append(f"High event count: {total_events}")
        
        # Проверяем количество ошибок
        error_events = stats["events"]["by_level"].get("error", {})
        total_errors = sum(error_events.values())
        if total_errors > 100:
            health_status = "warning"
            issues.append(f"High error count: {total_errors}")
        
        # Проверяем активные операции
        active_ops = stats["active_operations"]
        if active_ops > 10:
            health_status = "warning"
            issues.append(f"High active operations count: {active_ops}")
        
        # Проверяем время выполнения операций
        for op_name, op_stats in stats["metrics"]["by_operation"].items():
            if op_stats["avg_duration"] > 30:  # Более 30 секунд
                health_status = "warning"
                issues.append(f"Slow operation {op_name}: {op_stats['avg_duration']:.1f}s average")
        
        return {
            "success": True,
            "status": health_status,
            "issues": issues,
            "statistics": stats,
            "timestamp": time.time()
        }
        
    except Exception as e:
        debug_logger.error("Failed to check debug system health", 
                         error=str(e), user_id=str(current_user.id))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check debug system health: {str(e)}"
        )


@router.post("/export", 
             summary="Export debug data",
             description="Export all debug data to a file")
async def export_debug_data(
    filepath: str = Query(..., description="Path to export file"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Экспорт данных отладки
    """
    try:
        debug_logger.info("Exporting debug data", 
                         user_id=str(current_user.id),
                         filepath=filepath)
        
        # Экспортируем данные
        debug_system.export_data(filepath)
        
        return {
            "success": True,
            "message": f"Debug data exported to {filepath}",
            "filepath": filepath,
            "timestamp": time.time()
        }
        
    except Exception as e:
        debug_logger.error("Failed to export debug data", 
                         error=str(e), user_id=str(current_user.id))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export debug data: {str(e)}"
        )


@router.post("/clear", 
             summary="Clear debug data",
             description="Clear all debug data")
async def clear_debug_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Очистка данных отладки
    """
    try:
        debug_logger.info("Clearing debug data", user_id=str(current_user.id))
        
        # Очищаем данные
        debug_system.clear_data()
        
        return {
            "success": True,
            "message": "Debug data cleared successfully",
            "timestamp": time.time()
        }
        
    except Exception as e:
        debug_logger.error("Failed to clear debug data", 
                         error=str(e), user_id=str(current_user.id))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear debug data: {str(e)}"
        )


@router.post("/config", 
             summary="Update debug system configuration",
             description="Update configuration parameters for the debug system")
async def update_debug_config(
    config_updates: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновление конфигурации системы отладки
    """
    try:
        debug_logger.info("Updating debug system configuration", 
                         user_id=str(current_user.id),
                         config_updates=config_updates)
        
        # Обновляем конфигурацию
        debug_system.update_config(config_updates)
        
        return {
            "success": True,
            "message": "Debug system configuration updated successfully",
            "config_updates": config_updates,
            "timestamp": time.time()
        }
        
    except Exception as e:
        debug_logger.error("Failed to update debug configuration", 
                         error=str(e), user_id=str(current_user.id))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update debug configuration: {str(e)}"
        )


@router.get("/realtime", 
            summary="Get real-time debug data",
            description="Get real-time debug data for monitoring")
async def get_realtime_debug_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение данных отладки в реальном времени
    """
    try:
        debug_logger.info("Getting real-time debug data", user_id=str(current_user.id))
        
        # Получаем последние события (за последние 5 минут)
        since = time.time() - 300
        recent_events = debug_system.get_events(since=since, limit=50)
        
        # Получаем последние метрики (за последние 5 минут)
        recent_metrics = debug_system.get_metrics(since=since, limit=50)
        
        # Получаем статистику
        stats = debug_system.get_statistics()
        
        # Анализируем тренды
        trends = {
            "error_rate": 0.0,
            "avg_response_time": 0.0,
            "memory_usage": 0.0,
            "active_operations": stats["active_operations"]
        }
        
        # Вычисляем тренды
        if recent_metrics:
            total_ops = len(recent_metrics)
            failed_ops = sum(1 for m in recent_metrics if not m["success"])
            trends["error_rate"] = failed_ops / total_ops if total_ops > 0 else 0.0
            trends["avg_response_time"] = sum(m["duration"] for m in recent_metrics) / total_ops
            trends["memory_usage"] = sum(m["memory_delta"] for m in recent_metrics) / total_ops
        
        return {
            "success": True,
            "realtime_data": {
                "recent_events": recent_events,
                "recent_metrics": recent_metrics,
                "trends": trends,
                "statistics": stats
            },
            "timestamp": time.time()
        }
        
    except Exception as e:
        debug_logger.error("Failed to get real-time debug data", 
                         error=str(e), user_id=str(current_user.id))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get real-time debug data: {str(e)}"
        )
