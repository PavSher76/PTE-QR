"""
Нормоконтроль документов API endpoints
"""

import asyncio
import random
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.api.dependencies import get_current_user
from app.core.logging import configure_logging
from app.models.user import User
from app.services.pdf_service import PDFService
from app.services.qr_service import QRService

logger = configure_logging()
router = APIRouter()

# Модели данных для нормоконтроля
class NormoControlRequest(BaseModel):
    """Запрос на нормоконтроль документа"""
    enovia_id: str
    revision: str = "0"
    control_type: str = "full"  # full, quick, custom
    requirements: Optional[List[str]] = None

class NormoControlResult(BaseModel):
    """Результат нормоконтроля"""
    document_id: str
    control_id: str
    status: str  # passed, failed, warning
    score: float  # 0.0 - 100.0
    issues: List[Dict[str, str]]
    recommendations: List[str]
    qr_codes_added: int
    processing_time: float
    timestamp: datetime

class NormoControlResponse(BaseModel):
    """Ответ API нормоконтроля"""
    success: bool
    message: str
    result: Optional[NormoControlResult] = None
    error: Optional[str] = None

# Моки для нормоконтроля
NORMOCONTROL_MOCKS = {
    "requirements": [
        "Соответствие ГОСТ 2.301-68",
        "Правильность оформления основной надписи",
        "Соответствие масштабов ГОСТ 2.302-68",
        "Правильность нанесения размеров",
        "Соответствие линий ГОСТ 2.303-68",
        "Правильность оформления спецификации",
        "Соответствие форматов листов ГОСТ 2.301-68",
        "Правильность нанесения технических требований"
    ],
    "issues_templates": [
        {
            "type": "error",
            "code": "NC001",
            "description": "Несоответствие формата листа ГОСТ 2.301-68",
            "severity": "high",
            "location": "Общие параметры документа"
        },
        {
            "type": "warning", 
            "code": "NC002",
            "description": "Отклонение от рекомендуемого масштаба",
            "severity": "medium",
            "location": "Масштаб чертежа"
        },
        {
            "type": "info",
            "code": "NC003", 
            "description": "Рекомендуется добавить технические требования",
            "severity": "low",
            "location": "Технические требования"
        }
    ],
    "recommendations": [
        "Проверить соответствие формата листа стандарту ГОСТ 2.301-68",
        "Убедиться в правильности оформления основной надписи",
        "Проверить соответствие линий ГОСТ 2.303-68",
        "Добавить недостающие размеры на чертеж",
        "Проверить правильность нанесения технических требований"
    ]
}

def generate_mock_control_result(
    document_id: str,
    qr_codes_count: int,
    processing_time: float
) -> NormoControlResult:
    """Генерирует моковый результат нормоконтроля"""
    
    # Случайная генерация статуса (80% passed, 15% warning, 5% failed)
    status_rand = random.random()
    if status_rand < 0.8:
        status = "passed"
        score = random.uniform(85.0, 100.0)
    elif status_rand < 0.95:
        status = "warning"
        score = random.uniform(70.0, 84.9)
    else:
        status = "failed"
        score = random.uniform(40.0, 69.9)
    
    # Генерация проблем в зависимости от статуса
    issues = []
    if status == "failed":
        # 2-4 серьезные проблемы
        num_issues = random.randint(2, 4)
        for i in range(num_issues):
            issue = random.choice(NORMOCONTROL_MOCKS["issues_templates"])
            issues.append({
                "id": f"NC{random.randint(1, 999):03d}",
                "type": issue["type"],
                "code": issue["code"],
                "description": issue["description"],
                "severity": issue["severity"],
                "location": issue["location"],
                "page": random.randint(1, 10) if random.random() > 0.3 else None
            })
    elif status == "warning":
        # 1-2 предупреждения
        num_issues = random.randint(1, 2)
        for i in range(num_issues):
            issue = random.choice([i for i in NORMOCONTROL_MOCKS["issues_templates"] if i["severity"] in ["medium", "low"]])
            issues.append({
                "id": f"NC{random.randint(1, 999):03d}",
                "type": issue["type"],
                "code": issue["code"],
                "description": issue["description"],
                "severity": issue["severity"],
                "location": issue["location"],
                "page": random.randint(1, 10) if random.random() > 0.5 else None
            })
    
    # Генерация рекомендаций
    recommendations = random.sample(
        NORMOCONTROL_MOCKS["recommendations"],
        random.randint(1, 3)
    )
    
    return NormoControlResult(
        document_id=document_id,
        control_id=str(uuid4()),
        status=status,
        score=round(score, 1),
        issues=issues,
        recommendations=recommendations,
        qr_codes_added=qr_codes_count,
        processing_time=round(processing_time, 2),
        timestamp=datetime.now()
    )

@router.post("/upload", response_model=NormoControlResponse)
async def normocontrol_upload(
    file: UploadFile = File(...),
    enovia_id: str = Form(...),
    revision: str = Form("0"),
    control_type: str = Form("full")
):
    """
    Загрузка PDF документа для нормоконтроля
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Начало нормоконтроля документа", 
                   filename=file.filename,
                   enovia_id=enovia_id,
                   control_type=control_type)
        
        # Валидация файла
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Поддерживаются только PDF файлы"
            )
        
        # Читаем содержимое файла
        pdf_content = await file.read()
        
        # Создаем временный файл для обработки
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(pdf_content)
            temp_file_path = temp_file.name
        
        try:
            # Инициализируем сервисы
            pdf_service = PDFService()
            qr_service = QRService()
            
            # Обрабатываем PDF и добавляем QR коды
            logger.info("Обработка PDF документа для нормоконтроля")
            processed_pdf_content, qr_data_list = await pdf_service.add_qr_codes_to_pdf(
                pdf_content=pdf_content,
                enovia_id=enovia_id,
                revision=revision,
                output_path=temp_file_path
            )
            
            # Генерируем моковый результат нормоконтроля
            processing_time = (datetime.now() - start_time).total_seconds()
            control_result = generate_mock_control_result(
                document_id=enovia_id,
                qr_codes_count=len(qr_data_list),
                processing_time=processing_time
            )
            
            # Сохраняем обработанный PDF
            output_filename = f"normocontrol_{enovia_id}_{revision}_{uuid4().hex[:8]}.pdf"
            output_path = f"/tmp/processed_pdfs/{output_filename}"
            
            with open(output_path, 'wb') as output_file:
                output_file.write(processed_pdf_content)
            
            logger.info("Нормоконтроль завершен успешно",
                       document_id=enovia_id,
                       status=control_result.status,
                       score=control_result.score,
                       qr_codes_added=control_result.qr_codes_added,
                       issues_count=len(control_result.issues))
            
            return NormoControlResponse(
                success=True,
                message=f"Нормоконтроль завершен. Статус: {control_result.status.upper()}",
                result=control_result
            )
            
        finally:
            # Удаляем временный файл
            import os
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
    except Exception as e:
        logger.error("Ошибка при нормоконтроле документа",
                    error=str(e),
                    filename=file.filename)
        
        return NormoControlResponse(
            success=False,
            message="Ошибка при проведении нормоконтроля",
            error=str(e)
        )

@router.get("/requirements", response_model=Dict[str, List[str]])
async def get_normocontrol_requirements():
    """
    Получение списка требований для нормоконтроля
    """
    return {
        "requirements": NORMOCONTROL_MOCKS["requirements"]
    }

@router.get("/status/{control_id}", response_model=NormoControlResponse)
async def get_normocontrol_status(
    control_id: str
):
    """
    Получение статуса нормоконтроля по ID
    """
    # Моковый ответ - в реальной системе здесь был бы запрос к БД
    mock_result = NormoControlResult(
        document_id="MOCK_DOC_001",
        control_id=control_id,
        status="completed",
        score=92.5,
        issues=[
            {
                "id": "NC001",
                "type": "warning",
                "code": "NC001",
                "description": "Рекомендуется проверить соответствие масштаба",
                "severity": "medium",
                "location": "Масштаб чертежа",
                "page": 2
            }
        ],
        recommendations=[
            "Проверить соответствие формата листа стандарту ГОСТ 2.301-68",
            "Убедиться в правильности оформления основной надписи"
        ],
        qr_codes_added=15,
        processing_time=3.45,
        timestamp=datetime.now()
    )
    
    return NormoControlResponse(
        success=True,
        message="Статус нормоконтроля получен",
        result=mock_result
    )

@router.get("/history", response_model=Dict[str, List[NormoControlResult]])
async def get_normocontrol_history(
    limit: int = 10
):
    """
    Получение истории нормоконтроля пользователя
    """
    # Генерируем моковую историю
    history = []
    
    for i in range(min(limit, 5)):  # Максимум 5 записей
        mock_result = generate_mock_control_result(
            document_id=f"MOCK_DOC_{i+1:03d}",
            qr_codes_count=random.randint(5, 25),
            processing_time=random.uniform(1.0, 5.0)
        )
        history.append(mock_result)
    
    return {
        "history": history,
        "total": len(history)
    }

@router.post("/validate", response_model=Dict[str, Any])
async def validate_document_structure(
    file: UploadFile = File(...)
):
    """
    Валидация структуры документа (быстрая проверка)
    """
    try:
        # Читаем PDF
        pdf_content = await file.read()
        
        # Моковая валидация
        validation_result = {
            "valid": True,
            "pages_count": 12,
            "format": "A4",
            "orientation": "landscape",
            "has_stamp": True,
            "has_frame": True,
            "issues": [
                {
                    "type": "info",
                    "message": "Документ соответствует базовым требованиям",
                    "severity": "low"
                }
            ],
            "recommendations": [
                "Рекомендуется провести полный нормоконтроль"
            ]
        }
        
        return validation_result
        
    except Exception as e:
        logger.error("Ошибка валидации документа", error=str(e))
        raise HTTPException(status_code=500, detail="Ошибка валидации документа")
