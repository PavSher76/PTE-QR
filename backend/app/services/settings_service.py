"""
Settings service for managing system configuration
"""

import json
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.settings import SystemSettings

class SettingsService:
    def __init__(self, db: Session):
        self.db = db

    async def get_settings(self) -> Dict[str, Any]:
        """
        Get current system settings
        """
        # Получаем настройки из базы данных
        settings = self.db.query(SystemSettings).first()
        
        if not settings:
            # Если настроек нет, создаем дефолтные
            default_settings = self._get_default_settings()
            settings = SystemSettings(
                settings_data=json.dumps(default_settings)
            )
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        
        # Парсим JSON данные
        settings_data = json.loads(settings.settings_data) if settings.settings_data else {}
        
        # Объединяем с дефолтными настройками
        default_settings = self._get_default_settings()
        merged_settings = {**default_settings, **settings_data}
        
        return merged_settings

    async def update_settings(self, new_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update system settings
        """
        # Валидируем настройки
        validated_settings = self._validate_settings(new_settings)
        
        # Получаем существующие настройки
        settings = self.db.query(SystemSettings).first()
        
        if settings:
            # Обновляем существующие настройки
            settings.settings_data = json.dumps(validated_settings)
        else:
            # Создаем новые настройки
            settings = SystemSettings(
                settings_data=json.dumps(validated_settings)
            )
            self.db.add(settings)
        
        self.db.commit()
        self.db.refresh(settings)
        
        return validated_settings

    def _get_default_settings(self) -> Dict[str, Any]:
        """
        Get default system settings
        """
        return {
            "urlPrefix": "https://pte-qr.example.com",
            "documentStatusUrl": "/r",
            "systemName": "PTE QR System",
            "systemDescription": "Система проверки актуальности документов через QR-коды",
            "maxDocumentSize": 10485760,  # 10MB
            "allowedFileTypes": ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "jpg", "jpeg", "png"],
            "sessionTimeout": 3600,  # 1 hour
            "enableNotifications": True,
            "enableAuditLog": True,
            "enableApiRateLimit": True,
            "apiRateLimit": 1000,
            "enableMaintenanceMode": False,
            "maintenanceMessage": "Система временно недоступна для технического обслуживания",
            "enableUserRegistration": False,
            "enableEmailVerification": True,
            "enableTwoFactorAuth": False,
            "enablePasswordReset": True,
            "enableApiDocumentation": True,
            "enableMetrics": True,
            "enableLogging": True,
            "logLevel": "INFO",
            "enableBackup": True,
            "backupFrequency": "daily",
            "enableMonitoring": True,
            "monitoringInterval": 300
        }

    def _validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize settings
        """
        validated = {}
        
        # URL настройки
        if "urlPrefix" in settings:
            url_prefix = settings["urlPrefix"]
            if isinstance(url_prefix, str) and url_prefix.strip():
                validated["urlPrefix"] = url_prefix.strip().rstrip('/')
            else:
                validated["urlPrefix"] = "https://pte-qr.example.com"
        
        if "documentStatusUrl" in settings:
            doc_url = settings["documentStatusUrl"]
            if isinstance(doc_url, str) and doc_url.strip():
                validated["documentStatusUrl"] = doc_url.strip().lstrip('/')
            else:
                validated["documentStatusUrl"] = "r"
        
        # Системные настройки
        if "systemName" in settings:
            system_name = settings["systemName"]
            if isinstance(system_name, str) and system_name.strip():
                validated["systemName"] = system_name.strip()
            else:
                validated["systemName"] = "PTE QR System"
        
        if "systemDescription" in settings:
            system_desc = settings["systemDescription"]
            if isinstance(system_desc, str):
                validated["systemDescription"] = system_desc.strip()
            else:
                validated["systemDescription"] = "Система проверки актуальности документов через QR-коды"
        
        # Числовые настройки
        numeric_fields = {
            "maxDocumentSize": (int, 10485760),
            "sessionTimeout": (int, 3600),
            "apiRateLimit": (int, 1000),
            "monitoringInterval": (int, 300)
        }
        
        for field, (field_type, default_value) in numeric_fields.items():
            if field in settings:
                try:
                    value = field_type(settings[field])
                    if value >= 0:
                        validated[field] = value
                    else:
                        validated[field] = default_value
                except (ValueError, TypeError):
                    validated[field] = default_value
            else:
                validated[field] = default_value
        
        # Булевы настройки
        boolean_fields = [
            "enableNotifications", "enableAuditLog", "enableApiRateLimit",
            "enableMaintenanceMode", "enableUserRegistration", "enableEmailVerification",
            "enableTwoFactorAuth", "enablePasswordReset", "enableApiDocumentation",
            "enableMetrics", "enableLogging", "enableBackup", "enableMonitoring"
        ]
        
        for field in boolean_fields:
            if field in settings:
                validated[field] = bool(settings[field])
            else:
                validated[field] = True  # Дефолтное значение для большинства булевых полей
        
        # Строковые настройки
        string_fields = {
            "maintenanceMessage": "Система временно недоступна для технического обслуживания",
            "logLevel": "INFO",
            "backupFrequency": "daily"
        }
        
        for field, default_value in string_fields.items():
            if field in settings:
                value = settings[field]
                if isinstance(value, str) and value.strip():
                    validated[field] = value.strip()
                else:
                    validated[field] = default_value
            else:
                validated[field] = default_value
        
        # Массив разрешенных типов файлов
        if "allowedFileTypes" in settings:
            file_types = settings["allowedFileTypes"]
            if isinstance(file_types, list):
                validated["allowedFileTypes"] = [
                    str(ft).lower().strip() 
                    for ft in file_types 
                    if isinstance(ft, str) and ft.strip()
                ]
            else:
                validated["allowedFileTypes"] = ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "jpg", "jpeg", "png"]
        else:
            validated["allowedFileTypes"] = ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "jpg", "jpeg", "png"]
        
        return validated
