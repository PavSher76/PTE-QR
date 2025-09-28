"""
Полностью переработанный API endpoint для загрузки PDF
Максимальная эффективность, без временных файлов
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import time

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.core.logging import DebugLogger
from app.models.user import User
from app.services.pdf_service_v2 import PDFServiceV2
from app.utils.pdf_exceptions import PDFAnalysisError, PDFFileError

router = APIRouter()
logger = structlog.get_logger()
debug_logger = DebugLogger(__name__)

# Глобальный экземпляр сервиса
pdf_service = PDFServiceV2()


@router.post("/upload-with-qr-codes", 
             summary="Upload PDF and add QR codes",
             description="Upload a PDF file and add QR codes to each page")
async def upload_pdf_with_qr_codes_v2(
    file: UploadFile = File(..., description="PDF file to process"),
    qr_data: str = Form(..., description="Comma-separated QR code data for each page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Загрузка PDF файла и добавление QR кодов
    Полностью переработанная версия без временных файлов
    """
    start_time = time.time()
    
    try:
        debug_logger.info("Starting PDF upload with QR codes", 
                         user_id=str(current_user.id),
                         filename=file.filename,
                         content_type=file.content_type)
        
        # Валидация файла
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        if file.content_type and file.content_type != 'application/pdf':
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Читаем содержимое файла
        pdf_content = await file.read()
        
        if not pdf_content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        if len(pdf_content) > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")
        
        # Парсим QR данные
        qr_data_list = [data.strip() for data in qr_data.split(',') if data.strip()]
        
        if not qr_data_list:
            raise HTTPException(status_code=400, detail="No QR data provided")
        
        debug_logger.info("Processing PDF with QR codes", 
                         content_size=len(pdf_content),
                         qr_count=len(qr_data_list))
        
        # Обрабатываем PDF
        result_pdf_content = pdf_service.add_qr_codes_to_pdf(pdf_content, qr_data_list)
        
        processing_time = time.time() - start_time
        
        debug_logger.info("PDF processing completed successfully", 
                         user_id=str(current_user.id),
                         processing_time=processing_time,
                         result_size=len(result_pdf_content))
        
        # Возвращаем результат
        from fastapi.responses import Response
        
        return Response(
            content=result_pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=processed_{file.filename}",
                "X-Processing-Time": str(processing_time),
                "X-QR-Codes-Added": str(len(qr_data_list)),
                "X-Original-Size": str(len(pdf_content)),
                "X-Result-Size": str(len(result_pdf_content))
            }
        )
        
    except HTTPException:
        raise
    except PDFAnalysisError as e:
        debug_logger.error("PDF analysis error", 
                         error=str(e),
                         error_code=getattr(e, 'error_code', 'UNKNOWN'),
                         user_id=str(current_user.id))
        raise HTTPException(
            status_code=422,
            detail=f"PDF analysis error: {str(e)}"
        )
    except PDFFileError as e:
        debug_logger.error("PDF file error", 
                         error=str(e),
                         error_code=getattr(e, 'error_code', 'UNKNOWN'),
                         user_id=str(current_user.id))
        raise HTTPException(
            status_code=400,
            detail=f"PDF file error: {str(e)}"
        )
    except Exception as e:
        processing_time = time.time() - start_time
        debug_logger.error("Unexpected error during PDF processing", 
                         error=str(e),
                         processing_time=processing_time,
                         user_id=str(current_user.id),
                         exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/analyze-layout", 
             summary="Analyze PDF page layout",
             description="Analyze the layout of a specific page in a PDF")
async def analyze_pdf_layout_v2(
    file: UploadFile = File(..., description="PDF file to analyze"),
    page_number: int = Form(0, description="Page number to analyze (0-based)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Анализ макета страницы PDF
    """
    try:
        debug_logger.info("Starting PDF layout analysis", 
                         user_id=str(current_user.id),
                         filename=file.filename,
                         page_number=page_number)
        
        # Валидация файла
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Читаем содержимое файла
        pdf_content = await file.read()
        
        if not pdf_content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Анализируем макет
        layout_info = pdf_service.analyze_pdf_layout(pdf_content, page_number)
        
        debug_logger.info("PDF layout analysis completed", 
                         user_id=str(current_user.id),
                         page_number=page_number,
                         layout_info=layout_info)
        
        return {
            "success": True,
            "layout_info": layout_info,
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except PDFAnalysisError as e:
        debug_logger.error("PDF analysis error", 
                         error=str(e),
                         error_code=getattr(e, 'error_code', 'UNKNOWN'),
                         user_id=str(current_user.id))
        raise HTTPException(
            status_code=422,
            detail=f"PDF analysis error: {str(e)}"
        )
    except Exception as e:
        debug_logger.error("Unexpected error during PDF analysis", 
                         error=str(e),
                         user_id=str(current_user.id),
                         exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/service-stats", 
            summary="Get PDF service statistics",
            description="Get detailed statistics about PDF service performance")
async def get_pdf_service_stats_v2(
    current_user: User = Depends(get_current_user)
):
    """
    Получение статистики PDF сервиса
    """
    try:
        debug_logger.info("Getting PDF service statistics", user_id=str(current_user.id))
        
        stats = pdf_service.get_service_stats()
        
        return {
            "success": True,
            "stats": stats,
            "timestamp": time.time()
        }
        
    except Exception as e:
        debug_logger.error("Failed to get PDF service statistics", 
                         error=str(e), user_id=str(current_user.id))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get service statistics: {str(e)}"
        )


@router.post("/clear-cache", 
             summary="Clear PDF service cache",
             description="Clear all caches in the PDF service")
async def clear_pdf_service_cache_v2(
    current_user: User = Depends(get_current_user)
):
    """
    Очистка кэша PDF сервиса
    """
    try:
        debug_logger.info("Clearing PDF service cache", user_id=str(current_user.id))
        
        pdf_service.clear_cache()
        
        return {
            "success": True,
            "message": "PDF service cache cleared successfully",
            "timestamp": time.time()
        }
        
    except Exception as e:
        debug_logger.error("Failed to clear PDF service cache", 
                         error=str(e), user_id=str(current_user.id))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )


@router.post("/update-config", 
             summary="Update PDF analyzer configuration",
             description="Update configuration parameters for PDF analysis")
async def update_pdf_analyzer_config_v2(
    config_updates: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Обновление конфигурации PDF анализатора
    """
    try:
        debug_logger.info("Updating PDF analyzer configuration", 
                         user_id=str(current_user.id),
                         config_updates=config_updates)
        
        pdf_service.update_analyzer_config(config_updates)
        
        return {
            "success": True,
            "message": "PDF analyzer configuration updated successfully",
            "config_updates": config_updates,
            "timestamp": time.time()
        }
        
    except Exception as e:
        debug_logger.error("Failed to update PDF analyzer configuration", 
                         error=str(e), user_id=str(current_user.id))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update configuration: {str(e)}"
        )


@router.get("/health", 
            summary="Check PDF service health",
            description="Check the health status of the PDF service")
async def check_pdf_service_health_v2(
    current_user: User = Depends(get_current_user)
):
    """
    Проверка состояния PDF сервиса
    """
    try:
        debug_logger.info("Checking PDF service health", user_id=str(current_user.id))
        
        stats = pdf_service.get_service_stats()
        
        # Определяем статус здоровья
        health_status = "healthy"
        issues = []
        
        # Проверяем статистику ошибок
        total_ops = stats.get("total_operations", 0)
        failed_ops = stats.get("failed_operations", 0)
        
        if total_ops > 0:
            error_rate = failed_ops / total_ops
            if error_rate > 0.1:  # Более 10% ошибок
                health_status = "warning"
                issues.append(f"High error rate: {error_rate:.1%}")
            elif error_rate > 0.2:  # Более 20% ошибок
                health_status = "critical"
                issues.append(f"Critical error rate: {error_rate:.1%}")
        
        # Проверяем время обработки
        avg_time = stats.get("average_operation_time", 0)
        if avg_time > 10:  # Более 10 секунд
            health_status = "warning"
            issues.append(f"Slow processing: {avg_time:.1f}s average")
        
        # Проверяем доступность анализатора
        analyzer_stats = stats.get("analyzer_stats", {})
        if not analyzer_stats.get("cv_available", False):
            health_status = "warning"
            issues.append("OpenCV not available, using fallback mode")
        
        return {
            "success": True,
            "status": health_status,
            "issues": issues,
            "stats": stats,
            "timestamp": time.time()
        }
        
    except Exception as e:
        debug_logger.error("Failed to check PDF service health", 
                         error=str(e), user_id=str(current_user.id))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check service health: {str(e)}"
        )
