"""
Settings API endpoints
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.schemas import UserResponse
from app.services.settings_service import SettingsService

router = APIRouter()

@router.get("/settings", response_model=Dict[str, Any])
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get system settings
    """
    # Проверяем, что пользователь является администратором
    if not current_user.is_superuser and not any(role.name == 'admin' for role in current_user.roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access settings"
        )
    
    settings_service = SettingsService(db)
    settings = await settings_service.get_settings()
    return settings

@router.put("/settings", response_model=Dict[str, Any])
async def update_settings(
    settings: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update system settings
    """
    # Проверяем, что пользователь является администратором
    if not current_user.is_superuser and not any(role.name == 'admin' for role in current_user.roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update settings"
        )
    
    settings_service = SettingsService(db)
    updated_settings = await settings_service.update_settings(settings)
    return updated_settings
