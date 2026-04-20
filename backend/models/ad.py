# backend/models/ad.py
"""
نموذج الإعلانات العادية
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger
from datetime import datetime, date

from backend.models.base import Base


class AdWatch(Base):
    """جدول مشاهدة الإعلانات"""
    __tablename__ = 'ad_watches'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    date = Column(DateTime, default=datetime.now)
    points_earned = Column(Float, default=0.0)