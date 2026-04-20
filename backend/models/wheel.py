# backend/models/wheel.py
"""
نموذج عجلة الحظ
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger
from datetime import datetime, date

from backend.models.base import Base


class WheelSpin(Base):
    """جدول لعب عجلة الحظ"""
    __tablename__ = 'wheel_spins'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    date = Column(DateTime, default=datetime.now)
    reward_points = Column(Float, default=0.0)