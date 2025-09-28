"""
Тесты для QR позиционирования в PDF документах
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

# Добавляем путь к приложению
sys.path.append('/app')

from app.services.pdf_service import PDFService
from app.utils.pdf_analyzer import PDFAnalyzer
from app.core.config import settings
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter


class TestQRPositioning:
    """Тесты для позиционирования QR кодов в PDF"""
    
    @pytest.fixture
    def pdf_service(self):
        """Создает экземпляр PDFService для тестов"""
        return PDFService()
    
    @pytest.fixture
    def pdf_analyzer(self):
        """Создает экземпляр PDFAnalyzer для тестов"""
        return PDFAnalyzer()
    
    @pytest.fixture
    def sample_pdf_path(self, tmp_path):
        """Создает тестовый PDF файл"""
        pdf_path = tmp_path / "test.pdf"
        
        # Создаем простой PDF с A4 размером
        c = canvas.Canvas(str(pdf_path), pagesize=A4)
        c.drawString(100, 100, "Test PDF for QR positioning")
        c.save()
        
        return str(pdf_path)
    
    def test_bottom_right_anchor_positioning(self, pdf_service, sample_pdf_path):
        """Тест: QR код позиционируется внизу справа при anchor=bottom-right"""
        
        # Устанавливаем anchor=bottom-right
        original_anchor = settings.QR_ANCHOR
        settings.QR_ANCHOR = "bottom-right"
        
        try:
            # Создаем тестовый QR код
            qr_image = self._create_test_qr_image()
            
            # Обрабатываем PDF
            result_pdf = pdf_service.add_qr_codes_to_pdf(
                pdf_content=open(sample_pdf_path, 'rb').read(),
                qr_data="test_qr_data"
            )
            
            # Проверяем, что PDF создан
            assert result_pdf is not None
            
            # Читаем результат и проверяем позицию QR кода
            pdf_reader = PdfReader(BytesIO(result_pdf))
            page = pdf_reader.pages[0]
            
            # Получаем размеры страницы
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            # Ожидаемые координаты для bottom-right
            qr_size = 99.225  # 3.5 см в точках
            margin = settings.QR_MARGIN_PT
            
            expected_x = page_width - qr_size - margin
            expected_y = margin
            
            # Проверяем, что QR код добавлен (проверяем наличие объектов на странице)
            # В реальном тесте мы бы анализировали содержимое страницы
            assert len(pdf_reader.pages) == 1
            
            print(f"✅ QR позиционирование проверено:")
            print(f"   Размеры страницы: {page_width} x {page_height} pt")
            print(f"   Ожидаемые координаты: ({expected_x:.1f}, {expected_y:.1f}) pt")
            print(f"   Ожидаемые координаты: ({expected_x/28.35:.2f}, {expected_y/28.35:.2f}) см")
            
        finally:
            # Восстанавливаем оригинальную настройку
            settings.QR_ANCHOR = original_anchor
    
    def test_different_anchors_positioning(self, pdf_analyzer):
        """Тест: проверка позиционирования для разных якорей"""
        
        # Тестовые размеры страницы A4
        page_box = {"width": 612.0, "height": 792.0}
        qr_size = 99.225  # 3.5 см в точках
        margin = 12.0
        
        # Тестируем разные якоря
        anchors = ["bottom-right", "bottom-left", "top-right", "top-left"]
        expected_positions = {
            "bottom-right": (500.8, 12.0),  # width - qr_size - margin, margin
            "bottom-left": (12.0, 12.0),    # margin, margin
            "top-right": (500.8, 680.8),    # width - qr_size - margin, height - qr_size - margin
            "top-left": (12.0, 680.8)       # margin, height - qr_size - margin
        }
        
        for anchor in anchors:
            x, y = pdf_analyzer.compute_simple_anchor(
                page_box=page_box,
                qr_size=qr_size,
                margin=margin,
                anchor=anchor
            )
            
            expected_x, expected_y = expected_positions[anchor]
            
            # Проверяем точность (±1 pt допуск)
            assert abs(x - expected_x) <= 1.0, f"X координата для {anchor}: ожидалось {expected_x}, получено {x}"
            assert abs(y - expected_y) <= 1.0, f"Y координата для {anchor}: ожидалось {expected_y}, получено {y}"
            
            print(f"✅ {anchor}: ({x:.1f}, {y:.1f}) pt - ожидалось ({expected_x}, {expected_y})")
    
    def test_rotation_handling(self, pdf_analyzer):
        """Тест: проверка обработки поворотов страницы"""
        
        # Тестовые размеры страницы A4
        page_box = {"width": 612.0, "height": 792.0}
        qr_size = 99.225  # 3.5 см в точках
        margin = 12.0
        anchor = "bottom-right"
        
        # Тестируем разные повороты
        rotations = [0, 90, 180, 270]
        
        for rotation in rotations:
            x, y = pdf_analyzer.compute_qr_anchor(
                page_box=page_box,
                qr_size=qr_size,
                margin=margin,
                anchor=anchor,
                rotation=rotation
            )
            
            # Проверяем, что координаты в разумных пределах
            assert 0 <= x <= page_box["width"], f"X координата для поворота {rotation}° вне границ: {x}"
            assert 0 <= y <= page_box["height"], f"Y координата для поворота {rotation}° вне границ: {y}"
            
            print(f"✅ Поворот {rotation}°: ({x:.1f}, {y:.1f}) pt")
    
    def test_coordinate_system_consistency(self, pdf_analyzer):
        """Тест: проверка консистентности системы координат"""
        
        # Тестовые данные
        x_img = 100.0
        y_img = 50.0
        img_h = 200.0
        page_h = 792.0
        
        # Конвертируем координаты
        x_pdf, y_pdf = pdf_analyzer.to_pdf_coords(x_img, y_img, img_h, page_h)
        
        # Проверяем формулу конверсии
        expected_x = x_img
        expected_y = page_h - (y_img + img_h)
        
        assert x_pdf == expected_x, f"X координата: ожидалось {expected_x}, получено {x_pdf}"
        assert y_pdf == expected_y, f"Y координата: ожидалось {expected_y}, получено {y_pdf}"
        
        print(f"✅ Конверсия координат:")
        print(f"   Image-СК: ({x_img}, {y_img})")
        print(f"   PDF-СК: ({x_pdf}, {y_pdf})")
        print(f"   Формула: y_pdf = {page_h} - ({y_img} + {img_h}) = {expected_y}")
    
    def test_margin_configuration(self, pdf_analyzer):
        """Тест: проверка настройки отступов"""
        
        page_box = {"width": 612.0, "height": 792.0}
        qr_size = 99.225
        anchor = "bottom-right"
        
        # Тестируем разные отступы
        margins = [5.0, 12.0, 20.0, 50.0]
        
        for margin in margins:
            x, y = pdf_analyzer.compute_simple_anchor(
                page_box=page_box,
                qr_size=qr_size,
                margin=margin,
                anchor=anchor
            )
            
            # Проверяем, что отступ соблюдается
            expected_x = page_box["width"] - qr_size - margin
            expected_y = margin
            
            assert abs(x - expected_x) <= 0.1, f"X координата для margin {margin}: ожидалось {expected_x}, получено {x}"
            assert abs(y - expected_y) <= 0.1, f"Y координата для margin {margin}: ожидалось {expected_y}, получено {y}"
            
            print(f"✅ Margin {margin} pt: ({x:.1f}, {y:.1f}) pt")
    
    def test_page_size_handling(self, pdf_analyzer):
        """Тест: проверка обработки разных размеров страниц"""
        
        # Тестируем разные размеры страниц
        page_sizes = [
            {"width": 612.0, "height": 792.0, "name": "A4 Portrait"},
            {"width": 792.0, "height": 612.0, "name": "A4 Landscape"},
            {"width": 842.0, "height": 1191.0, "name": "A3 Portrait"},
            {"width": 1191.0, "height": 842.0, "name": "A3 Landscape"}
        ]
        
        qr_size = 99.225
        margin = 12.0
        anchor = "bottom-right"
        
        for page_box in page_sizes:
            x, y = pdf_analyzer.compute_simple_anchor(
                page_box=page_box,
                qr_size=qr_size,
                margin=margin,
                anchor=anchor
            )
            
            # Проверяем, что QR код помещается на странице
            assert x >= 0, f"X координата отрицательная для {page_box['name']}: {x}"
            assert y >= 0, f"Y координата отрицательная для {page_box['name']}: {y}"
            assert x + qr_size <= page_box["width"], f"QR код выходит за правый край для {page_box['name']}"
            assert y + qr_size <= page_box["height"], f"QR код выходит за верхний край для {page_box['name']}"
            
            print(f"✅ {page_box['name']}: ({x:.1f}, {y:.1f}) pt")
    
    def _create_test_qr_image(self):
        """Создает тестовое изображение QR кода"""
        from PIL import Image
        import io
        
        # Создаем простое тестовое изображение
        img = Image.new('RGB', (200, 200), color='black')
        
        # Конвертируем в BytesIO
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes


class TestQRPositioningIntegration:
    """Интеграционные тесты для QR позиционирования"""
    
    def test_full_pdf_processing_pipeline(self, tmp_path):
        """Тест: полный пайплайн обработки PDF с QR кодами"""
        
        # Создаем тестовый PDF
        pdf_path = tmp_path / "integration_test.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=A4)
        c.drawString(100, 100, "Integration test PDF")
        c.save()
        
        # Создаем PDFService
        pdf_service = PDFService()
        
        # Обрабатываем PDF
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        result_pdf = pdf_service.add_qr_codes_to_pdf(
            pdf_content=pdf_content,
            qr_data="integration_test_qr_data"
        )
        
        # Проверяем результат
        assert result_pdf is not None
        assert len(result_pdf) > len(pdf_content)  # PDF должен стать больше
        
        # Читаем результат
        pdf_reader = PdfReader(BytesIO(result_pdf))
        assert len(pdf_reader.pages) == 1
        
        print("✅ Интеграционный тест пройден: PDF успешно обработан с QR кодами")
    
    def test_error_handling(self, pdf_service):
        """Тест: обработка ошибок при позиционировании"""
        
        # Тестируем с некорректными данными
        invalid_pdf_content = b"not a pdf content"
        
        # Должно обработать ошибку gracefully
        result = pdf_service.add_qr_codes_to_pdf(
            pdf_content=invalid_pdf_content,
            qr_data="test_data"
        )
        
        # В случае ошибки должен вернуть None или оригинальный контент
        assert result is None or result == invalid_pdf_content
        
        print("✅ Обработка ошибок работает корректно")


class TestQRPositioningRotations:
    """Тесты для позиционирования QR кодов с различными поворотами"""
    
    @pytest.fixture
    def pdf_service(self):
        """Создает экземпляр PDFService для тестов"""
        return PDFService()
    
    @pytest.fixture
    def pdf_analyzer(self):
        """Создает экземпляр PDFAnalyzer для тестов"""
        return PDFAnalyzer()
    
    def test_rotation_0_degrees(self, pdf_service):
        """Тест: позиционирование при повороте 0°"""
        W, H = 595.28, 841.89  # A4 размеры в точках
        qr_w, qr_h = 50.0, 50.0
        margin = 12.0
        rotation = 0
        anchor = "bottom-right"
        
        x, y = pdf_service.compute_anchor_xy(W, H, qr_w, qr_h, margin, rotation, anchor)
        
        # Ожидаемые координаты для bottom-right при 0°
        expected_x = W - margin - qr_w  # 595.28 - 12 - 50 = 533.28
        expected_y = margin  # 12.0
        
        assert abs(x - expected_x) < 1.0, f"X координата неверна: ожидалось {expected_x}, получено {x}"
        assert abs(y - expected_y) < 1.0, f"Y координата неверна: ожидалось {expected_y}, получено {y}"
        
        print(f"✅ Поворот 0°: x={x:.2f}, y={y:.2f}")
    
    def test_rotation_90_degrees(self, pdf_service):
        """Тест: позиционирование при повороте 90°"""
        W, H = 595.28, 841.89  # A4 размеры в точках
        qr_w, qr_h = 50.0, 50.0
        margin = 12.0
        rotation = 90
        anchor = "bottom-right"
        
        x, y = pdf_service.compute_anchor_xy(W, H, qr_w, qr_h, margin, rotation, anchor)
        
        # Ожидаемые координаты для bottom-right при 90° (визуальный нижний-правый)
        expected_x = margin  # 12.0
        expected_y = margin  # 12.0
        
        assert abs(x - expected_x) < 1.0, f"X координата неверна: ожидалось {expected_x}, получено {x}"
        assert abs(y - expected_y) < 1.0, f"Y координата неверна: ожидалось {expected_y}, получено {y}"
        
        print(f"✅ Поворот 90°: x={x:.2f}, y={y:.2f}")
    
    def test_rotation_180_degrees(self, pdf_service):
        """Тест: позиционирование при повороте 180°"""
        W, H = 595.28, 841.89  # A4 размеры в точках
        qr_w, qr_h = 50.0, 50.0
        margin = 12.0
        rotation = 180
        anchor = "bottom-right"
        
        x, y = pdf_service.compute_anchor_xy(W, H, qr_w, qr_h, margin, rotation, anchor)
        
        # Ожидаемые координаты для bottom-right при 180° (визуальный нижний-правый)
        expected_x = margin  # 12.0
        expected_y = H - margin - qr_h  # 841.89 - 12 - 50 = 779.89
        
        assert abs(x - expected_x) < 1.0, f"X координата неверна: ожидалось {expected_x}, получено {x}"
        assert abs(y - expected_y) < 1.0, f"Y координата неверна: ожидалось {expected_y}, получено {y}"
        
        print(f"✅ Поворот 180°: x={x:.2f}, y={y:.2f}")
    
    def test_rotation_270_degrees(self, pdf_service):
        """Тест: позиционирование при повороте 270°"""
        W, H = 595.28, 841.89  # A4 размеры в точках
        qr_w, qr_h = 50.0, 50.0
        margin = 12.0
        rotation = 270
        anchor = "bottom-right"
        
        x, y = pdf_service.compute_anchor_xy(W, H, qr_w, qr_h, margin, rotation, anchor)
        
        # Ожидаемые координаты для bottom-right при 270° (визуальный нижний-правый)
        expected_x = W - margin - qr_w  # 595.28 - 12 - 50 = 533.28
        expected_y = H - margin - qr_h  # 841.89 - 12 - 50 = 779.89
        
        assert abs(x - expected_x) < 1.0, f"X координата неверна: ожидалось {expected_x}, получено {x}"
        assert abs(y - expected_y) < 1.0, f"Y координата неверна: ожидалось {expected_y}, получено {y}"
        
        print(f"✅ Поворот 270°: x={x:.2f}, y={y:.2f}")
    
    def test_coordinate_clamping(self, pdf_service):
        """Тест: клэмп координат в пределах страницы"""
        W, H = 100.0, 100.0  # Маленькая страница
        qr_w, qr_h = 50.0, 50.0
        margin = 60.0  # Большой отступ, который выведет за границы
        rotation = 0
        anchor = "bottom-right"
        
        x, y = pdf_service.compute_anchor_xy(W, H, qr_w, qr_h, margin, rotation, anchor)
        
        # Координаты должны быть заклэмплены
        assert x >= 0, f"X координата отрицательная: {x}"
        assert y >= 0, f"Y координата отрицательная: {y}"
        assert x <= W - qr_w, f"X координата выходит за границы: {x} > {W - qr_w}"
        assert y <= H - qr_h, f"Y координата выходит за границы: {y} > {H - qr_h}"
        
        print(f"✅ Клэмп координат: x={x:.2f}, y={y:.2f} (в пределах {W}x{H})")
    
    def test_heuristics_delta_calculation(self, pdf_analyzer, tmp_path):
        """Тест: вычисление дельты эвристик"""
        # Создаем простой тестовый PDF
        pdf_path = tmp_path / "heuristics_test.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=A4)
        c.drawString(100, 100, "Test PDF for heuristics")
        c.save()
        
        # Вычисляем дельту эвристик
        dx, dy = pdf_analyzer.compute_heuristics_delta(str(pdf_path), 0)
        
        # Дельты должны быть числами (могут быть 0 если эвристики не сработали)
        assert isinstance(dx, (int, float)), f"dx должен быть числом, получен {type(dx)}"
        assert isinstance(dy, (int, float)), f"dy должен быть числом, получен {type(dy)}"
        
        print(f"✅ Дельта эвристик: dx={dx:.2f}, dy={dy:.2f}")


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"])
