#!/usr/bin/env python3
"""
Скрипт для генерации 10 QR-кодов через API PTE-QR
Сохраняет сгенерированные QR-коды в папку test_results
"""

import base64
import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List

import requests

# Конфигурация API
API_BASE_URL = "http://localhost:8000/api/v1"
LOGIN_ENDPOINT = f"{API_BASE_URL}/auth/login"
QR_GENERATE_ENDPOINT = f"{API_BASE_URL}/qrcodes/"

# Тестовые данные для аутентификации
TEST_USER = {"username": "test_user", "password": "test_password"}

# Тестовые данные для документа
TEST_DOCUMENT = {
    "doc_uid": "TEST-DOC-001",
    "revision": "A",
    "pages": list(range(1, 11)),  # Страницы 1-10
    "style": "BLACK",
    "dpi": 300,
}

# Папка для сохранения результатов
OUTPUT_DIR = "test_results/qr_codes"
RESULTS_FILE = "test_results/qr_generation_results.json"


class QRCodeGenerator:
    """Класс для генерации QR-кодов через API"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

    def login(self, username: str, password: str) -> bool:
        """Аутентификация пользователя"""
        try:
            print(f"🔐 Выполняется вход пользователя: {username}")

            response = self.session.post(
                LOGIN_ENDPOINT,
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                print(f"✅ Успешная аутентификация")
                return True
            else:
                print(f"❌ Ошибка аутентификации: {response.status_code}")
                print(f"Ответ: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Ошибка при аутентификации: {e}")
            return False

    def generate_qr_codes(
        self,
        doc_uid: str,
        revision: str,
        pages: List[int],
        style: str = "BLACK",
        dpi: int = 300,
    ) -> Dict[str, Any]:
        """Генерация QR-кодов для указанных страниц"""
        try:
            if not self.token:
                raise Exception("Необходима аутентификация")

            print(f"📱 Генерация QR-кодов для документа {doc_uid}, ревизия {revision}")
            print(f"📄 Страницы: {pages}")

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }

            payload = {
                "doc_uid": doc_uid,
                "revision": revision,
                "pages": pages,
                "style": style,
                "dpi": dpi,
                "mode": "qr-only",
            }

            response = self.session.post(
                QR_GENERATE_ENDPOINT, json=payload, headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Успешно сгенерировано {len(data.get('items', []))} QR-кодов")
                return data
            else:
                print(f"❌ Ошибка генерации QR-кодов: {response.status_code}")
                print(f"Ответ: {response.text}")
                return {}

        except Exception as e:
            print(f"❌ Ошибка при генерации QR-кодов: {e}")
            return {}

    def save_qr_codes(self, qr_data: Dict[str, Any], output_dir: str) -> List[str]:
        """Сохранение QR-кодов в файлы"""
        saved_files = []

        try:
            # Создаем папку если не существует
            os.makedirs(output_dir, exist_ok=True)

            items = qr_data.get("items", [])
            doc_uid = qr_data.get("doc_uid", "unknown")
            revision = qr_data.get("revision", "unknown")

            print(f"💾 Сохранение QR-кодов в папку: {output_dir}")

            for item in items:
                page = item.get("page")
                format_type = item.get("format")
                data_base64 = item.get("data_base64")
                url = item.get("url")

                if not data_base64:
                    continue

                # Декодируем base64 данные
                try:
                    image_data = base64.b64decode(data_base64)
                except Exception as e:
                    print(f"❌ Ошибка декодирования base64 для страницы {page}: {e}")
                    continue

                # Формируем имя файла
                filename = (
                    f"{doc_uid}_rev{revision}_page{page:02d}.{format_type.lower()}"
                )
                filepath = os.path.join(output_dir, filename)

                # Сохраняем файл
                with open(filepath, "wb") as f:
                    f.write(image_data)

                saved_files.append(filepath)
                print(f"  ✅ Сохранен: {filename}")

            return saved_files

        except Exception as e:
            print(f"❌ Ошибка при сохранении QR-кодов: {e}")
            return saved_files

    def save_results_metadata(
        self, qr_data: Dict[str, Any], saved_files: List[str], output_file: str
    ) -> None:
        """Сохранение метаданных о генерации QR-кодов"""
        try:
            metadata = {
                "generation_time": datetime.now().isoformat(),
                "document": {
                    "doc_uid": qr_data.get("doc_uid"),
                    "revision": qr_data.get("revision"),
                    "mode": qr_data.get("mode"),
                },
                "generated_items": len(qr_data.get("items", [])),
                "saved_files": len(saved_files),
                "files": saved_files,
                "api_response": qr_data,
            }

            # Создаем папку если не существует
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            print(f"📋 Метаданные сохранены в: {output_file}")

        except Exception as e:
            print(f"❌ Ошибка при сохранении метаданных: {e}")


def main():
    """Основная функция скрипта"""
    print("🚀 Запуск скрипта генерации QR-кодов")
    print("=" * 50)

    # Создаем генератор QR-кодов
    generator = QRCodeGenerator(API_BASE_URL)

    # Аутентификация
    if not generator.login(TEST_USER["username"], TEST_USER["password"]):
        print("❌ Не удалось выполнить аутентификацию. Завершение работы.")
        return

    print()

    # Генерация QR-кодов
    qr_data = generator.generate_qr_codes(
        doc_uid=TEST_DOCUMENT["doc_uid"],
        revision=TEST_DOCUMENT["revision"],
        pages=TEST_DOCUMENT["pages"],
        style=TEST_DOCUMENT["style"],
        dpi=TEST_DOCUMENT["dpi"],
    )

    if not qr_data:
        print("❌ Не удалось сгенерировать QR-коды. Завершение работы.")
        return

    print()

    # Сохранение QR-кодов
    saved_files = generator.save_qr_codes(qr_data, OUTPUT_DIR)

    if saved_files:
        print(f"\n✅ Успешно сохранено {len(saved_files)} файлов QR-кодов")
    else:
        print("\n❌ Не удалось сохранить QR-коды")
        return

    print()

    # Сохранение метаданных
    generator.save_results_metadata(qr_data, saved_files, RESULTS_FILE)

    print()
    print("🎉 Генерация QR-кодов завершена успешно!")
    print(f"📁 QR-коды сохранены в: {OUTPUT_DIR}")
    print(f"📋 Метаданные сохранены в: {RESULTS_FILE}")

    # Выводим статистику
    items = qr_data.get("items", [])
    png_count = len([item for item in items if item.get("format") == "PNG"])
    svg_count = len([item for item in items if item.get("format") == "SVG"])

    print(f"\n📊 Статистика:")
    print(f"  • Всего сгенерировано элементов: {len(items)}")
    print(f"  • PNG файлов: {png_count}")
    print(f"  • SVG файлов: {svg_count}")
    print(f"  • Сохранено файлов: {len(saved_files)}")


if __name__ == "__main__":
    main()
