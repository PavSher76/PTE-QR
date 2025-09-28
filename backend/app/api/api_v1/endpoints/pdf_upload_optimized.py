"""
Оптимизированный endpoint для загрузки PDF с QR кодами
Устранены проблемы с временными файлами и улучшена производительность
"""

import os
import time
import uuid
from typing import Dict, Any

import structlog
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.core.logging import DebugLogger
from app.models.user import User
from app.services.document_service import DocumentService
from app.services.pdf_service_optimized import OptimizedPDFService
from app.services.qr_service import QRService

router = APIRouter()
logger = structlog.get_logger()
debug_logger = DebugLogger(__name__)

@router.post("/upload-optimized", summary="Upload PDF and generate QR codes (optimized)", 
             description="Upload PDF document and generate QR codes for each page with optimized processing")
async def upload_pdf_with_qr_codes_optimized(
    file: UploadFile = File(..., description="PDF file to upload"),
    enovia_id: str = Form(..., description="ENOVIA document ID"),
    title: str = Form(..., description="Document title"),
    revision: str = Form(..., description="Document revision"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Оптимизированная загрузка PDF с генерацией QR кодов
    """
    start_time = time.time()
    
    try:
        debug_logger.info("Starting optimized PDF upload", 
                        filename=file.filename,
                        enovia_id=enovia_id,
                        title=title,
                        revision=revision,
                        user_id=str(current_user.id))
        
        # Валидация файла
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed"
            )
        
        # Проверка размера файла (максимум 50MB)
        file_content = await file.read()
        if len(file_content) > 50 * 1024 * 1024:  # 50MB
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds 50MB limit"
            )
        
        # Проверка магических байтов PDF
        if not file_content.startswith(b'%PDF'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid PDF file format"
            )
        
        # Инициализация сервисов
        pdf_service = OptimizedPDFService()
        qr_service = QRService()
        document_service = DocumentService(db)
        
        # Обработка PDF с QR кодами (оптимизированно)
        result = await pdf_service.process_pdf_with_qr_codes_optimized(
            pdf_content=file_content,
            enovia_id=enovia_id,
            title=title,
            revision=revision,
            created_by=current_user.id,
            qr_service=qr_service,
            document_service=document_service
        )
        
        duration = time.time() - start_time
        
        debug_logger.info("PDF upload completed successfully", 
                        document_id=result["document_id"],
                        enovia_id=enovia_id,
                        total_pages=result["total_pages"],
                        qr_codes_created=result["qr_codes_created"],
                        duration=duration)
        
        return {
            "success": True,
            "message": "PDF processed successfully with QR codes",
            "document_id": result["document_id"],
            "enovia_id": enovia_id,
            "title": title,
            "revision": revision,
            "total_pages": result["total_pages"],
            "qr_codes_created": result["qr_codes_created"],
            "output_filename": os.path.basename(result["output_path"]),
            "processing_time": duration
        }
        
    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        error_message = str(e)
        
        debug_logger.error("PDF upload failed", 
                         filename=file.filename,
                         enovia_id=enovia_id,
                         error=error_message,
                         duration=duration)
        
        # Handle specific database errors
        if "duplicate key value violates unique constraint" in error_message:
            if "documents_enovia_id_key" in error_message:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Document with ENOVIA ID '{enovia_id}' already exists. Please use a different ENOVIA ID or update the existing document."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A document with this information already exists. Please check your input data."
                )
        elif "EOF marker not found" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid PDF file. Please ensure the file is a valid PDF document."
            )
        elif "expected str, bytes or os.PathLike object" in error_message:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing PDF file. Please try again or contact support."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing PDF: {error_message}"
            )

@router.get("/download-optimized/{filename}", summary="Download processed PDF (optimized)", 
            description="Download processed PDF with QR codes")
async def download_processed_pdf_optimized(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Скачивание обработанного PDF файла
    """
    try:
        # Проверка безопасности имени файла
        if not filename.endswith('.pdf') or '..' in filename or '/' in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filename"
            )
        
        # Путь к файлу
        file_path = os.path.join("output", filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Читаем файл
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        debug_logger.info("PDF file downloaded", 
                        filename=filename,
                        file_size=len(file_content),
                        user_id=str(current_user.id))
        
        return {
            "filename": filename,
            "content": file_content,
            "content_type": "application/pdf"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        debug_logger.error("Error downloading PDF file", 
                         filename=filename,
                         error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error downloading file"
        )

@router.get("/info-optimized", summary="Get PDF info (optimized)", 
            description="Get information about PDF file without processing")
async def get_pdf_info_optimized(
    file: UploadFile = File(..., description="PDF file to analyze"),
    current_user: User = Depends(get_current_user)
):
    """
    Получение информации о PDF файле без обработки
    """
    try:
        debug_logger.info("Getting PDF info", 
                        filename=file.filename,
                        user_id=str(current_user.id))
        
        # Валидация файла
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed"
            )
        
        # Читаем содержимое файла
        file_content = await file.read()
        
        # Проверка магических байтов PDF
        if not file_content.startswith(b'%PDF'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid PDF file format"
            )
        
        # Получаем информацию о PDF
        pdf_service = OptimizedPDFService()
        pdf_info = pdf_service.get_pdf_info_optimized(file_content)
        
        debug_logger.info("PDF info retrieved", 
                        filename=file.filename,
                        total_pages=pdf_info.get("total_pages", 0))
        
        return {
            "success": True,
            "filename": file.filename,
            "file_size": len(file_content),
            "pdf_info": pdf_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        debug_logger.error("Error getting PDF info", 
                         filename=file.filename,
                         error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error analyzing PDF file"
        )
