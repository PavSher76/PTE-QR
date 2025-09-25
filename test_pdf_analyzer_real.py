#!/usr/bin/env python3
"""
Тестовый скрипт для проверки PDF анализатора с реальными файлами
"""

import sys
import os
sys.path.append('backend')

from app.utils.pdf_analyzer import PDFAnalyzer

def test_pdf_analyzer():
    """Тестирует PDF анализатор на реальных файлах"""
    
    print("=== Тест PDF анализатора на реальных файлах ===")
    
    # Путь к тестовым документам
    test_docs_dir = "../test_docs"
    
    if not os.path.exists(test_docs_dir):
        print(f"❌ Директория с тестовыми документами не найдена: {test_docs_dir}")
        return
    
    # Создаем анализатор
    analyzer = PDFAnalyzer()
    
    # Получаем список тестовых PDF файлов
    pdf_files = [f for f in os.listdir(test_docs_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"❌ PDF файлы не найдены в директории: {test_docs_dir}")
        return
    
    print(f"📁 Найдено PDF файлов: {len(pdf_files)}")
    print(f"📄 Файлы: {pdf_files}")
    print()
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(test_docs_dir, pdf_file)
        print(f"🔍 Анализируем файл: {pdf_file}")
        
        try:
            # Анализируем первую страницу каждого PDF
            layout_info = analyzer.analyze_page_layout(pdf_path, 0)
            
            print(f"  📊 Результаты анализа:")
            print(f"    - Номер страницы: {layout_info.get('page_number', 'N/A')}")
            print(f"    - Размеры: {layout_info.get('page_width', 'N/A')} x {layout_info.get('page_height', 'N/A')} точек")
            print(f"    - Ориентация: {'Landscape' if layout_info.get('is_landscape') else 'Portrait'}")
            print(f"    - Верхний край штампа: {layout_info.get('stamp_top_edge', 'не найден')}")
            print(f"    - Правый край рамки: {layout_info.get('right_frame_edge', 'не найден')}")
            print(f"    - Нижний край рамки: {layout_info.get('bottom_frame_edge', 'не найден')}")
            
            # Тестируем отдельные функции для landscape страниц
            if layout_info.get("is_landscape"):
                print(f"  🔍 Детальная детекция для landscape страницы:")
                
                stamp_top = analyzer.detect_stamp_top_edge_landscape(pdf_path, 0)
                print(f"    - Детекция штампа: {stamp_top if stamp_top else 'не найден'}")
                
                right_frame = analyzer.detect_right_frame_edge(pdf_path, 0)
                print(f"    - Детекция правой рамки: {right_frame if right_frame else 'не найден'}")
                
                bottom_frame = analyzer.detect_bottom_frame_edge(pdf_path, 0)
                print(f"    - Детекция нижней рамки: {bottom_frame if bottom_frame else 'не найден'}")
            
            print(f"  ✅ Анализ завершен успешно")
            
        except Exception as e:
            print(f"  ❌ Ошибка при анализе: {str(e)}")
        
        print()

if __name__ == "__main__":
    test_pdf_analyzer()
    print("=== Тестирование завершено ===")
