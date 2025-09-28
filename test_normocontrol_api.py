#!/usr/bin/env python3
"""
Тестирование API нормоконтроля
"""

import asyncio
import json
import tempfile
from pathlib import Path

import httpx
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def create_test_pdf():
    """Создает тестовый PDF файл"""
    temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    
    c = canvas.Canvas(temp_file.name, pagesize=A4)
    
    # Добавляем текст на страницу
    c.drawString(100, 750, "Тестовый документ для нормоконтроля")
    c.drawString(100, 700, "Документ ID: TEST-NORMO-001")
    c.drawString(100, 650, "Ревизия: 1")
    c.drawString(100, 600, "Дата: 2024-09-25")
    
    # Добавляем основную надпись (штамп)
    c.rect(400, 50, 150, 80)  # Рамка штампа
    c.drawString(410, 110, "Основная надпись")
    c.drawString(410, 90, "Документ: TEST-001")
    c.drawString(410, 70, "Ревизия: 1")
    
    c.showPage()
    c.save()
    
    return temp_file.name

async def test_normocontrol_api():
    """Тестирует API нормоконтроля"""
    
    base_url = "http://localhost:8000/api/v1"
    
    # Создаем тестовый PDF
    test_pdf_path = create_test_pdf()
    
    try:
        async with httpx.AsyncClient() as client:
            print("🧪 Тестирование API нормоконтроля...")
            
            # 1. Тест получения требований
            print("\n1. Получение требований нормоконтроля...")
            try:
                response = await client.get(f"{base_url}/normocontrol/requirements")
                if response.status_code == 200:
                    requirements = response.json()
                    print(f"✅ Требования получены: {len(requirements['requirements'])} пунктов")
                    for i, req in enumerate(requirements['requirements'][:3], 1):
                        print(f"   {i}. {req}")
                else:
                    print(f"❌ Ошибка получения требований: {response.status_code}")
            except Exception as e:
                print(f"❌ Ошибка запроса требований: {e}")
            
            # 2. Тест валидации структуры документа
            print("\n2. Валидация структуры документа...")
            try:
                with open(test_pdf_path, 'rb') as f:
                    files = {'file': ('test_document.pdf', f, 'application/pdf')}
                    response = await client.post(f"{base_url}/normocontrol/validate", files=files)
                
                if response.status_code == 200:
                    validation = response.json()
                    print(f"✅ Валидация завершена:")
                    print(f"   - Страниц: {validation['pages_count']}")
                    print(f"   - Формат: {validation['format']}")
                    print(f"   - Ориентация: {validation['orientation']}")
                    print(f"   - Есть штамп: {validation['has_stamp']}")
                    print(f"   - Есть рамка: {validation['has_frame']}")
                else:
                    print(f"❌ Ошибка валидации: {response.status_code}")
            except Exception as e:
                print(f"❌ Ошибка запроса валидации: {e}")
            
            # 3. Тест загрузки для нормоконтроля
            print("\n3. Загрузка документа для нормоконтроля...")
            try:
                with open(test_pdf_path, 'rb') as f:
                    files = {'file': ('test_document.pdf', f, 'application/pdf')}
                    data = {
                        'enovia_id': 'TEST-NORMO-001',
                        'revision': '1',
                        'control_type': 'full'
                    }
                    response = await client.post(f"{base_url}/normocontrol/upload", files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    if result['success']:
                        control_result = result['result']
                        print(f"✅ Нормоконтроль завершен:")
                        print(f"   - Статус: {control_result['status'].upper()}")
                        print(f"   - Оценка: {control_result['score']}/100")
                        print(f"   - QR-кодов добавлено: {control_result['qr_codes_added']}")
                        print(f"   - Время обработки: {control_result['processing_time']}с")
                        print(f"   - Проблем найдено: {len(control_result['issues'])}")
                        print(f"   - Рекомендаций: {len(control_result['recommendations'])}")
                        
                        if control_result['issues']:
                            print("   Проблемы:")
                            for issue in control_result['issues']:
                                print(f"     - {issue['code']}: {issue['description']} ({issue['severity']})")
                        
                        if control_result['recommendations']:
                            print("   Рекомендации:")
                            for rec in control_result['recommendations']:
                                print(f"     - {rec}")
                    else:
                        print(f"❌ Нормоконтроль не удался: {result['message']}")
                else:
                    print(f"❌ Ошибка загрузки: {response.status_code}")
                    print(f"   Ответ: {response.text}")
            except Exception as e:
                print(f"❌ Ошибка запроса загрузки: {e}")
            
            # 4. Тест получения истории
            print("\n4. Получение истории нормоконтроля...")
            try:
                response = await client.get(f"{base_url}/normocontrol/history?limit=3")
                if response.status_code == 200:
                    history = response.json()
                    print(f"✅ История получена: {len(history['history'])} записей")
                    for i, record in enumerate(history['history'], 1):
                        print(f"   {i}. {record['document_id']} - {record['status']} ({record['score']}/100)")
                else:
                    print(f"❌ Ошибка получения истории: {response.status_code}")
            except Exception as e:
                print(f"❌ Ошибка запроса истории: {e}")
            
            # 5. Тест получения статуса
            print("\n5. Получение статуса нормоконтроля...")
            try:
                response = await client.get(f"{base_url}/normocontrol/status/test-control-id-123")
                if response.status_code == 200:
                    status = response.json()
                    if status['success']:
                        result = status['result']
                        print(f"✅ Статус получен:")
                        print(f"   - ID контроля: {result['control_id']}")
                        print(f"   - Статус: {result['status']}")
                        print(f"   - Оценка: {result['score']}/100")
                    else:
                        print(f"❌ Ошибка получения статуса: {status['message']}")
                else:
                    print(f"❌ Ошибка запроса статуса: {response.status_code}")
            except Exception as e:
                print(f"❌ Ошибка запроса статуса: {e}")
            
    finally:
        # Удаляем тестовый файл
        Path(test_pdf_path).unlink(missing_ok=True)

async def test_api_documentation():
    """Тестирует доступность документации API"""
    print("\n📚 Проверка документации API...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Проверяем OpenAPI схему
            response = await client.get("http://localhost:8000/openapi.json")
            if response.status_code == 200:
                openapi_schema = response.json()
                normocontrol_paths = [path for path in openapi_schema['paths'] if '/normocontrol' in path]
                print(f"✅ OpenAPI схема доступна")
                print(f"   Найдено эндпоинтов нормоконтроля: {len(normocontrol_paths)}")
                for path in normocontrol_paths:
                    print(f"     - {path}")
            else:
                print(f"❌ OpenAPI схема недоступна: {response.status_code}")
            
            # Проверяем Swagger UI
            response = await client.get("http://localhost:8000/docs")
            if response.status_code == 200:
                print("✅ Swagger UI доступен: http://localhost:8000/docs")
            else:
                print(f"❌ Swagger UI недоступен: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Ошибка проверки документации: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестирования API нормоконтроля")
    print("=" * 50)
    
    # Запускаем тесты
    asyncio.run(test_normocontrol_api())
    asyncio.run(test_api_documentation())
    
    print("\n" + "=" * 50)
    print("✅ Тестирование завершено!")
    print("\n📖 Документация API доступна по адресу:")
    print("   http://localhost:8000/docs")
    print("\n🔗 Эндпоинты нормоконтроля:")
    print("   POST /api/v1/normocontrol/upload - Загрузка документа")
    print("   GET  /api/v1/normocontrol/requirements - Требования")
    print("   GET  /api/v1/normocontrol/status/{id} - Статус контроля")
    print("   GET  /api/v1/normocontrol/history - История")
    print("   POST /api/v1/normocontrol/validate - Валидация структуры")