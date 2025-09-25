"""
Settings model for storing system configuration
"""

from sqlalchemy import Column, Integer, Text, DateTime, func
from app.core.database import Base

class SystemSettings(Base):
    """
    System settings model
    """
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    settings_data = Column(Text, nullable=True)  # JSON string of settings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
