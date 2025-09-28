"""
API endpoints для получения статистики анализа PDF
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.core.logging import DebugLogger
from app.models.user import User
from app.utils.pdf_analyzer import PDFAnalyzer

router = APIRouter()
logger = structlog.get_logger()
debug_logger = DebugLogger(__name__)

@router.get("/stats", summary="Get PDF analysis statistics", 
            description="Get detailed statistics about PDF analysis performance and errors")
async def get_pdf_analysis_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение статистики анализа PDF
    """
    try:
        debug_logger.info("Getting PDF analysis statistics", user_id=str(current_user.id))
        
        # Создаем экземпляр анализатора для получения статистики
        analyzer = PDFAnalyzer()
        stats = analyzer.get_analysis_stats()
        
        # Дополнительная информация о системе
        import psutil
        import sys
        import platform
        
        system_info = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "memory_available_gb": psutil.virtual_memory().available / (1024**3),
            "disk_usage_percent": psutil.disk_usage('/').percent
        }
        
        # Анализ производительности
        performance_analysis = {
            "success_rate": 0.0,
            "average_analysis_time": stats.get("average_analysis_time", 0.0),
            "fallback_usage_rate": 0.0,
            "memory_efficiency": "good"
        }
        
        total_analyses = stats.get("total_analyses", 0)
        if total_analyses > 0:
            performance_analysis["success_rate"] = (
                stats.get("successful_analyses", 0) / total_analyses * 100
            )
            performance_analysis["fallback_usage_rate"] = (
                stats.get("fallback_analyses", 0) / total_analyses * 100
            )
        
        # Анализ использования памяти
        memory_history = stats.get("memory_usage_history", [])
        if memory_history:
            recent_memory = memory_history[-1]["memory_mb"] if memory_history else 0
            if recent_memory > 500:  # Более 500MB
                performance_analysis["memory_efficiency"] = "high"
            elif recent_memory > 200:  # Более 200MB
                performance_analysis["memory_efficiency"] = "medium"
            else:
                performance_analysis["memory_efficiency"] = "low"
        
        # Рекомендации по оптимизации
        recommendations = []
        
        if performance_analysis["success_rate"] < 80:
            recommendations.append({
                "type": "error_rate",
                "message": "High error rate detected. Consider checking PDF file quality and system resources.",
                "priority": "high"
            })
        
        if performance_analysis["fallback_usage_rate"] > 50:
            recommendations.append({
                "type": "opencv_dependency",
                "message": "High fallback usage detected. Consider installing OpenCV for better analysis quality.",
                "priority": "medium"
            })
        
        if performance_analysis["average_analysis_time"] > 10:
            recommendations.append({
                "type": "performance",
                "message": "Slow analysis detected. Consider optimizing system resources or reducing PDF complexity.",
                "priority": "medium"
            })
        
        if performance_analysis["memory_efficiency"] == "high":
            recommendations.append({
                "type": "memory",
                "message": "High memory usage detected. Consider increasing system memory or optimizing analysis parameters.",
                "priority": "low"
            })
        
        result = {
            "success": True,
            "analysis_stats": stats,
            "system_info": system_info,
            "performance_analysis": performance_analysis,
            "recommendations": recommendations,
            "timestamp": time.time()
        }
        
        debug_logger.info("PDF analysis statistics retrieved successfully", 
                        total_analyses=total_analyses,
                        success_rate=performance_analysis["success_rate"],
                        recommendations_count=len(recommendations))
        
        return result
        
    except Exception as e:
        debug_logger.error("Failed to get PDF analysis statistics", 
                         error=str(e), user_id=str(current_user.id))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get PDF analysis statistics: {str(e)}"
        )

@router.get("/health", summary="Check PDF analysis health", 
            description="Check the health status of PDF analysis system")
async def check_pdf_analysis_health(
    current_user: User = Depends(get_current_user)
):
    """
    Проверка состояния системы анализа PDF
    """
    try:
        debug_logger.info("Checking PDF analysis health", user_id=str(current_user.id))
        
        # Проверяем доступность зависимостей
        dependencies_status = {
            "opencv": False,
            "scipy": False,
            "pymupdf": False,
            "pillow": False
        }
        
        try:
            import cv2
            dependencies_status["opencv"] = True
        except ImportError:
            pass
        
        try:
            import scipy
            dependencies_status["scipy"] = True
        except ImportError:
            pass
        
        try:
            import fitz
            dependencies_status["pymupdf"] = True
        except ImportError:
            pass
        
        try:
            import PIL
            dependencies_status["pillow"] = True
        except ImportError:
            pass
        
        # Проверяем системные ресурсы
        import psutil
        
        system_health = {
            "memory_available_gb": psutil.virtual_memory().available / (1024**3),
            "cpu_usage_percent": psutil.cpu_percent(interval=1),
            "disk_usage_percent": psutil.disk_usage('/').percent,
            "status": "healthy"
        }
        
        # Определяем общий статус здоровья
        if system_health["memory_available_gb"] < 1.0:
            system_health["status"] = "warning"
        elif system_health["memory_available_gb"] < 0.5:
            system_health["status"] = "critical"
        
        if system_health["cpu_usage_percent"] > 90:
            system_health["status"] = "warning"
        
        if system_health["disk_usage_percent"] > 90:
            system_health["status"] = "warning"
        
        # Проверяем критичные зависимости
        critical_deps = ["pymupdf", "pillow"]
        missing_critical = [dep for dep in critical_deps if not dependencies_status[dep]]
        
        if missing_critical:
            system_health["status"] = "critical"
        
        result = {
            "success": True,
            "status": system_health["status"],
            "dependencies": dependencies_status,
            "system_health": system_health,
            "timestamp": time.time()
        }
        
        debug_logger.info("PDF analysis health check completed", 
                        status=system_health["status"],
                        missing_deps=missing_critical)
        
        return result
        
    except Exception as e:
        debug_logger.error("Failed to check PDF analysis health", 
                         error=str(e), user_id=str(current_user.id))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check PDF analysis health: {str(e)}"
        )

@router.post("/reset-stats", summary="Reset PDF analysis statistics", 
             description="Reset all PDF analysis statistics and counters")
async def reset_pdf_analysis_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Сброс статистики анализа PDF
    """
    try:
        debug_logger.info("Resetting PDF analysis statistics", user_id=str(current_user.id))
        
        # Создаем новый экземпляр анализатора (статистика сбрасывается)
        analyzer = PDFAnalyzer()
        
        result = {
            "success": True,
            "message": "PDF analysis statistics reset successfully",
            "timestamp": time.time()
        }
        
        debug_logger.info("PDF analysis statistics reset successfully", user_id=str(current_user.id))
        
        return result
        
    except Exception as e:
        debug_logger.error("Failed to reset PDF analysis statistics", 
                         error=str(e), user_id=str(current_user.id))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset PDF analysis statistics: {str(e)}"
        )
