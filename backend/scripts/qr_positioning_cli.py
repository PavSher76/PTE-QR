#!/usr/bin/env python3
"""
CLI для тестирования и настройки QR позиционирования
"""

import sys
import os
import argparse
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

def analyze_pdf(pdf_path: str, page_number: int = 0, **kwargs):
    """Анализирует PDF и показывает информацию о координатах"""
    
    if not os.path.exists(pdf_path):
        logger.error("❌ PDF файл не найден", pdf_path=pdf_path)
        return False
    
    logger.info("🔍 Анализируем PDF файл", pdf_path=pdf_path, page_number=page_number)
    
    pdf_analyzer = PDFAnalyzer()
    
    try:
        # Анализируем макет страницы
        layout_info = pdf_analyzer.analyze_page_layout(pdf_path, page_number)
        
        if not layout_info:
            logger.error("❌ Не удалось проанализировать макет страницы")
            return False
        
        # Показываем информацию о координатах
        coordinate_info = layout_info.get("coordinate_info", {})
        
        print("\n" + "="*60)
        print("📊 ИНФОРМАЦИЯ О КООРДИНАТАХ СТРАНИЦЫ")
        print("="*60)
        
        print(f"📄 Страница: {page_number}")
        print(f"📏 Размеры: {layout_info['page_width']:.1f} x {layout_info['page_height']:.1f} pt")
        print(f"🔄 Поворот: {layout_info['rotation']}°")
        print(f"📐 Ориентация: {'Альбомная' if layout_info['is_landscape'] else 'Портретная'}")
        print(f"📦 Активный бокс: {coordinate_info.get('active_box_type', 'N/A')}")
        
        # Информация о MediaBox
        mediabox = coordinate_info.get("mediabox", {})
        print(f"\n📦 MediaBox:")
        print(f"   Размеры: {mediabox.get('width', 0):.1f} x {mediabox.get('height', 0):.1f} pt")
        print(f"   Координаты: ({mediabox.get('x0', 0):.1f}, {mediabox.get('y0', 0):.1f}) - ({mediabox.get('x1', 0):.1f}, {mediabox.get('y1', 0):.1f})")
        
        # Информация о CropBox (если есть)
        cropbox = coordinate_info.get("cropbox")
        if cropbox:
            print(f"\n✂️ CropBox:")
            print(f"   Размеры: {cropbox.get('width', 0):.1f} x {cropbox.get('height', 0):.1f} pt")
            print(f"   Координаты: ({cropbox.get('x0', 0):.1f}, {cropbox.get('y0', 0):.1f}) - ({cropbox.get('x1', 0):.1f}, {cropbox.get('y1', 0):.1f})")
        
        # Информация о конфигурации
        config = coordinate_info.get("config", {})
        print(f"\n⚙️ Конфигурация:")
        print(f"   Бокс для позиционирования: {config.get('position_box', 'N/A')}")
        print(f"   Учет поворота: {config.get('respect_rotation', 'N/A')}")
        
        # Рассчитываем позицию QR кода
        page_box = {
            "width": layout_info["page_width"],
            "height": layout_info["page_height"]
        }
        
        qr_size = 99.225  # 3.5 см в точках
        
        x, y = pdf_analyzer.compute_qr_anchor(
            page_box=page_box,
            qr_size=qr_size,
            rotation=layout_info["rotation"]
        )
        
        print(f"\n🎯 ПОЗИЦИЯ QR КОДА")
        print("="*60)
        print(f"📍 Координаты: ({x:.1f}, {y:.1f}) pt")
        print(f"📏 В сантиметрах: ({x/28.35:.2f}, {y/28.35:.2f}) см")
        print(f"🔧 Якорь: {settings.QR_ANCHOR}")
        print(f"📏 Отступ: {settings.QR_MARGIN_PT} pt")
        print(f"🔄 Учет поворота: {settings.QR_RESPECT_ROTATION}")
        
        # Отрисовываем debug рамку если включено
        if settings.QR_DEBUG_FRAME:
            debug_file = pdf_analyzer._draw_debug_frame(pdf_path, page_number, x, y, qr_size, qr_size)
            if debug_file:
                print(f"🎨 Debug рамка сохранена: {debug_file}")
        
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.error("❌ Ошибка при анализе PDF", error=str(e))
        return False

def test_coordinates(pdf_path: str, **kwargs):
    """Тестирует расчет координат для разных якорей и поворотов"""
    
    if not os.path.exists(pdf_path):
        logger.error("❌ PDF файл не найден", pdf_path=pdf_path)
        return False
    
    logger.info("🧪 Тестируем расчет координат", pdf_path=pdf_path)
    
    pdf_analyzer = PDFAnalyzer()
    
    try:
        # Анализируем макет страницы
        layout_info = pdf_analyzer.analyze_page_layout(pdf_path, 0)
        
        if not layout_info:
            logger.error("❌ Не удалось проанализировать макет страницы")
            return False
        
        page_box = {
            "width": layout_info["page_width"],
            "height": layout_info["page_height"]
        }
        
        qr_size = 99.225  # 3.5 см в точках
        rotation = layout_info["rotation"]
        
        print("\n" + "="*80)
        print("🧪 ТЕСТИРОВАНИЕ РАСЧЕТА КООРДИНАТ")
        print("="*80)
        print(f"📄 Файл: {os.path.basename(pdf_path)}")
        print(f"📏 Размеры страницы: {page_box['width']:.1f} x {page_box['height']:.1f} pt")
        print(f"🔄 Поворот страницы: {rotation}°")
        print(f"📏 Размер QR кода: {qr_size:.1f} pt ({qr_size/28.35:.1f} см)")
        print("="*80)
        
        # Тестируем разные якоря
        anchors = ["bottom-right", "bottom-left", "top-right", "top-left"]
        
        print(f"{'Якорь':<15} {'X (pt)':<10} {'Y (pt)':<10} {'X (см)':<10} {'Y (см)':<10}")
        print("-" * 80)
        
        for anchor in anchors:
            x, y = pdf_analyzer.compute_qr_anchor(
                page_box=page_box,
                qr_size=qr_size,
                anchor=anchor,
                rotation=rotation
            )
            
            print(f"{anchor:<15} {x:<10.1f} {y:<10.1f} {x/28.35:<10.2f} {y/28.35:<10.2f}")
        
        print("="*80)
        
        return True
        
    except Exception as e:
        logger.error("❌ Ошибка при тестировании координат", error=str(e))
        return False

def show_config(**kwargs):
    """Показывает текущую конфигурацию"""
    
    print("\n" + "="*60)
    print("⚙️ ТЕКУЩАЯ КОНФИГУРАЦИЯ QR ПОЗИЦИОНИРОВАНИЯ")
    print("="*60)
    
    print(f"🎯 Якорь: {settings.QR_ANCHOR}")
    print(f"📏 Отступ: {settings.QR_MARGIN_PT} pt ({settings.QR_MARGIN_PT/28.35:.2f} см)")
    print(f"📦 Бокс для позиционирования: {settings.QR_POSITION_BOX}")
    print(f"🔄 Учет поворота: {settings.QR_RESPECT_ROTATION}")
    print(f"🎨 Debug рамка: {settings.QR_DEBUG_FRAME}")
    
    print("\n📋 Доступные якоря:")
    print("   - bottom-right: нижний правый угол")
    print("   - bottom-left: нижний левый угол")
    print("   - top-right: верхний правый угол")
    print("   - top-left: верхний левый угол")
    
    print("\n📦 Доступные боксы:")
    print("   - media: MediaBox (по умолчанию)")
    print("   - crop: CropBox (если доступен)")
    
    print("="*60)
    
    return True

def main():
    """Основная функция CLI"""
    
    parser = argparse.ArgumentParser(
        description="CLI для тестирования и настройки QR позиционирования",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Показать текущую конфигурацию
  python qr_positioning_cli.py --show-config

  # Анализировать PDF файл
  python qr_positioning_cli.py --analyze /path/to/file.pdf

  # Анализировать конкретную страницу
  python qr_positioning_cli.py --analyze /path/to/file.pdf --page 2

  # Тестировать расчет координат
  python qr_positioning_cli.py --test-coordinates /path/to/file.pdf

  # Анализировать с настройкой якоря
  python qr_positioning_cli.py --analyze /path/to/file.pdf --anchor bottom-left

  # Анализировать с настройкой отступа
  python qr_positioning_cli.py --analyze /path/to/file.pdf --margin-pt 20

  # Анализировать с отключением учета поворота
  python qr_positioning_cli.py --analyze /path/to/file.pdf --no-rotation

  # Включить debug рамку
  python qr_positioning_cli.py --analyze /path/to/file.pdf --debug-frame
        """
    )
    
    # Основные команды
    parser.add_argument('--show-config', action='store_true',
                       help='Показать текущую конфигурацию')
    parser.add_argument('--analyze', type=str, metavar='PDF_FILE',
                       help='Анализировать PDF файл')
    parser.add_argument('--test-coordinates', type=str, metavar='PDF_FILE',
                       help='Тестировать расчет координат для разных якорей')
    
    # Параметры анализа
    parser.add_argument('--page', type=int, default=0,
                       help='Номер страницы для анализа (по умолчанию: 0)')
    
    # Параметры конфигурации
    parser.add_argument('--anchor', type=str, 
                       choices=['bottom-right', 'bottom-left', 'top-right', 'top-left'],
                       help='Якорь для позиционирования QR кода')
    parser.add_argument('--margin-pt', type=float,
                       help='Отступ в точках')
    parser.add_argument('--position-box', type=str,
                       choices=['media', 'crop'],
                       help='Бокс для позиционирования (media или crop)')
    parser.add_argument('--respect-rotation', action='store_true',
                       help='Учитывать поворот страницы')
    parser.add_argument('--no-rotation', action='store_true',
                       help='Не учитывать поворот страницы')
    parser.add_argument('--debug-frame', action='store_true',
                       help='Включить отрисовку debug рамки')
    
    args = parser.parse_args()
    
    # Применяем параметры конфигурации
    if args.anchor:
        settings.QR_ANCHOR = args.anchor
    if args.margin_pt:
        settings.QR_MARGIN_PT = args.margin_pt
    if args.position_box:
        settings.QR_POSITION_BOX = args.position_box
    if args.respect_rotation:
        settings.QR_RESPECT_ROTATION = True
    if args.no_rotation:
        settings.QR_RESPECT_ROTATION = False
    if args.debug_frame:
        settings.QR_DEBUG_FRAME = True
    
    # Выполняем команды
    success = True
    
    if args.show_config:
        success &= show_config()
    
    if args.analyze:
        success &= analyze_pdf(args.analyze, args.page)
    
    if args.test_coordinates:
        success &= test_coordinates(args.test_coordinates)
    
    if not any([args.show_config, args.analyze, args.test_coordinates]):
        parser.print_help()
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
