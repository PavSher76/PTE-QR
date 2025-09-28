#!/usr/bin/env python3
"""
Генерация тестовых PDF-шаблонов для проверки системы координат
"""

import sys
import os
sys.path.append('/app')

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A3, landscape
from reportlab.lib.units import cm
import structlog

# Настройка логирования
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def create_test_pdf(filename: str, page_size, rotation: int = 0, title: str = ""):
    """
    Создает тестовый PDF с рамкой и информацией о координатах
    
    Args:
        filename: Имя файла для сохранения
        page_size: Размер страницы (A4, A3, landscape(A4), etc.)
        rotation: Поворот страницы в градусах (0, 90, 180, 270)
        title: Заголовок документа
    """
    try:
        # Создаем PDF
        c = canvas.Canvas(filename, pagesize=page_size)
        width, height = page_size
        
        # Применяем поворот
        if rotation == 90:
            c.rotate(90)
            c.translate(0, -width)
        elif rotation == 180:
            c.rotate(180)
            c.translate(-width, -height)
        elif rotation == 270:
            c.rotate(270)
            c.translate(-height, 0)
        
        # Рисуем рамку (отступ 1 см от краев)
        margin = 1 * cm
        c.setStrokeColor('black')
        c.setLineWidth(2)
        c.rect(margin, margin, width - 2*margin, height - 2*margin)
        
        # Рисуем внутреннюю рамку (отступ 2 см)
        inner_margin = 2 * cm
        c.setLineWidth(1)
        c.rect(inner_margin, inner_margin, width - 2*inner_margin, height - 2*inner_margin)
        
        # Добавляем заголовок
        c.setFont('Helvetica-Bold', 16)
        c.drawString(3*cm, height - 3*cm, title)
        
        # Добавляем информацию о размерах и повороте
        c.setFont('Helvetica', 12)
        info_text = f"Размер: {width:.1f} x {height:.1f} pt"
        c.drawString(3*cm, height - 4*cm, info_text)
        
        info_text = f"Поворот: {rotation}°"
        c.drawString(3*cm, height - 4.5*cm, info_text)
        
        # Добавляем информацию о координатной системе
        c.setFont('Helvetica', 10)
        coord_text = "PDF координатная система: origin = bottom-left, единицы = points"
        c.drawString(3*cm, height - 5.5*cm, coord_text)
        
        # Рисуем сетку для визуализации координат (каждые 2 см)
        c.setStrokeColor('lightgray')
        c.setLineWidth(0.5)
        
        # Вертикальные линии
        for x in range(int(margin), int(width - margin), int(2*cm)):
            c.line(x, margin, x, height - margin)
        
        # Горизонтальные линии
        for y in range(int(margin), int(height - margin), int(2*cm)):
            c.line(margin, y, width - margin, y)
        
        # Добавляем подписи координат
        c.setFont('Helvetica', 8)
        c.setFillColor('gray')
        
        # Подписи по X (каждые 4 см)
        for x in range(int(2*cm), int(width - 2*cm), int(4*cm)):
            c.drawString(x, 0.5*cm, f"{x:.0f}")
        
        # Подписи по Y (каждые 4 см)
        for y in range(int(2*cm), int(height - 2*cm), int(4*cm)):
            c.drawString(0.5*cm, y, f"{y:.0f}")
        
        # Добавляем маркеры для QR кода (bottom-right corner)
        qr_size = 3.5 * cm
        margin_qr = 1 * cm
        
        # Показываем ожидаемое место для QR кода
        c.setStrokeColor('red')
        c.setLineWidth(2)
        c.setDash([5, 5])  # Пунктирная линия
        
        qr_x = width - qr_size - margin_qr
        qr_y = margin_qr
        
        c.rect(qr_x, qr_y, qr_size, qr_size)
        
        # Подпись для QR кода
        c.setFillColor('red')
        c.setFont('Helvetica-Bold', 10)
        c.drawString(qr_x, qr_y + qr_size + 0.2*cm, "QR Code Position")
        
        c.save()
        
        logger.info("✅ Test PDF created", 
                   filename=filename,
                   page_size=(width, height),
                   rotation=rotation,
                   title=title)
        
        return True
        
    except Exception as e:
        logger.error("❌ Error creating test PDF", 
                    filename=filename, error=str(e))
        return False

def generate_all_test_pdfs():
    """Генерирует все тестовые PDF файлы"""
    
    logger.info("🔧 Генерируем тестовые PDF-шаблоны для проверки системы координат")
    
    # Создаем директорию для тестовых файлов
    test_dir = "/app/test_pdfs"
    os.makedirs(test_dir, exist_ok=True)
    
    # Список тестовых файлов
    test_files = [
        {
            "filename": f"{test_dir}/A4_portrait_0deg.pdf",
            "page_size": A4,
            "rotation": 0,
            "title": "A4 Portrait 0°"
        },
        {
            "filename": f"{test_dir}/A4_portrait_90deg.pdf", 
            "page_size": A4,
            "rotation": 90,
            "title": "A4 Portrait 90°"
        },
        {
            "filename": f"{test_dir}/A4_portrait_180deg.pdf",
            "page_size": A4,
            "rotation": 180,
            "title": "A4 Portrait 180°"
        },
        {
            "filename": f"{test_dir}/A4_portrait_270deg.pdf",
            "page_size": A4,
            "rotation": 270,
            "title": "A4 Portrait 270°"
        },
        {
            "filename": f"{test_dir}/A3_landscape_0deg.pdf",
            "page_size": landscape(A3),
            "rotation": 0,
            "title": "A3 Landscape 0°"
        },
        {
            "filename": f"{test_dir}/A3_landscape_90deg.pdf",
            "page_size": landscape(A3),
            "rotation": 90,
            "title": "A3 Landscape 90°"
        }
    ]
    
    # Ожидаемые координаты QR кода для каждого файла
    expected_coordinates = {
        "A4_portrait_0deg.pdf": {"x": 612 - 99.225 - 28.35, "y": 28.35},  # bottom-right
        "A4_portrait_90deg.pdf": {"x": 792 - 28.35, "y": 28.35},  # после поворота
        "A4_portrait_180deg.pdf": {"x": 28.35, "y": 792 - 99.225 - 28.35},  # после поворота
        "A4_portrait_270deg.pdf": {"x": 28.35, "y": 612 - 28.35},  # после поворота
        "A3_landscape_0deg.pdf": {"x": 1191 - 99.225 - 28.35, "y": 28.35},  # bottom-right
        "A3_landscape_90deg.pdf": {"x": 842 - 28.35, "y": 28.35},  # после поворота
    }
    
    successful_files = 0
    
    for test_file in test_files:
        success = create_test_pdf(**test_file)
        if success:
            successful_files += 1
    
    # Создаем JSON файл с ожидаемыми координатами
    import json
    coordinates_file = f"{test_dir}/expected_coordinates.json"
    with open(coordinates_file, 'w', encoding='utf-8') as f:
        json.dump(expected_coordinates, f, indent=2, ensure_ascii=False)
    
    logger.info("📊 Результаты генерации тестовых PDF",
               total_files=len(test_files),
               successful_files=successful_files,
               coordinates_file=coordinates_file)
    
    logger.info("🏁 Генерация тестовых PDF завершена")
    
    return successful_files == len(test_files)

if __name__ == "__main__":
    generate_all_test_pdfs()
