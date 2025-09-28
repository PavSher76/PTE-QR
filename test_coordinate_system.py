#!/usr/bin/env python3
"""
Тест новой системы координат и конфигурации QR позиционирования
"""

import sys
import os
sys.path.append('/app')

from app.utils.pdf_analyzer import PDFAnalyzer
from app.core.config import settings
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

def test_coordinate_system():
    """Тестирует новую систему координат и конфигурацию"""
    
    logger.info("🧪 Тестируем новую систему координат и конфигурацию QR позиционирования")
    
    # Показываем текущую конфигурацию
    logger.info("📋 Текущая конфигурация QR позиционирования",
               anchor=settings.QR_ANCHOR,
               margin_pt=settings.QR_MARGIN_PT,
               position_box=settings.QR_POSITION_BOX,
               respect_rotation=settings.QR_RESPECT_ROTATION,
               debug_frame=settings.QR_DEBUG_FRAME)
    
    # Инициализируем анализатор PDF
    pdf_analyzer = PDFAnalyzer()
    
    # Тестируем функцию compute_qr_anchor с разными параметрами
    test_cases = [
        {
            "name": "A4 Portrait (612x792 pt)",
            "page_box": {"width": 612.0, "height": 792.0},
            "qr_size": 99.225,  # 3.5 см в точках
            "rotation": 0
        },
        {
            "name": "A4 Portrait rotated 90°",
            "page_box": {"width": 612.0, "height": 792.0},
            "qr_size": 99.225,
            "rotation": 90
        },
        {
            "name": "A4 Portrait rotated 180°",
            "page_box": {"width": 612.0, "height": 792.0},
            "qr_size": 99.225,
            "rotation": 180
        },
        {
            "name": "A4 Portrait rotated 270°",
            "page_box": {"width": 612.0, "height": 792.0},
            "qr_size": 99.225,
            "rotation": 270
        },
        {
            "name": "A3 Landscape (842x1191 pt)",
            "page_box": {"width": 842.0, "height": 1191.0},
            "qr_size": 99.225,
            "rotation": 0
        },
        {
            "name": "A3 Landscape rotated 90°",
            "page_box": {"width": 842.0, "height": 1191.0},
            "qr_size": 99.225,
            "rotation": 90
        }
    ]
    
    # Тестируем разные якоря
    anchors = ["bottom-right", "bottom-left", "top-right", "top-left"]
    
    for test_case in test_cases:
        logger.info(f"🔍 Тестируем: {test_case['name']}")
        
        for anchor in anchors:
            x, y = pdf_analyzer.compute_qr_anchor(
                page_box=test_case["page_box"],
                qr_size=test_case["qr_size"],
                anchor=anchor,
                rotation=test_case["rotation"]
            )
            
            logger.info(f"  📍 Якорь {anchor}: ({x:.1f}, {y:.1f}) pt",
                       anchor=anchor,
                       x=x, y=y,
                       x_cm=round(x / 28.35, 2),
                       y_cm=round(y / 28.35, 2))
    
    # Тестируем с реальными файлами из test_docs (если доступны)
    test_files = [
        "/app/test_docs/3401-21089-РД-01-220-221-АР_4_0_RU_IFC.pdf",
        "/app/test_docs/Е110-0038-УКК_24.848-РД-01-02.12.032-АР_0_0_RU_IFC.pdf"
    ]
    
    for pdf_path in test_files:
        if os.path.exists(pdf_path):
            logger.info(f"📄 Тестируем реальный файл: {os.path.basename(pdf_path)}")
            
            try:
                # Анализируем макет страницы
                layout_info = pdf_analyzer.analyze_page_layout(pdf_path, 0)
                
                if layout_info:
                    coordinate_info = layout_info.get("coordinate_info", {})
                    
                    logger.info("📊 Результат анализа макета",
                               page_width=layout_info.get("page_width"),
                               page_height=layout_info.get("page_height"),
                               rotation=layout_info.get("rotation"),
                               is_landscape=layout_info.get("is_landscape"),
                               active_box_type=coordinate_info.get("active_box_type"),
                               position_box_config=coordinate_info.get("config", {}).get("position_box"))
                    
                    # Тестируем compute_qr_anchor с реальными данными
                    page_box = {
                        "width": layout_info["page_width"],
                        "height": layout_info["page_height"]
                    }
                    
                    x, y = pdf_analyzer.compute_qr_anchor(
                        page_box=page_box,
                        qr_size=99.225,  # 3.5 см
                        rotation=layout_info["rotation"]
                    )
                    
                    logger.info("🎯 Позиция QR кода для реального файла",
                               x=x, y=y,
                               x_cm=round(x / 28.35, 2),
                               y_cm=round(y / 28.35, 2),
                               anchor=settings.QR_ANCHOR,
                               rotation=layout_info["rotation"])
                    
                    # Включаем debug frame для визуальной проверки
                    if settings.QR_DEBUG_FRAME:
                        debug_file = pdf_analyzer._draw_debug_frame(
                            pdf_path, 0, x, y, 99.225, 99.225
                        )
                        if debug_file:
                            logger.info(f"🎨 Debug frame сохранен: {debug_file}")
                
            except Exception as e:
                logger.error(f"❌ Ошибка при тестировании файла {pdf_path}", error=str(e))
        else:
            logger.warning(f"⚠️ Файл не найден: {pdf_path}")
    
    logger.info("🏁 Тестирование системы координат завершено")

if __name__ == "__main__":
    test_coordinate_system()
