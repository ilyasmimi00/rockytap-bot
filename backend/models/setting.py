# backend/models/setting.py
"""
نموذج إعدادات النظام
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from backend.models.base import Base


class SystemSetting(Base):
    """جدول إعدادات النظام"""
    __tablename__ = 'system_settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)