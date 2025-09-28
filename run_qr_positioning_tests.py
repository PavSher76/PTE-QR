#!/usr/bin/env python3
"""
Скрипт для запуска тестов QR позиционирования
"""

import sys
import os
import subprocess
from pathlib import Path

def run_tests():
    """Запускает все тесты QR позиционирования"""
    
    print("🚀 Запуск тестов QR позиционирования")
    print("=" * 50)
    
    # Создаем директорию для результатов
    os.makedirs('/app/tmp', exist_ok=True)
    
    # Запускаем pytest тесты
    print("📋 Запуск pytest тестов...")
    try:
        result = subprocess.run([
            'python', '-m', 'pytest', 
            'backend/tests/test_qr_positioning.py', 
            '-v', '--tb=short'
        ], capture_output=True, text=True, cwd='/app')
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ pytest тесты пройдены успешно!")
        else:
            print("❌ pytest тесты провалены")
            
    except Exception as e:
        print(f"❌ Ошибка при запуске pytest: {e}")
    
    print("\n" + "=" * 50)
    
    # Запускаем тест верификации
    print("🎯 Запуск теста верификации позиционирования...")
    try:
        result = subprocess.run([
            'python', 'test_qr_positioning_verification.py'
        ], capture_output=True, text=True, cwd='/app')
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Тест верификации пройден успешно!")
        else:
            print("❌ Тест верификации провален")
            
    except Exception as e:
        print(f"❌ Ошибка при запуске теста верификации: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Тестирование завершено")
    
    # Показываем созданные файлы
    tmp_dir = Path('/app/tmp')
    if tmp_dir.exists():
        print("\n📁 Созданные файлы:")
        for file in tmp_dir.glob('*.pdf'):
            print(f"   - {file.name}")
        for file in tmp_dir.glob('*.json'):
            print(f"   - {file.name}")

if __name__ == "__main__":
    run_tests()
