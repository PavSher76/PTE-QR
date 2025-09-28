#!/usr/bin/env python3
"""
Регресс-тесты для системы координат QR позиционирования
"""

import sys
import os
import json
from pathlib import Path

# Добавляем путь к приложению
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

def test_coordinate_regression():
    """Запускает регресс-тесты для системы координат"""
    
    logger.info("🧪 Запуск регресс-тестов системы координат")
    
    # Создаем PDFAnalyzer
    pdf_analyzer = PDFAnalyzer()
    
    # Тестовые файлы и ожидаемые координаты
    test_cases = [
        {
            "file": "/app/test_pdfs/A4_portrait_0deg.pdf",
            "expected": {"x": 500.8, "y": 12.0},  # bottom-right с margin 12pt
            "description": "A4 Portrait 0°"
        },
        {
            "file": "/app/test_pdfs/A4_portrait_90deg.pdf",
            "expected": {"x": 12.0, "y": 500.8},  # после поворота 90°
            "description": "A4 Portrait 90°"
        },
        {
            "file": "/app/test_pdfs/A4_portrait_180deg.pdf",
            "expected": {"x": 12.0, "y": 680.8},  # после поворота 180°
            "description": "A4 Portrait 180°"
        },
        {
            "file": "/app/test_pdfs/A4_portrait_270deg.pdf",
            "expected": {"x": 680.8, "y": 12.0},  # после поворота 270°
            "description": "A4 Portrait 270°"
        },
        {
            "file": "/app/test_pdfs/A3_landscape_0deg.pdf",
            "expected": {"x": 1063.8, "y": 12.0},  # A3 landscape bottom-right
            "description": "A3 Landscape 0°"
        },
        {
            "file": "/app/test_pdfs/A3_landscape_90deg.pdf",
            "expected": {"x": 12.0, "y": 1063.8},  # A3 landscape после поворота 90°
            "description": "A3 Landscape 90°"
        }
    ]
    
    results = []
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases):
        logger.info(f"🔍 Тест {i+1}/{total_tests}: {test_case['description']}")
        
        if not os.path.exists(test_case["file"]):
            logger.error(f"❌ Файл не найден: {test_case['file']}")
            results.append({
                "test": test_case["description"],
                "status": "FAILED",
                "error": "File not found"
            })
            continue
        
        try:
            # Анализируем PDF
            layout_info = pdf_analyzer.analyze_page_layout(test_case["file"], 0)
            
            if not layout_info:
                logger.error(f"❌ Не удалось проанализировать: {test_case['file']}")
                results.append({
                    "test": test_case["description"],
                    "status": "FAILED",
                    "error": "Layout analysis failed"
                })
                continue
            
            # Получаем информацию о координатах
            coordinate_info = layout_info.get("coordinate_info", {})
            page_box = {
                "width": layout_info["page_width"],
                "height": layout_info["page_height"]
            }
            rotation = layout_info["rotation"]
            
            # Рассчитываем позицию QR кода
            qr_size = 99.225  # 3.5 см в точках
            x, y = pdf_analyzer.compute_qr_anchor(
                page_box=page_box,
                qr_size=qr_size,
                rotation=rotation
            )
            
            # Сравниваем с ожидаемыми координатами
            expected = test_case["expected"]
            tolerance = 1.0  # Допуск ±1 pt
            
            x_diff = abs(x - expected["x"])
            y_diff = abs(y - expected["y"])
            
            if x_diff <= tolerance and y_diff <= tolerance:
                logger.info(f"✅ Тест пройден: {test_case['description']}")
                logger.info(f"   Ожидаемо: ({expected['x']}, {expected['y']})")
                logger.info(f"   Получено: ({x:.1f}, {y:.1f})")
                logger.info(f"   Разница: ({x_diff:.1f}, {y_diff:.1f})")
                
                results.append({
                    "test": test_case["description"],
                    "status": "PASSED",
                    "expected": expected,
                    "actual": {"x": x, "y": y},
                    "difference": {"x": x_diff, "y": y_diff}
                })
                passed_tests += 1
            else:
                logger.error(f"❌ Тест провален: {test_case['description']}")
                logger.error(f"   Ожидаемо: ({expected['x']}, {expected['y']})")
                logger.error(f"   Получено: ({x:.1f}, {y:.1f})")
                logger.error(f"   Разница: ({x_diff:.1f}, {y_diff:.1f})")
                
                results.append({
                    "test": test_case["description"],
                    "status": "FAILED",
                    "expected": expected,
                    "actual": {"x": x, "y": y},
                    "difference": {"x": x_diff, "y": y_diff}
                })
        
        except Exception as e:
            logger.error(f"❌ Ошибка в тесте: {test_case['description']}", error=str(e))
            results.append({
                "test": test_case["description"],
                "status": "FAILED",
                "error": str(e)
            })
    
    # Сохраняем результаты
    results_file = "/app/test_results/coordinate_regression_results.json"
    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": f"{(passed_tests/total_tests)*100:.1f}%"
            },
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    # Выводим итоги
    logger.info("📊 РЕЗУЛЬТАТЫ РЕГРЕСС-ТЕСТОВ")
    logger.info(f"Всего тестов: {total_tests}")
    logger.info(f"Пройдено: {passed_tests}")
    logger.info(f"Провалено: {total_tests - passed_tests}")
    logger.info(f"Успешность: {(passed_tests/total_tests)*100:.1f}%")
    logger.info(f"Результаты сохранены: {results_file}")
    
    return passed_tests == total_tests

def test_anchor_variations():
    """Тестирует разные якоря для одного PDF"""
    
    logger.info("🎯 Тестирование разных якорей")
    
    pdf_analyzer = PDFAnalyzer()
    test_file = "/app/test_pdfs/A4_portrait_0deg.pdf"
    
    if not os.path.exists(test_file):
        logger.error(f"❌ Тестовый файл не найден: {test_file}")
        return False
    
    # Анализируем PDF
    layout_info = pdf_analyzer.analyze_page_layout(test_file, 0)
    if not layout_info:
        logger.error("❌ Не удалось проанализировать PDF")
        return False
    
    page_box = {
        "width": layout_info["page_width"],
        "height": layout_info["page_height"]
    }
    rotation = layout_info["rotation"]
    qr_size = 99.225  # 3.5 см в точках
    
    # Тестируем разные якоря
    anchors = ["bottom-right", "bottom-left", "top-right", "top-left"]
    
    logger.info("🎯 Результаты для разных якорей:")
    logger.info(f"{'Якорь':<15} {'X (pt)':<10} {'Y (pt)':<10} {'X (см)':<10} {'Y (см)':<10}")
    logger.info("-" * 60)
    
    for anchor in anchors:
        x, y = pdf_analyzer.compute_qr_anchor(
            page_box=page_box,
            qr_size=qr_size,
            anchor=anchor,
            rotation=rotation
        )
        
        logger.info(f"{anchor:<15} {x:<10.1f} {y:<10.1f} {x/28.35:<10.2f} {y/28.35:<10.2f}")
    
    return True

def test_rotation_variations():
    """Тестирует разные повороты для одного PDF"""
    
    logger.info("🔄 Тестирование разных поворотов")
    
    pdf_analyzer = PDFAnalyzer()
    test_file = "/app/test_pdfs/A4_portrait_0deg.pdf"
    
    if not os.path.exists(test_file):
        logger.error(f"❌ Тестовый файл не найден: {test_file}")
        return False
    
    # Анализируем PDF
    layout_info = pdf_analyzer.analyze_page_layout(test_file, 0)
    if not layout_info:
        logger.error("❌ Не удалось проанализировать PDF")
        return False
    
    page_box = {
        "width": layout_info["page_width"],
        "height": layout_info["page_height"]
    }
    qr_size = 99.225  # 3.5 см в точках
    
    # Тестируем разные повороты
    rotations = [0, 90, 180, 270]
    
    logger.info("🔄 Результаты для разных поворотов (bottom-right якорь):")
    logger.info(f"{'Поворот':<10} {'X (pt)':<10} {'Y (pt)':<10} {'X (см)':<10} {'Y (см)':<10}")
    logger.info("-" * 60)
    
    for rotation in rotations:
        x, y = pdf_analyzer.compute_qr_anchor(
            page_box=page_box,
            qr_size=qr_size,
            rotation=rotation
        )
        
        logger.info(f"{rotation}°{'':<6} {x:<10.1f} {y:<10.1f} {x/28.35:<10.2f} {y/28.35:<10.2f}")
    
    return True

def main():
    """Основная функция"""
    
    logger.info("🚀 Запуск регресс-тестов системы координат QR позиционирования")
    
    # Проверяем наличие тестовых файлов
    test_dir = "/app/test_pdfs"
    if not os.path.exists(test_dir):
        logger.error(f"❌ Директория с тестовыми файлами не найдена: {test_dir}")
        logger.info("💡 Запустите сначала: python generate_test_pdfs.py")
        return 1
    
    success = True
    
    # Запускаем основные регресс-тесты
    success &= test_coordinate_regression()
    
    # Тестируем разные якоря
    success &= test_anchor_variations()
    
    # Тестируем разные повороты
    success &= test_rotation_variations()
    
    if success:
        logger.info("🎉 Все тесты пройдены успешно!")
        return 0
    else:
        logger.error("❌ Некоторые тесты провалены")
        return 1

if __name__ == "__main__":
    sys.exit(main())
