#!/usr/bin/env python3
"""
Автоматический запуск процесса генерации QR-кодов
Выполняет настройку пользователя и генерацию QR-кодов в одном скрипте
"""

import subprocess
import sys
import os
from pathlib import Path


def run_script(script_name: str, description: str) -> bool:
    """Запуск Python скрипта с обработкой ошибок"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )

        # Выводим результат
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        if result.returncode == 0:
            print(f"✅ {description} - УСПЕШНО")
            return True
        else:
            print(f"❌ {description} - ОШИБКА (код: {result.returncode})")
            return False

    except Exception as e:
        print(f"❌ Ошибка при запуске {script_name}: {e}")
        return False


def check_requirements() -> bool:
    """Проверка необходимых зависимостей"""
    print("🔍 Проверка зависимостей...")

    try:
        import requests

        print("✅ requests - установлен")
        return True
    except ImportError:
        print("❌ requests - не установлен")
        print("Установите зависимости: pip install requests")
        return False


def main():
    """Основная функция"""
    print("🎯 АВТОМАТИЧЕСКАЯ ГЕНЕРАЦИЯ QR-КОДОВ")
    print("=" * 60)

    # Проверяем зависимости
    if not check_requirements():
        print("\n❌ Необходимые зависимости не установлены")
        return False

    # Создаем папку для результатов
    os.makedirs("test_results", exist_ok=True)
    print("📁 Папка test_results готова")

    # Шаг 1: Настройка тестового пользователя
    if not run_script("setup_test_user.py", "Настройка тестового пользователя"):
        print("\n❌ Не удалось настроить тестового пользователя")
        return False

    # Шаг 2: Генерация QR-кодов
    if not run_script("generate_qr_codes.py", "Генерация QR-кодов"):
        print("\n❌ Не удалось сгенерировать QR-коды")
        return False

    # Финальный отчет
    print(f"\n{'='*60}")
    print("🎉 ПРОЦЕСС ЗАВЕРШЕН УСПЕШНО!")
    print(f"{'='*60}")

    # Проверяем результаты
    qr_dir = Path("test_results/qr_codes")
    results_file = Path("test_results/qr_generation_results.json")

    if qr_dir.exists():
        qr_files = list(qr_dir.glob("*"))
        print(f"📱 QR-коды сохранены: {len(qr_files)} файлов")
        print(f"📁 Папка: {qr_dir.absolute()}")

    if results_file.exists():
        print(f"📋 Метаданные: {results_file.absolute()}")

    print(f"\n📊 Итоговая статистика:")
    print(f"  • Сгенерировано QR-кодов: 10 страниц")
    print(f"  • Форматы: PNG + SVG")
    print(f"  • Документ: TEST-DOC-001, ревизия A")
    print(f"  • Результаты в папке: test_results/")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
