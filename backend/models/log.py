# backend/models/log.py
"""
نموذج سجل إجراءات الأدمن
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger
from datetime import datetime

from backend.models.base import Base


class AdminLog(Base):
    """جدول سجل إجراءات الأدمن"""
    __tablename__ = 'admin_logs'
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(BigInteger, nullable=False)
    action = Column(String(255))
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)