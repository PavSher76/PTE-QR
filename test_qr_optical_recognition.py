#!/usr/bin/env python3
"""
Тесты с оптическим распознаванием места фактического размещения QR кода на листе
Проверяет работу функционала QR кодирования и размещения кода на странице
"""

import sys
import os
import asyncio
import tempfile
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import json
from datetime import datetime

# Добавляем путь к проекту
sys.path.append('.')

from app.core.logging import configure_logging
from app.services.pdf_service import PDFService
from app.services.qr_service import QRService
from app.utils.pdf_analyzer import PDFAnalyzer

# Импорты для оптического распознавания
import cv2
import numpy as np
from PIL import Image
import fitz  # PyMuPDF
import qrcode
from pyzbar import pyzbar
import io

class QROpticalRecognitionTester:
    """Класс для тестирования оптического распознавания QR кодов"""
    
    def __init__(self):
        self.logger = configure_logging()
        self.pdf_service = PDFService()
        self.qr_service = QRService()
        self.pdf_analyzer = PDFAnalyzer()
        self.test_results = []
        
    def extract_qr_codes_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Извлекает QR коды из PDF с их координатами"""
        qr_codes = []
        
        try:
            # Открываем PDF
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Конвертируем страницу в изображение с высоким разрешением
                mat = fitz.Matrix(3.0, 3.0)  # 3x увеличение для лучшего качества
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # Конвертируем в PIL Image
                pil_image = Image.open(io.BytesIO(img_data))
                img_array = np.array(pil_image)
                
                # Ищем QR коды на странице
                detected_qrs = pyzbar.decode(img_array)
                
                for qr in detected_qrs:
                    # Получаем координаты и данные QR кода
                    rect = qr.rect
                    qr_data = qr.data.decode('utf-8')
                    
                    # Конвертируем координаты в точки PDF (учитывая масштаб)
                    scale_factor = 3.0
                    x_points = rect.left / scale_factor
                    y_points = rect.top / scale_factor
                    width_points = rect.width / scale_factor
                    height_points = rect.height / scale_factor
                    
                    qr_info = {
                        'page_number': page_num + 1,
                        'data': qr_data,
                        'x_points': x_points,
                        'y_points': y_points,
                        'width_points': width_points,
                        'height_points': height_points,
                        'x_cm': round(x_points / 28.35, 2),
                        'y_cm': round(y_points / 28.35, 2),
                        'width_cm': round(width_points / 28.35, 2),
                        'height_cm': round(height_points / 28.35, 2),
                        'quality': qr.quality,
                        'type': qr.type
                    }
                    
                    qr_codes.append(qr_info)
                    
                    print(f"🔍 QR код обнаружен на странице {page_num + 1}:")
                    print(f"   📍 Позиция: ({qr_info['x_cm']:.2f} см, {qr_info['y_cm']:.2f} см)")
                    print(f"   📏 Размер: {qr_info['width_cm']:.2f} × {qr_info['height_cm']:.2f} см")
                    print(f"   📄 Данные: {qr_data[:50]}...")
                    print(f"   ⭐ Качество: {qr.quality}")
                    print()
            
            doc.close()
            
        except Exception as e:
            print(f"❌ Ошибка при извлечении QR кодов: {e}")
            
        return qr_codes
    
    def analyze_page_layout(self, pdf_path: str, page_number: int) -> Dict:
        """Анализирует макет страницы для определения элементов"""
        try:
            # Используем PDFAnalyzer для анализа страницы
            with open(pdf_path, 'rb') as f:
                pdf_content = f.read()
            analysis_result = self.pdf_analyzer.analyze_page_layout(pdf_content, page_number)
            
            print(f"📊 Анализ макета страницы {page_number}:")
            print(f"   🖼️  Ориентация: {'Landscape' if analysis_result.get('is_landscape') else 'Portrait'}")
            
            if analysis_result.get('stamp_top_edge'):
                print(f"   📋 Штамп: {analysis_result['stamp_top_edge']:.1f} точек от низа ({analysis_result['stamp_top_edge']/28.35:.2f} см)")
            
            if analysis_result.get('right_frame_edge'):
                print(f"   📐 Правая рамка: {analysis_result['right_frame_edge']:.1f} точек от левого края ({analysis_result['right_frame_edge']/28.35:.2f} см)")
                
            if analysis_result.get('bottom_frame_edge'):
                print(f"   📐 Нижняя рамка: {analysis_result['bottom_frame_edge']:.1f} точек от верха ({analysis_result['bottom_frame_edge']/28.35:.2f} см)")
            
            print()
            return analysis_result
            
        except Exception as e:
            print(f"❌ Ошибка при анализе макета: {e}")
            return {}
    
    def validate_qr_positioning(self, qr_codes: List[Dict], page_analysis: Dict) -> Dict:
        """Проверяет корректность позиционирования QR кодов"""
        validation_results = {
            'total_qr_codes': len(qr_codes),
            'correctly_positioned': 0,
            'positioning_errors': [],
            'summary': {}
        }
        
        for qr in qr_codes:
            page_num = qr['page_number']
            qr_x = qr['x_points']
            qr_y = qr['y_points']
            
            # Проверяем позиционирование относительно штампа
            if page_analysis.get('stamp_top_edge'):
                stamp_y = page_analysis['stamp_top_edge']
                expected_y = stamp_y + (0.5 * 28.35)  # 0.5 см от штампа
                
                # Допустимое отклонение ±1 см
                tolerance = 1.0 * 28.35
                y_diff = abs(qr_y - expected_y)
                
                if y_diff <= tolerance:
                    validation_results['correctly_positioned'] += 1
                    print(f"✅ QR код на странице {page_num}: позиция корректна (отклонение {y_diff/28.35:.2f} см)")
                else:
                    error = {
                        'page': page_num,
                        'expected_y_cm': expected_y / 28.35,
                        'actual_y_cm': qr_y / 28.35,
                        'deviation_cm': y_diff / 28.35,
                        'type': 'Y-positioning'
                    }
                    validation_results['positioning_errors'].append(error)
                    print(f"❌ QR код на странице {page_num}: неправильная Y позиция (отклонение {y_diff/28.35:.2f} см)")
            
            # Проверяем позиционирование относительно правой рамки
            if page_analysis.get('right_frame_edge'):
                frame_x = page_analysis['right_frame_edge']
                expected_x = frame_x - (1.0 * 28.35) - qr['width_points']  # 1 см от правой рамки
                
                # Допустимое отклонение ±1 см
                tolerance = 1.0 * 28.35
                x_diff = abs(qr_x - expected_x)
                
                if x_diff <= tolerance:
                    print(f"✅ QR код на странице {page_num}: X позиция корректна (отклонение {x_diff/28.35:.2f} см)")
                else:
                    error = {
                        'page': page_num,
                        'expected_x_cm': expected_x / 28.35,
                        'actual_x_cm': qr_x / 28.35,
                        'deviation_cm': x_diff / 28.35,
                        'type': 'X-positioning'
                    }
                    validation_results['positioning_errors'].append(error)
                    print(f"❌ QR код на странице {page_num}: неправильная X позиция (отклонение {x_diff/28.35:.2f} см)")
        
        # Подсчитываем статистику
        validation_results['summary'] = {
            'accuracy_percentage': (validation_results['correctly_positioned'] / max(validation_results['total_qr_codes'], 1)) * 100,
            'total_errors': len(validation_results['positioning_errors']),
            'y_errors': len([e for e in validation_results['positioning_errors'] if e['type'] == 'Y-positioning']),
            'x_errors': len([e for e in validation_results['positioning_errors'] if e['type'] == 'X-positioning'])
        }
        
        return validation_results
    
    def test_qr_generation_and_placement(self, test_document_path: str) -> Dict:
        """Основной тест генерации и размещения QR кодов"""
        print("🚀 Запуск теста оптического распознавания QR кодов")
        print("=" * 60)
        
        test_result = {
            'test_name': 'QR Optical Recognition Test',
            'timestamp': datetime.now().isoformat(),
            'input_document': test_document_path,
            'qr_codes_found': [],
            'page_analysis': {},
            'validation_results': {},
            'success': False
        }
        
        try:
            # 1. Читаем исходный документ
            print(f"📄 Загружаем тестовый документ: {test_document_path}")
            with open(test_document_path, 'rb') as f:
                original_pdf_content = f.read()
            
            print(f"   Размер документа: {len(original_pdf_content)} байт")
            
            # 2. Генерируем QR коды и добавляем в PDF
            print("\n🔧 Генерируем QR коды и добавляем в PDF...")
            result = asyncio.run(self.pdf_service.add_qr_codes_to_pdf(
                original_pdf_content,
                'OPTICAL-TEST',
                '0',
                '/tmp/optical_test.pdf'
            ))
            
            processed_pdf_content, qr_data_list = result
            print(f"   Добавлено QR кодов: {len(qr_data_list)}")
            
            # 3. Сохраняем обработанный PDF
            output_path = '/tmp/processed_optical_test.pdf'
            with open(output_path, 'wb') as f:
                f.write(processed_pdf_content)
            
            print(f"   Обработанный PDF сохранен: {output_path}")
            
            # 4. Извлекаем QR коды с помощью оптического распознавания
            print("\n🔍 Извлекаем QR коды с помощью оптического распознавания...")
            detected_qr_codes = self.extract_qr_codes_from_pdf(output_path)
            test_result['qr_codes_found'] = detected_qr_codes
            
            print(f"   Обнаружено QR кодов: {len(detected_qr_codes)}")
            
            # 5. Анализируем макет страниц
            print("\n📊 Анализируем макет страниц...")
            page_analysis = {}
            for qr in detected_qr_codes:
                page_num = qr['page_number']
                if page_num not in page_analysis:
                    analysis = self.analyze_page_layout(output_path, page_num - 1)  # 0-based index
                    page_analysis[page_num] = analysis
            
            test_result['page_analysis'] = page_analysis
            
            # 6. Проверяем корректность позиционирования
            print("\n✅ Проверяем корректность позиционирования...")
            validation_results = self.validate_qr_positioning(detected_qr_codes, page_analysis)
            test_result['validation_results'] = validation_results
            
            # 7. Выводим итоговую статистику
            print("\n📈 ИТОГОВАЯ СТАТИСТИКА:")
            print("=" * 40)
            print(f"📄 Всего QR кодов обнаружено: {len(detected_qr_codes)}")
            print(f"✅ Корректно позиционированы: {validation_results['correctly_positioned']}")
            print(f"❌ Ошибки позиционирования: {len(validation_results['positioning_errors'])}")
            print(f"📊 Точность позиционирования: {validation_results['summary']['accuracy_percentage']:.1f}%")
            
            if validation_results['positioning_errors']:
                print(f"\n🔍 ДЕТАЛИ ОШИБОК:")
                for error in validation_results['positioning_errors']:
                    print(f"   Страница {error['page']}: {error['type']} - отклонение {error['deviation_cm']:.2f} см")
            
            # 8. Определяем успешность теста
            test_result['success'] = (
                len(detected_qr_codes) > 0 and 
                validation_results['summary']['accuracy_percentage'] >= 80.0
            )
            
            if test_result['success']:
                print(f"\n🎉 ТЕСТ ПРОЙДЕН УСПЕШНО!")
            else:
                print(f"\n⚠️  ТЕСТ НЕ ПРОЙДЕН!")
            
        except Exception as e:
            print(f"❌ Ошибка во время теста: {e}")
            test_result['error'] = str(e)
        
        return test_result
    
    def run_comprehensive_test(self, test_documents: List[str]) -> List[Dict]:
        """Запускает комплексный тест на нескольких документах"""
        print("🧪 ЗАПУСК КОМПЛЕКСНОГО ТЕСТА ОПТИЧЕСКОГО РАСПОЗНАВАНИЯ")
        print("=" * 70)
        
        all_results = []
        
        for i, doc_path in enumerate(test_documents, 1):
            print(f"\n📋 ТЕСТ {i}/{len(test_documents)}: {os.path.basename(doc_path)}")
            print("-" * 50)
            
            if not os.path.exists(doc_path):
                print(f"❌ Документ не найден: {doc_path}")
                continue
            
            result = self.test_qr_generation_and_placement(doc_path)
            all_results.append(result)
            
            # Сохраняем результат в файл
            result_file = f"/tmp/optical_test_result_{i}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Результат сохранен: {result_file}")
        
        # Генерируем сводный отчет
        self.generate_summary_report(all_results)
        
        return all_results
    
    def generate_summary_report(self, results: List[Dict]):
        """Генерирует сводный отчет по всем тестам"""
        print("\n" + "=" * 70)
        print("📊 СВОДНЫЙ ОТЧЕТ ПО ВСЕМ ТЕСТАМ")
        print("=" * 70)
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.get('success', False))
        total_qr_codes = sum(len(r.get('qr_codes_found', [])) for r in results)
        
        print(f"📈 Общая статистика:")
        print(f"   🧪 Всего тестов: {total_tests}")
        print(f"   ✅ Успешных тестов: {successful_tests}")
        print(f"   📄 Всего QR кодов: {total_qr_codes}")
        print(f"   📊 Процент успеха: {(successful_tests/total_tests)*100:.1f}%")
        
        # Детальная статистика по каждому тесту
        for i, result in enumerate(results, 1):
            doc_name = os.path.basename(result.get('input_document', f'Test {i}'))
            qr_count = len(result.get('qr_codes_found', []))
            success = result.get('success', False)
            accuracy = result.get('validation_results', {}).get('summary', {}).get('accuracy_percentage', 0)
            
            status = "✅ ПРОЙДЕН" if success else "❌ НЕ ПРОЙДЕН"
            print(f"   📋 {doc_name}: {qr_count} QR кодов, точность {accuracy:.1f}% - {status}")
        
        # Сохраняем сводный отчет
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'total_qr_codes': total_qr_codes,
            'success_rate': (successful_tests/total_tests)*100,
            'detailed_results': results
        }
        
        summary_file = '/tmp/optical_test_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Сводный отчет сохранен: {summary_file}")


def main():
    """Основная функция для запуска тестов"""
    print("🔬 СИСТЕМА ТЕСТИРОВАНИЯ ОПТИЧЕСКОГО РАСПОЗНАВАНИЯ QR КОДОВ")
    print("=" * 70)
    
    # Создаем тестер
    tester = QROpticalRecognitionTester()
    
    # Определяем тестовые документы
    test_documents = [
        '/app/tmp/processed_pdfs/DOC-001_0_0daf5415.pdf',
        '/app/tmp/processed_pdfs/DOC-001_Y_FIXED.pdf',
        '/app/tmp/processed_pdfs/DOC-001_EXPANDED_REGION.pdf'
    ]
    
    # Запускаем комплексный тест
    results = tester.run_comprehensive_test(test_documents)
    
    print(f"\n🏁 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print(f"📊 Результаты: {len(results)} тестов выполнено")


if __name__ == "__main__":
    main()
